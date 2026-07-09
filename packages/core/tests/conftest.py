import httpx
import pytest

SAMPLE_HTML = """
<html><body>
<span class="titleline"><a href="#">First headline</a></span>
<span class="titleline"><a href="#">Second headline</a></span>
<span class="titleline"><a href="#">Third headline</a></span>
</body></html>
"""


@pytest.fixture
def sample_html() -> str:
    return SAMPLE_HTML


@pytest.fixture
def fake_get(monkeypatch: pytest.MonkeyPatch, sample_html: str) -> None:
    def _get(url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(200, text=sample_html, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", _get)
