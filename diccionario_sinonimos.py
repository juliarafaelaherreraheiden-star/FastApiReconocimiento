# diccionario_sinonimos.py

SINONIMOS_INGREDIENTES = {
    "pollo": ["gallina", "ave"],
    "ajo": ["diente de ajo", "ajo fresco"],
    "azúcar": ["azucar", "dulce", "azúcar refinado"],
    "tomate": ["jitomate", "tomate rojo"],
    # Agrega aquí más ingredientes y sus sinónimos
}

def obtener_sinonimos(ingredientes):
    resultado = {}
    for ingr in ingredientes:
        if ingr in SINONIMOS_INGREDIENTES:
            resultado[ingr] = SINONIMOS_INGREDIENTES[ingr]
    return resultado
