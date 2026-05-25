from __future__ import annotations

import json
import mimetypes
import secrets
import shutil
import threading
import time
import re
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from queue import Empty, Full, Queue
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlparse

from .codeforces_api import CodeforcesAPI, CodeforcesAPIError
from .config import Config, save_codeforces_credentials, save_ui_settings
from .ide import (
    clangd_status,
    compiler_syntax_diagnostics,
    detect_clangd,
    run_lsp_websocket_proxy,
    websocket_accept_key,
)
from .models import PayloadValidationError, Problem
from .paths import problem_directory
from .runner import add_custom_test, run_problem_tests
from .schema import SchemaError, parse_codeforces_url
from .statement_capture import MAX_STATEMENT_PAYLOAD_BYTES, save_statement_capture
from .storage import (
    create_folder,
    create_problem,
    delete_folder,
    delete_problem,
    iter_problem_dirs,
    judge_root,
    list_workspace_folders,
    load_problem_json,
    rename_folder,
    rename_problem,
    resolve_problem_path,
    save_capture,
)
from .submit import build_submit_url_from_problem_json
from .submit_prefill import PREFILL_ENDPOINT, build_submit_prefill_payload, build_submit_prefill_url
from .sync import sync_solved_submissions
from .web_ui import render_index


EARLY_CONTEST_RATING_BONUSES = (500, 350, 250, 150, 100, 50)
SOURCE_FILE_SUFFIXES = {".cpp", ".cc", ".cxx", ".c++"}


def save_problem_from_payload(
    payload: dict[str, Any],
    *,
    workspace: Path,
    template_path: Path | None = None,
) -> Path:
    problem = Problem.from_companion_payload(payload)
    destination = problem_directory(workspace, problem.name, problem.url)
    tests_dir = destination / "tests"
    build_dir = destination / "build"
    tests_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    problem_json = destination / "problem.json"
    problem_data = problem.to_json_data()
    problem_data.setdefault("contestIncluded", False)
    with problem_json.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(problem_data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    source_path = destination / "main.cpp"
    resolved_template = template_path if template_path and template_path.exists() else _package_template()
    if not source_path.exists():
        shutil.copyfile(resolved_template, source_path)

    for index, test in enumerate(problem.tests, start=1):
        (tests_dir / f"{index}.in").write_text(test.input, encoding="utf-8", newline="\n")
        (tests_dir / f"{index}.ans").write_text(test.output, encoding="utf-8", newline="\n")

    return destination


def run_server(config: Config, *, host: str = "127.0.0.1", port: int = 27121) -> None:
    if host != "127.0.0.1":
        raise ValueError("cfw listen binds only to 127.0.0.1")

    class Handler(CompetitiveCompanionHandler):
        workspace = config.workspace
        template_path = config.template
        listen_port = port
        compiler = config.compiler
        language = config.language
        compare_mode = config.compare_mode
        judge_subdir = config.judge_subdir
        api_min_interval_seconds = config.api_min_interval_seconds
        codeforces_handle = config.codeforces_handle
        codeforces_api_key = config.codeforces_api_key
        codeforces_api_secret = config.codeforces_api_secret
        ide_clangd = config.ide_clangd
        ui_language = config.ui_language

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"CF Workbench listening on http://{host}:{port}", flush=True)
    print(f"Workspace: {config.workspace}", flush=True)
    print("Waiting for Competitive Companion payloads...", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


class CompetitiveCompanionHandler(BaseHTTPRequestHandler):
    workspace: Path
    template_path: Path | None
    listen_port: int = 27121
    compiler: str | None = None
    language: str = "cpp17"
    compare_mode: str = "tokens"
    judge_subdir: str = "codeforces"
    api_min_interval_seconds: float = 2.2
    codeforces_handle: str | None = None
    codeforces_api_key: str | None = None
    codeforces_api_secret: str | None = None
    ide_clangd: str | None = None
    ui_language: str = "en"
    solved_sync_limit: int = 500
    problem_metadata_cache: dict[str, dict[str, Any]] | None = None
    problem_metadata_loaded_at: float = 0.0
    problem_metadata_failed_at: float = 0.0
    submit_prefill_payloads: dict[str, tuple[float, dict[str, Any]]] = {}
    submit_prefill_ttl_seconds: float = 120.0
    ui_event_queues: list[Queue[dict[str, Any]]] = []
    ui_event_lock = threading.Lock()

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        if path == "/":
            self._send_html(HTTPStatus.OK, render_index())
            return
        if path == "/api/ide/lsp":
            self._handle_lsp_websocket(parse_qs(parsed_url.query))
            return
        if path.startswith("/static/"):
            self._send_static_asset(path.removeprefix("/static/"))
            return
        if path == PREFILL_ENDPOINT:
            self._handle_submit_prefill_fetch()
            return
        if path == "/api/events":
            self._handle_events()
            return
        if path == "/health":
            self._send_json(HTTPStatus.OK, self._health_payload())
            return
        if path == "/api/problems":
            query = parse_qs(parsed_url.query)
            self._send_json(HTTPStatus.OK, self._api_problem_list(sync_solved=self._truthy_query(query, "syncSolved")))
            return
        if path == "/api/templates":
            self._send_json(HTTPStatus.OK, self._api_template_list())
            return
        if path == "/api/account":
            self._send_json(HTTPStatus.OK, self._api_account())
            return
        if path == "/api/settings":
            self._send_json(HTTPStatus.OK, self._api_settings())
            return
        if path == "/api/stats":
            query = parse_qs(parsed_url.query)
            self._send_json(HTTPStatus.OK, self._api_stats(sync_solved=self._truthy_query(query, "syncSolved")))
            return
        if path.startswith("/api/problems/"):
            parts = self._api_parts(path)
            if len(parts) == 1:
                query = parse_qs(parsed_url.query)
                source_name = (query.get("sourceName") or [""])[0] or None
                self._send_json(HTTPStatus.OK, self._api_problem_detail(parts[0], source_name=source_name))
                return
        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT.value)
        self._send_cors_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/account":
            self._handle_account_save()
            return
        if path == "/api/settings":
            self._handle_settings_save()
            return
        if path == "/api/folders":
            self._handle_create_folder()
            return
        if path.startswith("/api/folders/"):
            self._handle_api_folder_post(path)
            return
        if path == "/api/problems":
            self._handle_create_problem()
            return
        if path == "/api/templates":
            self._handle_create_template()
            return
        if path == "/api/templates/rename":
            self._handle_rename_template()
            return
        if path == "/shutdown":
            self._handle_shutdown()
            return
        if path.startswith("/api/problems/"):
            self._handle_api_post(path)
            return
        if path == "/capture-statement":
            self._handle_statement_capture()
            return
        if path not in {"/", "/capture"}:
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {"ok": False, "error": "POST /, /capture, or /capture-statement only"},
            )
            return
        try:
            payload = self._read_json_payload()
            stored = save_capture(
                payload,
                workspace=self.workspace,
                template_path=self.template_path,
                judge_subdir=self.judge_subdir,
            )
        except (PayloadValidationError, SchemaError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid JSON"})
            return
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return

        print(f"Imported Codeforces problem: {stored.problem_key}", flush=True)
        print(f"Path: {stored.path}", flush=True)
        print(f"Samples: {stored.samples}", flush=True)
        self._broadcast_problem_event("problem-imported", stored.problem_key, stored.path)
        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "problemKey": stored.problem_key,
                "path": str(stored.path),
                "samples": stored.samples,
            },
        )

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/templates":
            self._handle_delete_template(parse_qs(parsed.query))
            return
        if path.startswith("/api/folders/"):
            self._handle_delete_folder(path)
            return
        if path.startswith("/api/problems/"):
            parts = self._api_parts(path)
            if len(parts) == 2 and parts[1] == "sources":
                self._handle_delete_problem_source(parts[0], parse_qs(parsed.query))
                return
            if len(parts) == 3 and parts[1] == "tests":
                self._handle_delete_problem_test(parts[0], parts[2])
                return
            self._handle_delete_problem(path)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "unknown API endpoint"})

    def _handle_create_folder(self) -> None:
        try:
            body = self._read_json_payload()
            name = body.get("name", body.get("path"))
            if not isinstance(name, str) or not name.strip():
                raise ValueError("folder name must be a non-empty string")
            folder_path = create_folder(self.workspace, name, judge_subdir=self.judge_subdir)
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "folder": self._folder_payload(folder_path),
                },
            )
        except (FileExistsError, ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_delete_folder(self, path: str) -> None:
        try:
            folder = self._api_tail(path, "/api/folders/")
            deleted = delete_folder(self.workspace, folder, judge_subdir=self.judge_subdir)
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "folder": str(deleted),
                },
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_api_folder_post(self, path: str) -> None:
        try:
            tail = self._api_tail(path, "/api/folders/")
            if not tail.endswith("/rename"):
                raise ValueError("unknown API endpoint")
            folder = tail[: -len("/rename")]
            if not folder:
                raise ValueError("missing folder path")
            body = self._read_json_payload()
            new_name = body.get("name", body.get("path"))
            if not isinstance(new_name, str) or not new_name.strip():
                raise ValueError("folder name must be a non-empty string")
            renamed = rename_folder(self.workspace, folder, new_name, judge_subdir=self.judge_subdir)
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "folder": self._folder_payload(renamed),
                },
            )
        except (FileExistsError, FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_create_problem(self) -> None:
        try:
            body = self._read_json_payload()
            problem_key = body.get("problemKey")
            if not isinstance(problem_key, str) or not problem_key.strip():
                raise ValueError("problemKey must be a non-empty string")
            name = body.get("name")
            url = body.get("url")
            folder = body.get("folder")
            created = create_problem(
                self.workspace,
                problem_key,
                name=name if isinstance(name, str) else None,
                url=url if isinstance(url, str) else None,
                folder=folder if isinstance(folder, str) and folder.strip() else None,
                template_path=self.template_path,
                judge_subdir=self.judge_subdir,
            )
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "problemKey": created.problem_key,
                    "path": str(created.path),
                },
            )
        except (FileExistsError, ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_create_template(self) -> None:
        try:
            body = self._read_json_payload()
            kind = body.get("kind") or "template"
            algorithm = body.get("algorithm")
            if not isinstance(algorithm, str) or not algorithm.strip():
                raise ValueError("algorithm must be a non-empty string")
            if kind == "algorithm":
                payload = self._save_template_algorithm(algorithm)
            elif kind == "template":
                name = body.get("name")
                source = body.get("source", "")
                extension = body.get("extension", ".cpp")
                if not isinstance(name, str) or not name.strip():
                    raise ValueError("template name must be a non-empty string")
                if not isinstance(source, str):
                    raise ValueError("source must be a string")
                if not isinstance(extension, str):
                    raise ValueError("extension must be a string")
                payload = self._save_template(algorithm, name, source, extension=extension)
            else:
                raise ValueError("kind must be algorithm or template")
            self._send_json(HTTPStatus.OK, {"ok": True, **payload})
        except (FileExistsError, ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_rename_template(self) -> None:
        try:
            body = self._read_json_payload()
            kind = body.get("kind") or "template"
            algorithm = body.get("algorithm")
            new_name = body.get("name")
            if not isinstance(algorithm, str) or not algorithm.strip():
                raise ValueError("algorithm must be a non-empty string")
            if not isinstance(new_name, str) or not new_name.strip():
                raise ValueError("name must be a non-empty string")
            if kind == "algorithm":
                payload = self._rename_template_algorithm(algorithm, new_name)
            elif kind == "template":
                template_name = body.get("template")
                if not isinstance(template_name, str) or not template_name.strip():
                    raise ValueError("template name must be a non-empty string")
                payload = self._rename_template(algorithm, template_name, new_name)
            else:
                raise ValueError("kind must be algorithm or template")
            self._send_json(HTTPStatus.OK, {"ok": True, **payload})
        except (FileExistsError, FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_delete_problem(self, path: str) -> None:
        try:
            key = self._api_tail(path, "/api/problems/")
            if "/" in key:
                raise ValueError("unknown API endpoint")
            deleted = delete_problem(self.workspace, key, judge_subdir=self.judge_subdir)
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "problemKey": key,
                    "path": str(deleted),
                },
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_delete_template(self, query: dict[str, list[str]]) -> None:
        try:
            kind = (query.get("kind") or ["template"])[0].strip() or "template"
            algorithm = (query.get("algorithm") or [""])[0]
            if kind == "algorithm":
                payload = self._delete_template_algorithm(algorithm)
            elif kind == "template":
                name = (query.get("name") or [""])[0]
                payload = self._delete_template(algorithm, name)
            else:
                raise ValueError("kind must be algorithm or template")
            self._send_json(HTTPStatus.OK, {"ok": True, **payload})
        except (FileNotFoundError, OSError, ValueError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_delete_problem_test(self, key: str, test_ref: str) -> None:
        try:
            problem_dir = self._problem_dir(key)
            deleted = self._delete_problem_test(problem_dir, test_ref)
            self._send_json(HTTPStatus.OK, {"ok": True, **deleted})
        except (FileNotFoundError, OSError, ValueError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_delete_problem_source(self, key: str, query: dict[str, list[str]]) -> None:
        try:
            source_name = (query.get("sourceName") or [""])[0]
            if not source_name:
                raise ValueError("sourceName is required")
            problem_dir = self._problem_dir(key)
            payload = self._delete_problem_source(problem_dir, source_name)
            self._send_json(HTTPStatus.OK, {"ok": True, **payload})
        except (FileNotFoundError, OSError, ValueError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_statement_capture(self) -> None:
        try:
            payload = self._read_json_payload(max_bytes=MAX_STATEMENT_PAYLOAD_BYTES)
            stored = save_statement_capture(
                payload,
                workspace=self.workspace,
                template_path=self.template_path,
                judge_subdir=self.judge_subdir,
            )
        except (json.JSONDecodeError, ValueError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return

        print(f"Captured statement DOM: {stored.problem_key}", flush=True)
        print(f"Path: {stored.path}", flush=True)
        self._broadcast_problem_event("statement-captured", stored.problem_key, stored.path)
        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "problemKey": stored.problem_key,
                "path": str(stored.path),
                "createdProblem": stored.created_problem,
                "htmlFile": str(stored.html_file),
                "textFile": str(stored.text_file),
            },
        )

    def _handle_api_post(self, path: str) -> None:
        parts = self._api_parts(path)
        if len(parts) == 4 and parts[1] == "tests" and parts[3] == "rename":
            try:
                body = self._read_json_payload()
                name = body.get("name")
                if not isinstance(name, str) or not name.strip():
                    raise ValueError("test name must be a non-empty string")
                problem_dir = self._problem_dir(parts[0])
                renamed = self._rename_problem_test(problem_dir, parts[2], name)
                self._send_json(HTTPStatus.OK, {"ok": True, **renamed})
            except (FileExistsError, FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return
        if len(parts) != 2:
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "unknown API endpoint"})
            return
        key, action = parts
        try:
            if action == "source":
                body = self._read_json_payload()
                source = body.get("source")
                if not isinstance(source, str):
                    raise ValueError("source must be a string")
                problem_dir = self._problem_dir(key)
                source_name = body.get("sourceName") or "main.cpp"
                if not isinstance(source_name, str):
                    raise ValueError("sourceName must be a string")
                source_path = self._source_file_path(problem_dir, source_name)
                source_path.write_text(source, encoding="utf-8", newline="\n")
                self._send_json(
                    HTTPStatus.OK,
                    {"ok": True, "sourceName": source_path.name, "sourceFiles": self._source_files_payload(problem_dir)},
                )
                return
            if action == "sources":
                body = self._read_json_payload()
                source_name = body.get("sourceName", "")
                if not isinstance(source_name, str):
                    raise ValueError("sourceName must be a string")
                problem_dir = self._problem_dir(key)
                payload = self._create_problem_source(problem_dir, source_name)
                self._send_json(HTTPStatus.OK, {"ok": True, **payload})
                return
            if action == "rename":
                body = self._read_json_payload()
                name = body.get("name")
                if not isinstance(name, str) or not name.strip():
                    raise ValueError("problem name must be a non-empty string")
                problem_dir = self._problem_dir(key)
                data = rename_problem(self.workspace, key, name, judge_subdir=self.judge_subdir)
                self._send_json(HTTPStatus.OK, {"ok": True, "problem": self._public_problem(problem_dir, data)})
                return
            if action == "contest":
                body = self._read_json_payload()
                included = body.get("contestIncluded")
                if not isinstance(included, bool):
                    raise ValueError("contestIncluded must be a boolean")
                problem_dir = self._problem_dir(key)
                data = self._set_problem_contest_included(problem_dir, included)
                self._send_json(HTTPStatus.OK, {"ok": True, "problem": self._public_problem(problem_dir, data)})
                return
            if action == "diagnostics":
                body = self._read_json_payload(max_bytes=2 * 1024 * 1024)
                source = body.get("source")
                if not isinstance(source, str):
                    raise ValueError("source must be a string")
                source_name = body.get("sourceName") or "main.cpp"
                if not isinstance(source_name, str):
                    raise ValueError("sourceName must be a string")
                problem_dir = self._problem_dir(key)
                self._source_file_path(problem_dir, source_name)
                diagnostics = compiler_syntax_diagnostics(
                    problem_dir,
                    source_name,
                    source,
                    configured_compiler=self.compiler,
                )
                self._send_json(HTTPStatus.OK, {"ok": True, "diagnostics": diagnostics})
                return
            if action == "test":
                body = self._read_json_payload()
                compare = body.get("compare")
                if compare not in {"exact", "trim", "tokens", None}:
                    raise ValueError("compare must be exact, trim, or tokens")
                timeout = body.get("timeout")
                timeout_seconds = float(timeout) if timeout not in {None, ""} else None
                problem_dir = self._problem_dir(key)
                source_name = body.get("sourceName") or "main.cpp"
                if not isinstance(source_name, str):
                    raise ValueError("sourceName must be a string")
                result = run_problem_tests(
                    problem_dir,
                    source_name=self._resolve_existing_source_file(problem_dir, source_name).name,
                    configured_compiler=self.compiler,
                    compare_mode=compare or self.compare_mode,  # type: ignore[arg-type]
                    timeout_seconds=timeout_seconds,
                )
                self._send_json(HTTPStatus.OK, self._run_result_json(result))
                return
            if action == "submit-prefill":
                body = self._read_json_payload()
                language = body.get("language") or self.language
                if not isinstance(language, str) or not language.strip():
                    raise ValueError("language must be a non-empty string")
                source_name = body.get("sourceName") or "main.cpp"
                if not isinstance(source_name, str) or not source_name.strip():
                    raise ValueError("sourceName must be a non-empty string")
                submit_url = body.get("submitUrl")
                if submit_url is not None and not isinstance(submit_url, str):
                    raise ValueError("submitUrl must be a string")
                problem_dir = self._problem_dir(key)
                source_path = self._resolve_existing_source_file(problem_dir, source_name)
                problem_data = load_problem_json(problem_dir)
                resolved_submit_url = submit_url.strip() if submit_url else build_submit_url_from_problem_json(problem_data)
                payload = build_submit_prefill_payload(
                    problem_data,
                    problem_key=key,
                    source_path=source_path,
                    language=language,
                    submit_url=resolved_submit_url,
                )
                token = self._store_submit_prefill_payload(payload)
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "url": build_submit_prefill_url(
                            resolved_submit_url,
                            port=self.listen_port,
                            token=token,
                        ),
                        "submitUrl": resolved_submit_url,
                    },
                )
                return
            if action == "tests":
                body = self._read_json_payload()
                test_input = body.get("input")
                test_output = body.get("output")
                if not isinstance(test_input, str) or not isinstance(test_output, str):
                    raise ValueError("input and output must be strings")
                problem_dir = self._problem_dir(key)
                case = add_custom_test(problem_dir, test_input, test_output)
                self._append_custom_test_metadata(problem_dir, case.input_path, case.answer_path)
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "name": case.name or case.input_path.stem,
                        "inputFile": str(case.input_path.relative_to(problem_dir)).replace("\\", "/"),
                        "outputFile": str(case.answer_path.relative_to(problem_dir)).replace("\\", "/"),
                    },
                )
                return
        except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "unknown API action"})

    def _handle_submit_prefill_fetch(self) -> None:
        query = parse_qs(urlparse(self.path).query)
        token = (query.get("token") or [""])[0]
        if not token:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing token"})
            return
        self._prune_submit_prefill_payloads()
        stored = type(self).submit_prefill_payloads.pop(token, None)
        if stored is None:
            self._send_json(HTTPStatus.FORBIDDEN, {"ok": False, "error": "invalid or expired token"})
            return
        _, payload = stored
        self._send_json(HTTPStatus.OK, {"ok": True, **payload})

    def log_message(self, format: str, *args: object) -> None:
        return

    def _handle_shutdown(self) -> None:
        self._send_json(HTTPStatus.OK, {"ok": True, "shuttingDown": True})
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def _handle_events(self) -> None:
        events: Queue[dict[str, Any]] = Queue(maxsize=50)
        self._add_ui_event_queue(events)
        try:
            self.send_response(HTTPStatus.OK.value)
            self._send_cors_headers()
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self._write_sse("ready", {"ok": True})
            while True:
                try:
                    event = events.get(timeout=25)
                except Empty:
                    self._write_sse("ping", {"time": time.time()})
                    continue
                self._write_sse(str(event.get("type") or "message"), event)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, OSError):
            return
        finally:
            self._remove_ui_event_queue(events)

    def _write_sse(self, event_type: str, payload: dict[str, Any]) -> None:
        safe_event_type = "".join(ch for ch in event_type if ch.isalnum() or ch in {"-", "_", "."}) or "message"
        encoded = f"event: {safe_event_type}\ndata: {json.dumps(payload)}\n\n".encode("utf-8")
        self.wfile.write(encoded)
        self.wfile.flush()

    @classmethod
    def _add_ui_event_queue(cls, events: Queue[dict[str, Any]]) -> None:
        with cls.ui_event_lock:
            cls.ui_event_queues.append(events)

    @classmethod
    def _remove_ui_event_queue(cls, events: Queue[dict[str, Any]]) -> None:
        with cls.ui_event_lock:
            cls.ui_event_queues = [candidate for candidate in cls.ui_event_queues if candidate is not events]

    @classmethod
    def _broadcast_ui_event(cls, payload: dict[str, Any]) -> None:
        with cls.ui_event_lock:
            queues = list(cls.ui_event_queues)
        for events in queues:
            try:
                events.put_nowait(payload)
            except Full:
                continue

    def _broadcast_problem_event(self, event_type: str, problem_key: str, problem_path: Path) -> None:
        self._broadcast_ui_event(
            {
                "type": event_type,
                "problemKey": problem_key,
                "path": str(problem_path),
                "time": time.time(),
            }
        )

    def _read_json_payload(self, *, max_bytes: int = 2 * 1024 * 1024) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise ValueError("Content-Length required")
        length = int(raw_length)
        if length > max_bytes:
            raise ValueError("payload too large")
        raw = self.rfile.read(length)
        decoded = raw.decode("utf-8")
        payload = json.loads(decoded)
        if not isinstance(payload, dict):
            raise ValueError("payload must be a JSON object")
        return payload

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status.value)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_html(self, status: HTTPStatus, html: str) -> None:
        encoded = html.encode("utf-8")
        self.send_response(status.value)
        self._send_cors_headers()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_static_asset(self, relative_path: str) -> None:
        try:
            root = (Path(__file__).parent / "static").resolve()
            target = (root / relative_path).resolve()
            target.relative_to(root)
            if not target.is_file():
                raise FileNotFoundError(relative_path)
            content = target.read_bytes()
        except (FileNotFoundError, OSError, ValueError):
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "asset not found"})
            return
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if target.suffix == ".js":
            content_type = "application/javascript"
        elif target.suffix == ".wasm":
            content_type = "application/wasm"
        self.send_response(HTTPStatus.OK.value)
        self._send_cors_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def _handle_lsp_websocket(self, query: dict[str, list[str]]) -> None:
        if self.headers.get("Upgrade", "").lower() != "websocket":
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "websocket upgrade required"})
            return
        key = self.headers.get("Sec-WebSocket-Key")
        if not key:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing Sec-WebSocket-Key"})
            return
        problem_key = (query.get("problemKey") or [""])[0]
        source_name = (query.get("sourceName") or ["main.cpp"])[0]
        try:
            detect_clangd(self.ide_clangd)
            problem_dir = self._problem_dir(problem_key)
            source_path = self._resolve_existing_source_file(problem_dir, source_name)
        except (FileNotFoundError, OSError, ValueError) as exc:
            self._send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"ok": False, "error": str(exc)})
            return
        self.send_response(HTTPStatus.SWITCHING_PROTOCOLS.value)
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", websocket_accept_key(key))
        self.end_headers()
        self.close_connection = True
        try:
            run_lsp_websocket_proxy(
                sock=self.connection,
                stream=self.rfile,
                problem_dir=problem_dir,
                source_path=source_path,
                configured_clangd=self.ide_clangd,
                configured_compiler=self.compiler,
            )
        except OSError:
            return

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _health_payload(self) -> dict[str, Any]:
        return {
            "ok": True,
            "name": "cf-workbench",
            "version": "0.1.0",
            "port": self.listen_port,
            "endpoints": {
                "health": "GET /health",
                "capture": ["POST /", "POST /capture"],
                "statementCapture": "POST /capture-statement",
                "submitPrefill": PREFILL_ENDPOINT,
                "ui": "GET /",
            },
        }

    def _store_submit_prefill_payload(self, payload: dict[str, Any]) -> str:
        self._prune_submit_prefill_payloads()
        token = secrets.token_urlsafe(24)
        type(self).submit_prefill_payloads[token] = (time.monotonic(), payload)
        return token

    def _prune_submit_prefill_payloads(self) -> None:
        now = time.monotonic()
        ttl = self.submit_prefill_ttl_seconds
        payloads = type(self).submit_prefill_payloads
        expired = [token for token, (created_at, _) in payloads.items() if now - created_at > ttl]
        for token in expired:
            payloads.pop(token, None)

    def _api_problem_list(self, *, sync_solved: bool = False) -> dict[str, Any]:
        solved_sync = self._sync_solved_from_account() if sync_solved else None
        problems: list[dict[str, Any]] = []
        metadata = self._codeforces_problem_metadata()
        for problem_dir in iter_problem_dirs(self.workspace, judge_subdir=self.judge_subdir):
            try:
                data = load_problem_json(problem_dir)
            except (OSError, json.JSONDecodeError):
                continue
            self._apply_problem_metadata(problem_dir, data, metadata)
            problems.append(self._problem_summary(problem_dir, data))
        problems.sort(key=lambda item: item.get("updated", ""), reverse=True)
        payload = {
            "ok": True,
            "workspace": str(self.workspace),
            "folders": self._api_folder_list([Path(str(item["path"])) for item in problems if item.get("path")]),
            "problems": problems,
        }
        if solved_sync is not None:
            payload["solvedSync"] = solved_sync
        return payload

    def _sync_solved_from_account(self) -> dict[str, Any]:
        handle = (self.codeforces_handle or "").strip()
        if not handle:
            return {
                "ok": False,
                "skipped": True,
                "error": "Codeforces handle is not configured",
            }
        api = CodeforcesAPI(
            min_interval_seconds=self.api_min_interval_seconds,
            api_key=self.codeforces_api_key,
            api_secret=self.codeforces_api_secret,
        )
        try:
            result = sync_solved_submissions(
                api,
                handle=handle,
                workspace=self.workspace,
                judge_subdir=self.judge_subdir,
                count=self.solved_sync_limit,
            )
        except CodeforcesAPIError as exc:
            return {
                "ok": False,
                "handle": handle,
                "error": str(exc),
            }
        return {
            "ok": True,
            "handle": result.handle,
            "fetched": result.fetched,
            "accepted": result.accepted,
            "localUpdated": result.local_updated,
            "solutionSnapshots": result.solution_snapshots,
            "indexPath": str(result.index_path),
        }

    def _api_problem_detail(self, key: str, *, source_name: str | None = None) -> dict[str, Any]:
        problem_dir = self._problem_dir(key)
        data = load_problem_json(problem_dir)
        self._apply_problem_metadata(problem_dir, data, self._codeforces_problem_metadata())
        source_path = self._selected_source_file(problem_dir, source_name)
        return {
            "ok": True,
            "problem": self._public_problem(problem_dir, data),
            "sourceName": source_path.name,
            "source": source_path.read_text(encoding="utf-8") if source_path.is_file() else "",
            **self._ide_source_payload(problem_dir, source_path),
        }

    def _api_template_list(self) -> dict[str, Any]:
        return {"ok": True, "templates": self._load_templates()}

    def _api_settings(self) -> dict[str, Any]:
        return {"ok": True, "uiLanguage": _ui_language(self.ui_language)}

    def _ide_source_payload(self, problem_dir: Path, source_path: Path) -> dict[str, Any]:
        problem_key = self._problem_key_for_dir(problem_dir)
        source_name = source_path.name
        return {
            "rootUri": problem_dir.resolve().as_uri(),
            "fileUri": source_path.resolve().as_uri(),
            "lspUrl": (
                f"/api/ide/lsp?problemKey={quote(problem_key, safe='')}"
                f"&sourceName={quote(source_name, safe='')}"
            ),
            "diagnosticsUrl": f"/api/problems/{quote(problem_key, safe='')}/diagnostics",
            "ide": clangd_status(self.ide_clangd),
        }

    def _api_account(self) -> dict[str, Any]:
        handle = (self.codeforces_handle or "").strip()
        payload: dict[str, Any] = {
            "ok": True,
            "configured": bool(handle),
            "handle": handle,
            "auth": {
                "apiKeyConfigured": bool(self.codeforces_api_key),
                "apiSecretConfigured": bool(self.codeforces_api_secret),
            },
            "workspace": str(self.workspace),
            "solvedIndex": self._solved_index_summary(),
        }
        if not handle:
            payload["message"] = "Codeforces handle is not configured"
            return payload

        api = CodeforcesAPI(
            min_interval_seconds=self.api_min_interval_seconds,
            api_key=self.codeforces_api_key,
            api_secret=self.codeforces_api_secret,
        )

        try:
            users = api.user_info(handle)
            payload["profile"] = users[0] if users else {}
        except CodeforcesAPIError as exc:
            payload["profileError"] = str(exc)
            payload["profile"] = {}

        try:
            rating_history = api.user_rating(handle)
            payload["ratingHistory"] = self._rating_history_with_early_contest_bonuses(rating_history)
        except CodeforcesAPIError as exc:
            payload["ratingError"] = str(exc)
            payload["ratingHistory"] = []

        try:
            submissions = api.user_status(handle, count=self.solved_sync_limit)
            payload["submissionSummary"] = self._submission_summary(submissions)
            payload["recentSubmissions"] = [self._submission_payload(item) for item in submissions[:25]]
        except CodeforcesAPIError as exc:
            payload["submissionError"] = str(exc)
            payload["submissionSummary"] = self._submission_summary([])
            payload["recentSubmissions"] = []

        if self.codeforces_api_key and self.codeforces_api_secret:
            try:
                payload["friends"] = api.user_friends()
            except CodeforcesAPIError as exc:
                payload["friendsError"] = str(exc)
                payload["friends"] = []
        else:
            payload["friends"] = []

        return payload

    def _handle_account_save(self) -> None:
        try:
            body = self._read_json_payload()
            payload = self._save_account_config(body)
            self._send_json(HTTPStatus.OK, {"ok": True, **payload})
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _handle_settings_save(self) -> None:
        try:
            body = self._read_json_payload()
            payload = self._save_settings_config(body)
            self._send_json(HTTPStatus.OK, {"ok": True, **payload})
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def _save_settings_config(self, body: dict[str, Any]) -> dict[str, Any]:
        ui_language = _ui_language(body.get("uiLanguage"))
        config_path = save_ui_settings(ui_language=ui_language)
        type(self).ui_language = ui_language
        return {"uiLanguage": ui_language, "configPath": str(config_path)}

    def _save_account_config(self, body: dict[str, Any]) -> dict[str, Any]:
        handle = body.get("handle")
        if not isinstance(handle, str) or not handle.strip():
            raise ValueError("Codeforces handle is required")
        api_key = _optional_config_text(body.get("apiKey"), existing=self.codeforces_api_key)
        api_secret = _optional_config_text(body.get("apiSecret"), existing=self.codeforces_api_secret)
        config_path = save_codeforces_credentials(
            handle=handle,
            api_key=api_key,
            api_secret=api_secret,
        )
        type(self).codeforces_handle = handle.strip()
        type(self).codeforces_api_key = api_key
        type(self).codeforces_api_secret = api_secret
        return {
            "configured": True,
            "handle": handle.strip(),
            "configPath": str(config_path),
            "auth": {
                "apiKeyConfigured": bool(api_key),
                "apiSecretConfigured": bool(api_secret),
            },
        }

    def _rating_history_with_early_contest_bonuses(
        self,
        rating_history: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        adjusted: list[dict[str, Any]] = []
        for index, item in enumerate(rating_history):
            if not isinstance(item, dict):
                continue
            contest_bonus = EARLY_CONTEST_RATING_BONUSES[index] if index < len(EARLY_CONTEST_RATING_BONUSES) else 0

            adjusted_item = dict(item)
            adjusted_item["contestNumber"] = index + 1
            adjusted_item["earlyContestBonus"] = contest_bonus
            old_rating = adjusted_item.get("oldRating")
            new_rating = adjusted_item.get("newRating")
            if self._is_rating_number(old_rating) and self._is_rating_number(new_rating):
                rating_change = new_rating - old_rating
                adjusted_item["ratingChange"] = rating_change
                adjusted_item["actualRatingChange"] = rating_change - contest_bonus
            adjusted.append(adjusted_item)
        return adjusted

    def _is_rating_number(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)

    def _api_stats(self, *, sync_solved: bool = False) -> dict[str, Any]:
        solved_sync = self._sync_solved_from_account() if sync_solved else None
        metadata = self._codeforces_problem_metadata()
        local_problems = self._local_problem_index(metadata)
        solved_index = self._load_solved_index()
        records = solved_index.get("problems") if isinstance(solved_index.get("problems"), list) else []
        problems = [
            self._stats_problem_record(record, metadata, local_problems)
            for record in records
            if isinstance(record, dict)
        ]
        problems.sort(key=lambda item: int(item.get("creationTimeSeconds") or 0), reverse=True)
        payload: dict[str, Any] = {
            "ok": True,
            "configured": bool((self.codeforces_handle or "").strip()),
            "handle": solved_index.get("handle") or (self.codeforces_handle or ""),
            "syncedAt": solved_index.get("syncedAt"),
            "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "localProblemCount": len(local_problems),
            "solvedCount": len(problems),
            "problems": problems,
        }
        if solved_sync is not None:
            payload["solvedSync"] = solved_sync
        return payload

    def _local_problem_index(self, metadata: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        problems: dict[str, dict[str, Any]] = {}
        for problem_dir in iter_problem_dirs(self.workspace, judge_subdir=self.judge_subdir):
            try:
                data = load_problem_json(problem_dir)
            except (OSError, json.JSONDecodeError):
                continue
            self._apply_problem_metadata(problem_dir, data, metadata)
            summary = self._problem_summary(problem_dir, data)
            problems[str(summary["problemKey"])] = summary
        return problems

    def _stats_problem_record(
        self,
        record: dict[str, Any],
        metadata: dict[str, dict[str, Any]],
        local_problems: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        problem_key = str(record.get("problemKey") or "")
        local = local_problems.get(problem_key)
        item = dict(record)
        item["problemKey"] = problem_key
        metadata_item = metadata.get(problem_key) or {}
        if local:
            item["local"] = True
            item["path"] = local.get("path")
            item["folder"] = local.get("folder")
            item["url"] = local.get("url") or item.get("url") or self._codeforces_problem_url(item)
            item["name"] = item.get("name") or local.get("name") or problem_key
            item["contest"] = local.get("contest") or self._contest_payload(item)
            item["rating"] = item.get("rating") or local.get("rating") or metadata_item.get("rating")
            item["tags"] = item.get("tags") or local.get("tags") or metadata_item.get("tags") or []
        else:
            item["local"] = False
            item["url"] = item.get("url") or self._codeforces_problem_url(item)
            item["name"] = item.get("name") or problem_key
            item["contest"] = self._contest_payload(item)
            item["rating"] = item.get("rating") or metadata_item.get("rating")
            item["tags"] = item.get("tags") or metadata_item.get("tags") or []
        if not isinstance(item.get("tags"), list):
            item["tags"] = []
        return item

    def _load_solved_index(self) -> dict[str, Any]:
        index_path = self._solved_index_path()
        if not index_path.is_file():
            return {"schemaVersion": 1, "handle": self.codeforces_handle, "count": 0, "problems": []}
        try:
            with index_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {"schemaVersion": 1, "handle": self.codeforces_handle, "count": 0, "problems": []}
        return data if isinstance(data, dict) else {"schemaVersion": 1, "handle": self.codeforces_handle, "count": 0, "problems": []}

    def _solved_index_summary(self) -> dict[str, Any]:
        data = self._load_solved_index()
        problems = data.get("problems") if isinstance(data.get("problems"), list) else []
        return {
            "handle": data.get("handle"),
            "syncedAt": data.get("syncedAt"),
            "count": len(problems),
            "path": str(self._solved_index_path()),
        }

    def _solved_index_path(self) -> Path:
        return judge_root(self.workspace, judge_subdir=self.judge_subdir) / ".cfw" / "solved.json"

    def _submission_summary(self, submissions: list[dict[str, Any]]) -> dict[str, Any]:
        verdicts: dict[str, int] = {}
        languages: dict[str, int] = {}
        attempted: set[str] = set()
        accepted: set[str] = set()
        for submission in submissions:
            verdict = str(submission.get("verdict") or "UNKNOWN")
            verdicts[verdict] = verdicts.get(verdict, 0) + 1
            language = submission.get("programmingLanguage")
            if language:
                language_text = str(language)
                languages[language_text] = languages.get(language_text, 0) + 1
            problem_key = self._problem_key_from_submission(submission)
            if problem_key:
                attempted.add(problem_key)
                if verdict == "OK":
                    accepted.add(problem_key)
        return {
            "fetched": len(submissions),
            "attemptedProblems": len(attempted),
            "acceptedProblems": len(accepted),
            "verdicts": verdicts,
            "languages": languages,
        }

    def _submission_payload(self, submission: dict[str, Any]) -> dict[str, Any]:
        problem = submission.get("problem") if isinstance(submission.get("problem"), dict) else {}
        problem_key = self._problem_key_from_submission(submission)
        item = {
            "id": submission.get("id"),
            "verdict": submission.get("verdict"),
            "programmingLanguage": submission.get("programmingLanguage"),
            "creationTimeSeconds": submission.get("creationTimeSeconds"),
            "timeConsumedMillis": submission.get("timeConsumedMillis"),
            "memoryConsumedBytes": submission.get("memoryConsumedBytes"),
            "problem": {
                "problemKey": problem_key,
                "contestId": problem.get("contestId"),
                "index": problem.get("index"),
                "name": problem.get("name"),
                "rating": problem.get("rating"),
                "tags": problem.get("tags") if isinstance(problem.get("tags"), list) else [],
            },
        }
        item["problem"]["url"] = self._codeforces_problem_url(item["problem"])
        return item

    def _problem_key_from_submission(self, submission: dict[str, Any]) -> str:
        problem = submission.get("problem") if isinstance(submission.get("problem"), dict) else {}
        contest_id = problem.get("contestId")
        index = problem.get("index")
        if contest_id is None or index in {None, ""}:
            return ""
        return f"{contest_id}{index}"

    def _codeforces_problem_url(self, item: dict[str, Any]) -> str:
        contest_id = item.get("contestId")
        index = item.get("index")
        if contest_id in {None, ""} or index in {None, ""}:
            return ""
        problem_key = str(item.get("problemKey") or "")
        if problem_key.startswith("gym-"):
            return f"https://codeforces.com/gym/{contest_id}/problem/{index}"
        return f"https://codeforces.com/problemset/problem/{contest_id}/{index}"

    def _problem_summary(self, problem_dir: Path, data: dict[str, Any]) -> dict[str, Any]:
        statement_capture = data.get("statementCapture")
        statement_html = problem_dir / "statement.html"
        updated = problem_dir.stat().st_mtime
        if statement_html.is_file():
            updated = max(updated, statement_html.stat().st_mtime)
        source_files = self._source_files_payload(problem_dir)
        for source_file in source_files:
            updated = max(updated, float(source_file.get("updated") or 0))
        contest = self._contest_payload(data)
        return {
            "problemKey": str(data.get("problemKey") or problem_dir.name),
            "name": str(data.get("name") or problem_dir.name),
            "group": data.get("group"),
            "contestId": data.get("contestId"),
            "index": data.get("index"),
            "groupCode": data.get("groupCode"),
            "contest": contest,
            "contestIncluded": bool(data.get("contestIncluded", False)),
            "folder": self._problem_folder(problem_dir),
            "rating": data.get("rating") or data.get("difficulty"),
            "tags": data.get("tags") if isinstance(data.get("tags"), list) else [],
            "url": str(data.get("url") or ""),
            "samples": len(data.get("tests") or []),
            "solved": data.get("solved") if isinstance(data.get("solved"), dict) else None,
            "updated": updated,
            "hasStatement": bool(isinstance(statement_capture, dict) and statement_html.is_file()),
            "sourceFiles": source_files,
            "path": str(problem_dir),
        }

    def _source_file_paths(self, problem_dir: Path) -> list[Path]:
        try:
            candidates = [
                path
                for path in problem_dir.iterdir()
                if path.is_file() and path.suffix.lower() in SOURCE_FILE_SUFFIXES
            ]
        except OSError:
            return []
        return sorted(candidates, key=self._source_sort_key)

    def _source_sort_key(self, path: Path) -> tuple[int, int, str]:
        lowered = path.name.lower()
        if lowered == "main.cpp":
            return (0, 0, lowered)
        match = re.fullmatch(r"main(\d+)\.(?:cpp|cc|cxx|c\+\+)", lowered)
        if match:
            return (1, int(match.group(1)), lowered)
        return (2, 0, lowered)

    def _source_files_payload(self, problem_dir: Path) -> list[dict[str, Any]]:
        payload: list[dict[str, Any]] = []
        for path in self._source_file_paths(problem_dir):
            try:
                stat = path.stat()
            except OSError:
                continue
            payload.append(
                {
                    "name": path.name,
                    "path": path.name,
                    "primary": path.name == "main.cpp",
                    "updated": stat.st_mtime,
                    "size": stat.st_size,
                }
            )
        return payload

    def _selected_source_file(self, problem_dir: Path, source_name: str | None = None) -> Path:
        source_files = self._source_file_paths(problem_dir)
        if source_name:
            requested = self._source_file_path(problem_dir, source_name)
            if requested.is_file() or not source_files:
                return requested
        if source_files:
            return source_files[0]
        return self._source_file_path(problem_dir, "main.cpp")

    def _resolve_existing_source_file(self, problem_dir: Path, source_name: str) -> Path:
        source_path = self._source_file_path(problem_dir, source_name)
        if not source_path.is_file():
            raise FileNotFoundError(f"source file not found: {source_path.name}")
        return source_path

    def _source_file_path(self, problem_dir: Path, source_name: str) -> Path:
        name = self._normalized_source_name(source_name)
        target = (problem_dir / name).resolve()
        try:
            target.relative_to(problem_dir.resolve())
        except ValueError as exc:
            raise ValueError("source path escapes problem directory") from exc
        return target

    def _normalized_source_name(self, source_name: str) -> str:
        name = str(source_name or "").strip()
        if not name:
            raise ValueError("sourceName must be a non-empty string")
        if "/" in name or "\\" in name or Path(name).name != name:
            raise ValueError("sourceName must be a file name, not a path")
        if name in {".", ".."} or name.startswith("."):
            raise ValueError("sourceName must be a visible C++ file")
        if Path(name).suffix.lower() not in SOURCE_FILE_SUFFIXES:
            raise ValueError("sourceName must be a C++ source file")
        forbidden = set('<>:"|?*')
        if any(ch in forbidden or ord(ch) < 32 for ch in name):
            raise ValueError("sourceName contains invalid filename characters")
        return name

    def _create_problem_source(self, problem_dir: Path, source_name: str) -> dict[str, Any]:
        name = self._source_name_for_create(problem_dir, source_name)
        source_path = self._source_file_path(problem_dir, name)
        if source_path.exists():
            raise FileExistsError(f"source file already exists: {source_path.name}")
        source = self._source_template_text()
        source_path.write_text(source, encoding="utf-8", newline="\n")
        data = load_problem_json(problem_dir)
        return {
            "sourceName": source_path.name,
            "source": source,
            "problem": self._public_problem(problem_dir, data),
            **self._ide_source_payload(problem_dir, source_path),
        }

    def _delete_problem_source(self, problem_dir: Path, source_name: str) -> dict[str, Any]:
        source_path = self._resolve_existing_source_file(problem_dir, source_name)
        source_files = self._source_file_paths(problem_dir)
        if len(source_files) <= 1:
            raise ValueError("cannot delete the only source file")
        source_path.unlink()
        selected = self._selected_source_file(problem_dir)
        data = load_problem_json(problem_dir)
        return {
            "deletedSourceName": source_path.name,
            "sourceName": selected.name,
            "source": selected.read_text(encoding="utf-8") if selected.is_file() else "",
            "problem": self._public_problem(problem_dir, data),
            **self._ide_source_payload(problem_dir, selected),
        }

    def _source_name_for_create(self, problem_dir: Path, source_name: str) -> str:
        name = str(source_name or "").strip()
        if not name:
            return self._next_source_name(problem_dir)
        if not Path(name).suffix:
            name += ".cpp"
        return name

    def _next_source_name(self, problem_dir: Path) -> str:
        existing = {path.name.lower() for path in self._source_file_paths(problem_dir)}
        for index in range(2, 1000):
            name = f"main{index}.cpp"
            if name.lower() not in existing:
                return name
        raise FileExistsError("too many source versions")

    def _source_template_text(self) -> str:
        configured_template = getattr(self, "template_path", None)
        template = configured_template if configured_template and configured_template.exists() else _package_template()
        source = template.read_text(encoding="utf-8")
        return source if source.endswith("\n") else source + "\n"

    def _contest_payload(self, data: dict[str, Any]) -> dict[str, Any] | None:
        contest_id = data.get("contestId")
        index = data.get("index")
        group_code = data.get("groupCode")
        parsed = None
        if contest_id in {None, ""} or index in {None, ""}:
            parsed = parse_codeforces_url(str(data.get("url") or ""))
            if parsed:
                contest_id = parsed.contest_id
                index = parsed.index
                group_code = group_code or parsed.group_code
        if contest_id in {None, ""} or index in {None, ""}:
            return None
        problem_key = str(data.get("problemKey") or "")
        title = data.get("group")
        kind = "contest"
        key = str(contest_id)
        if problem_key.startswith("gym-") or (parsed and parsed.source == "gym"):
            kind = "gym"
            key = f"gym-{contest_id}"
        elif group_code or (parsed and parsed.source == "group"):
            kind = "group"
            key = f"group-{group_code}-{contest_id}"
        title_text = str(title).strip() if title is not None else ""
        if title_text:
            label = f"{contest_id} - {title_text}"
        elif kind == "gym":
            label = f"Gym {contest_id}"
        elif kind == "group":
            label = f"Group {group_code} / Contest {contest_id}"
        else:
            label = f"Contest {contest_id}"
        return {
            "key": key,
            "label": label,
            "kind": kind,
            "contestId": contest_id,
            "index": index,
            "groupCode": group_code,
        }

    def _api_folder_list(self, problem_dirs: list[Path]) -> list[dict[str, Any]]:
        folders: list[dict[str, Any]] = []
        for folder in list_workspace_folders(self.workspace, judge_subdir=self.judge_subdir):
            count = sum(1 for problem_dir in problem_dirs if folder.path in problem_dir.parents)
            folders.append({**self._folder_payload(folder.path), "problems": count})
        return folders

    def _folder_payload(self, folder_path: Path) -> dict[str, Any]:
        root = self.workspace / self.judge_subdir
        return {
            "name": str(folder_path.relative_to(root)).replace("\\", "/"),
            "path": str(folder_path),
        }

    def _problem_folder(self, problem_dir: Path) -> str:
        workspace = getattr(self, "workspace", None)
        if workspace is None:
            return ""
        root = workspace / getattr(self, "judge_subdir", "codeforces")
        try:
            parent = problem_dir.parent.relative_to(root)
        except ValueError:
            return ""
        return "" if str(parent) == "." else parent.as_posix()

    def _problem_key_for_dir(self, problem_dir: Path) -> str:
        try:
            data = load_problem_json(problem_dir)
        except (FileNotFoundError, ValueError):
            return problem_dir.name
        problem_key = data.get("problemKey")
        return problem_key.strip() if isinstance(problem_key, str) and problem_key.strip() else problem_dir.name

    def _codeforces_problem_metadata(self) -> dict[str, dict[str, Any]]:
        handler_cls = type(self)
        if handler_cls.problem_metadata_cache is not None:
            return handler_cls.problem_metadata_cache
        if handler_cls.problem_metadata_failed_at and time.monotonic() - handler_cls.problem_metadata_failed_at < 300:
            return {}
        api = CodeforcesAPI(min_interval_seconds=self.api_min_interval_seconds)
        try:
            problems = api.problemset_problems()
        except CodeforcesAPIError:
            handler_cls.problem_metadata_failed_at = time.monotonic()
            return {}
        metadata: dict[str, dict[str, Any]] = {}
        for problem in problems:
            if not isinstance(problem, dict):
                continue
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id is None or not index:
                continue
            key = f"{contest_id}{index}"
            item: dict[str, Any] = {}
            if isinstance(problem.get("rating"), int):
                item["rating"] = problem["rating"]
            if isinstance(problem.get("tags"), list):
                item["tags"] = [str(tag) for tag in problem["tags"]]
            if item:
                metadata[key] = item
        handler_cls.problem_metadata_cache = metadata
        handler_cls.problem_metadata_loaded_at = time.monotonic()
        return metadata

    def _apply_problem_metadata(
        self,
        problem_dir: Path,
        data: dict[str, Any],
        metadata: dict[str, dict[str, Any]],
    ) -> None:
        key = str(data.get("problemKey") or problem_dir.name)
        item = metadata.get(key)
        if not item:
            return
        changed = False
        if "rating" in item and data.get("rating") != item["rating"]:
            data["rating"] = item["rating"]
            changed = True
        if "tags" in item and data.get("tags") != item["tags"]:
            data["tags"] = item["tags"]
            changed = True
        if changed:
            problem_json = problem_dir / "problem.json"
            problem_json.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _set_problem_contest_included(self, problem_dir: Path, included: bool) -> dict[str, Any]:
        problem_json = problem_dir / "problem.json"
        data = load_problem_json(problem_dir)
        data["contestIncluded"] = included
        problem_json.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return data

    def _public_problem(self, problem_dir: Path, data: dict[str, Any]) -> dict[str, Any]:
        return {
            **self._problem_summary(problem_dir, data),
            "group": data.get("group"),
            "timeLimitMs": data.get("timeLimitMs") or data.get("timeLimit"),
            "memoryLimitMb": data.get("memoryLimitMb") or data.get("memoryLimit"),
            "interactive": bool(data.get("interactive", False)),
            "tests": self._public_tests(problem_dir, data),
            "statement": self._statement_payload(problem_dir, data),
            "path": str(problem_dir),
        }

    def _public_tests(self, problem_dir: Path, data: dict[str, Any]) -> list[dict[str, Any]]:
        tests: list[dict[str, Any]] = []
        for index, test in enumerate(data.get("tests") or [], start=1):
            if not isinstance(test, dict):
                continue
            item = {
                "name": str(test.get("name") or f"sample_{index}"),
                "inputFile": test.get("inputFile"),
                "outputFile": test.get("outputFile"),
                "input": test.get("input") if isinstance(test.get("input"), str) else "",
                "output": test.get("output") if isinstance(test.get("output"), str) else "",
            }
            if item["inputFile"] and not item["input"]:
                item["input"] = self._read_problem_text_file(problem_dir, str(item["inputFile"]))
            if item["outputFile"] and not item["output"]:
                item["output"] = self._read_problem_text_file(problem_dir, str(item["outputFile"]))
            tests.append(item)
        return tests

    def _read_problem_text_file(self, problem_dir: Path, relative_path: str) -> str:
        target = problem_dir / relative_path
        try:
            target.resolve().relative_to(problem_dir.resolve())
        except ValueError:
            return ""
        try:
            return target.read_text(encoding="utf-8")
        except OSError:
            return ""

    def _statement_payload(self, problem_dir: Path, data: dict[str, Any]) -> dict[str, Any]:
        sections: list[dict[str, str]] = []
        sources: list[dict[str, Any]] = [data]
        extra = data.get("extra")
        if isinstance(extra, dict):
            sources.append(extra)

        field_titles = {
            "statement": "Statement",
            "legend": "Statement",
            "problemStatement": "Statement",
            "inputSpecification": "Input",
            "outputSpecification": "Output",
            "notes": "Notes",
            "note": "Notes",
        }
        seen: set[tuple[str, str]] = set()
        for source in sources:
            for field, title in field_titles.items():
                value = source.get(field)
                text = self._extract_statement_text(value)
                if not text:
                    continue
                marker = (title, text)
                if marker in seen:
                    continue
                seen.add(marker)
                sections.append({"title": title, "text": text})
        statement_capture = data.get("statementCapture")
        captured: dict[str, Any] = {}
        if isinstance(statement_capture, dict):
            html_file = statement_capture.get("htmlFile")
            text_file = statement_capture.get("textFile")
            captured = {
                "kind": statement_capture.get("kind"),
                "capturedAt": statement_capture.get("capturedAt"),
                "url": statement_capture.get("url"),
                "title": statement_capture.get("title"),
                "html": self._read_problem_text_file(problem_dir, str(html_file))
                if isinstance(html_file, str)
                else "",
                "text": self._read_problem_text_file(problem_dir, str(text_file))
                if isinstance(text_file, str)
                else "",
            }
        return {"sections": sections, "capture": captured}

    def _extract_statement_text(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            for key in ("text", "plainText", "html", "value"):
                nested = value.get(key)
                if isinstance(nested, str) and nested.strip():
                    return nested.strip()
        if isinstance(value, list):
            parts = [self._extract_statement_text(item) for item in value]
            return "\n\n".join(part for part in parts if part)
        return ""

    def _problem_dir(self, key: str) -> Path:
        candidate = resolve_problem_path(self.workspace, key, judge_subdir=self.judge_subdir)
        self._ensure_inside_workspace(candidate)
        return candidate

    def _ensure_inside_workspace(self, path: Path) -> None:
        workspace = self.workspace.resolve()
        resolved = path.resolve()
        try:
            resolved.relative_to(workspace)
        except ValueError as exc:
            raise ValueError("path escapes workspace") from exc

    def _api_parts(self, path: str) -> list[str]:
        prefix = "/api/problems/"
        tail = path.removeprefix(prefix)
        return [unquote(part) for part in tail.split("/") if part]

    def _truthy_query(self, query: dict[str, list[str]], name: str) -> bool:
        value = (query.get(name) or [""])[0].strip().lower()
        return value in {"1", "true", "yes", "on"}

    def _api_tail(self, path: str, prefix: str) -> str:
        tail = unquote(path.removeprefix(prefix)).strip("/")
        if not tail:
            raise ValueError("missing API path")
        return tail

    def _run_result_json(self, result) -> dict[str, Any]:
        return {
            "ok": True,
            "success": result.success,
            "skippedReason": result.skipped_reason,
            "compile": {
                "success": result.compile_result.success,
                "command": result.compile_result.command,
                "returncode": result.compile_result.returncode,
                "stdout": result.compile_result.stdout,
                "stderr": result.compile_result.stderr,
                "warning": result.compile_result.warning,
            },
            "cases": [
                {
                    "name": case.case.name or f"case_{case.case.number}",
                    "status": case.status,
                    "expected": case.expected,
                    "actual": case.actual,
                    "stderr": case.stderr,
                    "returncode": case.returncode,
                    "diff": case.diff,
                    "elapsedMs": case.elapsed_ms,
                }
                for case in result.cases
            ],
        }

    def _append_custom_test_metadata(self, problem_dir: Path, input_path: Path, output_path: Path) -> None:
        problem_json = problem_dir / "problem.json"
        data = load_problem_json(problem_dir)
        tests = data.setdefault("tests", [])
        name = input_path.stem
        tests.append(
            {
                "name": name,
                "inputFile": str(input_path.relative_to(problem_dir)).replace("\\", "/"),
                "outputFile": str(output_path.relative_to(problem_dir)).replace("\\", "/"),
            }
        )
        problem_json.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _template_store_dir(self) -> Path:
        root = self.workspace.resolve() / self.judge_subdir / ".cfw"
        self._ensure_inside_workspace(root)
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _template_index_path(self) -> Path:
        return self._template_store_dir() / "templates.json"

    def _template_files_dir(self) -> Path:
        path = self._template_store_dir() / "templates"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _load_templates(self) -> list[dict[str, Any]]:
        path = self._template_index_path()
        if not path.is_file():
            return []
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return []
        algorithms = data.get("algorithms") if isinstance(data, dict) else None
        if not isinstance(algorithms, list):
            return []
        loaded = [item for item in algorithms if isinstance(item, dict)]
        root = self._template_store_dir()
        for algorithm in loaded:
            templates = algorithm.get("templates")
            if not isinstance(templates, list):
                continue
            for template in templates:
                if not isinstance(template, dict):
                    continue
                relative = template.get("file")
                if not isinstance(relative, str):
                    continue
                path = (root / relative).resolve()
                try:
                    path.relative_to(root)
                    template["source"] = path.read_text(encoding="utf-8") if path.is_file() else ""
                except (OSError, ValueError):
                    template["source"] = ""
        return loaded

    def _write_templates(self, algorithms: list[dict[str, Any]]) -> None:
        payload = {"schemaVersion": 1, "algorithms": algorithms}
        self._template_index_path().write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def _save_template_algorithm(self, algorithm: str) -> dict[str, Any]:
        algorithms = self._load_templates()
        name = algorithm.strip()
        existing = self._find_template_algorithm(algorithms, name)
        if existing is None:
            algorithms.append({"name": name, "templates": []})
            self._write_templates(algorithms)
        return {"templates": algorithms}

    def _save_template(self, algorithm: str, name: str, source: str, *, extension: str = ".cpp") -> dict[str, Any]:
        algorithms = self._load_templates()
        algorithm_name = algorithm.strip()
        template_name = name.strip()
        item = self._find_template_algorithm(algorithms, algorithm_name)
        if item is None:
            item = {"name": algorithm_name, "templates": []}
            algorithms.append(item)
        templates = item.setdefault("templates", [])
        if not isinstance(templates, list):
            templates = []
            item["templates"] = templates
        safe_extension = extension.strip() if extension.strip().startswith(".") else f".{extension.strip() or 'cpp'}"
        file_path = self._template_files_dir() / _safe_template_part(algorithm_name) / f"{_safe_template_part(template_name)}{safe_extension}"
        self._ensure_inside_workspace(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(source, encoding="utf-8", newline="\n")
        relative_path = str(file_path.relative_to(self._template_store_dir())).replace("\\", "/")
        existing = None
        for candidate in templates:
            if isinstance(candidate, dict) and candidate.get("name") == template_name:
                existing = candidate
                break
        payload = {
            "name": template_name,
            "file": relative_path,
            "source": source,
            "updatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
        if existing is None:
            templates.append(payload)
        else:
            existing.update(payload)
        self._write_templates(algorithms)
        return {"templates": algorithms, "template": payload}

    def _rename_template_algorithm(self, algorithm: str, new_name: str) -> dict[str, Any]:
        algorithm_name = algorithm.strip()
        renamed_name = new_name.strip()
        if not algorithm_name:
            raise ValueError("algorithm must be a non-empty string")
        if not renamed_name:
            raise ValueError("name must be a non-empty string")
        algorithms = self._load_templates()
        item = self._find_template_algorithm(algorithms, algorithm_name)
        if item is None:
            raise FileNotFoundError(f"template algorithm not found: {algorithm_name}")
        existing = self._find_template_algorithm(algorithms, renamed_name)
        if existing is not None and existing is not item:
            raise FileExistsError(f"template algorithm already exists: {renamed_name}")

        old_safe = _safe_template_part(algorithm_name)
        new_safe = _safe_template_part(renamed_name)
        old_dir = self._template_files_dir() / old_safe
        new_dir = self._template_files_dir() / new_safe
        if old_dir != new_dir and old_dir.exists():
            if new_dir.exists():
                raise FileExistsError(f"template folder already exists: {renamed_name}")
            new_dir.parent.mkdir(parents=True, exist_ok=True)
            old_dir.rename(new_dir)

        item["name"] = renamed_name
        templates = item.get("templates")
        if isinstance(templates, list):
            for template in templates:
                if not isinstance(template, dict):
                    continue
                relative = template.get("file")
                if not isinstance(relative, str):
                    continue
                prefix = f"templates/{old_safe}/"
                if relative.startswith(prefix):
                    template["file"] = f"templates/{new_safe}/{relative[len(prefix):]}"
                    template["updatedAt"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        self._write_templates(algorithms)
        return {"templates": algorithms, "algorithm": renamed_name}

    def _rename_template(self, algorithm: str, name: str, new_name: str) -> dict[str, Any]:
        algorithm_name = algorithm.strip()
        template_name = name.strip()
        renamed_name = new_name.strip()
        if not algorithm_name:
            raise ValueError("algorithm must be a non-empty string")
        if not template_name:
            raise ValueError("template name must be a non-empty string")
        if not renamed_name:
            raise ValueError("name must be a non-empty string")
        algorithms = self._load_templates()
        item = self._find_template_algorithm(algorithms, algorithm_name)
        if item is None:
            raise FileNotFoundError(f"template algorithm not found: {algorithm_name}")
        templates = item.get("templates")
        if not isinstance(templates, list):
            raise FileNotFoundError(f"template not found: {template_name}")
        target = None
        for template in templates:
            if not isinstance(template, dict):
                continue
            current_name = str(template.get("name") or "").strip()
            if current_name.lower() == renamed_name.lower() and current_name.lower() != template_name.lower():
                raise FileExistsError(f"template already exists: {renamed_name}")
            if current_name.lower() == template_name.lower():
                target = template
        if target is None:
            raise FileNotFoundError(f"template not found: {template_name}")

        root = self._template_store_dir()
        relative = target.get("file")
        old_path: Path | None = None
        if isinstance(relative, str) and relative.strip():
            old_path = (root / relative).resolve()
            try:
                old_path.relative_to(root)
            except ValueError as exc:
                raise ValueError("template file escapes template store") from exc
        extension = Path(str(relative or "")).suffix or ".cpp"
        new_path = self._template_files_dir() / _safe_template_part(algorithm_name) / f"{_safe_template_part(renamed_name)}{extension}"
        self._ensure_inside_workspace(new_path)
        new_path.parent.mkdir(parents=True, exist_ok=True)
        if old_path and old_path.is_file() and old_path != new_path:
            if new_path.exists():
                raise FileExistsError(f"template file already exists: {renamed_name}")
            old_path.rename(new_path)
            self._remove_empty_template_dir(algorithm_name)
        elif not new_path.is_file() and isinstance(target.get("source"), str):
            new_path.write_text(str(target.get("source") or ""), encoding="utf-8", newline="\n")
        target["name"] = renamed_name
        target["file"] = str(new_path.relative_to(root)).replace("\\", "/")
        target["updatedAt"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        self._write_templates(algorithms)
        return {"templates": algorithms, "algorithm": algorithm_name, "template": target}

    def _delete_template_algorithm(self, algorithm: str) -> dict[str, Any]:
        algorithm_name = algorithm.strip()
        if not algorithm_name:
            raise ValueError("algorithm must be a non-empty string")
        algorithms = self._load_templates()
        item = self._find_template_algorithm(algorithms, algorithm_name)
        if item is None:
            raise FileNotFoundError(f"template algorithm not found: {algorithm_name}")
        for template in item.get("templates") if isinstance(item.get("templates"), list) else []:
            if isinstance(template, dict):
                self._delete_template_file(template.get("file"))
        algorithms = [
            candidate
            for candidate in algorithms
            if str(candidate.get("name") or "").strip().lower() != algorithm_name.lower()
        ]
        self._write_templates(algorithms)
        self._remove_empty_template_dir(algorithm_name)
        return {"templates": algorithms, "algorithm": algorithm_name}

    def _delete_template(self, algorithm: str, name: str) -> dict[str, Any]:
        algorithm_name = algorithm.strip()
        template_name = name.strip()
        if not algorithm_name:
            raise ValueError("algorithm must be a non-empty string")
        if not template_name:
            raise ValueError("template name must be a non-empty string")
        algorithms = self._load_templates()
        item = self._find_template_algorithm(algorithms, algorithm_name)
        if item is None:
            raise FileNotFoundError(f"template algorithm not found: {algorithm_name}")
        templates = item.get("templates")
        if not isinstance(templates, list):
            raise FileNotFoundError(f"template not found: {template_name}")
        match_index = next(
            (
                index
                for index, template in enumerate(templates)
                if isinstance(template, dict)
                and str(template.get("name") or "").strip().lower() == template_name.lower()
            ),
            None,
        )
        if match_index is None:
            raise FileNotFoundError(f"template not found: {template_name}")
        removed = templates.pop(match_index)
        if isinstance(removed, dict):
            self._delete_template_file(removed.get("file"))
        if not templates:
            algorithms = [
                candidate
                for candidate in algorithms
                if str(candidate.get("name") or "").strip().lower() != algorithm_name.lower()
            ]
        self._write_templates(algorithms)
        self._remove_empty_template_dir(algorithm_name)
        return {"templates": algorithms, "algorithm": algorithm_name, "template": template_name}

    def _delete_template_file(self, relative: Any) -> None:
        if not isinstance(relative, str) or not relative.strip():
            return
        root = self._template_store_dir()
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError("template file escapes template store") from exc
        if path.is_file():
            path.unlink()

    def _remove_empty_template_dir(self, algorithm: str) -> None:
        directory = self._template_files_dir() / _safe_template_part(algorithm)
        try:
            directory.relative_to(self._template_store_dir())
        except ValueError:
            return
        if directory.is_dir():
            try:
                directory.rmdir()
            except OSError:
                pass

    def _find_template_algorithm(self, algorithms: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
        lowered = name.strip().lower()
        for item in algorithms:
            if str(item.get("name") or "").strip().lower() == lowered:
                return item
        return None

    def _delete_problem_test(self, problem_dir: Path, test_ref: str) -> dict[str, Any]:
        problem_json = problem_dir / "problem.json"
        data = load_problem_json(problem_dir)
        tests = data.get("tests")
        if not isinstance(tests, list) or not tests:
            raise FileNotFoundError("test not found")

        index = self._test_index(tests, test_ref)
        removed = tests.pop(index)
        if not isinstance(removed, dict):
            removed = {}

        remaining_paths = self._referenced_test_paths(problem_dir, tests)
        deleted_files: list[str] = []
        delete_errors: list[str] = []
        for field in ("inputFile", "outputFile"):
            relative = removed.get(field)
            if not isinstance(relative, str):
                continue
            target = self._safe_problem_file(problem_dir, relative)
            if target in remaining_paths or not target.is_file():
                continue
            display_path = str(target.relative_to(problem_dir)).replace("\\", "/")
            try:
                target.unlink()
            except OSError as exc:
                delete_errors.append(f"{display_path}: {exc}")
                continue
            deleted_files.append(display_path)

        problem_json.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        payload = {
            "name": str(removed.get("name") or test_ref),
            "deletedFiles": deleted_files,
            "tests": len(tests),
        }
        if delete_errors:
            payload["deleteErrors"] = delete_errors
        return payload

    def _rename_problem_test(self, problem_dir: Path, test_ref: str, new_name: str) -> dict[str, Any]:
        problem_json = problem_dir / "problem.json"
        data = load_problem_json(problem_dir)
        tests = data.get("tests")
        if not isinstance(tests, list) or not tests:
            raise FileNotFoundError("test not found")

        safe_name = _safe_test_part(new_name)
        index = self._test_index(tests, test_ref)
        test = tests[index]
        if not isinstance(test, dict):
            raise FileNotFoundError("test not found")
        for position, item in enumerate(tests):
            if position == index or not isinstance(item, dict):
                continue
            names = {
                str(item.get("name") or ""),
                Path(str(item.get("inputFile") or "")).stem,
                Path(str(item.get("outputFile") or "")).stem,
            }
            if safe_name in names:
                raise FileExistsError(f"test already exists: {safe_name}")

        renamed_files: dict[str, str] = {}
        for field, default_suffix in (("inputFile", ".in"), ("outputFile", ".out")):
            relative = test.get(field)
            if not isinstance(relative, str) or not relative.strip():
                continue
            old_path = self._safe_problem_file(problem_dir, relative)
            suffix = old_path.suffix or default_suffix
            new_path = old_path.with_name(f"{safe_name}{suffix}")
            self._safe_problem_file(problem_dir, str(new_path.relative_to(problem_dir)))
            if old_path != new_path:
                if new_path.exists():
                    raise FileExistsError(f"test file already exists: {new_path.name}")
                if old_path.is_file():
                    old_path.rename(new_path)
            test[field] = str(new_path.relative_to(problem_dir)).replace("\\", "/")
            renamed_files[field] = test[field]

        test["name"] = safe_name
        problem_json.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return {
            "name": safe_name,
            "inputFile": renamed_files.get("inputFile", test.get("inputFile")),
            "outputFile": renamed_files.get("outputFile", test.get("outputFile")),
        }

    def _test_index(self, tests: list[Any], test_ref: str) -> int:
        try:
            index = int(test_ref) - 1
        except ValueError:
            index = -1
        if 0 <= index < len(tests):
            return index
        for position, item in enumerate(tests):
            if not isinstance(item, dict):
                continue
            names = [
                item.get("name"),
                Path(str(item.get("inputFile") or "")).stem,
                Path(str(item.get("outputFile") or "")).stem,
            ]
            if any(str(name) == test_ref for name in names if name):
                return position
        raise FileNotFoundError(f"test not found: {test_ref}")

    def _referenced_test_paths(self, problem_dir: Path, tests: list[Any]) -> set[Path]:
        paths: set[Path] = set()
        for item in tests:
            if not isinstance(item, dict):
                continue
            for field in ("inputFile", "outputFile"):
                relative = item.get(field)
                if isinstance(relative, str):
                    paths.add(self._safe_problem_file(problem_dir, relative))
        return paths

    def _safe_problem_file(self, problem_dir: Path, relative_path: str) -> Path:
        target = (problem_dir / relative_path).resolve()
        try:
            target.relative_to(problem_dir.resolve())
        except ValueError as exc:
            raise ValueError("test file path escapes problem folder") from exc
        return target


def _package_template() -> Path:
    return Path(__file__).parent / "templates" / "main.cpp"


def _safe_template_part(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in value.strip())
    cleaned = cleaned.strip("-._")
    return cleaned or "template"


def _safe_test_part(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in value.strip())
    cleaned = cleaned.strip("-._")
    return cleaned or "test"


def _optional_config_text(value: Any, *, existing: str | None = None) -> str | None:
    if value is None:
        return existing
    if not isinstance(value, str):
        raise ValueError("Codeforces API values must be strings")
    return value.strip() or existing


def _ui_language(value: Any) -> str:
    text = str(value or "en").strip().lower()
    if text in {"ko", "kr", "korean", "한국어"}:
        return "ko"
    if text in {"en", "english", ""}:
        return "en"
    raise ValueError("uiLanguage must be 'en' or 'ko'")
