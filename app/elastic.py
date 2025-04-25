import time

from elasticsearch import Elasticsearch
from app.config import ELASTICSEARCH_URL

es = Elasticsearch(
                    ELASTICSEARCH_URL,
                    verify_certs=False,  # skip SSL verification if not using HTTPS
                    request_timeout=30
                )

INDEX_NAME = "product"


def wait_for_es(timeout=200):
    for _ in range(timeout):
        if es.ping():
            print("Elasticsearch is ready.")
            return True
        print("Waiting for Elasticsearch...")
        time.sleep(1)
    raise ConnectionError("Elasticsearch is not reachable.")


def create_index():
    wait_for_es()
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
