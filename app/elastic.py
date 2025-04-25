from elasticsearch import Elasticsearch
from app.config import ELASTICSEARCH_URL
import logging

es = Elasticsearch(
                    ELASTICSEARCH_URL,
                    verify_certs=False,  # skip SSL verification if not using HTTPS
                    request_timeout=30
                )

INDEX_NAME = "product"
logger = logging.getLogger("Logger")


def create_index():
    print(es.ping())
    if not es.indices.exists(index=INDEX_NAME):
        print("Creating index: ", INDEX_NAME)
        es.indices.create(index=INDEX_NAME)


def index_product_es(product_id: int, data: dict):
    es.index(index=INDEX_NAME, id=product_id, body=data)


def get_product_es(product_id: int):
    try:
        return es.get(index=INDEX_NAME, id=product_id)["_source"]
    except:
        return None
