import anthropic
import json
import os
from typing import List
from config import CLAUDE_API_KEY

_client: anthropic.AsyncAnthropic | None = None

_PARSE_SYSTEM = (
    "You are an online store assistant. Extract product information from the text "
    "and return ONLY valid JSON without markdown or explanation.\n"
    "Format:\n"
    '{"name": "product name", "price": 0.0, "description": "description", '
    '"category": "category", "specs": {}}\n'
    "Rules: if price is not mentioned — use 0; guess category from context; "
    "return ONLY JSON."
)

_CHAT_SYSTEM = (
    "You are a polite and friendly online store consultant. "
    "Help customers: answer questions about products, compare items, give recommendations, "
    "describe specifications from the catalog. "
    "If a product is not in the catalog — say so honestly. "
    "If the question is not related to the store — politely redirect to store topics. "
    "Always respond in English. Be concise and to the point."
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
        "content": f"Product catalog:\n{products_text}\n\nQuestion: {message}",
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