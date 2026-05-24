from fastapi import APIRouter, Request
import httpx
from services import strapi_service, claude_service
from config import TELEGRAM_TOKEN

router = APIRouter(prefix="/webhook", tags=["telegram"])

HELP_TEXT = (
    "Hi! I'm a shop bot.\n\n"
    "<b>Commands:</b>\n"
    "/list — list all products\n"
    "/get &lt;id&gt; — product details\n"
    "/add &lt;description&gt; — add a product (Claude will parse the text)\n"
    "/delete &lt;id&gt; — delete a product\n\n"
    "Send a product description — I'll add it to the catalog.\n"
    "Ask a question ending with ? — I'll answer as a consultant."
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
        f"Price: {price}",
        f"Category: {category}",
        f"{description}",
    ]
    return "\n".join(lines)


async def _cmd_list(chat_id: int) -> None:
    result = await strapi_service.get_products()
    products = result.get("data", [])

    if not products:
        await _send(chat_id, "No products yet.")
        return

    lines = [f"<b>Products in store: {len(products)}</b>\n"]
    for p in products:
        pid = p.get("id", "?")
        name = p.get("name") or "—"
        price = p.get("price", "—")
        lines.append(f"• <b>{name}</b> — {price}  (ID: {pid})")

    await _send(chat_id, "\n".join(lines))


async def _cmd_get(chat_id: int, args: str) -> None:
    if not args.isdigit():
        await _send(chat_id, "Please provide a numeric ID: /get 5")
        return

    result = await strapi_service.get_product(int(args))
    product = result.get("data")

    if not product:
        await _send(chat_id, f"Product with ID {args} not found.")
        return

    await _send(chat_id, _format_product(product))


async def _cmd_add(chat_id: int, description: str) -> None:
    if not description:
        await _send(chat_id, "Please provide a product description after /add")
        return

    await _send(chat_id, "Claude is parsing the description...")

    try:
        product_data = await claude_service.parse_product(description)
    except Exception as e:
        await _send(chat_id, f"Claude couldn't parse the text: {e}")
        return

    result = await strapi_service.create_product(product_data)
    saved = result.get("data", {})

    await _send(chat_id, f"Product added!\n\n{_format_product(saved)}")


async def _cmd_delete(chat_id: int, args: str) -> None:
    if not args.isdigit():
        await _send(chat_id, "Please provide a numeric ID: /delete 5")
        return

    product_id = int(args)
    result = await strapi_service.delete_product(product_id)

    if result.get("error"):
        await _send(chat_id, f"Failed to delete product #{product_id}.")
    else:
        await _send(chat_id, f"Product #{product_id} deleted.")


async def _cmd_chat(chat_id: int, text: str) -> None:
    products = await strapi_service.get_products()
    try:
        answer = await claude_service.chat_response(text, products)
        await _send(chat_id, answer)
    except Exception as e:
        await _send(chat_id, f"Couldn't respond: {e}")


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
        if args.endswith("?"):
            await _cmd_chat(chat_id, args)
        else:
            await _cmd_add(chat_id, args)
    else:
        await _send(chat_id, f"Unknown command. {HELP_TEXT}")

    return {"ok": True}