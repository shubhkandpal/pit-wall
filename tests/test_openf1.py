import pytest
import requests

from pitwall import config, openf1


class FakeResponse:
    def __init__(self, status_code: int, rows: list | None = None) -> None:
        self.status_code = status_code
        self._rows = rows or []

    def json(self) -> list:
        return self._rows

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")


@pytest.fixture
def api(monkeypatch, tmp_path):
    """Point the cache at a temp folder, never sleep, and fake the network."""
    monkeypatch.setattr(config, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(openf1, "_last_call", 0.0)
    monkeypatch.setattr(config, "MIN_SECONDS_BETWEEN_CALLS", 0)
    sleeps: list[float] = []
    monkeypatch.setattr(openf1.time, "sleep", sleeps.append)
    calls: list[dict] = []
    replies: list[FakeResponse] = []

    def fake_get(url, params=None, timeout=None):
        calls.append({"url": url, "params": params})
        return replies.pop(0)

    monkeypatch.setattr(openf1.requests, "get", fake_get)
    return {"calls": calls, "replies": replies, "sleeps": sleeps, "cache": tmp_path}


def test_second_call_comes_from_cache(api):
    api["replies"].append(FakeResponse(200, [{"lap_number": 1}]))
    first = openf1.get("laps", session_key=9158)
    second = openf1.get("laps", session_key=9158)
    assert first == second == [{"lap_number": 1}]
    assert len(api["calls"]) == 1


def test_parameter_order_does_not_matter(api):
    a = openf1.cache_path("laps", {"session_key": 1, "driver_number": 44})
    b = openf1.cache_path("laps", {"driver_number": 44, "session_key": 1})
    assert a == b


def test_retries_after_rate_limit(api):
    api["replies"].extend([FakeResponse(429), FakeResponse(429), FakeResponse(200, [{"ok": 1}])])
    assert openf1.get("pit", session_key=1) == [{"ok": 1}]
    assert len(api["calls"]) == 3
    assert api["sleeps"] == [2, 4]


def test_gives_up_and_caches_nothing(api, monkeypatch):
    monkeypatch.setattr(config, "MAX_RETRIES", 2)
    api["replies"].extend([FakeResponse(500)] * 3)
    with pytest.raises(requests.HTTPError):
        openf1.get("weather", session_key=1)
    assert not list(api["cache"].rglob("*.json"))


def test_no_results_is_empty_and_not_cached(api):
    api["replies"].append(FakeResponse(404))
    assert openf1.get("sessions", year=1999) == []
    assert not list(api["cache"].rglob("*.json"))


def test_waits_between_calls(api, monkeypatch):
    monkeypatch.setattr(config, "MIN_SECONDS_BETWEEN_CALLS", 2.5)
    api["replies"].extend([FakeResponse(200, [{"a": 1}]), FakeResponse(200, [{"b": 2}])])
    openf1.get("stints", session_key=1)
    openf1.get("stints", session_key=2)
    assert len(api["sleeps"]) == 1
    assert 2.0 < api["sleeps"][0] <= 2.5
