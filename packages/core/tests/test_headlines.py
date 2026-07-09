import httpx
import pytest
from core import NEWS_URL, fetch_headlines


def test_fetch_headlines_returns_titles(fake_get: None) -> None:
    assert fetch_headlines() == ["First headline", "Second headline", "Third headline"]


def test_fetch_headlines_respects_limit(fake_get: None) -> None:
    assert fetch_headlines(limit=2) == ["First headline", "Second headline"]


def test_fetch_headlines_raises_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _get(url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(500, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", _get)

    with pytest.raises(httpx.HTTPStatusError):
        fetch_headlines()


def test_news_url_points_at_hacker_news() -> None:
    assert NEWS_URL == "https://news.ycombinator.com"
