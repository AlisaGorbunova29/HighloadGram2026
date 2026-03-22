import os
import logging
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="HighloadGram_1_0")

log = logging.getLogger(__name__)
INSTANCE_ID = os.environ.get("INSTANCE_ID", os.environ.get("HOSTNAME", "local"))

MESSAGE_ITEM = {
    "id": 1,
    "author": "admin",
    "text": "Hello, HighloadGram!",
}

HISTORY_SIZE = 10_000
GENERATED_BOTS_SIZE = 10_000


@app.get("/api/history")
def get_history() -> dict:
    history = [MESSAGE_ITEM] * HISTORY_SIZE
    return {
        "server_time": datetime.now(timezone.utc).isoformat(),
        "messages": history,
    }


@app.post("/api/generate")
def generate_bots(bot_prefix: str = "promo") -> dict:
    log.info(f"[demonstration_balance] instance={INSTANCE_ID}")
    generated = [
        f"{bot_prefix}_{index}" for index in range(1, GENERATED_BOTS_SIZE + 1)
    ]
    return {"bots": generated}
