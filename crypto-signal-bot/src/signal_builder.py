import time
import numpy as np
from src.utils import generate_serial

def build_signal(symbol, tf, df, strat, sl_mult, tp_mult, slno):
    try:
        side = strat['side']
        entry = float(df['close'].iloc[-1])
        atr = float(df['ATR'].iloc[-1])
        if np.isnan(atr) or atr == 0:
            return None

        # ATR-based SL/TP per strategy
        if side == "LONG":
            sl = entry - atr * sl_mult
            tp = [entry + atr * m for m in tp_mult]
        else:
            sl = entry + atr * sl_mult
            tp = [entry - atr * m for m in tp_mult]

        return {
            'slno': slno,
            'symbol': symbol,
            'timeframe': tf,
            'side': side,
            'entry': round(entry, 2),
            'sl': round(sl, 2),
            'sl_multiplier': sl_mult,
            'tp': [round(x, 2) for x in tp],
            'tp_multipliers': tp_mult,
            'strategy': strat['strategy'],
            'opened_at': int(time.time())
        }
    except Exception:
        return None

def check_trade_exit(trade, df):
    side = trade['side']
    entry = trade['entry']
    sl = trade['sl']
    tp = trade['tp']
    closes = df['close'].iloc[-10:]

    # Cost-to-cost: only if price first moves in favor by 0.5x ATR, then returns to entry
    atr = float(df['ATR'].iloc[-1])
    c2c_trigger = False
    if side == "LONG":
        if any(c >= entry + 0.5 * atr for c in closes) and closes.iloc[-1] <= entry:
            c2c_trigger = True
    else:
        if any(c <= entry - 0.5 * atr for c in closes) and closes.iloc[-1] >= entry:
            c2c_trigger = True

    if c2c_trigger:
        return {'closed': True, 'reason': 'Cost-to-Cost', 'exit_price': closes.iloc[-1]}

    # SL/TP hit
    if side == 'LONG':
        if any(c <= sl for c in closes):
            return {'closed': True, 'reason': 'SL Hit', 'exit_price': sl}
        for i, t in enumerate(tp[::-1]):
            if any(c >= t for c in closes):
                return {'closed': True, 'reason': f'TP{len(tp)-i} Hit', 'exit_price': t, 'candles_to_win': i+1}
    else:
        if any(c >= sl for c in closes):
            return {'closed': True, 'reason': 'SL Hit', 'exit_price': sl}
        for i, t in enumerate(tp[::-1]):
            if any(c <= t for c in closes):
                return {'closed': True, 'reason': f'TP{len(tp)-i} Hit', 'exit_price': t, 'candles_to_win': i+1}
    return {'closed': False}