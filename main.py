import datetime as dt
import logging
import time

import config
from exchange import BingX
from notifier import send
from scanner import scan

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")


def fmt(sig):
    head = "🟢 LONG" if sig["side"] == "LONG" else "🔴 SHORT"
    qm = " · QM" if sig["qm"] else ""
    return (
        f"{head} {sig['symbol']} ({config.TIMEFRAME}){qm}\n"
        f"Score: {sig['score']}/100\n"
        f"Entrada: {sig['entry']:.6g}\n"
        f"SL: {sig['sl']:.6g}\n"
        f"TP: {sig['tp']:.6g}\n"
        f"Volumen x{sig['vol_ratio']:.1f} · Compresión {sig['compression']:.2f}"
    )


def can_trade(ex, sig, day_start_bal):
    if day_start_bal is not None:
        bal = ex.balance_usdt()
        if day_start_bal - bal >= config.DAILY_LOSS_LIMIT:
            send("⛔ Límite de pérdida diaria alcanzado. No se abren más operaciones hoy.")
            return False
    positions = ex.open_positions()
    if len(positions) >= config.MAX_OPEN:
        return False
    if any(p.get("symbol") == sig["symbol"] for p in positions):
        return False
    return True


def main():
    ex = BingX()
    ex.load()
    send(f"🤖 Bot iniciado · modo={config.TRADE_MODE} · TF={config.TIMEFRAME}")

    cooldown = {}
    day = None
    day_start_bal = None

    while True:
        try:
            now = time.time()
            today = dt.date.today()
            if config.TRADE_MODE == "live" and day != today:
                day = today
                day_start_bal = ex.balance_usdt()

            for sig in scan(ex):
                sym = sig["symbol"]
                if now - cooldown.get(sym, 0) < config.COOLDOWN_MIN * 60:
                    continue
                cooldown[sym] = now
                send(fmt(sig))

                if config.TRADE_MODE == "dry":
                    send(f"🧪 DRY: se habría abierto {sym} {sig['side']}")
                elif config.TRADE_MODE == "live":
                    if can_trade(ex, sig, day_start_bal):
                        ex.place_trade(sig)
                        send(f"✅ Orden ejecutada: {sym} {sig['side']}")
        except Exception as e:
            log.exception("Error en ciclo: %s", e)
            send(f"⚠️ Error en el bot: {e}")

        time.sleep(config.SCAN_INTERVAL)


if __name__ == "__main__":
    main()
