import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from services.technical_analysis import compute_ema, detect_price_ema_cross


def test_compute_ema_adds_column():
    df = pd.DataFrame({'close': [1, 2, 3, 4, 5]})
    result = compute_ema(df, span=2)
    assert 'ema' in result.columns
    assert len(result) == len(df)


def test_detect_price_ema_cross_bullish():
    df = pd.DataFrame({'close': [10, 12], 'ema': [11, 11]})
    assert detect_price_ema_cross(df) == 1


def test_detect_price_ema_cross_bearish():
    df = pd.DataFrame({'close': [12, 10], 'ema': [11, 11]})
    assert detect_price_ema_cross(df) == -1


def test_detect_price_ema_cross_none():
    df = pd.DataFrame({'close': [12, 13], 'ema': [11, 11]})
    assert detect_price_ema_cross(df) == 0