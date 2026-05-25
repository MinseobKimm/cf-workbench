from __future__ import annotations

import shutil
import subprocess
import webbrowser
from dataclasses import dataclass
import json
from pathlib import Path

from .models import Problem
from .paths import parse_codeforces_problem_url
from .runner import run_problem_tests
from .submit_prefill import build_submit_prefill_payload, open_submit_page_with_prefill


@dataclass(frozen=True)
class SubmitPlan:
    executable: str | None
    command: list[str] | None
    problem_name: str
    problem_url: str
    manual_submit_url: str
    solution_path: Path
    language: str


def find_cf_tool() -> str | None:
    return shutil.which("cf-tool") or shutil.which("cf")


def build_cf_tool_command(executable: str, problem_url: str, solution_path: Path) -> list[str]:
    parsed = parse_codeforces_problem_url(problem_url)
    command = [executable, "submit", "-f", str(solution_path)]
    if parsed is not None:
        command.append(parsed.cf_tool_label)
    return command


def build_manual_submit_url(problem_url: str) -> str:
    parsed = parse_codeforces_problem_url(problem_url)
    if parsed is None:
        return problem_url
    if parsed.source == "group" and parsed.group_code:
        return f"https://codeforces.com/group/{parsed.group_code}/contest/{parsed.contest_id}/submit"
    if parsed.source == "gym":
        return f"https://codeforces.com/gym/{parsed.contest_id}/submit"
    if parsed.source == "problemset":
        return "https://codeforces.com/problemset/submit"
    return f"https://codeforces.com/contest/{parsed.contest_id}/submit"


def build_submit_url_from_problem_json(problem_data: dict) -> str:
    problem_url = str(problem_data.get("url", ""))
    if parse_codeforces_problem_url(problem_url) is not None:
        return build_manual_submit_url(problem_url)

    group_code = problem_data.get("groupCode")
    contest_id = problem_data.get("contestId")
    problem_key = str(problem_data.get("problemKey", ""))
    if group_code and contest_id:
        return f"https://codeforces.com/group/{group_code}/contest/{contest_id}/submit"
    if problem_key.startswith("gym-") and contest_id:
        return f"https://codeforces.com/gym/{contest_id}/submit"
    if contest_id:
        return f"https://codeforces.com/contest/{contest_id}/submit"
    return build_manual_submit_url(str(problem_data.get("url", "")))


def build_submit_plan(
    problem: Problem,
    problem_dir: Path,
    *,
    source_name: str = "main.cpp",
    language: str = "cpp17",
    cf_tool_executable: str | None = None,
) -> SubmitPlan:
    solution_path = (problem_dir / source_name).resolve()
    executable = cf_tool_executable if cf_tool_executable is not None else find_cf_tool()
    command = build_cf_tool_command(executable, problem.url, solution_path) if executable else None
    return SubmitPlan(
        executable=executable,
        command=command,
        problem_name=problem.name,
        problem_url=problem.url,
        manual_submit_url=build_manual_submit_url(problem.url),
        solution_path=solution_path,
        language=language,
    )


def submit_problem(
    problem: Problem,
    problem_dir: Path,
    *,
    source_name: str,
    language: str,
    configured_compiler: str | None,
    tokens: bool,
    force_after_failed_tests: bool = False,
) -> int:
    run_result = run_problem_tests(
        problem_dir,
        source_name=source_name,
        configured_compiler=configured_compiler,
        tokens=tokens,
    )
    if not run_result.success and not force_after_failed_tests:
        print("Local tests did not pass. Use --force-after-failed-tests to continue anyway.")
        return 1

    plan = build_submit_plan(problem, problem_dir, source_name=source_name, language=language)
    print("Submit target")
    print(f"  Problem: {plan.problem_name}")
    print(f"  URL: {plan.problem_url}")
    print(f"  File: {plan.solution_path}")
    print(f"  Language: {plan.language}")
    if plan.command:
        print(f"  Command: {' '.join(plan.command)}")
    else:
        print("  Command: cf-tool not found; browser manual submit fallback")
        print(f"  Submit page: {plan.manual_submit_url}")

    confirmation = input("Type SUBMIT to continue: ")
    if confirmation != "SUBMIT":
        print("Submission cancelled.")
        return 1

    if plan.command:
        completed = subprocess.run(plan.command, cwd=problem_dir)
        return completed.returncode

    print("cf-tool was not found. Opening the submit page for manual submission.")
    print("Install cf-tool and configure it if you want CLI submission.")
    webbrowser.open(plan.manual_submit_url)
    return 0


def open_submit_page_after_tests(
    problem_dir: Path,
    *,
    problem_key: str,
    source_name: str,
    language: str,
    configured_compiler: str | None,
    compare_mode: str,
    timeout_seconds: float | None = None,
    force_interactive: bool = False,
    force_after_failed_tests: bool = False,
    prefill: bool = False,
    prefill_timeout_seconds: float = 90.0,
    submit_url_override: str | None = None,
) -> int:
    problem_data = _load_problem_json(problem_dir)
    if problem_data.get("interactive") and not force_interactive:
        print("Interactive problem detected; refusing to open submit page without --force.")
        return 1

    run_result = run_problem_tests(
        problem_dir,
        source_name=source_name,
        configured_compiler=configured_compiler,
        compare_mode=compare_mode,  # type: ignore[arg-type]
        timeout_seconds=timeout_seconds,
        force_interactive=force_interactive,
    )
    if not run_result.success and not force_after_failed_tests:
        print("Local tests did not pass. Submit page was not opened.")
        return 1
    if not run_result.success:
        print("Local tests did not pass. Continuing because --force-after-failed-tests was set.")

    submit_url = submit_url_override or build_submit_url_from_problem_json(problem_data)
    solution_path = (problem_dir / source_name).resolve()
    print("Submit target")
    print(f"  Problem: {problem_key}")
    print(f"  File: {solution_path}")
    print(f"  Language: {language}")
    print(f"  Submit URL: {submit_url}")
    confirmation = input(f"Type SUBMIT {problem_key} to open the submit page: ")
    if confirmation != f"SUBMIT {problem_key}":
        print("Submission cancelled.")
        return 1
    if prefill:
        payload = build_submit_prefill_payload(
            problem_data,
            problem_key=problem_key,
            source_path=solution_path,
            language=language,
            submit_url=submit_url,
        )
        result = open_submit_page_with_prefill(
            submit_url,
            payload,
            timeout_seconds=prefill_timeout_seconds,
        )
        return 0 if result.delivered else 1
    webbrowser.open(submit_url)
    return 0


def _load_problem_json(problem_dir: Path) -> dict:
    with (problem_dir / "problem.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)
