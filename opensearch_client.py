from opensearchpy import OpenSearch
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("OPENSEARCH_HOST")
port = int(os.getenv("OPENSEARCH_PORT", 443))
user = os.getenv("OPENSEARCH_USER")
password = os.getenv("OPENSEARCH_PASS")  # o PASSWORD según tengas

if not all([host, user, password]):
    raise ValueError("❌ Faltan variables de conexión a OpenSearch (HOST, USER, PASS)")

client = OpenSearch(
    hosts=[{"host": host, "port": port}],
    http_auth=(user, password),
    use_ssl=True,
    verify_certs=True,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
    http_compress=True
)

print(f"✅ Conectado a OpenSearch en {host}:{port}")
