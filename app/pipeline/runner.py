from __future__ import annotations

import logging
from typing import List

from ..schemas import CollectedItem, StandardTask
from ..ai.generator import TaskGenerator
from ..filters.rules import filter_collected_item, filter_generated_task
from ..validator.validator import validate_task
from ..publisher.client import TaskApiClient

from prometheus_client import Counter

logger = logging.getLogger(__name__)

METRIC_COLLECTED = Counter("ingest_collected_items", "Items collected", ["collector"]) 
METRIC_FILTERED = Counter("ingest_filtered_items", "Items filtered", ["stage", "reason"]) 
METRIC_TASKS_PUBLISHED = Counter("ingest_published_tasks", "Tasks published")
METRIC_TASKS_FAILED = Counter("ingest_publish_failures", "Task publish failures", ["reason"]) 


def run_collector(collector) -> List[CollectedItem]:
    items = collector.collect()
    METRIC_COLLECTED.labels(collector=collector.id).inc(len(items))
    return items


async def process_items(items: List[CollectedItem], task_api: TaskApiClient, generator: TaskGenerator) -> None:
    for item in items:
        ok, reason = filter_collected_item(item)
        if not ok:
            METRIC_FILTERED.labels(stage="collect", reason=reason or "unknown").inc()
            continue

        task: StandardTask = generator.generate(item)

        ok2, reason2 = filter_generated_task(task)
        if not ok2:
            METRIC_FILTERED.labels(stage="generate", reason=reason2 or "unknown").inc()
            continue

        valid, reason3 = await validate_task(task)
        if not valid:
            METRIC_FILTERED.labels(stage="validate", reason=reason3 or "unknown").inc()
            continue

        # Optional: check existence by external_source_id
        existing_id = await task_api.find_existing_by_external_id(task.external_source_id)
        if existing_id:
            METRIC_FILTERED.labels(stage="publish", reason="already_exists").inc()
            continue

        result = await task_api.publish(task)
        if result.success:
            METRIC_TASKS_PUBLISHED.inc()
            logger.info("Published task id=%s title=%s", result.task_id, task.title)
        else:
            METRIC_TASKS_FAILED.labels(reason=result.error or "unknown").inc()
            logger.warning("Publish failed: %s", result.error)