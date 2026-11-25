import logging
import ccxt

import config

log = logging.getLogger("exchange")


class BingX:
    def __init__(self):
        self.ex = ccxt.bingx({
            "apiKey": config.BINGX_API_KEY,
            "secret": config.BINGX_SECRET,
            "enableRateLimit": True,
            "options": {"defaultType": "swap"},
        })

    def load(self):
        self.ex.load_markets()

    def top_symbols(self, n):
        tickers = self.ex.fetch_tickers()
        rows = []
        for sym, t in tickers.items():
            m = self.ex.markets.get(sym)
            # descarta solo los mercados marcados como inactivos (ccxt puede devolver None)
            if not m or not m.get("swap") or m.get("quote") != "USDT" or m.get("active") is False:
                continue
            qv = t.get("quoteVolume") or 0
            rows.append((qv, sym))
        rows.sort(reverse=True)
        return [s for _, s in rows[:n]]

    def fetch_ohlcv(self, symbol, timeframe, limit):
        return self.ex.fetch_ohlcv(symbol, timeframe, limit=limit)

    def balance_usdt(self):
        bal = self.ex.fetch_balance()
        return float(bal["total"].get("USDT", 0) or 0)

    def open_positions(self):
        pos = self.ex.fetch_positions()
        return [p for p in pos if float(p.get("contracts") or 0) > 0]

    def place_trade(self, sig):
        sym = sig["symbol"]
        is_long = sig["side"] == "LONG"
        notional = config.RISK_USDT * config.LEVERAGE
        amount = float(self.ex.amount_to_precision(sym, notional / sig["entry"]))
        sl = float(self.ex.price_to_precision(sym, sig["sl"]))
        tp = float(self.ex.price_to_precision(sym, sig["tp"]))

        self.ex.set_leverage(config.LEVERAGE, sym)
        params = {"stopLossPrice": sl, "takeProfitPrice": tp}
        order = self.ex.create_order(sym, "market", "buy" if is_long else "sell", amount, None, params)
        log.info("Orden enviada %s %s: %s", sym, sig["side"], order.get("id"))
        return order
