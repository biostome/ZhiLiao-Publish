from __future__ import annotations

import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_fixed

try:
    import litellm
except Exception:  # pragma: no cover
    litellm = None  # type: ignore

from ..config import settings
from ..schemas import CollectedItem, StandardTask
from ..utils.dedupe import compute_item_hash


SYSTEM_PROMPT = (
    "你是一个任务信息抽取助手。请从输入的新闻/公告中提取标准化任务，使用 JSON 格式输出："
    "{title, description, priority, status}. priority 取值: low|medium|high, status 固定为 not_started。"
)


class TaskGenerator:
    def __init__(self) -> None:
        self.enabled = settings.ENABLE_AI and (settings.MODEL_API_KEY != "")
        if self.enabled and litellm is not None:
            # Configure provider
            litellm.set_verbose = False

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        assert litellm is not None
        response = litellm.completion(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=400,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
            api_key=settings.MODEL_API_KEY,
        )
        text = response["choices"][0]["message"]["content"]
        try:
            # try find JSON in text
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                text = text[start : end + 1]
            data = json.loads(text)
            return data
        except Exception:
            # fallthrough
            return {}

    def generate(self, item: CollectedItem) -> StandardTask:
        external_source_id = item.raw.get("external_source_id") if item.raw else None
        if not external_source_id:
            external_source_id = compute_item_hash(item.source_id, str(item.url))

        if not self.enabled or litellm is None:
            title = item.title or "未命名任务"
            description = (item.summary or title or "").strip()
            priority = "medium"
            return StandardTask(
                external_source_id=external_source_id,
                title=title[:200],
                description=description[:2000] if description else title,
                priority=priority,
                status="not_started",
                source_url=item.url,
                source_id=item.source_id,
                meta={"generator": "fallback"},
            )

        # AI path
        user_prompt = f"标题: {item.title}\n摘要: {item.summary}\n链接: {item.url}"
        data = self._call_llm(user_prompt)
        title = data.get("title") or (item.title or "未命名任务")
        description = data.get("description") or (item.summary or title)
        priority = data.get("priority") or "medium"
        status = data.get("status") or "not_started"

        return StandardTask(
            external_source_id=external_source_id,
            title=str(title)[:200],
            description=str(description)[:2000],
            priority=str(priority),
            status=str(status),
            source_url=item.url,
            source_id=item.source_id,
            meta={"generator": settings.MODEL_NAME},
        )