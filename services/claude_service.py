import anthropic
import json
import os
from typing import List
from config import CLAUDE_API_KEY

_client: anthropic.AsyncAnthropic | None = None

_PARSE_SYSTEM = (
    "Ты помощник интернет-магазина. Извлеки из текста информацию о товаре "
    "и верни ТОЛЬКО валидный JSON без markdown и без пояснений.\n"
    "Формат:\n"
    '{"name": "название", "price": 0.0, "description": "описание", '
    '"category": "категория", "specs": {}}\n'
    "Правила: если цена не указана - 0; категорию угадай по контексту; "
    "верни ТОЛЬКО JSON."
)

_CHAT_SYSTEM = (
    "Ты вежливый и дружелюбный консультант интернет-магазина. "
    "Помогай покупателям: отвечай на вопросы о товарах, сравнивай, советуй что выбрать, "
    "рассказывай о характеристиках из каталога. "
    "Если товара нет в каталоге - честно скажи об этом. "
    "Если вопрос не связан с магазином - вежливо перенаправь к теме магазина. "
    "Отвечай на том же языке что и покупатель. Будь кратким и по делу."
)


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        key = CLAUDE_API_KEY or os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        _client = anthropic.AsyncAnthropic(api_key=key or None)
    return _client


async def parse_product(text: str) -> dict:
    message = await _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=[{
            "type": "text",
            "text": _PARSE_SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": text}],
    )

    raw = message.content[0].text.strip()

    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip()

    return json.loads(raw)


async def chat_response(message: str, products: dict, history: List[dict] = []) -> str:
    products_text = json.dumps(products.get("data", []), ensure_ascii=False)

    messages = []

    for entry in history:
        role = entry.get("role")
        content = entry.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({
        "role": "user",
        "content": f"Каталог товаров:\n{products_text}\n\nВопрос: {message}",
    })

    response = await _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": _CHAT_SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=messages,
    )

    return response.content[0].text
