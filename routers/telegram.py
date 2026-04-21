from fastapi import APIRouter, Request
import httpx
from services import strapi_service, claude_service
from config import TELEGRAM_TOKEN

router = APIRouter(prefix="/webhook", tags=["telegram"])

async def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})

@router.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not text:
        return {"ok": True}

    # Claude парсит текст → JSON товара (сейчас mock)
    product_data = await claude_service.parse_product(text)

    # Сохраняем товар в Strapi
    result = await strapi_service.create_product(product_data)

    product_name = result.get("data", {}).get("name", "Товар")

    # Отвечаем пользователю в Telegram
    await send_telegram_message(
        chat_id,
        f"✅ Товар '{product_name}' добавлен в магазин!"
    )

    return {"ok": True}


# from fastapi import APIRouter, Request
# from services import strapi_service, claude_service
#
# router = APIRouter(prefix="/webhook", tags=["telegram"])
#
#
# @router.post("/telegram")
# async def telegram_webhook(request: Request):
#     data = await request.json()
#
#     # Получаем сообщение из Telegram
#     message = data.get("message", {})
#     chat_id = message.get("chat", {}).get("id")
#     text = message.get("text", "")
#
#     if not text:
#         return {"ok": True}
#
#     # Claude парсит текст → JSON товара (сейчас mock)
#     product_data = await claude_service.parse_product(text)
#
#     # Сохраняем товар в Strapi
#     result = await strapi_service.create_product(product_data)
#
#     return {
#         "ok": True,
#         "chat_id": chat_id,
#         "product_saved": result
#     }