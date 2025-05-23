from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from services.price_fetcher import fetch_ohlcv, EXCHANGE_ID_BITGET
from services.technical_analysis import compute_ema, detect_price_ema_cross

# Liste des paires à surveiller (pour commencer en dur)
PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "HYPE/USDT"]
TIMEFRAME = "1h"  # ou configurable

def schedule_alerts(scheduler: AsyncIOScheduler, app: Bot) -> None:
    for symbol in PAIRS:
        scheduler.add_job(
            func=check_pair,
            trigger="interval",
            minutes=1,
            kwargs={"app": app, "symbol": symbol},
            id=f"alert_{symbol}",
            replace_existing=True,
        )

async def check_pair(app: Bot, symbol: str) -> None:
    df = fetch_ohlcv(EXCHANGE_ID_BITGET, symbol, timeframe=TIMEFRAME, limit=EMA_PERIOD+2)
    df = compute_ema(df)
    signal = detect_price_ema_cross(df)
    if signal != 0:
        direction = "🔔 Croisement haussier" if signal == 1 else "🔔 Croisement baissier"
        price = df.iloc[-1]["close"]
        timestamp = df.iloc[-1]["timestamp"]
        await app.send_message(
            chat_id=YOUR_CHAT_ID,
            text=f"{direction} {symbol} à {price:.2f} USDT 📅 {timestamp:%Y-%m-%d %H:%M}"
        )