# services/alert_system.py

from typing import Dict, Tuple
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from database.connection import SessionLocal
from database.crud import get_pairs, get_price_alerts, remove_price_alert
from services.price_fetcher import fetch_ohlcv
from services.technical_analysis import compute_ema, detect_price_ema_cross, EMA_PERIOD

# On stocke pour chaque (chat_id, symbol, timeframe) la dernière valeur de signal envoyée
_last_signals: Dict[Tuple[int, str, str], int] = {}

def schedule_alerts(scheduler: AsyncIOScheduler, app: Bot, chat_id: int) -> None:
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

    scheduler.add_job(
        func=check_price_alerts,
        trigger="interval",
        minutes=1,
        kwargs={"bot": app.bot, "chat_id": chat_id},
        id=f"price_alerts_{chat_id}",
        replace_existing=True,
        misfire_grace_time=30,
    )

async def check_pair(
    bot: Bot,
    chat_id: int,
    symbol: str,
    timeframe: str,
) -> None:
    """
    Vérifie le croisement prix↔EMA100 pour une paire/timeframe
    et n'envoie une alerte que si le signal a changé depuis la dernière exécution.
    """
    limit = EMA_PERIOD + 2
    df = fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = compute_ema(df, span=EMA_PERIOD)
    signal = detect_price_ema_cross(df)  #  1, -1 ou 0

    key = (chat_id, symbol, timeframe)
    last = _last_signals.get(key, 0)

    # On ne notifie que si on passe d'un état à un autre non-nul
    if signal != 0 and signal != last:
        direction = "🔔 Croisement haussier" if signal == 1 else "🔔 Croisement baissier"
        price = df.iloc[-1]["close"]
        timestamp = df.iloc[-1]["timestamp"]
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"{direction} {symbol} ({timeframe}) à {price:.2f} USDT  "
                f"📅 {timestamp:%Y-%m-%d %H:%M}"
            )
        )
        _last_signals[key] = signal

    # Si on repasse en « inactif » (signal 0), on réinitialise pour détecter le prochain croisement
    elif signal == 0 and last != 0:
        _last_signals[key] = 0


async def check_price_alerts(bot: Bot, chat_id: int) -> None:
    db = SessionLocal()
    alerts = get_price_alerts(db, chat_id)
    for alert in alerts:
        try:
            df = fetch_ohlcv(alert.symbol, timeframe="1m", limit=1)
            price = df.iloc[-1]["close"]
            if (
                alert.direction == "above" and price >= alert.target_price
            ) or (
                alert.direction == "below" and price <= alert.target_price
            ):
                await bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"🔔 Alerte prix {alert.symbol} atteint {price:.2f} USDT "
                        f"(seuil {alert.target_price:.2f})"
                    ),
                )
                remove_price_alert(db, alert.id)
        except Exception:
            continue
    db.close()

