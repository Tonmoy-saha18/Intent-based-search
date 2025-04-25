import faiss
import numpy as np
from typing import List, Optional, Dict
import os
import pickle
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.index = None
        self.id_to_index = {}
        self.index_path = os.getenv("FAISS_INDEX_PATH", "data/faiss_index.pkl")
        self.load_index()

    def load_index(self):
        try:
            if os.path.exists(self.index_path):
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    self.index = data["index"]
                    self.id_to_index = data["id_to_index"]
                logger.info(f"Loaded FAISS index with {len(self.id_to_index)} vectors")
            else:
                self.index = faiss.IndexFlatL2(384)  # Default dimension
                self.id_to_index = {}
                logger.warning("Created new empty FAISS index")
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {str(e)}")
            raise

    def save_index(self):
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            with open(self.index_path, "wb") as f:
                pickle.dump({
                    "index": self.index,
                    "id_to_index": self.id_to_index
                }, f)
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {str(e)}")
            raise

    def add_vectors(self, ids: List[str], vectors: np.ndarray):
        if len(ids) != vectors.shape[0]:
            raise ValueError("IDs and vectors count mismatch")

        start_idx = len(self.id_to_index)
        for i, product_id in enumerate(ids):
            self.id_to_index[product_id] = start_idx + i

        if not self.index:
            self.index = faiss.IndexFlatL2(vectors.shape[1])

        self.index.add(vectors)
        self.save_index()

    def search(
            self,
            vector: np.ndarray,
            k: int = 10,
            filters: Optional[Dict] = None
    ) -> List[str]:
        if not self.index:
            return []

        # Convert to 2D array if needed
        if len(vector.shape) == 1:
            vector = np.array([vector])

        # Search
        distances, indices = self.index.search(vector, k)

        # Map back to product IDs
        product_ids = []
        for idx in indices[0]:
            if idx == -1:  # FAISS returns -1 for empty slots
                continue

            for product_id, stored_idx in self.id_to_index.items():
                if stored_idx == idx:
                    product_ids.append(product_id)
                    break

        return product_ids


def get_vector_store():
    return VectorStore()