import urllib.error
import urllib.parse

import pytest

from cf_workbench.codeforces_api import CodeforcesAPI, CodeforcesAPIError


def test_api_wraps_network_errors(monkeypatch):
    def fake_urlopen(url, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    api = CodeforcesAPI(min_interval_seconds=0, use_system_proxy=True)

    with pytest.raises(CodeforcesAPIError, match="network error calling user.status"):
        api.user_status("tourist", count=1)


def test_problemset_problems_returns_problem_list(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return (
                b'{"status":"OK","result":{"problems":[{"contestId":112,'
                b'"index":"A","rating":800,"tags":["strings"]}],"problemStatistics":[]}}'
            )

    def fake_urlopen(url, timeout):
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    api = CodeforcesAPI(min_interval_seconds=0, use_system_proxy=True)

    assert api.problemset_problems() == [{"contestId": 112, "index": "A", "rating": 800, "tags": ["strings"]}]


def test_api_signs_authenticated_requests(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return b'{"status":"OK","result":[]}'

    def fake_urlopen(url, timeout):
        captured["url"] = url
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("time.time", lambda: 123456)
    monkeypatch.setattr("random.choice", lambda chars: "a")
    api = CodeforcesAPI(min_interval_seconds=0, api_key="key", api_secret="secret", use_system_proxy=True)

    api.user_status("tourist", count=1)

    query = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
    assert query["apiKey"] == ["key"]
    assert query["time"] == ["123456"]
    assert query["apiSig"][0].startswith("aaaaaa")


def test_api_bypasses_environment_proxy_by_default(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return b'{"status":"OK","result":[]}'

    class FakeOpener:
        def open(self, url, timeout):
            captured["url"] = url
            captured["timeout"] = timeout
            return FakeResponse()

    def fake_build_opener(handler):
        captured["proxy_handler"] = handler
        return FakeOpener()

    def fail_urlopen(url, timeout):
        raise AssertionError("system urlopen should not be used")

    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.setattr("urllib.request.urlopen", fail_urlopen)
    monkeypatch.setattr("urllib.request.build_opener", fake_build_opener)

    api = CodeforcesAPI(min_interval_seconds=0)

    assert api.user_status("tourist", count=1) == []
    assert captured["url"].startswith("https://codeforces.com/api/user.status?")
    assert captured["timeout"] == 20
    assert getattr(captured["proxy_handler"], "proxies", None) == {}
