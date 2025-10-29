# opensearch_client.py
from opensearchpy import OpenSearch
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

# Cargar variables desde el archivo .env
load_dotenv()

bonsai_url = os.getenv("OPENSEARCH_HOST")

if not bonsai_url:
    raise ValueError("❌ No se encontró OPENSEARCH_HOST en el archivo .env")

# Analizar la URL para extraer host, usuario y contraseña
parsed = urlparse(bonsai_url)
host = parsed.hostname
port = parsed.port or 443
scheme = parsed.scheme
user = parsed.username
password = parsed.password

# Crear cliente de OpenSearch
client = OpenSearch(
    hosts=[{"host": host, "port": port}],
    http_auth=(user, password),
    use_ssl=(scheme == "https"),
    verify_certs=True,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
    http_compress=True
)

print(f"✅ Conectado a OpenSearch en {host}:{port} (SSL={scheme == 'https'})")
