import logging
import ccxt
from ccxt.base.errors import AuthenticationError

import config

log = logging.getLogger("exchange")


class BingX:
    def __init__(self):
        opts = {
            "enableRateLimit": True,
            "options": {
                "defaultType": "swap",
                "adjustForTimeDifference": True,
            },
        }

        # Solo añadimos keys si existen (permite modo signals sin keys)
        if config.BINGX_API_KEY and config.BINGX_SECRET:
            opts["apiKey"] = config.BINGX_API_KEY
            opts["secret"] = config.BINGX_SECRET

        self.ex = ccxt.bingx(opts)
        self.authenticated = bool(config.BINGX_API_KEY and config.BINGX_SECRET)
        self._markets_loaded = False

    def load(self):
        """Carga mercados. Solo verifica auth si hay keys."""
        try:
            self.ex.load_markets()
            self._markets_loaded = True
            log.info("Mercados cargados (%d)", len(self.ex.markets))

            if self.authenticated:
                # Prueba de autenticación real
                self.ex.fetch_balance()
                log.info("✅ API Key de BingX válida")
            else:
                log.info("Modo público (sin API keys) — solo señales")

        except AuthenticationError as e:
            log.error("❌ AuthenticationError: API Key o Secret incorrectos")
            log.error("→ Ve a https://bingx.com/en/account/api")
            log.error("→ Crea nueva key con permisos de Futures/Swap")
            log.error("→ NO actives restricción de IP")
            log.error("→ Copia Key y Secret SIN espacios")
            raise
        except Exception as e:
            log.error("Error cargando mercados: %s", e)
            raise

    def top_symbols(self, n):
        tickers = self.ex.fetch_tickers()
        rows = []
        for sym, t in tickers.items():
            m = self.ex.markets.get(sym)
            if not m:
                continue
            if not m.get("swap"):
                continue
            if m.get("quote") != "USDT":
                continue
            if m.get("active") is False:
                continue
            qv = t.get("quoteVolume") or 0
            rows.append((qv, sym))
        rows.sort(reverse=True)
        return [s for _, s in rows[:n]]

    def fetch_ohlcv(self, symbol, timeframe, limit):
        return self.ex.fetch_ohlcv(symbol, timeframe, limit=limit)

    def balance_usdt(self):
        if not self.authenticated:
            return 0.0
        try:
            bal = self.ex.fetch_balance()
            return float(bal.get("total", {}).get("USDT", 0) or 0)
        except Exception as e:
            log.error("Error balance: %s", e)
            return 0.0

    def open_positions(self):
        if not self.authenticated:
            return []
        try:
            pos = self.ex.fetch_positions()
            return [p for p in pos if float(p.get("contracts") or 0) > 0]
        except Exception as e:
            log.error("Error posiciones: %s", e)
            return []

    def place_trade(self, sig):
        """Abre posición de mercado con SL y TP."""
        if not self.authenticated:
            raise RuntimeError("No se puede operar sin API keys")

        sym = sig["symbol"]
        is_long = sig["side"] == "LONG"
        side = "buy" if is_long else "sell"

        # Calculamos cantidad aproximada (notional / precio)
        notional = config.RISK_USDT * config.LEVERAGE
        raw_amount = notional / sig["entry"]
        amount = float(self.ex.amount_to_precision(sym, raw_amount))

        if amount <= 0:
            raise ValueError(f"Cantidad calculada inválida: {amount}")

        sl = float(self.ex.price_to_precision(sym, sig["sl"]))
        tp = float(self.ex.price_to_precision(sym, sig["tp"]))

        # Leverage
        try:
            self.ex.set_leverage(config.LEVERAGE, sym)
        except Exception as e:
            log.warning("set_leverage falló (%s): %s", sym, e)

        # Intentamos primero con params unified de ccxt
        params = {
            "stopLossPrice": sl,
            "takeProfitPrice": tp,
        }

        try:
            order = self.ex.create_order(sym, "market", side, amount, None, params)
            log.info("Orden OK %s %s id=%s", sym, sig["side"], order.get("id"))
            return order
        except Exception as e1:
            log.warning("Primer intento falló: %s — reintentando sin TP/SL adjunto", e1)

        # Fallback: orden market simple (sin SL/TP automático)
        order = self.ex.create_order(sym, "market", side, amount)
        log.info("Orden market simple %s %s id=%s (SL/TP manual)", sym, sig["side"], order.get("id"))
        return order
