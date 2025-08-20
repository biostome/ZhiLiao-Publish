from __future__ import annotations

from typing import Tuple

from ..schemas import CollectedItem, StandardTask
from ..utils.dedupe import is_duplicate, compute_item_hash


def filter_collected_item(item: CollectedItem) -> Tuple[bool, str | None]:
    # Basic sanity checks
    if not item.url:
        return False, "missing_url"
    # Example: dedupe on source+url
    key = compute_item_hash(item.source_id, str(item.url))
    if is_duplicate(key):
        return False, "duplicate_collected"
    return True, None


def filter_generated_task(task: StandardTask) -> Tuple[bool, str | None]:
    # Dedupe on external_source_id
    if is_duplicate(f"task:{task.external_source_id}"):
        return False, "duplicate_task"

    # Optional: simple noise filtering
    if len(task.title.strip()) < 5:
        return False, "title_too_short"

    return True, None