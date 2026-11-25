import os


def _bool(name, default):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _float(name, default):
    return float(os.getenv(name, default))


def _int(name, default):
    return int(os.getenv(name, default))


# Credenciales (se cargan desde variables de entorno de Railway, nunca en el código)
BINGX_API_KEY = os.getenv("BINGX_API_KEY", "").strip()
BINGX_SECRET = os.getenv("BINGX_SECRET", "").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Modo de operación: signals (solo avisos) | dry (simula) | live (opera de verdad)
TRADE_MODE = os.getenv("TRADE_MODE", "signals").strip().lower()

# Escaneo
TIMEFRAME = os.getenv("TIMEFRAME", "15m")
SCAN_INTERVAL = _int("SCAN_INTERVAL", 300)        # segundos entre escaneos
TOP_N = _int("TOP_N", 80)                         # cuántos pares por volumen revisar
MIN_SCORE = _float("MIN_SCORE", 70)               # puntuación mínima para señal (0-100)
COOLDOWN_MIN = _int("COOLDOWN_MIN", 120)          # minutos sin repetir señal del mismo par

# Patrón QM
PIVOT_LEN = _int("PIVOT_LEN", 5)
MIN_SWEEP_ATR = _float("MIN_SWEEP_ATR", 0.1)

# Gestión de riesgo
RISK_USDT = _float("RISK_USDT", 10)               # margen por operación
LEVERAGE = _int("LEVERAGE", 3)
MAX_OPEN = _int("MAX_OPEN", 3)                    # posiciones abiertas simultáneas
DAILY_LOSS_LIMIT = _float("DAILY_LOSS_LIMIT", 20) # pérdida diaria máxima en USDT
SL_ATR = _float("SL_ATR", 1.5)                    # stop loss = X * ATR
TP_RR = _float("TP_RR", 2.0)                      # take profit = X veces el riesgo

# Validación básica al arrancar
def validate():
    errors = []
    if not BINGX_API_KEY or not BINGX_SECRET:
        errors.append("BINGX_API_KEY o BINGX_SECRET estáníos. Revisa las variables de entorno en Railway.")
    if TRADE_MODE not in ("signals", "dry", "live"):
        errors.append(f"TRADE_MODE inválido: {TRADE_MODE}. Usa signals / dry / live")
    if TRADE_MODE == "live" and (not BINGX_API_KEY or not BINGX_SECRET):
        errors.append("No se puede usar TRADE_MODE=live sin API keys válidas.")
    return errors
