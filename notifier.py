import logging
import requests

import config

log = logging.getLogger("notifier")


def send(text):
    if not config.TELEGRAM_TOKEN or not config.TELEGRAM_CHAT_ID:
        log.info("[TG sin configurar] %s", text)
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=12,
        )
        if resp.status_code != 200:
            log.warning("Telegram respondió %s: %s", resp.status_code, resp.text[:200])
    except Exception as e:
        log.error("Telegram falló: %s", e)
