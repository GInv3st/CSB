import httpx
import pandas as pd
import numpy as np
from ta.volatility import AverageTrueRange

BINANCE_BASE = "https://api.binance.com/api/v3/klines"
TF_MAP = {"3m": "3m", "5m": "5m", "15m": "15m"}

def fetch_klines(symbol, interval, limit=200):
    url = f"{BINANCE_BASE}?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        r = httpx.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "taker_base_vol", "taker_quote_vol", "ignore"
        ])
        df = df.astype({
            "open": float, "high": float, "low": float, "close": float, "volume": float
        })
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)
        return df
    except Exception as e:
        return None

def fetch_all_data(symbols, timeframes):
    data = {}
    for symbol in symbols:
        for tf in timeframes:
            df = fetch_klines(symbol, TF_MAP[tf])
            if df is not None:
                df = add_atr(df)
                data[(symbol, tf)] = df
    return data

def add_atr(df, period=14):
    try:
        atr = AverageTrueRange(df['high'], df['low'], df['close'], window=period).average_true_range()
        df['ATR'] = atr
    except Exception:
        df['ATR'] = np.nan
    return df