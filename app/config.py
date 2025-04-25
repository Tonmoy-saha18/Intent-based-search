import os

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "vector.index")
