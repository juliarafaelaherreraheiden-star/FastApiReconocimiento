import json
from opensearchpy import OpenSearch, helpers
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# OpenSearch connection details from .env
host = os.getenv('OPENSEARCH_HOST')
port = int(os.getenv('OPENSEARCH_PORT'))
auth = (os.getenv('OPENSEARCH_USERNAME'), os.getenv('OPENSEARCH_PASSWORD'))

# Initialize OpenSearch client
client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_compress=True,
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

# Define index name
index_name = 'epirecipes'

# Define index mapping
mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "text"},
            "ingredients": {"type": "text"},
            "categories": {"type": "keyword"},
            "calories": {"type": "integer"},
            "protein": {"type": "integer"},
            "fat": {"type": "integer"},
            "sodium": {"type": "integer"},
            "rating": {"type": "float"},
            "date": {"type": "date"},
            "desc": {"type": "text"},
            "directions": {"type": "text"}
        }
    }
}

# Create index if it doesn't exist
if not client.indices.exists(index=index_name):
    client.indices.create(index=index_name, body=mapping)
    print(f"Created index '{index_name}'")
else:
    print(f"Index '{index_name}' already exists")

# Load JSON data
file_path = '../data/epirecipes/full_format_recipes.json'
with open(file_path) as f:
    data = json.load(f)

# Prepare documents for bulk indexing
actions = []
for idx, doc in enumerate(data):
    # Assuming the structure of the JSON data matches the following fields
    actions.append({
        "_index": index_name,
        "_id": idx,  # Optionally use the row index or some unique ID
        "_source": {
            "id": idx,
            "title": doc.get('title', 'No Title'),
            "ingredients": doc.get('ingredients', []),
            "categories": doc.get('categories', []),
            "calories": doc.get('calories', 0),
            "protein": doc.get('protein', 0),
            "fat": doc.get('fat', 0),
            "sodium": doc.get('sodium', 0),
            "rating": doc.get('rating', 0.0),
            "date": doc.get('date', None),
            "desc": doc.get('desc', None),
            "directions": doc.get('directions', [])
        }
    })

# Bulk index the data into OpenSearch
try:
    helpers.bulk(client, actions)
    print(f"Indexed {len(actions)} documents into '{index_name}'")
except Exception as e:
    print(f"Error during bulk indexing: {e}")
