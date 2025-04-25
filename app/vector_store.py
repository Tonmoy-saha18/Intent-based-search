from __future__ import annotations

from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance, CollectionStatus
from sentence_transformers import SentenceTransformer

QDRANT_HOST = "qdrant"  # or "qdrant" if inside Docker network
QDRANT_PORT = 6333
COLLECTION_NAME = "product_vectors"

model = SentenceTransformer('all-MiniLM-L6-v2')
DIM = 384  # embedding size of MiniLM

# Initialize client
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Create collection if it doesn't exist
collections = client.get_collections().collections
collection_names = [c.name for c in collections]

if COLLECTION_NAME not in collection_names:
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=DIM, distance=Distance.COSINE)
    )


def index_product_vector(product_id: int, name: str, description: str, price: float, category: Optional[str] = None):
    embedding = model.encode(description).tolist()

    payload = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
    }

    point = PointStruct(
        id=product_id,
        vector=embedding,
        payload=payload
    )

    client.upsert(collection_name=COLLECTION_NAME, points=[point])

