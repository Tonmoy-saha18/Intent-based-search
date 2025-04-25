from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from shared.csv_utils import generate_csv_template

router = APIRouter()

@router.get("/products/import/template", response_class=PlainTextResponse)
async def get_import_template():
    """Download CSV template for product imports"""
    return generate_csv_template()