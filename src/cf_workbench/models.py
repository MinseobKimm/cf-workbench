from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Mapping


class PayloadValidationError(ValueError):
    """Raised when a Competitive Companion payload is incomplete or malformed."""


@dataclass(frozen=True)
class ProblemTest:
    input: str
    output: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], index: int) -> "ProblemTest":
        if "input" not in value or "output" not in value:
            raise PayloadValidationError(f"tests[{index}] must contain input and output")
        test_input = value["input"]
        test_output = value["output"]
        if not isinstance(test_input, str) or not isinstance(test_output, str):
            raise PayloadValidationError(f"tests[{index}].input and output must be strings")
        return cls(input=test_input, output=test_output)

    def to_json(self) -> dict[str, str]:
        return {"input": self.input, "output": self.output}


@dataclass
class Problem:
    name: str
    url: str
    tests: list[ProblemTest]
    group: str | None = None
    interactive: bool = False
    memory_limit_mb: int | None = None
    time_limit_ms: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_companion_payload(cls, payload: Mapping[str, Any]) -> "Problem":
        if not isinstance(payload, Mapping):
            raise PayloadValidationError("payload must be a JSON object")
        for field_name in ("name", "url", "tests"):
            if field_name not in payload:
                raise PayloadValidationError(f"payload missing required field: {field_name}")
        name = payload["name"]
        url = payload["url"]
        tests_value = payload["tests"]
        if not isinstance(name, str) or not name.strip():
            raise PayloadValidationError("payload.name must be a non-empty string")
        if not isinstance(url, str) or not url.strip():
            raise PayloadValidationError("payload.url must be a non-empty string")
        if not isinstance(tests_value, list) or not tests_value:
            raise PayloadValidationError("payload.tests must be a non-empty list")

        tests: list[ProblemTest] = []
        for index, test_value in enumerate(tests_value):
            if not isinstance(test_value, Mapping):
                raise PayloadValidationError(f"tests[{index}] must be an object")
            tests.append(ProblemTest.from_mapping(test_value, index))

        group = payload.get("group")
        if group is not None and not isinstance(group, str):
            group = str(group)

        return cls(
            name=name,
            url=url,
            tests=tests,
            group=group,
            interactive=bool(payload.get("interactive", False)),
            memory_limit_mb=_optional_int(payload.get("memoryLimit")),
            time_limit_ms=_optional_int(payload.get("timeLimit")),
            raw=deepcopy(dict(payload)),
        )

    def to_json_data(self) -> dict[str, Any]:
        data = deepcopy(self.raw)
        data.update(
            {
                "name": self.name,
                "url": self.url,
                "interactive": self.interactive,
                "tests": [test.to_json() for test in self.tests],
            }
        )
        if self.group is not None:
            data["group"] = self.group
        if self.memory_limit_mb is not None:
            data["memoryLimit"] = self.memory_limit_mb
        if self.time_limit_ms is not None:
            data["timeLimit"] = self.time_limit_ms
        return data


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
