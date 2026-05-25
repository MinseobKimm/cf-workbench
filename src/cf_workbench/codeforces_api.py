from __future__ import annotations

import json
import hashlib
import os
import random
import string
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from dataclasses import field
from typing import Any


class CodeforcesAPIError(RuntimeError):
    pass


@dataclass
class CodeforcesAPI:
    min_interval_seconds: float = 2.2
    base_url: str = "https://codeforces.com/api"
    api_key: str | None = None
    api_secret: str | None = None
    use_system_proxy: bool = False
    _last_call: float = 0.0
    _direct_opener: urllib.request.OpenerDirector | None = field(default=None, init=False, repr=False)

    def call(self, method: str, *, require_auth: bool = False, **params: Any) -> Any:
        self._wait_for_rate_limit()
        request_params = {key: value for key, value in params.items() if value is not None}
        if require_auth or (self.api_key and self.api_secret):
            request_params = self._signed_params(method, request_params)
        query = urllib.parse.urlencode(request_params)
        url = f"{self.base_url}/{method}"
        if query:
            url = f"{url}?{query}"
        try:
            with self._urlopen(url, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            raise CodeforcesAPIError(f"network error calling {method}: {reason}") from exc
        except json.JSONDecodeError as exc:
            raise CodeforcesAPIError(f"invalid JSON from Codeforces API {method}") from exc
        if payload.get("status") != "OK":
            comment = payload.get("comment", "unknown Codeforces API error")
            raise CodeforcesAPIError(str(comment))
        return payload.get("result")

    def user_status(self, handle: str, *, count: int = 10) -> list[dict[str, Any]]:
        result = self.call("user.status", handle=handle, count=count)
        if not isinstance(result, list):
            raise CodeforcesAPIError("unexpected user.status response")
        return result

    def user_info(self, handles: str | list[str]) -> list[dict[str, Any]]:
        handle_text = ";".join(handles) if isinstance(handles, list) else handles
        result = self.call("user.info", handles=handle_text)
        if not isinstance(result, list):
            raise CodeforcesAPIError("unexpected user.info response")
        return result

    def user_rating(self, handle: str) -> list[dict[str, Any]]:
        result = self.call("user.rating", handle=handle)
        if not isinstance(result, list):
            raise CodeforcesAPIError("unexpected user.rating response")
        return result

    def user_friends(self, *, only_online: bool | None = None) -> list[str]:
        params: dict[str, Any] = {}
        if only_online is not None:
            params["onlyOnline"] = str(bool(only_online)).lower()
        result = self.call("user.friends", require_auth=True, **params)
        if not isinstance(result, list):
            raise CodeforcesAPIError("unexpected user.friends response")
        return [str(handle) for handle in result]

    def check_auth(self) -> None:
        if not self.api_key or not self.api_secret:
            raise CodeforcesAPIError("Codeforces API key and secret are not configured")
        self.call("user.status", require_auth=True, handle="tourist", count=1)

    def problemset_problems(self) -> list[dict[str, Any]]:
        result = self.call("problemset.problems")
        if not isinstance(result, dict) or not isinstance(result.get("problems"), list):
            raise CodeforcesAPIError("unexpected problemset.problems response")
        return result["problems"]

    def _urlopen(self, url: str, *, timeout: float):
        if self.use_system_proxy or _truthy_env("CFW_CODEFORCES_USE_SYSTEM_PROXY"):
            return urllib.request.urlopen(url, timeout=timeout)
        if self._direct_opener is None:
            self._direct_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        return self._direct_opener.open(url, timeout=timeout)

    def _wait_for_rate_limit(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_call
        if self._last_call and elapsed < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - elapsed)
        self._last_call = time.monotonic()

    def _signed_params(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key or not self.api_secret:
            raise CodeforcesAPIError("Codeforces API key and secret are not configured")
        signed = dict(params)
        signed["apiKey"] = self.api_key
        signed["time"] = int(time.time())
        prefix = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
        ordered = sorted((str(key), str(value)) for key, value in signed.items())
        query = urllib.parse.urlencode(ordered)
        digest = hashlib.sha512(f"{prefix}/{method}?{query}#{self.api_secret}".encode("utf-8")).hexdigest()
        signed["apiSig"] = prefix + digest
        return signed


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}
