import httpx
from config import STRAPI_URL, STRAPI_TOKEN

HEADERS = {
    "Authorization": f"Bearer {STRAPI_TOKEN}",
    "Content-Type": "application/json"
}

async def get_products():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{STRAPI_URL}/api/products", headers=HEADERS)
        return response.json()

async def get_product(product_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{STRAPI_URL}/api/products/{product_id}", headers=HEADERS)
        return response.json()

async def create_product(data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{STRAPI_URL}/api/products",
            headers=HEADERS,
            json={"data": data}
        )
        return response.json()

async def update_product(product_id: int, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{STRAPI_URL}/api/products/{product_id}",
            headers=HEADERS,
            json={"data": data}
        )
        return response.json()

async def delete_product(product_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{STRAPI_URL}/api/products/{product_id}",
            headers=HEADERS
        )
        return response.json()