"""Cached, rate-limited client for the OpenF1 REST API.

Every answer is saved to data/cache/<endpoint>/<params>.json, so each
request is made only once. Errors and empty answers are never saved.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import requests

from pitwall import config

RETRY_STATUSES = {429, 500, 502, 503, 504}

_last_call = 0.0


def cache_path(endpoint: str, params: dict[str, Any]) -> Path:
    """The cache file for one request. Parameter order does not matter."""
    name = "&".join(f"{key}={params[key]}" for key in sorted(params)) or "all"
    name = re.sub(r"[^A-Za-z0-9._=&-]", "_", name)
    return config.CACHE_DIR / endpoint / f"{name}.json"


def _wait_for_slot() -> None:
    """Sleep until at least MIN_SECONDS_BETWEEN_CALLS have passed since the last call."""
    global _last_call
    gap = time.monotonic() - _last_call
    if gap < config.MIN_SECONDS_BETWEEN_CALLS:
        time.sleep(config.MIN_SECONDS_BETWEEN_CALLS - gap)
    _last_call = time.monotonic()


def _fetch(endpoint: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    """Call the API, retrying after 2, 4, 8, 16, 32 seconds on rate limits and server errors."""
    url = f"{config.API_BASE}/{endpoint}"
    for attempt in range(config.MAX_RETRIES + 1):
        _wait_for_slot()
        last_try = attempt == config.MAX_RETRIES
        try:
            response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        except (requests.ConnectionError, requests.Timeout):
            if last_try:
                raise
            time.sleep(2 ** (attempt + 1))
            continue
        if response.status_code == 404:
            return []  # OpenF1 answers 404 when nothing matches
        if response.status_code in RETRY_STATUSES and not last_try:
            time.sleep(2 ** (attempt + 1))
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("unreachable")


def get(endpoint: str, **params: Any) -> list[dict[str, Any]]:
    """Rows from one OpenF1 endpoint, e.g. get("laps", session_key=9158)."""
    path = cache_path(endpoint, params)
    if path.exists():
        return json.loads(path.read_text())
    rows = _fetch(endpoint, params)
    if rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rows))
        tmp.replace(path)  # atomic: a crash never leaves half a file behind
    return rows
