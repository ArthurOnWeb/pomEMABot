# bot/messages.py

# START_MESSAGE = (
#     "👋 Salut !\n\n"
#     "Je suis ton EMA-Bot.\n"
#     "Je surveille les croisements entre le prix et l'EMA100.\n\n"
#     "Commandes disponibles:\n"
#     "/add <SYMBOL> <TF> – ajoute une paire (ex: BTC/USDT 1h)\n"
#     "/list – affiche les paires surveillées\n"
#     "/remove <SYMBOL> – supprime une paire\n"
#     "/chart – affiche le graphique EMA100\n"
#     "/help – ce message\n"
# )

HELP_MESSAGE = (
    "ℹ️ *Aide EMA-Bot*\n\n"
    "• `/add BTC/USDT 1h` : commence à surveiller BTC/USDT en 1 heure\n"
    "• `/list` : liste tes paires actives\n"
    "• `/remove BTC/USDT` : arrête de surveiller cette paire\n"
    "• `/alert BTC/USDT 30000` : alerte de prix personnalisée\n"
    "• `/chart` : génère un graphique OHLCV avec EMA100\n\n"
    "Le bot vérifie les croisements chaque minute et t’envoie une alerte."
)
