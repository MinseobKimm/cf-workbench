from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .compiler import CompileResult, compile_solution
from .compare import CompareMode, compare_outputs


@dataclass(frozen=True)
class TestCase:
    __test__ = False

    number: int
    input_path: Path
    answer_path: Path
    name: str | None = None


@dataclass
class CaseResult:
    case: TestCase
    status: str
    expected: str
    actual: str
    stderr: str = ""
    returncode: int | None = None
    diff: str = ""
    elapsed_ms: int | None = None


@dataclass
class ProblemRunResult:
    compile_result: CompileResult
    cases: list[CaseResult]
    skipped_reason: str | None = None

    @property
    def success(self) -> bool:
        return (
            self.skipped_reason is None
            and self.compile_result.success
            and all(case.status == "AC" for case in self.cases)
        )


def discover_tests(problem_dir: Path) -> list[TestCase]:
    problem_json = problem_dir / "problem.json"
    if problem_json.is_file():
        with problem_json.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        normalized_tests = data.get("tests")
        if isinstance(normalized_tests, list) and normalized_tests:
            cases: list[TestCase] = []
            for index, test in enumerate(normalized_tests, start=1):
                if not isinstance(test, dict):
                    continue
                input_file = test.get("inputFile")
                output_file = test.get("outputFile")
                if not isinstance(input_file, str) or not isinstance(output_file, str):
                    continue
                input_path = (problem_dir / input_file).resolve()
                answer_path = (problem_dir / output_file).resolve()
                if input_path.is_file() and answer_path.is_file():
                    cases.append(
                        TestCase(
                            number=index,
                            input_path=input_path,
                            answer_path=answer_path,
                            name=str(test.get("name") or f"sample_{index}"),
                        )
                    )
            if cases:
                return cases

    tests_dir = problem_dir / "tests"
    cases: list[TestCase] = []
    for input_path in tests_dir.glob("*.in"):
        number = _test_number(input_path)
        if number is None:
            continue
        answer_path = tests_dir / f"{input_path.stem}.out"
        if not answer_path.is_file():
            answer_path = tests_dir / f"{number}.ans"
        if answer_path.is_file():
            cases.append(
                TestCase(
                    number=number,
                    input_path=input_path,
                    answer_path=answer_path,
                    name=input_path.stem,
                )
            )
    return sorted(cases, key=lambda case: case.number)


def run_problem_tests(
    problem_dir: Path,
    *,
    source_name: str = "main.cpp",
    configured_compiler: str | None = None,
    tokens: bool | None = None,
    compare_mode: CompareMode = "tokens",
    timeout_seconds: float | None = None,
    force_interactive: bool = False,
) -> ProblemRunResult:
    problem_dir = problem_dir.resolve()
    problem_data = _load_problem_data(problem_dir)
    if tokens is not None:
        compare_mode = "tokens" if tokens else "trim"
    if bool(problem_data.get("interactive", False)) and not force_interactive:
        result = ProblemRunResult(
            compile_result=_dummy_compile_result(problem_dir),
            cases=[],
            skipped_reason="interactive problem; use --force for manual experiments",
        )
        _write_latest_log(problem_dir, result)
        return result

    compile_result = compile_solution(
        problem_dir,
        problem_dir / source_name,
        configured_compiler=configured_compiler,
    )
    if not compile_result.success:
        result = ProblemRunResult(compile_result=compile_result, cases=[])
        _write_latest_log(problem_dir, result)
        return result

    timeout = timeout_seconds if timeout_seconds is not None else timeout_for_problem(problem_dir)
    cases: list[CaseResult] = []
    for case in discover_tests(problem_dir):
        case_result = run_executable_case(
            [str(compile_result.executable)],
            case,
            timeout_seconds=timeout,
            compare_mode=compare_mode,
            cwd=problem_dir,
        )
        cases.append(case_result)
        if case_result.status != "AC":
            break
    result = ProblemRunResult(compile_result=compile_result, cases=cases)
    _write_latest_log(problem_dir, result)
    return result


def run_executable_case(
    command: Sequence[str],
    case: TestCase,
    *,
    timeout_seconds: float,
    tokens: bool | None = None,
    compare_mode: CompareMode = "tokens",
    cwd: Path | None = None,
) -> CaseResult:
    if tokens is not None:
        compare_mode = "tokens" if tokens else "trim"
    expected = case.answer_path.read_text(encoding="utf-8")
    test_input = case.input_path.read_text(encoding="utf-8")
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            list(command),
            input=test_input,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return CaseResult(
            case=case,
            status="TLE",
            expected=expected,
            actual=_process_text(exc.stdout),
            stderr=(f"Timed out after {timeout_seconds:g} seconds.\n{_process_text(exc.stderr)}").rstrip(),
            elapsed_ms=elapsed_ms,
        )

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    if completed.returncode != 0:
        return CaseResult(
            case=case,
            status="RE",
            expected=expected,
            actual=_process_text(completed.stdout),
            stderr=_process_text(completed.stderr),
            returncode=completed.returncode,
            elapsed_ms=elapsed_ms,
        )
    actual_output = _process_text(completed.stdout)
    stderr_output = _process_text(completed.stderr)
    compare_result = compare_outputs(expected, actual_output, mode=compare_mode)
    if compare_result.ok:
        return CaseResult(
            case=case,
            status="AC",
            expected=expected,
            actual=actual_output,
            stderr=stderr_output,
            returncode=completed.returncode,
            elapsed_ms=elapsed_ms,
        )
    return CaseResult(
        case=case,
        status="WA",
        expected=expected,
        actual=actual_output,
        stderr=stderr_output,
        returncode=completed.returncode,
        diff=compare_result.diff,
        elapsed_ms=elapsed_ms,
    )


def _process_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def timeout_for_problem(problem_dir: Path) -> float:
    time_limit_ms = 1000
    problem_json = problem_dir / "problem.json"
    if problem_json.is_file():
        with problem_json.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        try:
            time_limit_ms = int(data.get("timeLimitMs") or data.get("timeLimit") or 1000)
        except (TypeError, ValueError):
            time_limit_ms = 1000
    return max(2.0, time_limit_ms / 1000.0 + 1.0)


def add_custom_test(problem_dir: Path, input_text: str, output_text: str) -> TestCase:
    tests_dir = problem_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    existing_numbers = [case.number for case in discover_tests(problem_dir)]
    next_number = (max(existing_numbers) + 1) if existing_numbers else 1
    input_path = tests_dir / f"{next_number}.in"
    answer_path = tests_dir / f"{next_number}.ans"
    input_path.write_text(input_text, encoding="utf-8", newline="\n")
    answer_path.write_text(output_text, encoding="utf-8", newline="\n")
    return TestCase(number=next_number, input_path=input_path, answer_path=answer_path)


def _test_number(path: Path) -> int | None:
    if path.stem.startswith("sample_"):
        try:
            return int(path.stem.removeprefix("sample_"))
        except ValueError:
            return None
    try:
        return int(path.stem)
    except ValueError:
        return None


def _load_problem_data(problem_dir: Path) -> dict:
    problem_json = problem_dir / "problem.json"
    if not problem_json.is_file():
        return {}
    with problem_json.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _dummy_compile_result(problem_dir: Path) -> CompileResult:
    executable = problem_dir / ".cfw" / "build" / "main.exe"
    return CompileResult(
        success=True,
        command=[],
        executable=executable,
        returncode=0,
        stdout="",
        stderr="",
    )


def _write_latest_log(problem_dir: Path, result: ProblemRunResult) -> None:
    runs_dir = problem_dir / ".cfw" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if result.skipped_reason:
        lines.append(f"SKIP: {result.skipped_reason}")
    else:
        lines.append(f"Compile: {'OK' if result.compile_result.success else 'CE'}")
        if result.compile_result.command:
            lines.append(f"Command: {' '.join(result.compile_result.command)}")
        if result.compile_result.stdout:
            lines.append("Compiler stdout:")
            lines.append(result.compile_result.stdout.rstrip())
        if result.compile_result.stderr:
            lines.append("Compiler stderr:")
            lines.append(result.compile_result.stderr.rstrip())
        for case in result.cases:
            name = case.case.name or f"case_{case.case.number}"
            elapsed = "" if case.elapsed_ms is None else f" {case.elapsed_ms} ms"
            lines.append(f"{name}: {case.status}{elapsed}")
            if case.status != "AC":
                if case.stderr:
                    lines.append("stderr:")
                    lines.append(case.stderr.rstrip())
                lines.append("Expected:")
                lines.append(case.expected.rstrip())
                lines.append("Actual:")
                lines.append(case.actual.rstrip())
                if case.diff:
                    lines.append("Diff:")
                    lines.append(case.diff)
    (runs_dir / "latest.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
