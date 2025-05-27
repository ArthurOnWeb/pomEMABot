import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from services.alert_system import PAIRS,TIMEFRAME
from services.price_fetcher import fetch_ohlcv
from services.technical_analysis import compute_ema, EMA_PERIOD

from bot.messages import HELP_MESSAGE
# from services.alert_system import (
#     add_pair as svc_add_pair,
#     list_pairs as svc_list_pairs,
#     remove_pair as svc_remove_pair
# )
# from services.chart_generator import generate_chart


DEFAULT_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "HYPE/USDT"]

def register_handlers(app: Application) -> None:
    """
    Enregistre tous les handlers de commandes et callbacks sur l'application Telegram.
    """
    # Commandes de base
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    # Gestion des paires surveillées
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("remove", remove_command))
    # Prix et EMA à la demande
    app.add_handler(CommandHandler("last", last_command))
    # Graphe à la demande
    app.add_handler(CommandHandler("chart", chart_command))
    # Callbacks pour les inline buttons (si utilisés)
    app.add_handler(CallbackQueryHandler(callback_router))

    logging.info("🚀 Handlers enregistrés avec succès.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    with open("chat_id.txt", "w") as f:
        f.write(str(chat_id))
    await update.message.reply_text(f"✅ Bot activé pour ce chat ! ID : `{chat_id}`", parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_MESSAGE)


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # """Ajoute une paire/timeframe à la surveillance."""
    # args = context.args
    # if len(args) != 2:
    #     return await update.message.reply_text("Usage: /add <SYMBOL> <TIMEFRAME>")
    # symbol, timeframe = args
    # result = svc_add_pair(update.effective_chat.id, symbol.upper(), timeframe)
    # await update.message.reply_text(result)
    await update.message.reply_text("⚠️ La commande /add n'est pas encore disponible.")


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Liste les paires surveillées pour ce chat."""
    # result = svc_list_pairs(update.effective_chat.id)
    # await update.message.reply_text(result)
    message = "📋 Paires surveillées :\n" + "\n".join(f"• {pair}" for pair in PAIRS) + "\n à vérifier dans le code"
    await update.message.reply_text(message)



async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # """Supprime une paire de la surveillance."""
    # args = context.args
    # if not args:
    #     return await update.message.reply_text("Usage: /remove <SYMBOL>")
    # symbol = args[0].upper()
    # result = svc_remove_pair(update.effective_chat.id, symbol)
    # await update.message.reply_text(result)
    await update.message.reply_text("⚠️ La commande /remove n'est pas encore disponible.")


async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # """Envoie un graphique OHLCV avec EMAs pour toutes les paires surveillées."""
    # buf = generate_chart(update.effective_chat.id)
    # await update.message.reply_photo(photo=buf)
    await update.message.reply_text("📊 La génération de graphiques n'est pas encore disponible.")

async def last_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Utilisation : /last <SYMBOL> (ex: /last BTC/USDT)")
        return

    symbol = args[0].upper()

    try:
        df = fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=EMA_PERIOD + 2)
        df = compute_ema(df, span=EMA_PERIOD)
        last = df.iloc[-1]

        price = last["close"]
        ema = last["ema"]
        ts = last["timestamp"]

        await update.message.reply_text(
            f"📊 Derniers indicateurs pour {symbol} ({TIMEFRAME}):\n"
            f"• Prix actuel : {price:.2f} USDT\n"
            f"• EMA{EMA_PERIOD} : {ema:.2f} USDT\n"
            f"• Bougie de : {ts:%Y-%m-%d %H:%M}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Impossible d'obtenir les données pour {symbol}.")
        print(f"[ERREUR] /last {symbol} : {e}")


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route les callback_data des inline buttons vers la fonction appropriée."""
    query = update.callback_query
    await query.answer()
    data = query.data
    # Exemple de parsing: "remove:BTCUSDT"
    cmd, payload = data.split(":", 1)
    if cmd == "remove":
        response = svc_remove_pair(update.effective_chat.id, payload)
        await query.edit_message_text(response)
    else:
        await query.edit_message_text("Action non reconnue.")