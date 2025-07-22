import io
import mplfinance as mpf
import matplotlib.pyplot as plt

from services.price_fetcher import fetch_ohlcv
from services.technical_analysis import compute_ema, EMA_PERIOD


def generate_chart(symbol: str, timeframe: str = "1h") -> io.BytesIO:
    """Generate a candlestick chart with EMA overlay.

    Parameters
    ----------
    symbol: str
        Trading pair symbol like ``"BTC/USDT"``.
    timeframe: str
        Exchange timeframe (for example ``"4h"`` or ``"1d"``).

    Returns
    -------
    io.BytesIO
        Buffer containing the PNG image ready to be sent to Telegram.
    """
    # Fetch candles and compute EMA
    limit = EMA_PERIOD + 50
    df = fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = compute_ema(df, span=EMA_PERIOD)

    df = df.set_index("timestamp")

    apds = [mpf.make_addplot(df["ema"], color="orange", width=1)]

    fig, _ = mpf.plot(
        df,
        type="candle",
        style="binance",
        addplot=apds,
        volume=True,
        returnfig=True,
    )

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf
