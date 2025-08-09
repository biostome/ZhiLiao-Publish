from __future__ import annotations

import logging
import os
from typing import Dict, Any

import orjson
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .config import settings
from .db import init_db
from .scheduler import IngestScheduler, run_once_now


def _orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, default_response_class=JSONResponse)


@app.on_event("startup")
async def on_startup() -> None:
    try:
        init_db()
    except Exception as exc:
        logger.warning("DB init skipped: %s", exc)
    if settings.SCHEDULER_ENABLED:
        scheduler = IngestScheduler()
        scheduler.start()
        logger.info("Scheduler started")


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/config")
async def cfg() -> Dict[str, Any]:
    # redact secrets
    redacted = settings.model_dump()
    for k in list(redacted.keys()):
        if "KEY" in k or "TOKEN" in k:
            redacted[k] = "***"
    return redacted


@app.post("/run-now")
async def run_now():
    await run_once_now()
    return {"status": "done"}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return PlainTextResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)