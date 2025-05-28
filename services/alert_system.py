# services/alert_system.py

import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from database.connection import SessionLocal
from database.crud import get_pairs
from services.price_fetcher import fetch_ohlcv
from services.technical_analysis import compute_ema, detect_price_ema_cross, EMA_PERIOD

def schedule_alerts(scheduler: AsyncIOScheduler, bot: Bot, chat_id: int) -> None:
    """
    Planifie un check toutes les minutes pour chaque paire configurée en base.
    """
    # On récupère la liste des paires pour ce chat_id
    db = SessionLocal()
    pairs = get_pairs(db, chat_id)
    db.close()

    for pair in pairs:
        symbol = pair.symbol
        timeframe = pair.timeframe
        job_id = f"alert_{chat_id}_{symbol}_{timeframe}"

        scheduler.add_job(
            func=check_pair,
            trigger="interval",
            minutes=1,
            kwargs={
                "bot": app.bot,
                "chat_id": chat_id,
                "symbol": symbol,
                "timeframe": timeframe,
            },
            id=job_id,
            replace_existing=True,
            # tolérance de 30s si le job est retardé
            misfire_grace_time=30,
        )

async def check_pair(bot: Bot,chat_id: int, symbol: str, timeframe: str) -> None:
    """
    Vérifie le croisement prix↔EMA100 et envoie une alerte si besoin.
    """
    # on récupère juste assez de bougies pour EMA_PERIOD+2
    limit = EMA_PERIOD + 2
    df = fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
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
