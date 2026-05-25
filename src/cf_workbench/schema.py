from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping
from urllib.parse import unquote, urlparse


class SchemaError(ValueError):
    """Raised when an incoming capture payload cannot be normalized."""


@dataclass(frozen=True)
class ParsedCodeforcesUrl:
    source: str
    contest_id: int
    index: str
    problem_key: str
    group_code: str | None = None


@dataclass(frozen=True)
class CapturedSample:
    name: str
    input: str
    output: str


@dataclass(frozen=True)
class NormalizedProblem:
    schema_version: int
    judge: str
    problem_key: str
    contest_id: int | None
    index: str | None
    group_code: str | None
    name: str
    group: str | None
    url: str
    interactive: bool
    time_limit_ms: int
    memory_limit_mb: int
    test_type: str
    input: dict[str, Any]
    output: dict[str, Any]
    samples: list[CapturedSample]
    source: dict[str, Any]
    extra: dict[str, Any]

    def to_problem_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schemaVersion": self.schema_version,
            "judge": self.judge,
            "problemKey": self.problem_key,
            "contestId": self.contest_id,
            "index": self.index,
            "name": self.name,
            "group": self.group,
            "url": self.url,
            "interactive": self.interactive,
            "timeLimitMs": self.time_limit_ms,
            "memoryLimitMb": self.memory_limit_mb,
            "testType": self.test_type,
            "input": self.input,
            "output": self.output,
            "tests": [
                {
                    "name": sample.name,
                    "inputFile": f"tests/{sample.name}.in",
                    "outputFile": f"tests/{sample.name}.out",
                }
                for sample in self.samples
            ],
            "source": self.source,
        }
        if self.group_code:
            data["groupCode"] = self.group_code
        if self.extra:
            data["extra"] = self.extra
        return data


def normalize_companion_payload(
    payload: Mapping[str, Any],
    *,
    captured_at: datetime | None = None,
) -> NormalizedProblem:
    if not isinstance(payload, Mapping):
        raise SchemaError("payload must be a JSON object")

    name = _required_string(payload, "name")
    url = _required_string(payload, "url")
    tests_value = payload.get("tests")
    if not isinstance(tests_value, list) or not tests_value:
        raise SchemaError("payload.tests must be a non-empty list")

    samples: list[CapturedSample] = []
    for index, test_value in enumerate(tests_value, start=1):
        if not isinstance(test_value, Mapping):
            raise SchemaError(f"tests[{index - 1}] must be an object")
        sample_input = test_value.get("input")
        sample_output = test_value.get("output")
        if not isinstance(sample_input, str) or not isinstance(sample_output, str):
            raise SchemaError(f"tests[{index - 1}] input and output must be strings")
        samples.append(
            CapturedSample(
                name=f"sample_{index}",
                input=_ensure_final_newline(sample_input),
                output=_ensure_final_newline(sample_output),
            )
        )

    parsed = parse_codeforces_url(url)
    if parsed:
        problem_key = parsed.problem_key
        contest_id: int | None = parsed.contest_id
        problem_index: str | None = parsed.index
        group_code = parsed.group_code
    else:
        problem_key = f"unknown-{safe_slug(name)}-{_short_hash(url)}"
        contest_id = None
        problem_index = None
        group_code = None

    captured = captured_at or datetime.now(timezone.utc)
    batch = payload.get("batch")
    batch_id = batch.get("id") if isinstance(batch, Mapping) else None
    batch_size = batch.get("size") if isinstance(batch, Mapping) else None

    known_fields = {
        "name",
        "group",
        "url",
        "interactive",
        "memoryLimit",
        "timeLimit",
        "tests",
        "testType",
        "input",
        "output",
        "batch",
    }

    return NormalizedProblem(
        schema_version=1,
        judge="codeforces",
        problem_key=problem_key,
        contest_id=contest_id,
        index=problem_index,
        group_code=group_code,
        name=name,
        group=_optional_string(payload.get("group")),
        url=url,
        interactive=bool(payload.get("interactive", False)),
        time_limit_ms=_optional_int(payload.get("timeLimit"), default=1000),
        memory_limit_mb=_optional_int(payload.get("memoryLimit"), default=256),
        test_type=_optional_string(payload.get("testType")) or "single",
        input=dict(payload.get("input")) if isinstance(payload.get("input"), Mapping) else {"type": "stdin"},
        output=dict(payload.get("output")) if isinstance(payload.get("output"), Mapping) else {"type": "stdout"},
        samples=samples,
        source={
            "kind": "competitive-companion",
            "capturedAt": captured.astimezone(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "batchId": batch_id,
            "batchSize": batch_size,
        },
        extra={key: value for key, value in payload.items() if key not in known_fields},
    )


def parse_codeforces_url(url: str) -> ParsedCodeforcesUrl | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host and not (host == "codeforces.com" or host.endswith(".codeforces.com")):
        return None

    parts = [unquote(part) for part in parsed.path.strip("/").split("/") if part]
    if len(parts) >= 4 and parts[0] == "contest" and parts[2] == "problem":
        contest_id = _parse_contest_id(parts[1])
        if contest_id is None:
            return None
        return ParsedCodeforcesUrl(
            source="contest",
            contest_id=contest_id,
            index=parts[3],
            problem_key=f"{contest_id}{parts[3]}",
        )
    if len(parts) >= 4 and parts[0] == "problemset" and parts[1] == "problem":
        contest_id = _parse_contest_id(parts[2])
        if contest_id is None:
            return None
        return ParsedCodeforcesUrl(
            source="problemset",
            contest_id=contest_id,
            index=parts[3],
            problem_key=f"{contest_id}{parts[3]}",
        )
    if len(parts) >= 4 and parts[0] == "gym" and parts[2] == "problem":
        contest_id = _parse_contest_id(parts[1])
        if contest_id is None:
            return None
        return ParsedCodeforcesUrl(
            source="gym",
            contest_id=contest_id,
            index=parts[3],
            problem_key=f"gym-{contest_id}{parts[3]}",
        )
    if (
        len(parts) >= 6
        and parts[0] == "group"
        and parts[2] == "contest"
        and parts[4] == "problem"
    ):
        contest_id = _parse_contest_id(parts[3])
        if contest_id is None:
            return None
        return ParsedCodeforcesUrl(
            source="group",
            contest_id=contest_id,
            index=parts[5],
            problem_key=f"{contest_id}{parts[5]}",
            group_code=parts[1],
        )
    return None


def safe_slug(value: str, fallback: str = "problem") -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", value.strip().lower())
    slug = slug.strip("-_")
    return slug or fallback


def _required_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f"payload.{key} must be a non-empty string")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_contest_id(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def _ensure_final_newline(value: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    return normalized if normalized.endswith("\n") else f"{normalized}\n"


def _short_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
