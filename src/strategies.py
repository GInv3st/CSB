import numpy as np
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from src.utils import find_support_resistance, vwap, find_order_block_break

# Strict, auditable, proven strategies only
STRATEGY_LIST = [
    {
        "name": "RSI Divergence",
        "condition": lambda df: (
            RSIIndicator(df['close'], window=14).rsi().iloc[-1] < 30 and
            df['close'].iloc[-1] > df['open'].iloc[-1]
        ),
        "side": "LONG",
        "atr_mult": {"sl": 1.2, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "RSI Divergence",
        "condition": lambda df: (
            RSIIndicator(df['close'], window=14).rsi().iloc[-1] > 70 and
            df['close'].iloc[-1] < df['open'].iloc[-1]
        ),
        "side": "SHORT",
        "atr_mult": {"sl": 1.2, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "VWAP Breakout",
        "condition": lambda df: (
            df['close'].iloc[-1] > vwap(df) and
            df['close'].iloc[-2] < vwap(df) and
            df['volume'].iloc[-1] > df['volume'].rolling(20).mean().iloc[-1]
        ),
        "side": "LONG",
        "atr_mult": {"sl": 1.3, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "VWAP Breakdown",
        "condition": lambda df: (
            df['close'].iloc[-1] < vwap(df) and
            df['close'].iloc[-2] > vwap(df) and
            df['volume'].iloc[-1] > df['volume'].rolling(20).mean().iloc[-1]
        ),
        "side": "SHORT",
        "atr_mult": {"sl": 1.3, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "EMA Bullish Cross",
        "condition": lambda df: (
            EMAIndicator(df['close'], window=9).ema_indicator().iloc[-1] > EMAIndicator(df['close'], window=21).ema_indicator().iloc[-1] and
            EMAIndicator(df['close'], window=9).ema_indicator().iloc[-2] < EMAIndicator(df['close'], window=21).ema_indicator().iloc[-2]
        ),
        "side": "LONG",
        "atr_mult": {"sl": 1.2, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "EMA Bearish Cross",
        "condition": lambda df: (
            EMAIndicator(df['close'], window=9).ema_indicator().iloc[-1] < EMAIndicator(df['close'], window=21).ema_indicator().iloc[-1] and
            EMAIndicator(df['close'], window=9).ema_indicator().iloc[-2] > EMAIndicator(df['close'], window=21).ema_indicator().iloc[-2]
        ),
        "side": "SHORT",
        "atr_mult": {"sl": 1.2, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "Bollinger Squeeze Breakout",
        "condition": lambda df: (
            (BollingerBands(df['close'], window=20, window_dev=2).bollinger_hband() - BollingerBands(df['close'], window=20, window_dev=2).bollinger_lband()).iloc[-1] <
            (BollingerBands(df['close'], window=20, window_dev=2).bollinger_hband() - BollingerBands(df['close'], window=20, window_dev=2).bollinger_lband()).rolling(20).mean().iloc[-1] * 0.7 and
            df['close'].iloc[-1] > BollingerBands(df['close'], window=20, window_dev=2).bollinger_hband().iloc[-1]
        ),
        "side": "LONG",
        "atr_mult": {"sl": 1.5, "tp": [1.5, 2.5, 3.0]}
    },
    {
        "name": "Bollinger Squeeze Breakdown",
        "condition": lambda df: (
            (BollingerBands(df['close'], window=20, window_dev=2).bollinger_hband() - BollingerBands(df['close'], window=20, window_dev=2).bollinger_lband()).iloc[-1] <
            (BollingerBands(df['close'], window=20, window_dev=2).bollinger_hband() - BollingerBands(df['close'], window=20, window_dev=2).bollinger_lband()).rolling(20).mean().iloc[-1] * 0.7 and
            df['close'].iloc[-1] < BollingerBands(df['close'], window=20, window_dev=2).bollinger_lband().iloc[-1]
        ),
        "side": "SHORT",
        "atr_mult": {"sl": 1.5, "tp": [1.5, 2.5, 3.0]}
    },
    {
        "name": "MACD Bullish Cross",
        "condition": lambda df: (
            MACD(df['close']).macd_diff().iloc[-1] > 0 and
            MACD(df['close']).macd_diff().iloc[-2] < 0
        ),
        "side": "LONG",
        "atr_mult": {"sl": 1.3, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "MACD Bearish Cross",
        "condition": lambda df: (
            MACD(df['close']).macd_diff().iloc[-1] < 0 and
            MACD(df['close']).macd_diff().iloc[-2] > 0
        ),
        "side": "SHORT",
        "atr_mult": {"sl": 1.3, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "Stochastic Bullish Cross",
        "condition": lambda df: (
            StochasticOscillator(df['high'], df['low'], df['close'], window=14).stoch_signal().iloc[-1] > StochasticOscillator(df['high'], df['low'], df['close'], window=14).stoch().iloc[-1] and
            StochasticOscillator(df['high'], df['low'], df['close'], window=14).stoch_signal().iloc[-2] < StochasticOscillator(df['high'], df['low'], df['close'], window=14).stoch().iloc[-2]
        ),
        "side": "LONG",
        "atr_mult": {"sl": 1.2, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "Stochastic Bearish Cross",
        "condition": lambda df: (
            StochasticOscillator(df['high'], df['low'], df['close'], window=14).stoch_signal().iloc[-1] < StochasticOscillator(df['high'], df['low'], df['close'], window=14).stoch().iloc[-1] and
            StochasticOscillator(df['high'], df['low'], df['close'], window=14).stoch_signal().iloc[-2] > StochasticOscillator(df['high'], df['low'], df['close'], window=14).stoch().iloc[-2]
        ),
        "side": "SHORT",
        "atr_mult": {"sl": 1.2, "tp": [1.0, 1.5, 2.0]}
    },
    {
        "name": "Order Block Break (High)",
        "condition": lambda df: find_order_block_break(df, "LONG"),
        "side": "LONG",
        "atr_mult": {"sl": 1.4, "tp": [1.2, 1.8, 2.5]}
    },
    {
        "name": "Order Block Break (Low)",
        "condition": lambda df: find_order_block_break(df, "SHORT"),
        "side": "SHORT",
        "atr_mult": {"sl": 1.4, "tp": [1.2, 1.8, 2.5]}
    },
]

def run_all_strategies(df):
    results = []
    for strat in STRATEGY_LIST:
        try:
            if strat["condition"](df):
                results.append({
                    "strategy": strat["name"],
                    "side": strat["side"],
                    "atr_mult": strat["atr_mult"]
                })
        except Exception:
            continue
    return results