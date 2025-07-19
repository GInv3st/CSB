from ta.momentum import RSIIndicator, StochasticOscillator

def calculate_momentum(df):
    rsi = RSIIndicator(df['close'], window=14).rsi().iloc[-1]
    stoch = StochasticOscillator(df['high'], df['low'], df['close'], window=14).stoch().iloc[-1]
    return int((rsi + stoch) / 2)

def momentum_category(val):
    if val < 40:
        return "LOW"
    elif val < 60:
        return "MEDIUM"
    else:
        return "HIGH"