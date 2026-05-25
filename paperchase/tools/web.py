"""WebFetch — HTTPS-only stdlib-style HTTP GET tool."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx


MAX_BYTES = 1_000_000  # 1 MB cap to avoid blowing memory on giant pages


def web_fetch(url: str, timeout_s: int = 20) -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return {
            "status": "denied",
            "status_code": None,
            "body": "",
            "headers": {},
            "reason": "WebFetch only allows https:// — plain http blocked",
        }
    try:
        with httpx.Client(timeout=timeout_s, follow_redirects=True) as c:
            r = c.get(url)
            body = r.text[:MAX_BYTES]
            return {
                "status": "ok",
                "status_code": r.status_code,
                "body": body,
                "headers": dict(r.headers),
            }
    except Exception as e:
        return {
            "status": "error",
            "status_code": None,
            "body": "",
            "headers": {},
            "reason": str(e),
        }
