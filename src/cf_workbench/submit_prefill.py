from __future__ import annotations

import json
import secrets
import threading
import webbrowser
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, urlencode, urlparse, urlunparse

from .paths import parse_codeforces_problem_url


PREFILL_ENDPOINT = "/submit-prefill"
PREFILL_TIMEOUT_SECONDS = 90.0


@dataclass(frozen=True)
class SubmitPrefillResult:
    opened_url: str
    delivered: bool


def build_submit_prefill_payload(
    problem_data: dict[str, Any],
    *,
    problem_key: str,
    source_path: Path,
    language: str,
    submit_url: str,
) -> dict[str, Any]:
    source = source_path.read_text(encoding="utf-8")
    parsed = parse_codeforces_problem_url(str(problem_data.get("url", "")))
    contest_id = str(problem_data.get("contestId") or "") or None
    problem_index = str(problem_data.get("problemIndex") or problem_data.get("index") or "") or None
    normalized_key = str(problem_data.get("problemKey") or problem_key or "")

    if parsed is not None:
        contest_id = parsed.contest_id
        problem_index = parsed.index
        normalized_key = parsed.cf_tool_label

    return {
        "problemKey": normalized_key,
        "contestId": contest_id,
        "problemIndex": problem_index,
        "sourceName": source_path.name,
        "language": language,
        "source": source,
        "submitUrl": submit_url,
    }


def build_submit_prefill_url(submit_url: str, *, port: int, token: str) -> str:
    parsed = urlparse(submit_url)
    fragment_params = {
        "cfw-submit": "1",
        "cfw-port": str(port),
        "cfw-token": token,
    }
    fragment = urlencode(fragment_params)
    return urlunparse(parsed._replace(fragment=fragment))


class SubmitPrefillServer:
    def __init__(self, payload: dict[str, Any], *, host: str = "127.0.0.1", port: int = 0) -> None:
        self.token = secrets.token_urlsafe(24)
        self._delivered = threading.Event()
        self._server = self._build_server(host, port, payload)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def port(self) -> int:
        return int(self._server.server_address[1])

    def start(self) -> None:
        self._thread.start()

    def wait_until_delivered(self, timeout_seconds: float) -> bool:
        return self._delivered.wait(timeout_seconds)

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2.0)

    def _build_server(
        self,
        host: str,
        port: int,
        payload: dict[str, Any],
    ) -> ThreadingHTTPServer:
        expected_token = self.token
        delivered = self._delivered

        class Handler(BaseHTTPRequestHandler):
            def do_OPTIONS(self) -> None:
                self.send_response(HTTPStatus.NO_CONTENT.value)
                self._send_cors_headers()
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path != PREFILL_ENDPOINT:
                    self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})
                    return
                token = (parse_qs(parsed.query).get("token") or [""])[0]
                if not secrets.compare_digest(token, expected_token):
                    self._send_json(HTTPStatus.FORBIDDEN, {"ok": False, "error": "invalid token"})
                    return
                delivered.set()
                self._send_json(HTTPStatus.OK, {"ok": True, **payload})

            def log_message(self, format: str, *args: object) -> None:
                return

            def _send_json(self, status: HTTPStatus, data: dict[str, Any]) -> None:
                encoded = json.dumps(data).encode("utf-8")
                self.send_response(status.value)
                self._send_cors_headers()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def _send_cors_headers(self) -> None:
                self.send_header("Access-Control-Allow-Origin", "https://codeforces.com")
                self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")

        return ThreadingHTTPServer((host, port), Handler)


def open_submit_page_with_prefill(
    submit_url: str,
    payload: dict[str, Any],
    *,
    timeout_seconds: float = PREFILL_TIMEOUT_SECONDS,
) -> SubmitPrefillResult:
    server = SubmitPrefillServer(payload)
    opened_url = build_submit_prefill_url(submit_url, port=server.port, token=server.token)
    server.start()
    try:
        print("Opening Codeforces submit page with local source prefill.")
        print("Keep the updated cf-workbench browser extension enabled.")
        print(f"Waiting up to {timeout_seconds:g} seconds for the page to request the source...")
        webbrowser.open(opened_url)
        delivered = server.wait_until_delivered(timeout_seconds)
        if delivered:
            print("Source was delivered to the browser extension. Review the form before submitting.")
        else:
            print("Timed out before the browser extension requested the source.")
        return SubmitPrefillResult(opened_url=opened_url, delivered=delivered)
    finally:
        server.close()


def prefill_fetch_url(port: int, token: str) -> str:
    return f"http://127.0.0.1:{port}{PREFILL_ENDPOINT}?token={quote(token)}"
