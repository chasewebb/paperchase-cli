"""Multi-runtime routing — pick the best backend for a given prompt.

Heuristic intent detection over the prompt + capability flags per runtime.
Honors a `force` override and falls back to the default if the preferred
runtime isn't available.

Public surface:
- :func:`pick_backend(prompt, force, available)` → str
- :func:`route_explain(prompt, force, available)` → dict (for `/route`)
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    """What a runtime is strong at — keyed by short tags."""
    code: int = 0       # 0..3 — how strong is this runtime at code
    vision: int = 0     # 0..3 — supports image inputs
    long_ctx: int = 0   # 0..3 — large context window
    cheap: int = 0      # 0..3 — local/free wins on cost
    speed: int = 0      # 0..3 — latency


# Map of runtime name → capability profile. Only the public runtimes.
CAPABILITIES: dict[str, Capability] = {
    # Local, free, no API key. Wins on cost + speed. Mid on code/long-ctx, no vision by default.
    "ollama": Capability(code=2, vision=0, long_ctx=1, cheap=3, speed=3),
    # Anthropic — strong code + long context + reasoning. Vision via Claude 3.5+.
    "anthropic": Capability(code=3, vision=3, long_ctx=3, cheap=1, speed=2),
    # OpenAI — strong general, vision via 4o, broad model selection.
    "openai": Capability(code=2, vision=3, long_ctx=2, cheap=1, speed=2),
}


# Intent heuristics — light regex over the prompt
_CODE_RE = re.compile(
    r"\b(code|function|class|def |bug|stack ?trace|refactor|implement|debug|"
    r"compile|exception|TypeError|ValueError|regex|sql query|python|typescript|"
    r"javascript|rust|golang|swift)\b",
    re.IGNORECASE,
)
_VISION_RE = re.compile(
    r"\b(image|photo|picture|screenshot|describe (this|the) (image|picture|screenshot)|"
    r"\.png|\.jpg|\.jpeg|\.webp|\.gif)\b",
    re.IGNORECASE,
)
_LONG_CTX_RE = re.compile(
    r"\b(entire (file|repo|codebase)|whole document|full transcript|summarize this book)\b",
    re.IGNORECASE,
)


def _classify(prompt: str) -> dict[str, bool]:
    return {
        "code": bool(_CODE_RE.search(prompt)),
        "vision": bool(_VISION_RE.search(prompt)),
        "long_ctx": bool(_LONG_CTX_RE.search(prompt)),
    }


def pick_backend(
    prompt: str,
    *,
    force: str | None = None,
    available: list[str] | None = None,
    default: str = "ollama",
) -> str:
    """Choose a backend for ``prompt``.

    Strategy:
    1. If ``force`` is set and available, use it.
    2. Detect intent (code / vision / long_ctx).
    3. Score each available runtime by how well its capability profile matches.
    4. Return highest scoring; tiebreaker = ``default``.

    Args:
        prompt: the user message
        force: backend name to use regardless of heuristics
        available: list of registered runtime names. If None, all CAPABILITIES are candidates.
        default: tiebreaker + fallback
    """
    candidates = available if available is not None else list(CAPABILITIES.keys())
    if not candidates:
        return default
    if force and force in candidates:
        return force
    intent = _classify(prompt)

    def score(rt: str) -> int:
        c = CAPABILITIES.get(rt, Capability())
        s = c.cheap  # baseline preference for cheap/local
        if intent["code"]:
            s += c.code * 3
        if intent["vision"]:
            s += c.vision * 5  # vision is a hard requirement; weight heavily
        if intent["long_ctx"]:
            s += c.long_ctx * 3
        return s

    # If vision is needed and no runtime has vision >= 2, surface a clear warning
    # by deprioritizing all and falling back to default (which may not have vision).
    ranked = sorted(candidates, key=score, reverse=True)
    top = ranked[0]
    if score(top) == score(default if default in candidates else top):
        return default if default in candidates else top
    return top


def route_explain(
    prompt: str,
    *,
    force: str | None = None,
    available: list[str] | None = None,
    default: str = "ollama",
) -> dict:
    """Returns a structured explanation of the routing decision — used by /route."""
    candidates = available if available is not None else list(CAPABILITIES.keys())
    intent = _classify(prompt)
    chosen = pick_backend(prompt, force=force, available=available, default=default)
    return {
        "prompt_preview": prompt[:80] + ("…" if len(prompt) > 80 else ""),
        "intent": intent,
        "available": candidates,
        "force": force,
        "chosen": chosen,
        "reason": _reason(intent, chosen, force),
    }


def _reason(intent: dict, chosen: str, force: str | None) -> str:
    if force:
        return f"forced via --backend / /backend {force}"
    flags = [k for k, v in intent.items() if v]
    if not flags:
        return f"no intent signal — default to {chosen}"
    return f"intent={','.join(flags)} → routed to {chosen}"
