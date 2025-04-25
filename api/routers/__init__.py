from fastapi import APIRouter
from api.search.search_router import router as search_router
from api.product.import_file import router as product_import_router
from api.product.template import router as product_template_router

router = APIRouter()
router.include_router(search_router)
router.include_router(product_import_router)
router.include_router(product_template_router)