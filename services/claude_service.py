import json

async def parse_product(text: str) -> dict:
    """
    Парсит текст с характеристиками товара и возвращает JSON.
    Сейчас это mock — потом заменим на реальный Claude API.
    """
    # MOCK: имитируем что Claude распарсил текст
    # Когда будет реальный ключ — заменим это на вызов Claude API
    return {
        "name": "Ноутбук из текста",
        "price": 999.99,
        "description": text,
        "category": "Электроника",
        "specs": {
            "parsed": True,
            "original_text": text,
            "note": "mock - заменить на Claude API"
        }
    }

async def chat_response(message: str, products: list) -> str:
    """
    Отвечает на сообщение пользователя с контекстом товаров.
    Сейчас это mock — потом заменим на реальный Claude API.
    """
    # MOCK: имитируем ответ Claude
    products_count = len(products.get("data", []))
    return (
        f"[MOCK ответ] Привет! Ты написал: '{message}'. "
        f"В нашем магазине сейчас {products_count} товаров. "
        f"Когда подключим Claude API — здесь будет умный ответ!"
    )