def calculate_confidence(signal, df, winrate):
    score = 0.5 + (winrate - 0.5) * 0.5  # 0.25 to 0.75 based on winrate
    # ATR: lower ATR% = higher confidence
    atr = df['ATR'].iloc[-1]
    close = df['close'].iloc[-1]
    atr_pct = (atr / close) * 100
    if atr_pct < 1.5: score += 0.1
    elif atr_pct < 2.5: score += 0.05

    # Momentum: RSI
    from ta.momentum import RSIIndicator
    rsi = RSIIndicator(df['close'], window=14).rsi().iloc[-1]
    if signal['side'] == 'LONG' and rsi > 50: score += 0.05
    if signal['side'] == 'SHORT' and rsi < 50: score += 0.05

    return min(max(score, 0), 1.0)