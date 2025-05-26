# services/price_fetcher.py

import os
import ccxt
import pandas as pd

# Client Bitget unique
_bitget_client: ccxt.Exchange | None = None

def init_price_fetcher(
    api_key: str | None = None,
    secret: str | None = None,
    passphrase: str | None = None
) -> None:
    """
    Initialise le client Bitget (public si pas de clés, privé sinon).
    """
    global _bitget_client

    creds: dict = {'enableRateLimit': True}
    if api_key and secret and passphrase:
        creds.update({
            'apiKey': api_key,
            'secret': secret,
            'password': passphrase,
        })

    _bitget_client = ccxt.bitget(creds)


def fetch_ohlcv(
    symbol: str,
    timeframe: str = '1h',
    limit: int = 100,
) -> pd.DataFrame:
    """
    Récupère un DataFrame OHLCV pour la paire donnée sur Bitget.
    Initialise automatiquement un client public si nécessaire.
    """
    global _bitget_client
    if _bitget_client is None:
        init_price_fetcher()  # sans clés = accès public

    raw = _bitget_client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=[
        "timestamp", "open", "high", "low", "close", "volume"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df
