from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from services import strapi_service, claude_service

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    message: str
    history: Optional[List[dict]] = []


@router.post("/")
async def chat(body: ChatMessage):
    products = await strapi_service.get_products()
    response = await claude_service.chat_response(body.message, products, body.history)
    return {"reply": response}
