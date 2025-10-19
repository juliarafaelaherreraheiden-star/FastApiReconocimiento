import firebase_admin
from firebase_admin import credentials, firestore
from opensearchpy import OpenSearch
import unicodedata
import re
import os
import requests
import json
from diccionario_sinonimos import obtener_sinonimos
from opensearch_client import client
from firebase_admin import credentials, initialize_app

# ---------------------
# Configuración Firebase
# ---------------------

firebase_cred_json = os.getenv("FIREBASE_CREDENTIALS")
if not firebase_cred_json:
    raise Exception("No se encontró variable de entorno FIREBASE_CREDENTIALS")

cred_dict = json.loads(firebase_cred_json)

# 🔹 ESTA LÍNEA ES NECESARIA EN TU CASO
cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ---------------------
# Configuración OpenSearch
# ---------------------

# Cambia estos valores a la configuración de tu instancia OpenSearch
host = os.getenv('OPENSEARCH_HOST', 'localhost')
port = int(os.getenv('OPENSEARCH_PORT', 443))
user = os.getenv('OPENSEARCH_USER', 'admin')  # Cambio aquí para que coincida con tu env
password = os.getenv('OPENSEARCH_PASS', 'admin')  # Cambio aquí


# ---------------------
# Funciones auxiliares
# ---------------------
def normalize_text(text):
    """
    Quita acentos, convierte a minúsculas, quita signos de puntuación.
    Esto ayuda a que la búsqueda sea más tolerante.
    """
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode()
    text = re.sub(r"[^\w\s]", "", text)
    return text.lower()

# Simulamos una función que llama a una API de sinónimos para cada ingrediente
def obtener_sinonimos_api(ingredientes):
    return obtener_sinonimos(ingredientes)

def crear_indice_con_sinonimos():
    index_name = "recetas"
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)

    # Sacamos todos los ingredientes que hay en la base
    recetas_ref = db.collection("recetas")
    docs = recetas_ref.stream()
    ingredientes_unicos = set()

    for doc in docs:
        data = doc.to_dict()
        ingredientes = data.get("ingredientes", [])
        for ingr in ingredientes:
            nombre = normalize_text(ingr.get("nombre", ""))
            if nombre:
                ingredientes_unicos.add(nombre)

    # Obtenemos sinónimos solo para los ingredientes que existen
    sinonimos_dict = obtener_sinonimos_api(ingredientes_unicos)

    # Construimos la lista para OpenSearch (sinónimos separados por comas y unidos por saltos de línea)
    lista_sinonimos = []
    for key, values in sinonimos_dict.items():
        linea = ", ".join([key] + values)
        lista_sinonimos.append(linea)
    sinonimos_str = "\n".join(lista_sinonimos)

    index_body = {
        "settings": {
            "analysis": {
                "filter": {
                    "my_synonym_filter": {
                        "type": "synonym",
                        "synonyms": sinonimos_str.split("\n")
                    },
                    "spanish_stemmer": {
                        "type": "stemmer",
                        "language": "light_spanish"
                    }
                },
                "analyzer": {
                    "my_spanish_analyzer": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "my_synonym_filter",
                            "spanish_stemmer"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "titulo": {
                    "type": "text",
                    "analyzer": "my_spanish_analyzer",
                    "boost": 3
                },
                "ingredientes_texto": {
                    "type": "text",
                    "analyzer": "my_spanish_analyzer",
                    "boost": 2
                },
                "descripcion": {
                    "type": "text",
                    "analyzer": "my_spanish_analyzer",
                    "boost": 1.5
                },
                "pasos": {
                    "type": "text",
                    "analyzer": "my_spanish_analyzer"
                },
                "contenido_total": {
                    "type": "text",
                    "analyzer": "my_spanish_analyzer"
                },
                "calorias": {
                    "type": "integer"
                },
                "likes": { "type": "integer" },
                "popup_clicks": { "type": "integer" }
            }
        }
    }

    client.indices.create(index=index_name, body=index_body)
    print(f"✅ Índice '{index_name}' creado con sinónimos dinámicos.")



def crear_indice():
    """
    Crear índice OpenSearch con mapeo para asignar pesos a campos importantes.
    Si el índice ya existe, lo elimina y lo vuelve a crear.
    """
    index_name = "recetas"
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)

    index_body = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "standard"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "titulo": {
                    "type": "text",
                    "boost": 3  # Peso alto en el título
                },
                "ingredientes_texto": {
                    "type": "text",
                    "boost": 2  # Ingredientes tienen buen peso
                },
                "descripcion": {
                    "type": "text",
                    "boost": 1.5
                },
                "pasos": {
                    "type": "text"
                },
                "contenido_total": {
                    "type": "text"
                },
                "calorias": {
                    "type": "integer"
                },
                "likes": { "type": "integer" },
                "popup_clicks": { "type": "integer" }
            }
        }
    }

    client.indices.create(index=index_name, body=index_body)
    print(f"✅ Índice '{index_name}' creado en OpenSearch.")

# ---------------------
# Función principal para exportar e indexar
# ---------------------

def exportar_e_indexar_recetas():

    recetas_ref = db.collection("recetas")
    docs = recetas_ref.stream()

    count = 0
    for doc in docs:
        data = doc.to_dict()
        doc_id = doc.id  # ✅ Usar ID real de Firestore

        ingredientes = [normalize_text(i.get("nombre", "")) for i in data.get("ingredientes", [])]
        pasos = [normalize_text(p.get("descripcion", "")) for p in data.get("pasos", [])]
        titulo = normalize_text(data.get("titulo", ""))
        desc = normalize_text(data.get("descripcion", ""))

        doc_opensearch = {
            "titulo": titulo,
            "ingredientes_texto": " ".join(ingredientes),
            "descripcion": desc,
            "pasos": " ".join(pasos),
            "contenido_total": f"{titulo} {desc} {' '.join(ingredientes)} {' '.join(pasos)}",
            "calorias": data.get("calorias", 0),
            "likes": data.get("likes", 0),
            "popup_clicks": data.get("popup_clicks", 0)
        }

        client.index(index="recetas", id=doc_id, body=doc_opensearch)
        count += 1

    print(f"✅ Exportadas e indexadas {count} recetas en OpenSearch.")

def obtener_receta_por_id(receta_id: str) -> dict | None:
    doc_ref = db.collection("recetas").document(receta_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        
        ingredientes = [normalize_text(i.get("nombre", "")) for i in data.get("ingredientes", [])]
        pasos = [normalize_text(p.get("descripcion", "")) for p in data.get("pasos", [])]
        titulo = normalize_text(data.get("titulo", ""))
        desc = normalize_text(data.get("descripcion", ""))

        return {
            "id": receta_id,
            "titulo": titulo,
            "ingredientes_texto": " ".join(ingredientes),
            "descripcion": desc,
            "pasos": " ".join(pasos),
            "contenido_total": f"{titulo} {desc} {' '.join(ingredientes)} {' '.join(pasos)}",
            "calorias": data.get("calorias", 0),
            "likes": data.get("likes", 0),
            "popup_clicks": data.get("popup_clicks", 0)
        }
    return None

def indexar_una_receta(receta: dict):
    client.index(index="recetas", id=receta["id"], body=receta)


if __name__ == "__main__":
    crear_indice_con_sinonimos()
    exportar_e_indexar_recetas()