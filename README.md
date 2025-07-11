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

