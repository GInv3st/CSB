import os
import asyncio
from dotenv import load_dotenv

from src.data import fetch_klines, add_atr
from src.strategies import run_all_strategies
from src.signal_builder import build_signal
from src.cache import TradeCache
from src.momentum import calculate_momentum, momentum_category
from src.confidence import calculate_confidence
from src.telegram import TelegramBot

load_dotenv()

SYMBOL = "BTCUSDT"
TIMEFRAME = "5m"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def main():
    tg = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

    print(f"\n--- Testing signals for {SYMBOL} {TIMEFRAME} ---")
    df = fetch_klines(SYMBOL, TIMEFRAME, limit=200)
    if df is None or len(df) < 100:
        print("Not enough data.")
        return
    df = add_atr(df)
    signals = run_all_strategies(df)
    sent = 0
    for i, strat in enumerate(signals, 1):
        sl_mult = strat['atr_mult']['sl']
        tp_mult = strat['atr_mult']['tp']
        signal = build_signal(SYMBOL, TIMEFRAME, df, strat, sl_mult, tp_mult, f"{i:02d}")
        if not signal:
            continue
        signal['confidence'] = calculate_confidence(signal, df, 0.5)
        signal['momentum'] = calculate_momentum(df)
        signal['momentum_cat'] = momentum_category(signal['momentum'])
        print(f"\nSignal {i}:")
        print(f"  Strategy: {signal['strategy']}")
        print(f"  Side: {signal['side']}")
        print(f"  Entry: {signal['entry']}")
        print(f"  SL: {signal['sl']} ({signal['sl_multiplier']}x ATR)")
        print(f"  TP: {signal['tp']} ({signal['tp_multipliers']})")
        print(f"  Confidence: {int(round(signal['confidence'] * 100))}%")        
        print(f"  Momentum: {signal['momentum_cat']}")
        print(f"  SLNO: {signal['slno']}")
        # Send to Telegram
        await tg.send_signal(signal)
        sent += 1

    print("\n--- Telegram Status Message (Active Trades) ---")
    trade_cache = TradeCache(".cache/active_trades.json")
    trades = trade_cache.get_all()
    if not trades:
        print("No active trades.")
        await tg.send_status([])
    else:
        for t in trades:
            print(f"{t['side']} {t['symbol']}/{t['timeframe']} | Entry: {t['entry']} | SL: {t['sl']} | TPs: {t['tp']} | Confidence: {t['confidence']:.2f} | SLNO: {t['slno']}")
        await tg.send_status(trades)

    print(f"\n✅ Sent {sent} test signals and Telegram status.")

if __name__ == "__main__":
    asyncio.run(main())