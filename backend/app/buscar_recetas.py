from opensearchpy import OpenSearch
import string

# Configuración (igual que en tu otro código)
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "admin"

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
    use_ssl=False,
    verify_certs=False,
)

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
    
    # Luego juntamos todo con un bool must (AND entre las palabras/sinonimos)
    return {
        "bool": {
            "must": consulta_expandida
        }
    }

# def buscar_recetas(query, index="recetas", size=5):
#     query_expandida = expandir_con_sinonimos(query)
#     # body = {
#     #     "query": {
#     #         "multi_match": {
#     #             "query": query,
#     #             "fields": ["titulo^3", "ingredientes_texto^2", "descripcion", "pasos", "contenido_total"],
#     #             "fuzziness": "AUTO"  # Aquí añadimos fuzziness
#     #         }
#     #     }
#     # }
#     body = {
#     "query": query_expandida,
#     "rescore": {
#         "window_size": 50,  # Número de resultados a reordenar (ajusta según tu necesidad)
#         "query": {
#             "rescore_query": {
#                 "multi_match": {
#                     "query": query,
#                     "fields": ["titulo^3", "ingredientes_texto^2", "descripcion", "pasos", "contenido_total"],
#                     "type": "phrase",  # Busca frases ordenadas, más exactas
#                     "slop": 3          # Permite que las palabras estén separadas o en distinto orden hasta cierto punto
#                 }
#             },
#             "query_weight": 0.7,   # Peso de la consulta original
#             "rescore_query_weight": 1.8  # Peso del rescore (más importancia al rescore)
#         }
#     }
# }


#     response = client.search(index=index, body=body, size=size)

#     hits = response.get("hits", {}).get("hits", [])
    
#     if not hits:
#         print("No se encontraron recetas para la búsqueda:", query_expandida)
#         return

#     for hit in hits:
#         source = hit["_source"]
#         print(f"\nTítulo: {source.get('titulo', '')}")
#         print(f"Ingredientes: {source.get('ingredientes_texto', '')}")
#         print(f"Descripción: {source.get('descripcion', '')}")
#         print(f"Pasos: {source.get('pasos', '')}")
#         print("-" * 40)
def buscar_recetas(query, index="recetas", size=5, return_hits=False):
    query_expandida = expandir_con_sinonimos(query)

    body = {
        "query": query_expandida,
        "rescore": {
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
        }
    }

    response = client.search(index=index, body=body, size=size)
    hits = response.get("hits", {}).get("hits", [])

    recetas = []
    for hit in hits:
        source = hit["_source"]
        recetas.append({
            "titulo": source.get("titulo", ""),
            "ingredientes": source.get("ingredientes_texto", ""),
            "descripcion": source.get("descripcion", ""),
            "pasos": source.get("pasos", ""),
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
    # Elimina puntuación (como comas, puntos, etc.)
    texto = texto.translate(str.maketrans('', '', string.punctuation))

    stopwords = {
        "Quiero","quiero", "una", "unas", "un", "unos",
        "que", "ke",  # <-- aquí agregamos "ke"
        "tenga", "tengo", "tienes", "tiene", "tener",
        "reseta", "receta",  # <-- error común, puedes corregirlo o quitarlo
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
