import os
import ccxt
import pandas as pd

# Identifiant de l'exchange Bitget pour CCXT
EXCHANGE_ID_BITGET = "bitget"

# Dictionnaire des clients d'exchanges
_exchanges: dict[str, ccxt.Exchange] = {}


def init_price_fetcher(api_key: str | None = None, secret: str | None = None, passphrase: str | None = None) -> None:
    """
    Initialise le client Bitget pour la récupération des données de marché.
    Si on ne fournit pas de clés, on initialise un client public (pas d'authentification).

    :param api_key: Clé API privée (pour endpoints privés)
    :param secret: Secret API
    :param passphrase: Passphrase API
    """
    creds = {}
    if api_key and secret and passphrase:
        creds = {
            'apiKey': api_key,
            'secret': secret,
            'password': passphrase,
        }
    # Toujours activer la gestion du rate limit
    creds['enableRateLimit'] = True

    client = ccxt.bitget(creds)
    _exchanges[EXCHANGE_ID_BITGET] = client


def fetch_ohlcv(
    exchange_id: str,
    symbol: str,
    timeframe: str = '1h',
    limit: int = 100,
) -> pd.DataFrame:
    """
    Retourne un DataFrame OHLCV pour la paire spécifiée sur l'exchange donné.
    Cette opération est publique et ne nécessite pas d'authentification.

    :param exchange_id: Identifiant, e.g., 'bitget'
    :param symbol: Paire de trading, e.g., 'BTC/USDT'
    :param timeframe: Intervalle des bougies (CCXT), ex. '1h', '15m'.
    :param limit: Nombre maximal de bougies à récupérer.
    :return: DataFrame avec colonnes ['timestamp','open','high','low','close','volume']
    """
    # Si non initialisé, on crée un client public
    if exchange_id not in _exchanges:
        init_price_fetcher()

    client = _exchanges[exchange_id]
    # CCXT : interface fetch_ohlcv (public)
    raw = client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df
