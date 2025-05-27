# services/alert_system.py

import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from services.price_fetcher import fetch_ohlcv
from services.technical_analysis import compute_ema, detect_price_ema_cross, EMA_PERIOD

# Chat ID par défaut (tu peux le remplacer ou le rendre dynamique plus tard)
YOUR_CHAT_ID = int(os.getenv("YOUR_CHAT_ID", "123456789"))

# Paires à surveiller
PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "HYPE/USDT"]
TIMEFRAME = "1h"  # ou rendre configurable

def schedule_alerts(scheduler: AsyncIOScheduler, app: Bot, chat_id: int) -> None:
    """
    Planifie un check toutes les minutes pour chaque paire.
    """
    for symbol in PAIRS:
        scheduler.add_job(
            func=check_pair,
            trigger="interval",
            minutes=1,
            kwargs={"bot": app.bot, "chat_id": chat_id, "symbol": symbol},
            id=f"alert_{symbol}",
            replace_existing=True,
        )

async def check_pair(bot: Bot,chat_id: int, symbol: str) -> None:
    """
    Vérifie le croisement prix↔EMA100 et envoie une alerte si besoin.
    """
    # on récupère juste assez de bougies pour EMA_PERIOD+2
    limit = EMA_PERIOD + 2
    df = fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=limit)
    df = compute_ema(df, span=EMA_PERIOD)
    signal = detect_price_ema_cross(df)

    if signal != 0:
        direction = "🔔 Croisement haussier" if signal == 1 else "🔔 Croisement baissier"
        price = df.iloc[-1]["close"]
        timestamp = df.iloc[-1]["timestamp"]
        await bot.send_message(
            chat_id=chat_id,
            text=f"{direction} {symbol} à {price:.2f} USDT 📅 {timestamp:%Y-%m-%d %H:%M}"
        )
