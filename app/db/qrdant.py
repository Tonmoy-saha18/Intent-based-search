from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid

client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "products"


# Create the collection if not exists
def init_collection():
    if COLLECTION_NAME not in [col.name for col in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )


# Store embedding with metadata
def store_product_vector(product_id: str, embedding: list[float]):
    point = PointStruct(
        id=product_id,
        vector=embedding
    )
    client.upsert(collection_name=COLLECTION_NAME, points=[point])
