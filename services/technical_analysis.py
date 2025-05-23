import pandas as pd

# Constante pour la période de l'EMA
EMA_PERIOD = 100


def compute_ema(df: pd.DataFrame, span: int = EMA_PERIOD) -> pd.DataFrame:
    """
    Calcule l'EMA sur la colonne 'close' et l'ajoute au DataFrame.

    :param df: DataFrame avec au moins la colonne 'close'
    :param span: période de l'EMA (défaut 100)
    :return: DataFrame enrichi avec la colonne 'ema'
    """
    df = df.copy()
    df['ema'] = df['close'].ewm(span=span, adjust=False).mean()
    return df


def detect_price_ema_cross(df: pd.DataFrame) -> int:
    """
    Détecte le croisement entre le prix et l'EMA sur la dernière bougie.

    :return: 1 si le prix croise à la hausse (passe au-dessus),
             -1 si le prix croise à la baisse (passe en dessous),
             0 si pas de croisement.
    """
    if df.shape[0] < 2:
        return 0

    prev, curr = df.iloc[-2], df.iloc[-1]
    # Prix vs EMA précédent et actuel
    prev_diff = prev['close'] - prev['ema']
    curr_diff = curr['close'] - curr['ema']

    # Passage de négatif à positif => croisement haussier
    if prev_diff < 0 and curr_diff > 0:
        return 1
    # Passage de positif à négatif => croisement baissier
    if prev_diff > 0 and curr_diff < 0:
        return -1
    return 0