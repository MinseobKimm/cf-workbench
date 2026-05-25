from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from .schema import parse_codeforces_url, safe_slug
from .storage import find_problem_path, load_problem_json, problem_path, save_capture


MAX_STATEMENT_PAYLOAD_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class StoredStatementCapture:
    problem_key: str
    path: Path
    created_problem: bool
    html_file: Path
    text_file: Path


def save_statement_capture(
    payload: Mapping[str, Any],
    *,
    workspace: Path,
    template_path: Path | None = None,
    judge_subdir: str = "codeforces",
) -> StoredStatementCapture:
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be a JSON object")

    url = _required_string(payload, "url")
    raw_html = _required_string(payload, "html")
    statement_text = _optional_string(payload.get("text")) or ""
    problem_key = _problem_key_from_payload(payload, url)
    problem_dir = find_problem_path(workspace, problem_key, judge_subdir=judge_subdir)
    if problem_dir is None:
        problem_dir = problem_path(workspace, problem_key, judge_subdir=judge_subdir)

    created_problem = False
    if not (problem_dir / "problem.json").is_file():
        stored = save_capture(
            _companion_payload_from_dom_capture(payload, url, problem_key),
            workspace=workspace,
            template_path=template_path,
            judge_subdir=judge_subdir,
        )
        problem_dir = stored.path
        created_problem = True

    _ensure_inside(workspace, problem_dir)
    data = load_problem_json(problem_dir)
    _write_samples_if_missing(problem_dir, data, payload)

    html_file = problem_dir / "statement.html"
    text_file = problem_dir / "statement.txt"
    html_file.write_text(sanitize_statement_html(raw_html), encoding="utf-8", newline="\n")
    text_file.write_text(statement_text, encoding="utf-8", newline="\n")

    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    data["statementCapture"] = {
        "kind": "browser-dom",
        "capturedAt": captured_at,
        "url": url,
        "title": _optional_string(payload.get("title")),
        "htmlFile": html_file.name,
        "textFile": text_file.name,
    }
    problem_name = _problem_name_from_payload(payload, problem_key)
    if problem_name and not str(data.get("name") or "").strip():
        data["name"] = problem_name
    if _optional_int(payload.get("timeLimitMs")):
        data["timeLimitMs"] = _optional_int(payload.get("timeLimitMs"))
    if _optional_int(payload.get("memoryLimitMb")):
        data["memoryLimitMb"] = _optional_int(payload.get("memoryLimitMb"))
    (problem_dir / "problem.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return StoredStatementCapture(
        problem_key=str(data.get("problemKey") or problem_key),
        path=problem_dir,
        created_problem=created_problem,
        html_file=html_file,
        text_file=text_file,
    )


def sanitize_statement_html(value: str) -> str:
    parser = _StatementHTMLSanitizer()
    parser.feed(value)
    parser.close()
    return parser.output()


def _problem_key_from_payload(payload: Mapping[str, Any], url: str) -> str:
    explicit = _optional_string(payload.get("problemKey"))
    if explicit:
        return explicit
    parsed = parse_codeforces_url(url)
    if parsed:
        return parsed.problem_key
    return f"unknown-{safe_slug(_problem_name_from_payload(payload, 'problem'))}"


def _companion_payload_from_dom_capture(
    payload: Mapping[str, Any],
    url: str,
    problem_key: str,
) -> dict[str, Any]:
    samples = _samples_from_payload(payload)
    if not samples:
        raise ValueError(
            f"problem not found: {problem_key}; import it first or capture at least one sample test"
        )
    data: dict[str, Any] = {
        "name": _problem_name_from_payload(payload, problem_key),
        "url": url,
        "tests": samples,
    }
    group = _optional_string(payload.get("group"))
    if group:
        data["group"] = group
    time_limit = _optional_int(payload.get("timeLimitMs"))
    if time_limit:
        data["timeLimit"] = time_limit
    memory_limit = _optional_int(payload.get("memoryLimitMb"))
    if memory_limit:
        data["memoryLimit"] = memory_limit
    return data


def _write_samples_if_missing(problem_dir: Path, data: dict[str, Any], payload: Mapping[str, Any]) -> None:
    if data.get("tests"):
        return
    samples = _samples_from_payload(payload)
    if not samples:
        return
    tests_dir = problem_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    data["tests"] = []
    for index, sample in enumerate(samples, start=1):
        name = f"sample_{index}"
        input_path = tests_dir / f"{name}.in"
        output_path = tests_dir / f"{name}.out"
        input_path.write_text(_ensure_final_newline(sample["input"]), encoding="utf-8", newline="\n")
        output_path.write_text(_ensure_final_newline(sample["output"]), encoding="utf-8", newline="\n")
        data["tests"].append(
            {
                "name": name,
                "inputFile": f"tests/{name}.in",
                "outputFile": f"tests/{name}.out",
            }
        )


def _samples_from_payload(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    raw_html = payload.get("html")
    samples = _samples_from_codeforces_html(raw_html) if isinstance(raw_html, str) else []
    if not samples:
        samples = _samples_from_payload_tests(payload.get("tests"))
    return [
        {
            "input": _ensure_final_newline(sample["input"]),
            "output": _ensure_final_newline(sample["output"]),
        }
        for sample in samples
    ]


def _samples_from_payload_tests(raw_tests: Any) -> list[dict[str, str]]:
    if not isinstance(raw_tests, list):
        return []
    samples: list[dict[str, str]] = []
    for item in raw_tests:
        if not isinstance(item, Mapping):
            continue
        sample_input = item.get("input")
        sample_output = item.get("output")
        if isinstance(sample_input, str) and isinstance(sample_output, str):
            samples.append(
                {
                    "input": sample_input,
                    "output": sample_output,
                }
            )
    return samples


def _samples_from_codeforces_html(raw_html: str) -> list[dict[str, str]]:
    parser = _CodeforcesSampleHTMLParser()
    parser.feed(raw_html)
    parser.close()
    return parser.samples()


class _CodeforcesSampleHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._sample_depth = 0
        self._sample_stack: list[bool] = []
        self._kind_stack: list[str | None] = []
        self._pre: dict[str, Any] | None = None
        self._inputs: list[str] = []
        self._outputs: list[str] = []

    def samples(self) -> list[dict[str, str]]:
        samples: list[dict[str, str]] = []
        count = max(len(self._inputs), len(self._outputs))
        for index in range(count):
            sample_input = self._inputs[index] if index < len(self._inputs) else ""
            sample_output = self._outputs[index] if index < len(self._outputs) else ""
            if sample_input or sample_output:
                samples.append({"input": sample_input, "output": sample_output})
        return samples

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        classes = _class_set(attrs)
        entering_sample = "sample-test" in classes
        if entering_sample:
            self._sample_depth += 1

        previous_kind = self._kind_stack[-1] if self._kind_stack else None
        kind = previous_kind
        if self._sample_depth:
            if "input" in classes:
                kind = "input"
            elif "output" in classes:
                kind = "output"

        self._sample_stack.append(entering_sample)
        self._kind_stack.append(kind)

        if self._pre is not None:
            if tag == "br":
                self._append_pre_break()
            elif tag == "div":
                self._start_pre_line()
            return

        if tag == "pre" and self._sample_depth and kind in {"input", "output"}:
            self._pre = {
                "kind": kind,
                "plain": [],
                "lines": [],
                "line": [],
                "lineDepth": 0,
                "hasLineElements": False,
            }

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._pre is not None and tag.lower() == "br":
            self._append_pre_break()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._pre is not None:
            if tag == "pre":
                self._finish_pre()
            elif tag == "div":
                self._end_pre_line()

        if self._kind_stack:
            self._kind_stack.pop()
        if self._sample_stack:
            if self._sample_stack.pop():
                self._sample_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._pre is None:
            return
        if self._pre["hasLineElements"] and self._pre["lineDepth"] == 0:
            if data.strip():
                self._pre["plain"].append(data)
            return
        if self._pre["lineDepth"] > 0:
            self._pre["line"].append(data)
        else:
            self._pre["plain"].append(data)

    def _start_pre_line(self) -> None:
        if self._pre is None:
            return
        self._pre["hasLineElements"] = True
        self._pre["lineDepth"] += 1

    def _end_pre_line(self) -> None:
        if self._pre is None or self._pre["lineDepth"] <= 0:
            return
        self._pre["lineDepth"] -= 1
        if self._pre["lineDepth"] == 0:
            self._flush_pre_line()

    def _append_pre_break(self) -> None:
        if self._pre is None:
            return
        target = self._pre["line"] if self._pre["lineDepth"] > 0 else self._pre["plain"]
        target.append("\n")

    def _flush_pre_line(self) -> None:
        if self._pre is None:
            return
        line = _normalize_sample_text("".join(self._pre["line"]))
        self._pre["lines"].append(line)
        self._pre["line"] = []

    def _finish_pre(self) -> None:
        if self._pre is None:
            return
        if self._pre["line"]:
            self._flush_pre_line()
        if self._pre["hasLineElements"]:
            text = "\n".join(self._pre["lines"])
            plain = _normalize_sample_text("".join(self._pre["plain"]))
            if plain:
                text = f"{plain}\n{text}" if text else plain
        else:
            text = _normalize_sample_text("".join(self._pre["plain"]))

        if self._pre["kind"] == "input":
            self._inputs.append(text)
        else:
            self._outputs.append(text)
        self._pre = None


def _class_set(attrs: list[tuple[str, str | None]]) -> set[str]:
    for name, value in attrs:
        if name.lower() == "class" and value:
            return set(value.split())
    return set()


def _normalize_sample_text(value: str) -> str:
    return value.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n").strip("\n")


def _problem_name_from_payload(payload: Mapping[str, Any], fallback: str) -> str:
    for key in ("problemName", "name", "title"):
        value = _optional_string(payload.get(key))
        if value:
            return value
    return fallback


def _required_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _ensure_final_newline(value: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    return normalized if normalized.endswith("\n") else f"{normalized}\n"


def _ensure_inside(root: Path, target: Path) -> None:
    root_resolved = root.resolve()
    target_resolved = target.resolve()
    try:
        target_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"refusing to write outside workspace: {target_resolved}") from exc


class _StatementHTMLSanitizer(HTMLParser):
    _blocked_tags = {
        "script",
        "iframe",
        "object",
        "embed",
        "link",
        "meta",
        "base",
        "form",
        "input",
        "button",
        "textarea",
        "select",
        "option",
    }
    _void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def output(self) -> str:
        return "".join(self._parts).strip() + "\n"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self._skip_depth:
            if tag in self._blocked_tags:
                self._skip_depth += 1
            return
        if tag in self._blocked_tags:
            self._skip_depth = 1
            return
        if not _safe_tag_name(tag):
            return
        self._parts.append(f"<{tag}{self._attrs(attrs)}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self._skip_depth or tag in self._blocked_tags or not _safe_tag_name(tag):
            return
        self._parts.append(f"<{tag}{self._attrs(attrs)}>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._skip_depth:
            if tag in self._blocked_tags:
                self._skip_depth -= 1
            return
        if tag in self._blocked_tags or tag in self._void_tags or not _safe_tag_name(tag):
            return
        self._parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._parts.append(html.escape(data, quote=False))

    def handle_entityref(self, name: str) -> None:
        if not self._skip_depth:
            self._parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self._skip_depth:
            self._parts.append(f"&#{name};")

    def _attrs(self, attrs: list[tuple[str, str | None]]) -> str:
        rendered: list[str] = []
        for name, value in attrs:
            name = name.lower()
            if value is None or not _safe_attr_name(name):
                continue
            if name in {"href", "src"} and not _safe_url(value):
                continue
            if name == "style":
                value = _safe_style(value)
                if not value:
                    continue
            rendered.append(f' {name}="{html.escape(value, quote=True)}"')
        return "".join(rendered)


def _safe_tag_name(value: str) -> bool:
    return bool(re.fullmatch(r"[a-z][a-z0-9:-]*", value))


def _safe_attr_name(value: str) -> bool:
    if value.startswith("on") or value in {"srcdoc"}:
        return False
    return bool(
        value in {"class", "id", "title", "alt", "width", "height", "style", "href", "src"}
        or value.startswith("aria-")
        or value.startswith("data-")
    )


def _safe_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    if parsed.scheme in {"", "http", "https"}:
        return True
    return parsed.scheme == "data" and value.strip().lower().startswith("data:image/")


def _safe_style(value: str) -> str | None:
    lowered = value.lower()
    if "javascript:" in lowered or "expression" in lowered or "url(" in lowered:
        return None
    return value
