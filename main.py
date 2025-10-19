from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from buscar_recetas import buscar_recetas, limpiar_stopwords
from opensearch_client import client  
import os
from scripts.firestore_to_opensearch import crear_indice_con_sinonimos, exportar_e_indexar_recetas  # <--- IMPORTA LAS FUNCIONES
import time
from opensearchpy import exceptions
from routes.recetas import router as recetas_router

app = FastAPI(title="Buscador de Recetas")
app.include_router(recetas_router)

host = os.getenv('OPENSEARCH_HOST', 'localhost')
port = int(os.getenv('OPENSEARCH_PORT', 443))
user = os.getenv('OPENSEARCH_USER', 'admin')
password = os.getenv('OPENSEARCH_PASS', 'admin')


@app.get("/")
def read_root():
    return {"message": "Hola FastAPI"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/buscar")
def buscar(query: str = Query(..., description="Palabras clave para buscar recetas")):
    try:
        texto_filtrado = limpiar_stopwords(query)
        resultados = buscar_recetas(texto_filtrado, return_hits=True)  # usamos versión modificada
        return {
            "query_original": query,
            "query_filtrada": texto_filtrado,
            "total_resultados": len(resultados),
            "resultados": resultados
            }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/ping")
def ping_opensearch():
    try:
        if client.ping():
            return {"status": "OpenSearch OK"}
        else:
            return {"status": "OpenSearch no responde"}
    except Exception as e:
        return {"error": str(e)}

# @app.post("/admin/reindexar")
# def reindexar():
#     try:
#         from scripts.firestore_to_opensearch import exportar_e_indexar_recetas, crear_indice_con_sinonimos
#         crear_indice_con_sinonimos()
#         exportar_e_indexar_recetas()
#         return {"status": "Recetas reindexadas correctamente"}
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})
@app.post("/admin/reindexar")
def reindexar():
    index_name = "recetas"
    try:
        # Intentar eliminar si existe
        if client.indices.exists(index=index_name):
            try:
                client.indices.delete(index=index_name)
                print(f"Índice '{index_name}' eliminado correctamente.")
                time.sleep(1)
            except Exception as e:
                print(f"No se pudo eliminar el índice: {e}")

        # Crear índice (pero solo si no existe)
        try:
            if not client.indices.exists(index=index_name):
                crear_indice_con_sinonimos()
                print(f"Índice '{index_name}' creado correctamente.")
            else:
                print(f"Índice '{index_name}' ya existe, se usará tal cual.")
        except exceptions.RequestError as e:
            if "resource_already_exists_exception" in str(e):
                print("El índice ya existía, continuando...")
            else:
                raise

        # Reindexar las recetas desde Firebase
        total = exportar_e_indexar_recetas()
        return {"message": f"Reindexado correctamente ({total} recetas)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter
from scripts.firestore_to_opensearch import obtener_receta_por_id, indexar_una_receta

router = APIRouter()

@router.post("/admin/reindexar_receta/{receta_id}")
def reindexar_receta_individual(receta_id: str):
    receta = obtener_receta_por_id(receta_id)
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    indexar_una_receta(receta)
    return {"message": f"Receta {receta_id} reindexada con éxito"}

