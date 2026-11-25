import os


def _bool(name, default):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _float(name, default):
    return float(os.getenv(name, default))


def _int(name, default):
    return int(os.getenv(name, default))


# Credenciales
BINGX_API_KEY = os.getenv("BINGX_API_KEY", "").strip()
BINGX_SECRET = os.getenv("BINGX_SECRET", "").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Modo: signals | dry | live
TRADE_MODE = os.getenv("TRADE_MODE", "signals").strip().lower()

# Escaneo
TIMEFRAME = os.getenv("TIMEFRAME", "15m")
SCAN_INTERVAL = _int("SCAN_INTERVAL", 300)
TOP_N = _int("TOP_N", 60)
MIN_SCORE = _float("MIN_SCORE", 70)
COOLDOWN_MIN = _int("COOLDOWN_MIN", 120)

# QM
PIVOT_LEN = _int("PIVOT_LEN", 5)
MIN_SWEEP_ATR = _float("MIN_SWEEP_ATR", 0.1)

# Riesgo
RISK_USDT = _float("RISK_USDT", 10)
LEVERAGE = _int("LEVERAGE", 3)
MAX_OPEN = _int("MAX_OPEN", 3)
DAILY_LOSS_LIMIT = _float("DAILY_LOSS_LIMIT", 20)
SL_ATR = _float("SL_ATR", 1.5)
TP_RR = _float("TP_RR", 2.0)


def validate():
    errors = []
    if TRADE_MODE not in ("signals", "dry", "live"):
        errors.append(f"TRADE_MODE inválido: '{TRADE_MODE}'. Usa: signals / dry / live")

    # Solo exigimos keys si vamos a operar o simular con balance real
    if TRADE_MODE in ("live", "dry"):
        if not BINGX_API_KEY or not BINGX_SECRET:
            errors.append(
                "BINGX_API_KEY o BINGX_SECRET estáníos. "
                "Obligatorios para TRADE_MODE=live o dry. "
                "Créalas en https://bingx.com/en/account/api (permisos Futures, sin IP whitelist)."
            )
    return errors
