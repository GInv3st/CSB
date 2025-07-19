import json
import os
import time

def safe_load_json(path, default):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w") as f:
            json.dump(default, f)
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            with open(path, "w") as f2:
                json.dump(default, f2)
            return default

class SignalCache:
    def __init__(self, path):
        self.path = path
        self.cache = safe_load_json(self.path, [])

    def is_duplicate(self, signal):
        now = int(time.time())
        for s in self.cache:
            if s['slno'] == signal['slno'] and now - s['opened_at'] < 7200:
                return True
        return False

    def add(self, signal):
        self.cache.append({'slno': signal['slno'], 'opened_at': int(time.time())})
        self._save()

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.cache, f)

class TradeCache:
    def __init__(self, path):
        self.path = path
        self.trades = safe_load_json(self.path, [])

    def add(self, signal):
        if not any(t['slno'] == signal['slno'] for t in self.trades):
            self.trades.append(signal)
            self._save()

    def close(self, slno):
        self.trades = [t for t in self.trades if t['slno'] != slno]
        self._save()

    def get_all(self):
        return self.trades

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.trades, f)

class StrategyHistory:
    def __init__(self, path):
        self.path = path
        self.history = safe_load_json(self.path, {})

    def get(self, strategy):
        return self.history.get(strategy, [])

    def add(self, strategy, record):
        if strategy not in self.history:
            self.history[strategy] = []
        self.history[strategy].append(record)
        self.history[strategy] = self.history[strategy][-50:]
        self._save()

    def winrate(self, strategy):
        hist = self.get(strategy)
        if not hist:
            return 0.5
        wins = sum(1 for s in hist if "TP" in s.get("outcome", ""))
        return wins / len(hist)

    def next_slno(self):
        # Returns a 2-digit serial number as string, rolling from 01-99
        all_slno = []
        for v in self.history.values():
            all_slno += [int(s.get("slno", 0)) for s in v if "slno" in s]
        n = (max(all_slno) + 1) if all_slno else 1
        return f"{n:02d}"

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.history, f)