import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from services.price_fetcher import fetch_ohlcv
from services.technical_analysis import compute_ema, EMA_PERIOD

from database.connection import SessionLocal
from database.crud import (
    get_pairs,
    add_pair,
    remove_pair,
    add_price_alert,
    get_price_alerts,
)

from bot.messages import HELP_MESSAGE
# from services.alert_system import (
#     add_pair as svc_add_pair,
#     list_pairs as svc_list_pairs,
#     remove_pair as svc_remove_pair
# )
# from services.chart_generator import generate_chart


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
    app.add_handler(CommandHandler("alert", alert_command))
    app.add_handler(CommandHandler("alerts", list_alerts_command))
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

async def add_command(update, context):
    chat_id = update.effective_chat.id
    args = context.args
    if len(args) < 2:
        return await update.message.reply_text("Usage : /add <SYMBOL> <TIMEFRAME>")
    symbol, timeframe = args[0].upper(), args[1]
    db = SessionLocal()
    pair = add_pair(db, chat_id, symbol, timeframe)
    db.close()
    if pair:
        await update.message.reply_text(f"✅ {symbol} ({timeframe}) ajouté.")
    else:
        await update.message.reply_text(f"⚠️ {symbol} ({timeframe}) existe déjà.")

async def list_command(update, context):
    chat_id = update.effective_chat.id
    db = SessionLocal()
    pairs = get_pairs(db, chat_id)
    db.close()
    if not pairs:
        return await update.message.reply_text("📭 Aucune paire suivie.")
    text = "📋 Paires suivies :\n" + "\n".join(
        f"• {p.symbol} ({p.timeframe})" for p in pairs
    )
    await update.message.reply_text(text)

async def remove_command(update, context):
    chat_id = update.effective_chat.id
    args = context.args
    if not args:
        return await update.message.reply_text("Usage : /remove <SYMBOL>")
    symbol = args[0].upper()
    db = SessionLocal()
    count = remove_pair(db, chat_id, symbol)
    db.close()
    if count:
        await update.message.reply_text(f"✅ {symbol} supprimé.")
    else:
        await update.message.reply_text(f"❌ {symbol} introuvable.")


async def alert_command(update, context):
    chat_id = update.effective_chat.id
    args = context.args
    if len(args) < 2:
        return await update.message.reply_text("Usage : /alert <SYMBOL> <PRIX>")
    symbol = args[0].upper()
    try:
        target = float(args[1])
    except ValueError:
        return await update.message.reply_text("❌ Prix invalide.")

    try:
        df = fetch_ohlcv(symbol, timeframe="1m", limit=1)
        current_price = df.iloc[-1]["close"]
    except Exception:
        return await update.message.reply_text(f"❌ Impossible de récupérer {symbol}.")

    direction = "above" if current_price < target else "below"
    db = SessionLocal()
    add_price_alert(db, chat_id, symbol, target, direction)
    db.close()

    sign = ">=" if direction == "above" else "<="
    await update.message.reply_text(
        f"🔔 Alerte enregistrée : {symbol} {sign} {target:.2f} USDT"
    )


async def list_alerts_command(update, context):
    chat_id = update.effective_chat.id
    db = SessionLocal()
    alerts = get_price_alerts(db, chat_id)
    db.close()
    if not alerts:
        return await update.message.reply_text("📭 Aucune alerte enregistrée.")

    lines = [
        f"• {a.symbol} {'≥' if a.direction == 'above' else '≤'} {a.target_price:.2f}"
        for a in alerts
    ]
    await update.message.reply_text("📋 Alertes en cours :\n" + "\n".join(lines))

# async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     # """Ajoute une paire/timeframe à la surveillance."""
#     # args = context.args
#     # if len(args) != 2:
#     #     return await update.message.reply_text("Usage: /add <SYMBOL> <TIMEFRAME>")
#     # symbol, timeframe = args
#     # result = svc_add_pair(update.effective_chat.id, symbol.upper(), timeframe)
#     # await update.message.reply_text(result)
#     await update.message.reply_text("⚠️ La commande /add n'est pas encore disponible.")


# async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Liste les paires surveillées pour ce chat."""
#     # result = svc_list_pairs(update.effective_chat.id)
#     # await update.message.reply_text(result)
#     message = "📋 Paires surveillées :\n" + "\n".join(f"• {pair}" for pair in PAIRS) + "\n à vérifier dans le code"
#     await update.message.reply_text(message)



# async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     # """Supprime une paire de la surveillance."""
#     # args = context.args
#     # if not args:
#     #     return await update.message.reply_text("Usage: /remove <SYMBOL>")
#     # symbol = args[0].upper()
#     # result = svc_remove_pair(update.effective_chat.id, symbol)
#     # await update.message.reply_text(result)
#     await update.message.reply_text("⚠️ La commande /remove n'est pas encore disponible.")


async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # """Envoie un graphique OHLCV avec EMAs pour toutes les paires surveillées."""
    # buf = generate_chart(update.effective_chat.id)
    # await update.message.reply_photo(photo=buf)
    await update.message.reply_text("📊 La génération de graphiques n'est pas encore disponible.")

async def last_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ Utilisation : /last <SYMBOL> [TIMEFRAME]\n"
            "Exemple : /last BTC/USDT 4h"
        )
        return

    symbol = args[0].upper()
    # Par défaut 1h si pas de timeframe fourni
    timeframe = args[1] if len(args) > 1 else "1h"

    try:
        # on récupère juste assez de bougies
        df = fetch_ohlcv(symbol, timeframe=timeframe, limit=EMA_PERIOD + 2)
        df = compute_ema(df, span=EMA_PERIOD)
        last = df.iloc[-1]

        price = last["close"]
        ema = last["ema"]
        ts = last["timestamp"]

        await update.message.reply_text(
            f"📊 Derniers indicateurs pour {symbol} ({timeframe}):\n"
            f"• Prix actuel : {price:.2f} USDT\n"
            f"• EMA{EMA_PERIOD} : {ema:.2f} USDT\n"
            f"• Bougie de : {ts:%Y-%m-%d %H:%M}"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Impossible d'obtenir les données pour {symbol} en {timeframe}."
        )
        # Log détaillé en console pour debug
        print(f"[ERREUR] /last {symbol} {timeframe} : {e}")


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
