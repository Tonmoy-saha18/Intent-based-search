from typing import List, Dict, Optional
from storage.vector import VectorStore
from storage.catalog.store import ProductStore
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ProductRetriever:
    def __init__(self, vector_store: VectorStore, product_store: ProductStore):
        self.vector_store = vector_store
        self.product_store = product_store

    def retrieve(
            self,
            query_vector: np.ndarray,
            k: int = 100,
            filters: Optional[Dict] = None
    ) -> List[Dict]:
        try:
            # Get similar product IDs from vector store
            product_ids = self.vector_store.search(
                vector=query_vector,
                k=k,
                filters=filters
            )

            # Get full product data
            products = self.product_store.bulk_get(product_ids)

            return products
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            raise


def get_retriever():
    from storage.vector.store import get_vector_store
    from storage.catalog.store import get_product_store
    return ProductRetriever(get_vector_store(), get_product_store())