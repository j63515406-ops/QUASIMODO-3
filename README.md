# BingX QM Scanner Bot — Versión reparada

## Problema principal que tenías

```
ccxt.base.errors.AuthenticationError: bingx {"code":100413,"msg":"Incorrect apiKey..."}
```

**Causa:** La API Key o el Secret de BingX están incorrectos / vacíos / sin permisos de Futures.

## Cómo arreglar la API Key (OBLIGATORIO)

1. Entra en → https://bingx.com/en/account/api
2. **Borra** la key antigua si es posible
3. Crea una **nueva API Key**
4. Activa permisos de **Futures / Swap / Trade**
5. **NO actives** restricción de IP (Railway usa IPs dinámicas)
6. Copia `API Key` y `Secret Key` **sin espacios**
7. En Railway → Variables:
   - `BINGX_API_KEY` = tu key
   - `BINGX_SECRET` = tu secret
8. Haz **Redeploy**

## Mejoras de esta versión

- Modo `signals` funciona **sin** API keys (solo datos públicos)
- Mensajes de error mucho más claros
- No se cae silenciosamente
- Mejor cálculo de cantidad y manejo de órdenes
- Validación de configuración al arrancar
- Logging más limpio

## Variables de entorno recomendadas

```
TRADE_MODE=signals
TIMEFRAME=15m
SCAN_INTERVAL=300
TOP_N=60
MIN_SCORE=70
COOLDOWN_MIN=120
RISK_USDT=10
LEVERAGE=3
MAX_OPEN=3
DAILY_LOSS_LIMIT=20
SL_ATR=1.5
TP_RR=2.0
```

## Modos

| Modo       | Qué hace                          | ¿Necesita API Key? |
|------------|-----------------------------------|--------------------|
| `signals`  | Solo envía señales a Telegram     | No (recomendado)   |
| `dry`      | Simula operaciones                | Sí                 |
| `live`     | Opera de verdad                   | Sí                 |

**Empieza siempre con `TRADE_MODE=signals`** hasta que veas señales correctas.

## Aviso

Software experimental. No es asesoría financiera. Puedes perder todo el capital.
