from sentence_transformers import SentenceTransformer

# Load model once globally
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_product_embedding(product: dict) -> list[float]:
    text = prepare_embedding_text(product)
    embedding = model.encode(text)
    return embedding.tolist()


def prepare_embedding_text(product: dict) -> str:
    name = product.get("name", "")
    description = product.get("description", "")
    price = product.get("price", "")
    category = product.get("category", "")
    sub_category = product.get("sub_category", "")
    brand = product.get("brand", "")
    tags = " ".join(product.get("tags", []))

    # Specifications should be a dict
    specifications = product.get("specifications", {})
    specs_text = " ".join([f"{k}: {v}" for k, v in specifications.items()])

    # Construct combined text
    combined_text = " ".join([
        name,
        description,
        f"Price: {price} taka" if price else "",
        f"Category: {category} {sub_category}".strip(),
        f"Brand: {brand}" if brand else "",
        tags,
        specs_text
    ])

    return combined_text.strip()


def generate_embedding(query: str):
    return model.encode(query).tolist()
