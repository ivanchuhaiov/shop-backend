import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from services import strapi_service, claude_service
from config import TELEGRAM_TOKEN

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    # Claude парсит текст → JSON товара (сейчас mock)
    product_data = await claude_service.parse_product(text)

    # Сохраняем в Strapi
    result = await strapi_service.create_product(product_data)
    product_name = result.get("data", {}).get("name", "Товар")

    await update.message.reply_text(f"✅ Товар '{product_name}' добавлен в магазин!")

def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()