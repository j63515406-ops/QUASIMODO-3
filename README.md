# BingX QM Scanner Bot (Reparada & Mejorada)

Bot que escanea futuros USDT-M de BingX, detecta patrones QM + breakouts con volumen, envía señales a Telegram y opcionalmente opera.

## Cambios en esta versión reparada

- Validación de API keys al arrancar (mensaje claro si fallan)
- Mejor manejo de `AuthenticationError`
- Logging más claro
- Mayor robustez en `place_trade` (compatible con diferentes versiones de ccxt/BingX)
- Tabla de configuración validada
- Mensajes de error más útiles en Telegram

## Despliegue en Railway

1. Sube todos los archivos a un repositorio de GitHub.
2. En Railway: **New Project → Deploy from GitHub repo**.
3. En **Variables** pega las de `.env.example` con tus valores reales.
4. Start Command: `python main.py` (o deja el Procfile).
5. Empieza siempre con `TRADE_MODE=signals`.

## Variables importantes

| Variable | Descripción |
|----------|-----------|
| `BINGX_API_KEY` | API Key de BingX (Futures) |
| `BINGX_SECRET` | Secret Key |
| `TELEGRAM_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | Tu chat id |
| `TRADE_MODE` | `signals` / `dry` / `live` |

## Cómo crear la API Key de BingX correctamente

1. Ve a: https://bingx.com/en/account/api
2. Crea una nueva API Key
3. Activa permisos de **Futures / Swap**
4. **No actives restricción de IP** (Railway usa IPs dinámicas)
5. Copia Key y Secret **sin espacios**
6. Pégalas en Railway Variables

## Modos

- `signals` → solo envía avisos a Telegram
- `dry` → simula operaciones
- `live` → opera de verdad

## Aviso

Software experimental. No es asesoría financiera. Puedes perder todo el capital.
