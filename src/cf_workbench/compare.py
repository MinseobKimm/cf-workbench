from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Literal


CompareMode = Literal["exact", "trim", "tokens"]


@dataclass(frozen=True)
class CompareResult:
    ok: bool
    mode: CompareMode
    diff: str = ""


def compare_outputs(expected: str, actual: str, *, mode: CompareMode = "tokens") -> CompareResult:
    if mode == "tokens":
        ok = expected.split() == actual.split()
        return CompareResult(ok=ok, mode=mode, diff="" if ok else _diff(_trim_lines(expected), _trim_lines(actual)))
    if mode == "trim":
        expected_lines = _trim_lines(expected)
        actual_lines = _trim_lines(actual)
        ok = expected_lines == actual_lines
        return CompareResult(ok=ok, mode=mode, diff="" if ok else _diff(expected_lines, actual_lines))
    if mode == "exact":
        expected_normalized = _normalize_newlines(expected)
        actual_normalized = _normalize_newlines(actual)
        ok = expected_normalized == actual_normalized
        return CompareResult(
            ok=ok,
            mode=mode,
            diff="" if ok else _diff(expected_normalized.split("\n"), actual_normalized.split("\n")),
        )
    raise ValueError(f"unknown compare mode: {mode}")


def _normalize_newlines(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _trim_lines(value: str) -> list[str]:
    lines = _normalize_newlines(value).split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    return [line.rstrip() for line in lines]


def _diff(expected_lines: list[str], actual_lines: list[str]) -> str:
    return "\n".join(
        difflib.unified_diff(
            expected_lines,
            actual_lines,
            fromfile="expected",
            tofile="actual",
            lineterm="",
            n=2,
        )
    )
