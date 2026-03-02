"""Middleware rate limit — /run, /chat, /ingest (req/min par IP)."""

import os
import time
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# (ip, path_prefix) -> [timestamps]
_requests: dict[tuple[str, str], list[float]] = defaultdict(list)
_CLEANUP_INTERVAL = 60  # sec
_LAST_CLEANUP = time.monotonic()

# Chemins limités (prefix → key pour regrouper /run, /run/stream, /run/partial)
_LIMITED_PREFIXES = [("/run", "run"), ("/chat", "chat"), ("/ingest", "ingest")]

# Limites par défaut (req/min) — configurable via RATE_LIMIT_PER_MIN
_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "20"))
_WINDOW = 60.0


def _get_client_ip(request: Request) -> str:
    """IP client, en tenant compte du proxy (X-Forwarded-For, X-Real-IP)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


def _cleanup_if_needed():
    """Purge les entrées expirées (évite fuite mémoire)."""
    global _LAST_CLEANUP
    now = time.monotonic()
    if now - _LAST_CLEANUP < _CLEANUP_INTERVAL:
        return
    _LAST_CLEANUP = now
    cutoff = now - _WINDOW
    to_del = [k for k, v in _requests.items() if v and v[-1] < cutoff]
    for k in to_del:
        del _requests[k]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limite les requêtes par IP sur /run, /chat, /ingest."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        key_suffix = None
        for prefix, name in _LIMITED_PREFIXES:
            if path.startswith(prefix):
                key_suffix = name
                break
        if key_suffix is None:
            return await call_next(request)

        ip = _get_client_ip(request)
        key = (ip, key_suffix)
        now = time.monotonic()
        cutoff = now - _WINDOW

        _cleanup_if_needed()

        # Filtrer les timestamps dans la fenêtre
        _requests[key] = [t for t in _requests[key] if t > cutoff]
        if len(_requests[key]) >= _LIMIT:
            return JSONResponse(
                status_code=429,
                content={
                    "error": f"Trop de requêtes. Limite : {_LIMIT}/min. Réessayez dans quelques secondes.",
                },
            )
        _requests[key].append(now)

        return await call_next(request)
