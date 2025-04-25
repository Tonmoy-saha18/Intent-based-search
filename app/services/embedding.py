from sentence_transformers import SentenceTransformer

# Load model once globally
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_product_embedding(name: str, description: str = "") -> list[float]:
    text = f"{name}. {description}" if description else name
    embedding = model.encode(text)
    return embedding.tolist()
