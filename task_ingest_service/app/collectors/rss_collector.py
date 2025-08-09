from __future__ import annotations

from datetime import datetime
from typing import List
import time
import feedparser

from ..schemas import CollectedItem
from ..utils.dedupe import compute_item_hash


class RSSCollector:
    def __init__(self, source_id: str, name: str, url: str, interval_seconds: int = 600) -> None:
        self.id = source_id
        self.name = name
        self.url = url
        self.interval_seconds = interval_seconds

    def collect(self) -> List[CollectedItem]:
        feed = feedparser.parse(self.url)
        items: List[CollectedItem] = []
        for entry in feed.entries:
            link = getattr(entry, "link", None)
            title = getattr(entry, "title", None)
            summary = getattr(entry, "summary", None)
            published_parsed = getattr(entry, "published_parsed", None)
            published_at = datetime.fromtimestamp(time.mktime(published_parsed)) if published_parsed else None
            if not link:
                continue
            external_source_id = compute_item_hash(self.id, link)
            items.append(
                CollectedItem(
                    source_id=self.id,
                    url=link,
                    title=title,
                    summary=summary,
                    published_at=published_at,
                    raw={"external_source_id": external_source_id},
                )
            )
        return items