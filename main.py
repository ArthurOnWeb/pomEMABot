import os
import asyncio
from dotenv import load_dotenv

from telegram.ext import Application, ApplicationBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Optional

# from config.settings import TG_TOKEN, SCHEDULER_INTERVAL_MINUTES
from bot.handlers import register_handlers
from services.alert_system import schedule_alerts
from services.price_fetcher import init_price_fetcher

def read_chat_id_from_file() -> Optional[int]:
    try:
        with open("chat_id.txt") as f:
            content = f.read().strip()
            if content:
                return int(content)
    except FileNotFoundError:
        pass
    return None

def main():
    load_dotenv()
    token = os.getenv("TG_TOKEN")
    if not token:
        raise RuntimeError("TG_TOKEN manquant")

    # On tente de lire le chat_id (optionnel au démarrage)
    chat_id = read_chat_id_from_file()

    scheduler = AsyncIOScheduler(timezone="UTC")

    async def _start_scheduler(app):
        if chat_id:
            print(f"✅ Chat ID trouvé : {chat_id} → démarrage des alertes.")
            schedule_alerts(scheduler, app, chat_id)
            scheduler.start()
        else:
            print("⚠️ Aucun chat_id : les alertes EMA sont désactivées.")

    app = (
        ApplicationBuilder()
        .token(token)
        .post_init(_start_scheduler)
        .build()
    )

    # 3) Enregistre tes handlers
    register_handlers(app)

    # 4) Lancement du bot (et du loop sous-jacent)
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Arrêt du bot...")
