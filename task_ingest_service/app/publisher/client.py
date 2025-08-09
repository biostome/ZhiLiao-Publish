from __future__ import annotations

from typing import Any, Dict, Optional
import httpx
from ..config import settings
from ..schemas import StandardTask, PublishResult


class TaskApiClient:
    def __init__(self) -> None:
        self.base_url = settings.TASK_API_BASE_URL.rstrip("/")
        self.token = settings.TASK_API_TOKEN
        self.timeout = settings.TASK_API_TIMEOUT_SECONDS

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _task_payload(self, task: StandardTask) -> Dict[str, Any]:
        return {
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "source": {
                "source_id": task.source_id,
                "source_url": str(task.source_url),
                "external_source_id": task.external_source_id,
            },
            "created_at": task.created_at.isoformat(),
            "meta": task.meta,
        }

    async def publish(self, task: StandardTask) -> PublishResult:
        url = f"{self.base_url}/tasks"
        async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers()) as client:
            try:
                resp = await client.post(url, json=self._task_payload(task))
                if resp.status_code in (200, 201):
                    data = resp.json()
                    task_id = str(data.get("id") or data.get("task_id") or data.get("data", {}).get("id"))
                    return PublishResult(success=True, task_id=task_id)
                else:
                    return PublishResult(success=False, error=f"status={resp.status_code} body={resp.text}")
            except Exception as exc:
                return PublishResult(success=False, error=str(exc))

    async def find_existing_by_external_id(self, external_source_id: str) -> Optional[str]:
        # If the API supports querying by external id; otherwise return None
        url = f"{self.base_url}/tasks"
        params = {"external_source_id": external_source_id}
        async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers()) as client:
            try:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, dict):
                        items = data.get("items") or data.get("data") or []
                    else:
                        items = data
                    if items:
                        any_item = items[0]
                        return str(any_item.get("id") or any_item.get("task_id"))
                return None
            except Exception:
                return None