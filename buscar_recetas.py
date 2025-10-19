from opensearch_client import client
import string

# Configuración (igual que en tu otro código)
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "admin"


SINONIMOS_INGREDIENTES = {
    "pollo": ["gallina", "ave"],
    "gallina": ["pollo", "ave"],
    "ave": ["pollo", "gallina"],
    
    "ajo": ["diente de ajo", "ajo fresco"],
    "diente de ajo": ["ajo", "ajo fresco"],
    "ajo fresco": ["ajo", "diente de ajo"],

    "azúcar": ["azucar", "dulce", "azúcar refinado"],
    "azucar": ["azúcar", "dulce", "azúcar refinado"],
    "dulce": ["azúcar", "azucar"],
    "azúcar refinado": ["azúcar", "azucar"],

    "tomate": ["jitomate", "tomate rojo"],
    "jitomate": ["tomate", "tomate rojo"],
    "tomate rojo": ["tomate", "jitomate"],
}

def expandir_con_sinonimos(query):
    palabras = query.lower().split()
    consulta_expandida = []
    
    for palabra in palabras:
        sinonimos = SINONIMOS_INGREDIENTES.get(palabra, [])
        # Incluye la palabra original + sus sinónimos
        palabras_para_buscar = [palabra] + sinonimos
        
        # Por cada palabra + sinónimos hacemos una consulta tipo should (OR)
        consulta_expandida.append({
            "multi_match": {
                "query": " ".join(palabras_para_buscar),
                "fields": ["titulo^3", "ingredientes_texto^2", "descripcion", "pasos", "contenido_total"],
                "fuzziness": "AUTO",
                "operator": "or"
            }
        })
    
    return {
        "bool": {
            "must": consulta_expandida
        }
    }

def buscar_recetas(query, index="recetas", size=5, return_hits=False):
    query_expandida = expandir_con_sinonimos(query)

    body = {
    "query": {
        "function_score": {
            "query": query_expandida,
            "functions": [
                {
                    "field_value_factor": {
                        "field": "likes",
                        "factor": 1,
                        "modifier": "log1p",
                        "missing": 0
                    }
                },
                {
                    "field_value_factor": {
                        "field": "popup_clicks",
                        "factor": 0.5,  # menos peso que likes
                        "modifier": "log1p",
                        "missing": 0
                    }
                }
            ],
            "score_mode": "sum",
            "boost_mode": "sum"
        }
    },
    "rescore": {  # opcional, mantiene coincidencias exactas
        "window_size": 50,
        "query": {
            "rescore_query": {
                "multi_match": {
                    "query": query,
                    "fields": ["titulo^3", "ingredientes_texto^2", "descripcion", "pasos", "contenido_total"],
                    "type": "phrase",
                    "slop": 3
                }
            },
            "query_weight": 0.7,
            "rescore_query_weight": 1.8
        }
    },
    "size": 10
}


    response = client.search(index=index, body=body, size=size)
    hits = response.get("hits", {}).get("hits", [])

    recetas = []
    for hit in hits:
        source = hit["_source"]

        pasos_raw = source.get("pasos", "")
        pasos_lista = []

        if isinstance(pasos_raw, str):
            lineas = [linea.strip() for linea in pasos_raw.split('.') if linea.strip()]
            pasos_lista = [
                {"descripcion": linea, "imagen_url": "", "orden": idx + 1}
                for idx, linea in enumerate(lineas)
            ]
        elif isinstance(pasos_raw, list):
            pasos_lista = pasos_raw

        recetas.append({
            "id": hit["_id"],
            "titulo": source.get("titulo", ""),
            "descripcion": source.get("descripcion", ""),
            "imagen_final_url": source.get("imagen_final_url", ""),
            "calorias": source.get("calorias", 0),
            "tiempoPreparacion": source.get("tiempoPreparacion", ""),
            "porciones": source.get("porciones", 1),
            "ingrediente_principal": source.get("ingrediente_principal", ""),
            "ingredientes": source.get("ingredientes", []),
            "pasos": pasos_lista,
            "likes": source.get("likes", 0),
            "popup_clicks": source.get("popup_clicks", 0),
            "liked_by": source.get("liked_by", [])  # si lo estás usando en tu lógica de likes
        })



    if return_hits:
        return recetas

    if not hits:
        print("No se encontraron recetas para la búsqueda:", query_expandida)
        return

    for receta in recetas:
        print(f"\nTítulo: {receta['titulo']}")
        print(f"Ingredientes: {receta['ingredientes']}")
        print(f"Descripción: {receta['descripcion']}")
        print(f"Pasos: {receta['pasos']}")
        print("-" * 40)
        



def limpiar_stopwords(texto):
    texto = texto.lower()
    texto = texto.translate(str.maketrans('', '', string.punctuation))

    stopwords = {
        "Quiero","quiero", "una", "unas", "un", "unos",
        "que", "ke",  
        "tenga", "tengo", "tienes", "tiene", "tener",
        "reseta", "receta", 
        "el", "la", "los", "las",
        "y", "o", "u",
        "de", "del", "en", "con", "para", "por", "se", "al", "a", "mi", "tu", "su",
        "como", "más", "menos", "sin", "pero", "si",
        "me", "te", "le", "lo", "nos", "os", "les",
        "este", "esta", "estos", "estas",
        "es", "son", "fue", "era", "ser",
        "hoy", "ahora",
        "durante",
        "desde", "hasta",
        "antes", "después", "luego",
        "también",
        "algo",
        "mucho", "muchos", "poco", "pocos",
        "cada",
        "todos", "todas",
        "donde",
        "cuando",
        "cual", "cuales",
        "porque", "por qué"
    }
    palabras = texto.split()
    palabras_filtradas = [p for p in palabras if p not in stopwords]
    return " ".join(palabras_filtradas)

if __name__ == "__main__":
    while True:
        consulta = input("Ingrese ingrediente o palabra para buscar recetas (o 'salir' para terminar): ").strip()
        query = limpiar_stopwords(consulta)
        print("🔍 Texto limpio:", query)
        if consulta.lower() == "salir":
            break
        buscar_recetas(query)
