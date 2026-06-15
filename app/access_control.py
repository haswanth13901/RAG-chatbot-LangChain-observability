import time
from collections import defaultdict
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from app.config import APP_API_KEY, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

_request_log: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(api_key: str) -> None:
    now      = time.time()
    window   = now - RATE_LIMIT_WINDOW_SECONDS
    requests = _request_log[api_key]

    _request_log[api_key] = [t for t in requests if t > window]

    if len(_request_log[api_key]) >= RATE_LIMIT_REQUESTS:
        oldest   = _request_log[api_key][0]
        retry_in = int(RATE_LIMIT_WINDOW_SECONDS - (now - oldest)) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error":      "rate_limit_exceeded",
                "message":    f"Too many requests. Max {RATE_LIMIT_REQUESTS} per {RATE_LIMIT_WINDOW_SECONDS}s.",
                "retry_after": retry_in,
            },
            headers={"Retry-After": str(retry_in)},
        )

    _request_log[api_key].append(now)


def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error":   "missing_api_key",
                "message": "API key required. Add 'X-API-Key: <your-key>' to your request headers.",
            },
        )

    if api_key != APP_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error":   "invalid_api_key",
                "message": "Invalid API key.",
            },
        )

    _check_rate_limit(api_key)

    return api_key