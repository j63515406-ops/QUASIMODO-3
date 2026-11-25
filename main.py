import datetime as dt
import logging
import time
import sys

import config
from exchange import BingX
from notifier import send
from scanner import scan

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("main")


def fmt(sig):
    head = "🟢 LONG" if sig["side"] == "LONG" else "🔴 SHORT"
    qm = " · QM" if sig.get("qm") else ""
    return (
        f"{head} {sig['symbol']} ({config.TIMEFRAME}){qm}\n"
        f"Score: {sig['score']}/100\n"
        f"Entrada: {sig['entry']:.6g}\n"
        f"SL: {sig['sl']:.6g}\n"
        f"TP: {sig['tp']:.6g}\n"
        f"Vol x{sig['vol_ratio']:.1f} · Compresión {sig['compression']:.2f}"
    )


def can_trade(ex, sig, day_start_bal):
    if day_start_bal is not None:
        bal = ex.balance_usdt()
        if day_start_bal - bal >= config.DAILY_LOSS_LIMIT:
            send("⛔ Límite de pérdida diaria alcanzado.")
            return False

    positions = ex.open_positions()
    if len(positions) >= config.MAX_OPEN:
        log.info("Máximo de posiciones abiertas (%d)", config.MAX_OPEN)
        return False

    if any(p.get("symbol") == sig["symbol"] for p in positions):
        return False

    return True


def main():
    # ── Validación ──────────────────────────────────────────
    errors = config.validate()
    if errors:
        for e in errors:
            log.error(e)
            send(f"❌ Config: {e}")
        # No salimos del todo: dormimos y Railway reiniciará
        log.error("Esperando 90s antes de reintentar...")
        time.sleep(90)
        return

    # ── Conexión ────────────────────────────────────────────
    try:
        ex = BingX()
        ex.load()
    except Exception as e:
        msg = f"❌ No se pudo conectar a BingX:\n{e}"
        log.error(msg)
        send(msg)
        log.error("Esperando 120s...")
        time.sleep(120)
        return

    send(f"🤖 Bot iniciado · modo={config.TRADE_MODE} · TF={config.TIMEFRAME}")

    cooldown = {}
    day = None
    day_start_bal = None

    # ── Loop principal ──────────────────────────────────────
    while True:
        try:
            now = time.time()
            today = dt.date.today()

            if config.TRADE_MODE == "live" and day != today:
                day = today
                day_start_bal = ex.balance_usdt()
                log.info("Nuevo día · balance inicial: %.2f USDT", day_start_bal or 0)

            signals = scan(ex)
            log.info("Señales válidas: %d", len(signals))

            for sig in signals:
                sym = sig["symbol"]

                # Cooldown
                if now - cooldown.get(sym, 0) < config.COOLDOWN_MIN * 60:
                    continue
                cooldown[sym] = now

                # Aviso siempre
                send(fmt(sig))

                if config.TRADE_MODE == "dry":
                    send(f"🧪 DRY → se habría abierto {sym} {sig['side']}")

                elif config.TRADE_MODE == "live":
                    if can_trade(ex, sig, day_start_bal):
                        try:
                            ex.place_trade(sig)
                            send(f"✅ Orden ejecutada: {sym} {sig['side']}")
                        except Exception as e:
                            log.exception("Error abriendo %s", sym)
                            send(f"⚠️ Error al abrir {sym}:\n{e}")

        except Exception as e:
            log.exception("Error en ciclo: %s", e)
            send(f"⚠️ Error en el bot:\n{e}")

        time.sleep(config.SCAN_INTERVAL)


if __name__ == "__main__":
    main()
