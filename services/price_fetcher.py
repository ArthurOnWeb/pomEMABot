# services/price_fetcher.py

import ccxt
import pandas as pd
from typing import Optional

# Instance unique du client Binance (None tant qu'on n'appelle pas init_price_fetcher)
_binance_client: Optional[ccxt.Exchange] = None

def init_price_fetcher(
    api_key: Optional[str] = None,
    secret: Optional[str] = None,
    passphrase: Optional[str] = None
) -> None:
    """
    Initialise le client Binance :
     - si on passe api_key/secret → mode privé,
     - sinon → mode public (pas de clé).
    """
    global _binance_client

    creds: dict = {'enableRateLimit': True}
    if api_key and secret:
        creds.update({
            'apiKey': api_key,
            'secret': secret,
        })

    _binance_client = ccxt.binance(creds)


def fetch_ohlcv(
    symbol: str,
    timeframe: str = '1h',
    limit: int = 100,
) -> pd.DataFrame:
    """
    Récupère un DataFrame OHLCV pour la paire donnée sur Binance.
    Normalise le symbole si nécessaire (ex: 'ETHUSD' → 'ETH/USDT').
    Initialise automatiquement un client public si nécessaire.
    """
    global _binance_client
    if _binance_client is None:
        init_price_fetcher()  # mode public

    # Normalisation du symbole pour CCXT (format unifié)
    if '/' not in symbol:
        if symbol.endswith('USD'):
            # Remplace 'USD' par '/USDT' pour les paires USDT
            symbol = symbol[:-3] + '/USDT'
        else:
            # Assume paire USDT et ajoute '/USDT'
            symbol = symbol + '/USDT'

    raw = _binance_client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=[
        "timestamp", "open", "high", "low", "close", "volume"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df
