import os
import asyncio
from dotenv import load_dotenv

from telegram.ext import Application, ApplicationBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# from config.settings import TG_TOKEN, SCHEDULER_INTERVAL_MINUTES
from bot.handlers import register_handlers
from services.alert_system import schedule_alerts
from services.price_fetcher import init_price_fetcher


def main() -> None:
    # Charge les variables d'environnement depuis .env
    load_dotenv()

    # Initialise le bot Telegram
    token = os.getenv("TG_TOKEN")
    if not token:
        raise RuntimeError("Le token Telegram est manquant. Vérifie ton .env !")
    app: Application = ApplicationBuilder().token(token).build()

    # Enregistre les handlers de commandes & callbacks
    register_handlers(app)

    # Initialise le fetcher de prix (ex: configuration CCXT)
    init_price_fetcher()

    # Planificateur APScheduler
    scheduler = AsyncIOScheduler(timezone="UTC")
    # Schedule les vérifications de croisements EMA
    schedule_alerts(scheduler, app)
    scheduler.start()

    # Démarre le bot en mode polling
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Arrêt du bot...")
