from fastapi import APIRouter
from services import strapi_service

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
async def get_products():
    return await strapi_service.get_products()

@router.get("/{product_id}")
async def get_product(product_id: int):
    return await strapi_service.get_product(product_id)

@router.post("/")
async def create_product(data: dict):
    return await strapi_service.create_product(data)

@router.put("/{product_id}")
async def update_product(product_id: int, data: dict):
    return await strapi_service.update_product(product_id, data)

@router.delete("/{product_id}")
async def delete_product(product_id: int):
    return await strapi_service.delete_product(product_id)