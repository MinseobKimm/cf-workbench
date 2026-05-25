from __future__ import annotations

import difflib


def normalize_lines(value: str) -> list[str]:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    return [line.rstrip(" \t") for line in lines]


def outputs_match(expected: str, actual: str, *, tokens: bool = False) -> bool:
    if tokens:
        return expected.split() == actual.split()
    return normalize_lines(expected) == normalize_lines(actual)


def compact_diff(expected: str, actual: str, *, context: int = 2) -> str:
    diff = difflib.unified_diff(
        normalize_lines(expected),
        normalize_lines(actual),
        fromfile="expected",
        tofile="actual",
        lineterm="",
        n=context,
    )
    return "\n".join(diff)
