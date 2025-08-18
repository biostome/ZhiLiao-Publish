from __future__ import annotations

import asyncio
import logging
import yaml

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import settings
from .collectors.rss_collector import RSSCollector
from .pipeline.runner import run_collector, process_items
from .ai.generator import TaskGenerator
from .publisher.client import TaskApiClient

logger = logging.getLogger(__name__)


class IngestScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
        self.generator = TaskGenerator()
        self.task_api = TaskApiClient()

    def load_collectors(self):
        with open(settings.DATA_SOURCES_FILE, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        sources = cfg.get("sources", [])
        collectors = []
        for s in sources:
            if s.get("type") == "rss":
                collectors.append(
                    RSSCollector(
                        source_id=s.get("id"),
                        name=s.get("name", s.get("id")),
                        url=s.get("url"),
                        interval_seconds=int(s.get("interval_seconds", settings.SCHEDULE_INTERVAL_SECONDS)),
                    )
                )
        return collectors

    def start(self) -> None:
        collectors = self.load_collectors()
        for c in collectors:
            logger.info("Scheduling collector %s every %ss", c.id, c.interval_seconds)
            self.scheduler.add_job(
                self._run_once_for_collector,
                "interval",
                seconds=c.interval_seconds,
                args=[c],
                id=f"collector:{c.id}",
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
        self.scheduler.start()

    async def _run_once_for_collector(self, collector) -> None:
        try:
            items = run_collector(collector)
            await process_items(items, self.task_api, self.generator)
        except Exception as exc:
            logger.exception("Collector %s failed: %s", collector.id, exc)


async def run_once_now() -> None:
    sched = IngestScheduler()
    collectors = sched.load_collectors()
    for c in collectors:
        items = run_collector(c)
        await process_items(items, sched.task_api, sched.generator)