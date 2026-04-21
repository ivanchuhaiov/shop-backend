from fastapi import APIRouter
from pydantic import BaseModel
from services import strapi_service, claude_service

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    message: str


@router.post("/")
async def chat(body: ChatMessage):
    # Берём товары из Strapi для контекста
    products = await strapi_service.get_products()

    # Отправляем в Claude (сейчас mock)
    response = await claude_service.chat_response(body.message, products)

    return {"reply": response}