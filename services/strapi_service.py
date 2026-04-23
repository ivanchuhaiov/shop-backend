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
    result = await get_products()
    products = result.get("data", [])

    for p in products:
        if p.get("id") == product_id:
            return {"data": p}

    return {"data": None}

async def create_product(data: dict):
    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{STRAPI_URL}/api/products",
            headers=HEADERS,
            json={"data": data}
        )

        return response.json()

async def update_product(product_id: int, data: dict):
    result = await get_products()
    products = result.get("data", [])
    doc_id = None

    for p in products:
        if p.get("id") == product_id:
            doc_id = p.get("documentId")
            break
    if not doc_id:
        return {"error": "Not found"}

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{STRAPI_URL}/api/products/{doc_id}",
            headers=HEADERS,
            json={"data": data}
        )
        return response.json()

async def delete_product(product_id: int):
    result = await get_products()
    products = result.get("data", [])
    doc_id = None

    for p in products:
        if p.get("id") == product_id:
            doc_id = p.get("documentId")
            break
    if not doc_id:
        return {"error": "Not found"}

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{STRAPI_URL}/api/products/{doc_id}",
            headers=HEADERS
        )
        if response.status_code == 204:
            return {"ok": True}
        return response.json()