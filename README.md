# BingX QM Scanner Bot

Escanea futuros USDT-M de BingX, detecta patrones QM y movimientos con volumen,
envía señales a Telegram y opcionalmente opera.

## Despliegue en Railway
1. Sube todos los archivos a un repositorio de GitHub (sin carpetas).
2. En Railway: New Project → Deploy from GitHub repo.
3. En Variables, copia las de `.env.example` con tus valores reales.
4. Si Railway no arranca el proceso, en Settings → Deploy → Start Command pon `python main.py`.
5. Empieza con `TRADE_MODE=signals`. Cuando estés conforme, pasa a `dry` y luego a `live`.

## Crear el bot de Telegram
1. Habla con @BotFather, crea el bot y copia el token → `TELEGRAM_TOKEN`.
2. Envía un mensaje a tu bot, luego abre
   `https://api.telegram.org/bot<TOKEN>/getUpdates` y copia `chat.id` → `TELEGRAM_CHAT_ID`.

## Modos
- `signals`: solo envía avisos.
- `dry`: envía avisos y simula operaciones.
- `live`: opera de verdad en BingX con SL y TP.

## Aviso
Software experimental. No es asesoría financiera. Puedes perder todo lo que operes.
