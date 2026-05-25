"""Reference skill — single tool, single purpose: pull a URL's text."""
from __future__ import annotations

from typing import Any

from paperchase.tools.web import web_fetch


def run(args: dict[str, Any]) -> dict[str, Any]:
    url = args.get("url")
    if not url:
        return {"ok": False, "error": "url is required"}
    result = web_fetch(url)
    if result["status"] != "ok":
        return {"ok": False, "error": result.get("reason", result["status"])}
    body = result["body"]
    return {
        "ok": True,
        "url": url,
        "status_code": result["status_code"],
        "preview": body[:2000],
        "length": len(body),
    }
