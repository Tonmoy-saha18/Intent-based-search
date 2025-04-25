from sentence_transformers import SentenceTransformer
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.model = SentenceTransformer(model_name)
        logger.info(f"Loaded embedding model: {model_name}")

    def encode(self, text: str) -> np.ndarray:
        try:
            if isinstance(text, str):
                return self.model.encode(text)
            elif isinstance(text, list):
                return self.model.encode(text)
            else:
                raise ValueError("Input must be string or list of strings")
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            raise

# Singleton instance
embedding_service = EmbeddingService()

def get_embedding(text: str) -> np.ndarray:
    return embedding_service.encode(text)