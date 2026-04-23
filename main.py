from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import products, chat, telegram

app = FastAPI(title="Shop Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(chat.router)
app.include_router(telegram.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Shop Backend API работает!"}
