from __future__ import annotations

import httpx
from ..config import settings
from ..schemas import StandardTask


async def validate_task(task: StandardTask) -> tuple[bool, str | None]:
    if not settings.ENABLE_VALIDATION:
        return True, None

    timeout = settings.REQUEST_TIMEOUT_SECONDS
    headers = {"User-Agent": settings.USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            resp = await client.head(str(task.source_url))
            if resp.status_code >= 400:
                # try GET as fallback
                resp = await client.get(str(task.source_url))
            ok = resp.status_code < 400
            return ok, None if ok else f"bad_status:{resp.status_code}"
    except Exception as exc:
        return False, f"exception:{type(exc).__name__}"