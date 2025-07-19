import time
import numpy as np

def generate_serial(symbol, tf, side):
    return f"{symbol}-{tf}-{side}-{int(time.time())}"

def vwap(df):
    pv = (df['close'] * df['volume']).sum()
    vol = df['volume'].sum()
    return pv / vol if vol != 0 else df['close'].iloc[-1]

def find_support_resistance(df, lookback=20):
    closes = df['close'].iloc[-lookback:]
    sup = closes.min()
    res = closes.max()
    return sup, res

def find_order_block_break(df, side):
    highs = df['high'].rolling(10).max()
    lows = df['low'].rolling(10).min()
    if side == "LONG" and df['close'].iloc[-1] > highs.iloc[-2]:
        return True
    if side == "SHORT" and df['close'].iloc[-1] < lows.iloc[-2]:
        return True
    return False