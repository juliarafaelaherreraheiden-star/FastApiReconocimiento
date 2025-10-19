# opensearch_client.py
from opensearchpy import OpenSearch
from dotenv import load_dotenv
import os

load_dotenv()  # Carga desde .env

host = os.getenv('OPENSEARCH_HOST')
port = int(os.getenv('OPENSEARCH_PORT', 443))
user = os.getenv('OPENSEARCH_USER')  # antes: OPENSEARCH_USERNAME
password = os.getenv('OPENSEARCH_PASS')  # antes: OPENSEARCH_PASSWORD

client = OpenSearch(
    hosts=[{"host": host, "port": port}],
    http_auth=(user, password),
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=True,
    ssl_show_warn=True,
    http_compress=True
)
