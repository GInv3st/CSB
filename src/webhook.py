import os
from fastapi import FastAPI, Request, HTTPException
from src.cache import TradeCache
from src.telegram import TelegramBot

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

tg = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
trade_cache = TradeCache(".cache/active_trades.json")

@app.post("/webhook")
async def webhook(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = auth.split(" ")[1]
    if token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = await request.json()
    if data.get("cmd") == "/status":
        trades = trade_cache.get_all()
        tg.send_status(trades)
        return {"ok": True}
    return {"ok": False}