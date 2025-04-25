from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from io import StringIO
import csv
from datetime import datetime
from typing import List
import logging
from storage.catalog.store import ProductStore
from services.embedding.service import get_embedding
import numpy as np

router = APIRouter()


class CSVImportResponse(BaseModel):
    total_processed: int
    successful: int
    failed: int
    errors: List[str] = []


@router.post("/products/import", response_model=CSVImportResponse)
async def import_products(
        file: UploadFile = File(...),
        product_store: ProductStore = Depends(ProductStore)
):
    """
    Import products from CSV file.
    Expected CSV format:
    product_id,title,description,category,price,attributes
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    try:
        contents = await file.read()
        csv_file = StringIO(contents.decode('utf-8'))
        reader = csv.DictReader(csv_file)

        results = CSVImportResponse(
            total_processed=0,
            successful=0,
            failed=0
        )

        batch = []
        batch_size = 100

        for row in reader:
            try:
                # Validate and transform CSV row
                product = _transform_row(row)
                batch.append(product)
                results.total_processed += 1

                # Process batch when full
                if len(batch) >= batch_size:
                    await _process_batch(batch, product_store)
                    results.successful += len(batch)
                    batch = []

            except Exception as e:
                results.failed += 1
                results.errors.append(f"Row {results.total_processed + 1}: {str(e)}")
                logging.error(f"Failed to process row: {str(e)}")

        # Process remaining items in final batch
        if batch:
            await _process_batch(batch, product_store)
            results.successful += len(batch)

        return results

    except Exception as e:
        logging.error(f"Import failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process CSV file")


def _transform_row(row: dict) -> dict:
    """Convert CSV row to product document"""
    required_fields = ['product_id', 'title', 'category', 'price']
    for field in required_fields:
        if field not in row:
            raise ValueError(f"Missing required field: {field}")

    # Convert price to float
    try:
        price = float(row['price'])
    except ValueError:
        raise ValueError(f"Invalid price value: {row['price']}")

    # Build attributes dictionary
    attributes = {}
    if 'attributes' in row and row['attributes']:
        try:
            attributes = eval(row['attributes'])  # Expects properly formatted string
        except:
            attributes = {'raw': row['attributes']}

    return {
        "product_id": row['product_id'],
        "title": row['title'],
        "description": row.get('description', ''),
        "category": row['category'].split('|'),  # Pipe-delimited hierarchy
        "price": price,
        "attributes": attributes,
        "last_updated": datetime.utcnow(),
        "vector": None  # Will be set during batch processing
    }


async def _process_batch(batch: List[dict], product_store: ProductStore):
    """Process a batch of products including embedding generation"""
    # Generate embeddings for descriptions
    texts = [f"{p['title']} {p['description']}" for p in batch]
    embeddings = get_embedding(texts)

    # Add vectors to products
    for product, vector in zip(batch, embeddings):
        product['vector'] = vector.tolist()

    # Bulk insert to MongoDB
    for product in batch:
        product_store.update_product(product['product_id'], product)