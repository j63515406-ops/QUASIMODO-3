import logging
import ccxt
from ccxt.base.errors import AuthenticationError, NetworkError, ExchangeError

import config

log = logging.getLogger("exchange")


class BingX:
    def __init__(self):
        if not config.BINGX_API_KEY or not config.BINGX_SECRET:
            log.error("❌ BINGX_API_KEY o BINGX_SECRET no están configuradas.")
            raise ValueError("Faltan API keys de BingX. Configúralas en Railway Variables.")

        self.ex = ccxt.bingx({
            "apiKey": config.BINGX_API_KEY,
            "secret": config.BINGX_SECRET,
            "enableRateLimit": True,
            "options": {
                "defaultType": "swap",          # Futuros USDT-M
                "adjustForTimeDifference": True,
            },
        })
        self._markets_loaded = False

    def load(self):
        """Carga mercados y verifica autenticación."""
        try:
            self.ex.load_markets()
            self._markets_loaded = True
            # Prueba rápida de autenticación
            self.ex.fetch_balance()
            log.info("✅ Conexión a BingX OK (API Key válida)")
        except AuthenticationError as e:
            log.error("❌ AuthenticationError: API Key o Secret incorrectos.")
            log.error("Ve a https://bingx.com/en/account/api y genera nuevas keys con permisos de Futures.")
            raise
        except Exception as e:
            log.error("Error cargando mercados: %s", e)
            raise

    def top_symbols(self, n):
        tickers = self.ex.fetch_tickers()
        rows = []
        for sym, t in tickers.items():
            m = self.ex.markets.get(sym)
            if not m or not m.get("swap") or m.get("quote") != "USDT" or m.get("active") is False:
                continue
            qv = t.get("quoteVolume") or 0
            rows.append((qv, sym))
        rows.sort(reverse=True)
        return [s for _, s in rows[:n]]

    def fetch_ohlcv(self, symbol, timeframe, limit):
        return self.ex.fetch_ohlcv(symbol, timeframe, limit=limit)

    def balance_usdt(self):
        try:
            bal = self.ex.fetch_balance()
            return float(bal["total"].get("USDT", 0) or 0)
        except Exception as e:
            log.error("Error obteniendo balance: %s", e)
            return 0.0

    def open_positions(self):
        try:
            pos = self.ex.fetch_positions()
            return [p for p in pos if float(p.get("contracts") or 0) > 0]
        except Exception as e:
            log.error("Error obteniendo posiciones: %s", e)
            return []

    def place_trade(self, sig):
        sym = sig["symbol"]
        is_long = sig["side"] == "LONG"
        notional = config.RISK_USDT * config.LEVERAGE
        amount = float(self.ex.amount_to_precision(sym, notional / sig["entry"]))
        sl = float(self.ex.price_to_precision(sym, sig["sl"]))
        tp = float(self.ex.price_to_precision(sym, sig["tp"]))

        try:
            self.ex.set_leverage(config.LEVERAGE, sym)
        except Exception as e:
            log.warning("No se pudo setear leverage en %s: %s", sym, e)

        params = {
            "stopLoss": {"triggerPrice": sl, "type": "STOP_MARKET"},
            "takeProfit": {"triggerPrice": tp, "type": "TAKE_PROFIT_MARKET"},
        }

        # Fallback simple si la estructura anterior falla
        try:
            order = self.ex.create_order(
                sym,
                "market",
                "buy" if is_long else "sell",
                amount,
                None,
                params
            )
        except Exception:
            # Método más compatible
            params = {"stopLossPrice": sl, "takeProfitPrice": tp}
            order = self.ex.create_order(
                sym,
                "market",
                "buy" if is_long else "sell",
                amount,
                None,
                params
            )

        log.info("Orden enviada %s %s: %s", sym, sig["side"], order.get("id"))
        return order
