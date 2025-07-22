Ceci est un Bot Telegram qui a pour but de m'aider à trader les tendances de façon simplifiée

Nouveauté : il est maintenant possible de définir des alertes de prix avec la commande `/alert` et de les supprimer avec `/removealert`. Tu peux également afficher la liste de tes alertes avec `/alerts`. Le bot te notifiera dès que la valeur choisie est atteinte.

Attention ! Le Trading comporte des risques. Ce bot ne donnes pas de conseils financiers.

## Utilisation de /chart

La commande `/chart` affiche un graphique en chandeliers avec l'EMA100.

```
/chart BTC/USDT 4h
```

Le graphique est généré grâce à `mplfinance`. Pense à installer les dépendances :

```
pip install -r requirements.txt
```

## Configuration

Crée un fichier `.env` à la racine du projet contenant le token de ton bot Telegram :

```
TG_TOKEN=123456:ABCDEF
```

Remplace la valeur par le token obtenu auprès de BotFather.

## Base de données

Le bot stocke les paires surveillées et les alertes dans une base SQLite nommée `ema_bot.db`. Ce fichier est créé automatiquement au premier démarrage.

## Lancement du bot

1. Installe les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

2. Lance le bot avec :

   ```bash
   python main.py
   ```

   Le bot se connecte ensuite à Telegram et démarre la surveillance 