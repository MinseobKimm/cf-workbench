import subprocess
import sys

from cf_workbench.compiler import CompileResult, compile_solution
from cf_workbench.runner import (
    CaseResult,
    TestCase,
    run_executable_case,
    run_problem_tests,
    timeout_for_problem,
)


def test_timeout_for_problem_uses_minimum_three_seconds(tmp_path):
    (tmp_path / "problem.json").write_text('{"timeLimit": 400}', encoding="utf-8")
    assert timeout_for_problem(tmp_path) == 2.0


def test_run_executable_case_timeout(tmp_path):
    input_path = tmp_path / "1.in"
    answer_path = tmp_path / "1.ans"
    input_path.write_text("", encoding="utf-8")
    answer_path.write_text("", encoding="utf-8")
    case = TestCase(number=1, input_path=input_path, answer_path=answer_path)

    result = run_executable_case(
        [sys.executable, "-c", "import time; time.sleep(2)"],
        case,
        timeout_seconds=0.1,
        cwd=tmp_path,
    )

    assert result.status == "TLE"
    assert "Timed out after" in result.stderr


def test_run_executable_case_wrong_answer(tmp_path):
    input_path = tmp_path / "1.in"
    answer_path = tmp_path / "1.ans"
    input_path.write_text("", encoding="utf-8")
    answer_path.write_text("expected\n", encoding="utf-8")
    case = TestCase(number=1, input_path=input_path, answer_path=answer_path)

    result = run_executable_case(
        [sys.executable, "-c", "print('actual')"],
        case,
        timeout_seconds=1,
        cwd=tmp_path,
    )

    assert result.status == "WA"
    assert "expected" in result.diff
    assert "actual" in result.diff


def test_run_problem_tests_stops_after_first_failed_case(tmp_path, monkeypatch):
    cases = []
    for number in range(1, 4):
        input_path = tmp_path / f"{number}.in"
        answer_path = tmp_path / f"{number}.ans"
        input_path.write_text("", encoding="utf-8")
        answer_path.write_text("", encoding="utf-8")
        cases.append(TestCase(number=number, input_path=input_path, answer_path=answer_path))

    monkeypatch.setattr(
        "cf_workbench.runner.compile_solution",
        lambda *args, **kwargs: CompileResult(
            success=True,
            command=["g++"],
            executable=tmp_path / "main.exe",
            returncode=0,
            stdout="",
            stderr="",
        ),
    )
    monkeypatch.setattr("cf_workbench.runner.discover_tests", lambda problem_dir: cases)
    executed: list[int] = []

    def fake_run_case(command, case, **kwargs):
        executed.append(case.number)
        status = "WA" if case.number == 2 else "AC"
        return CaseResult(case=case, status=status, expected="", actual="")

    monkeypatch.setattr("cf_workbench.runner.run_executable_case", fake_run_case)

    result = run_problem_tests(tmp_path)

    assert executed == [1, 2]
    assert [case.status for case in result.cases] == ["AC", "WA"]


def test_compile_error_handling_with_mocked_subprocess(tmp_path, monkeypatch):
    source = tmp_path / "main.cpp"
    source.write_text("int main(", encoding="utf-8")

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=1, stdout="", stderr="compile error")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = compile_solution(tmp_path, source, compiler_path="g++")

    assert not result.success
    assert result.returncode == 1
    assert result.stderr == "compile error"


def test_compile_start_error_is_returned_as_compile_result(tmp_path, monkeypatch):
    source = tmp_path / "main.cpp"
    source.write_text("int main() {}", encoding="utf-8")

    def fake_run(*args, **kwargs):
        raise OSError("compiler missing")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = compile_solution(tmp_path, source, compiler_path="missing-g++")

    assert not result.success
    assert result.returncode == -1
    assert "Failed to start compiler" in result.stderr
    assert "compiler missing" in result.stderr
