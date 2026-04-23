import anthropic
import json
from config import CLAUDE_API_KEY

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=CLAUDE_API_KEY)
    return _client


_PARSE_SYSTEM = (
    "Ты помощник интернет-магазина. Извлеки из текста информацию о товаре "
    "и верни ТОЛЬКО валидный JSON без markdown и без пояснений.\n"
    "Формат:\n"
    '{"name": "название", "price": 0.0, "description": "описание", '
    '"category": "категория", "specs": {}}\n'
    "Правила: если цена не указана — 0; категорию угадай по контексту; "
    "верни ТОЛЬКО JSON."
)


async def parse_product(text: str) -> dict:
    """Парсит описание товара через Claude и возвращает структурированный dict."""
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

    # Claude иногда оборачивает ответ в ```json ... ```
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip()

    return json.loads(raw)


async def chat_response(message: str, products: dict) -> str:
    """Отвечает на вопрос покупателя, используя каталог товаров как контекст."""
    products_text = json.dumps(products.get("data", []), ensure_ascii=False)

    response = await _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": (
                "Ты помощник интернет-магазина. Отвечай на вопросы покупателей "
                "о товарах на русском языке. Будь кратким и полезным."
            ),
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{
            "role": "user",
            "content": f"Каталог товаров:\n{products_text}\n\nВопрос покупателя: {message}",
        }],
    )

    return response.content[0].text
