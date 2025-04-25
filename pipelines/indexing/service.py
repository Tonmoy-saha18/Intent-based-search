from storage.catalog.store import ProductStore
from services.embedding.service import get_embedding
from storage.vector import VectorStore
from typing import List, Dict
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class IndexingPipeline:
    def __init__(self):
        self.product_store = ProductStore()
        self.vector_store = VectorStore()

    def run_full_indexing(self, batch_size: int = 1000):
        logger.info("Starting full indexing process")

        # Get all product IDs
        product_ids = []
        cursor = self.product_store.products.find({}, {"product_id": 1})
        for doc in cursor:
            product_ids.append(doc["product_id"])

        # Process in batches
        for i in range(0, len(product_ids), batch_size):
            batch_ids = product_ids[i:i + batch_size]
            self._process_batch(batch_ids)

        logger.info("Completed full indexing")

    def _process_batch(self, product_ids: List[str]):
        logger.info(f"Processing batch of {len(product_ids)} products")

        # Get product data
        products = self.product_store.bulk_get(product_ids)

        # Generate embeddings
        texts = [
            f"{p['title']} {p['description']}"
            for p in products
        ]
        vectors = get_embedding(texts)

        # Update vector store
        self.vector_store.add_vectors(product_ids, vectors)

        # Update products with vectors
        for product, vector in zip(products, vectors):
            self.product_store.update_product(
                product["product_id"],
                {"vector": vector.tolist(), "last_updated": datetime.utcnow()}
            )


def run_indexing():
    pipeline = IndexingPipeline()
    pipeline.run_full_indexing()