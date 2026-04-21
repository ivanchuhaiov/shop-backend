from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import products, chat, telegram, cabinet

app = FastAPI(title="Shop Backend API")

# CORS — чтобы React мог обращаться к API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(products.router)
app.include_router(chat.router)
app.include_router(telegram.router)
app.include_router(cabinet.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Shop Backend API работает!"}