import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from app.config import VECTOR_DB_PATH

model = SentenceTransformer('all-MiniLM-L6-v2')

if os.path.exists(VECTOR_DB_PATH):
    index = faiss.read_index(VECTOR_DB_PATH)
    id_map = faiss.read_index("id_map.index")
else:
    index = faiss.IndexFlatL2(384)
    id_map = faiss.IndexIDMap(index)

def index_product_vector(product_id: int, description: str):
    embedding = model.encode([description])
    id_map.add_with_ids(np.array(embedding).astype('float32'), np.array([product_id]))
    faiss.write_index(id_map, "id_map.index")