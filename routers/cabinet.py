from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services import strapi_service

router = APIRouter(prefix="/cabinet", tags=["cabinet"])

class ProductCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = ""
    category: Optional[str] = ""
    specs: Optional[dict] = {}

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    specs: Optional[dict] = None

@router.get("/products")
async def list_products():
    return await strapi_service.get_products()

@router.post("/products")
async def add_product(product: ProductCreate):
    return await strapi_service.create_product(product.model_dump())

@router.put("/products/{product_id}")
async def edit_product(product_id: int, product: ProductUpdate):
    data = {k: v for k, v in product.model_dump().items() if v is not None}
    return await strapi_service.update_product(product_id, data)

@router.delete("/products/{product_id}")
async def remove_product(product_id: int):
    return await strapi_service.delete_product(product_id)