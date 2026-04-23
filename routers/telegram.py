from fastapi import APIRouter, Request
import httpx
from services import strapi_service, claude_service
from config import TELEGRAM_TOKEN

router = APIRouter(prefix="/webhook", tags=["telegram"])

HELP_TEXT = (
    "Привет! Я бот магазина.\n\n"
    "<b>Команды:</b>\n"
    "/list — список всех товаров\n"
    "/get &lt;id&gt; - информация о товаре\n"
    "/add &lt;описание&gt; - добавить товар (Claude разберёт текст)\n"
    "/delete &lt;id&gt; - удалить товар\n\n"
    "Или просто напиши описание товара — я добавлю его автоматически."
)


async def _send(chat_id: int, text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


def _format_product(p: dict, show_id: bool = True) -> str:
    pid = p.get("id", "?")
    name = p.get("name") or "—"
    price = p.get("price", "—")
    category = p.get("category") or "—"
    description = p.get("description") or "—"

    lines = []
    if show_id:
        lines.append(f"ID: {pid}")
    lines += [
        f"<b>{name}</b>",
        f"Цена: {price} грн",
        f"Категория: {category}",
        f"{description}",
    ]
    return "\n".join(lines)


async def _cmd_list(chat_id: int) -> None:
    result = await strapi_service.get_products()
    products = result.get("data", [])

    if not products:
        await _send(chat_id, "Товаров пока нет.")
        return

    lines = [f"<b>Товаров в магазине: {len(products)}</b>\n"]
    for p in products:
        pid = p.get("id", "?")
        name = p.get("name") or "—"
        price = p.get("price", "—")
        lines.append(f"• <b>{name}</b> — {price} грн  (ID: {pid})")

    await _send(chat_id, "\n".join(lines))


async def _cmd_get(chat_id: int, args: str) -> None:
    if not args.isdigit():
        await _send(chat_id, "Укажи числовой ID: /get 5")
        return

    result = await strapi_service.get_product(int(args))
    product = result.get("data")

    if not product:
        await _send(chat_id, f"Товар с ID {args} не найден.")
        return

    await _send(chat_id, _format_product(product))


async def _cmd_add(chat_id: int, description: str) -> None:
    if not description:
        await _send(chat_id, "Напиши описание товара после /add")
        return

    await _send(chat_id, "Claude разбирает описание...")

    try:
        product_data = await claude_service.parse_product(description)
    except Exception as e:
        await _send(chat_id, f"Claude не смог разобрать текст: {e}")
        return

    result = await strapi_service.create_product(product_data)
    saved = result.get("data", {})

    name = saved.get("name") or "Товар"
    price = saved.get("price", "—")
    pid = saved.get("id", "?")

    await _send(
        chat_id,
        f"Товар добавлен!\n\n{_format_product(saved)}",
    )


async def _cmd_delete(chat_id: int, args: str) -> None:
    if not args.isdigit():
        await _send(chat_id, "Укажи числовой ID: /delete 5")
        return

    product_id = int(args)
    result = await strapi_service.delete_product(product_id)

    if result.get("error"):
        await _send(chat_id, f"Не удалось удалить товар #{product_id}.")
    else:
        await _send(chat_id, f"Товар #{product_id} удалён.")


@router.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()

    if not text or not chat_id:
        return {"ok": True}

    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""
    else:
        cmd = None
        args = text

    if cmd in ("/start", "/help"):
        await _send(chat_id, HELP_TEXT)

    elif cmd == "/list":
        await _cmd_list(chat_id)

    elif cmd == "/get":
        await _cmd_get(chat_id, args)

    elif cmd == "/add":
        await _cmd_add(chat_id, args)

    elif cmd == "/delete":
        await _cmd_delete(chat_id, args)

    elif cmd is None:
        await _cmd_add(chat_id, args)

    else:
        await _send(chat_id, f"Неизвестная команда. {HELP_TEXT}")

    return {"ok": True}
