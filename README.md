# Intent-based-search

## Overview

Intent-based-search is a FastAPI application for semantic product search. It combines MongoDB for product storage, Qdrant for vector similarity search, and Sentence Transformers for embedding generation. The service also includes intent refinement via a Gemini-style API call and has monitoring support with Prometheus metrics.

## Features

- Import individual products via JSON payload
- Bulk import products from CSV files
- Intent-aware vector search over product data
- Protected admin-only endpoint for listing all products
- Rate limiting for key endpoints
- Prometheus metrics exposed at `/metrics`
- Qdrant vector search integration with MongoDB metadata lookup

## Architecture

- `app/main.py`: FastAPI application entrypoint, request rate limiting, and Prometheus metrics
- `app/api/v1/product.py`: API router for product import, search, and authentication
- `app/services/product_service.py`: Business logic for inserting products, generating embeddings, and searching
- `app/services/embedding.py`: Sentence Transformer embedding generation
- `app/db/mongo.py`: Async MongoDB connection and product collection access
- `app/db/qrdant.py`: Qdrant collection initialization, vector storage, and search
- `app/model/intent_extractor.py`: Query intent refinement using Gemini API
- `app/schemas/product.py`: Pydantic product schemas

## Requirements

- Python 3.10+
- MongoDB
- Qdrant
- Docker / Docker Compose (optional, for local stack)
- `requirements.txt` dependencies include FastAPI, Uvicorn, Motor, Sentence Transformers, Qdrant Client, SlowAPI, OpenTelemetry, Prometheus client, and more.

## Setup

1. Clone the repository

```bash
git clone https://github.com/Tonmoy-saha18/Intent-based-search.git
cd Intent-based-search
```

2. Start dependent services with Docker Compose

```bash
docker-compose up -d
```

3. Install Python dependencies

```bash
pip install -r requirements.txt
```

4. Run the app

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment variables

The app uses these defaults if not configured:

- `MONGO_URL` - MongoDB connection string (default: `mongodb://localhost:27017`)
- `DB_NAME` - MongoDB database name (default: `productdb`)

> Note: `app/model/intent_extractor.py` currently embeds a Gemini API key directly in code. For production use, replace it with a secure environment variable.

## API Endpoints

### Authentication

- `POST /api/v1/products/token`
  - Request body: `application/x-www-form-urlencoded`
  - Fields: `username`, `password`
  - Returns: `access_token` and `token_type`

### Product import

- `POST /api/v1/products/import`
  - Request body: JSON product object
  - Fields:
    - `name` (string)
    - `description` (string, optional)
    - `category` (string)
    - `brand` (string, optional)
    - `price` (float)
    - `lan` (string)

- `POST /api/v1/products/import/csv`
  - Request body: multipart form upload with `file` set to a `.csv`
  - Returns the count of inserted products

### Search

- `POST /api/v1/products/search/`
  - Query parameters: `query` (string), `rank` (integer, default `10`)
  - Returns: list of matching products by semantic similarity

### Admin-only product listing

- `GET /api/v1/products/`
  - Requires a valid Bearer token with admin privileges
  - Returns all products stored in MongoDB

### Monitoring

- `GET /metrics`
  - Exposes Prometheus metrics for request rates and latency

## Sample requests

### Import a product

```bash
curl -X POST http://localhost:8000/api/v1/products/import \
  -H "Content-Type: application/json" \
  -d '{"name":"Nike Air Max 270","description":"Lightweight running shoes","category":"Footwear","brand":"Nike","price":149.99,"lan":"en"}'
```

### Search products

```bash
curl -X POST "http://localhost:8000/api/v1/products/search/?query=running%20shoes&rank=5"
```

## Notes

- Qdrant runs on port `6333` and stores product vectors in the `products` collection.
- MongoDB stores product metadata in the `productdb` database.
- The intent refinement step is implemented in `app/model/intent_extractor.py`.
- If you need CSV upload support, ensure your file contains headers like `name,description,category,brand,price,stock,tags`.
