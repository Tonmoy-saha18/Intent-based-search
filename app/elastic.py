from elasticsearch import Elasticsearch
from app.config import ELASTICSEARCH_URL

es = Elasticsearch(ELASTICSEARCH_URL)

INDEX_NAME = "products"


def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME)


def index_product_es(product_id: int, data: dict):
    es.index(index=INDEX_NAME, id=product_id, body=data)


def get_product_es(product_id: int):
    try:
        return es.get(index=INDEX_NAME, id=product_id)["_source"]
    except:
        return None
