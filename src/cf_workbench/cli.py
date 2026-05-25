from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import webbrowser
from pathlib import Path

from .codeforces_api import CodeforcesAPI, CodeforcesAPIError
from .companion_server import run_server
from .config import ensure_runtime_files, init_project, init_user_config, load_config, save_codeforces_credentials
from .doctor import format_doctor_results, run_doctor
from .models import Problem
from .paths import find_problem_root
from .runner import add_custom_test, run_problem_tests
from .storage import (
    create_folder,
    create_problem,
    delete_folder,
    delete_problem,
    resolve_problem_path,
    save_capture,
)
from .submit import open_submit_page_after_tests, submit_problem
from .sync import sync_solved_submissions


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except (FileExistsError, FileNotFoundError, ValueError, CodeforcesAPIError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cfw", description="Codeforces local workbench")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="create local workspace config and template")
    init_parser.set_defaults(func=cmd_init)

    config_parser = subparsers.add_parser("config", help="manage user config")
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    config_init = config_subparsers.add_parser("init", help="create ~/.cfw/config.json")
    config_init.add_argument("--force", action="store_true")
    config_init.set_defaults(func=cmd_config_init)
    config_cf = config_subparsers.add_parser("codeforces", help="save Codeforces account/API settings")
    config_cf.add_argument("--handle", required=True)
    config_cf.add_argument("--api-key")
    config_cf.add_argument("--api-secret")
    config_cf.add_argument("--check", action="store_true", help="verify the configured API credentials")
    config_cf.set_defaults(func=cmd_config_codeforces)

    listen_parser = subparsers.add_parser("listen", help="receive Competitive Companion payloads")
    listen_parser.add_argument("--host", default="127.0.0.1")
    listen_parser.add_argument("--port", type=int)
    listen_parser.add_argument("--workspace", type=Path)
    listen_parser.set_defaults(func=cmd_listen)

    capture_parser = subparsers.add_parser("capture-file", help="import a Competitive Companion JSON file")
    capture_parser.add_argument("payload", type=Path)
    capture_parser.add_argument("--workspace", type=Path)
    capture_parser.add_argument("--force-template", action="store_true")
    capture_parser.set_defaults(func=cmd_capture_file)

    test_parser = subparsers.add_parser("test", help="compile and run local tests")
    test_parser.add_argument("problem_key", nargs="?")
    test_parser.add_argument("--path", type=Path, default=Path.cwd())
    test_parser.add_argument("--workspace", type=Path)
    test_parser.add_argument("--source", default="main.cpp")
    test_parser.add_argument("--compare", choices=["exact", "trim", "tokens"])
    test_parser.add_argument("--tokens", action="store_true", help="compat: compare output token-by-token")
    test_parser.add_argument("--timeout", type=float)
    test_parser.add_argument("--force", action="store_true", help="run even if problem is interactive")
    test_parser.set_defaults(func=cmd_test)

    add_parser = subparsers.add_parser("add-test", help="add a custom input/output test pair")
    add_parser.add_argument("--path", type=Path, default=Path.cwd())
    add_parser.add_argument("--input-file", type=Path, required=True)
    add_parser.add_argument("--output-file", type=Path, required=True)
    add_parser.set_defaults(func=cmd_add_test)

    submit_parser = subparsers.add_parser("submit", help="open submit page after tests and confirmation")
    submit_parser.add_argument("problem_key", nargs="?")
    submit_parser.add_argument("--path", type=Path, default=Path.cwd())
    submit_parser.add_argument("--workspace", type=Path)
    submit_parser.add_argument("--source", default="main.cpp")
    submit_parser.add_argument("--language")
    submit_parser.add_argument("--tokens", action="store_true")
    submit_parser.add_argument("--compare", choices=["exact", "trim", "tokens"])
    submit_parser.add_argument("--open-browser", action="store_true")
    submit_parser.add_argument(
        "--prefill",
        action="store_true",
        help="open the submit page and let the browser extension fill the form",
    )
    submit_parser.add_argument(
        "--prefill-timeout",
        type=float,
        default=90.0,
        help="seconds to wait for the browser extension to fetch the source",
    )
    submit_parser.add_argument(
        "--submit-url",
        help="override the submit page URL, for example https://codeforces.com/problemset/submit",
    )
    submit_parser.add_argument("--timeout", type=float)
    submit_parser.add_argument("--force", action="store_true")
    submit_parser.add_argument("--force-after-failed-tests", action="store_true")
    submit_parser.set_defaults(func=cmd_submit)

    open_parser = subparsers.add_parser("open", help="open or print a captured problem")
    open_parser.add_argument("problem_key")
    open_parser.add_argument("--workspace", type=Path)
    open_parser.add_argument("--browser", action="store_true")
    open_parser.add_argument("--folder", action="store_true")
    open_parser.set_defaults(func=cmd_open)

    folder_parser = subparsers.add_parser("folder", help="create or delete workspace folders")
    folder_subparsers = folder_parser.add_subparsers(dest="folder_command")
    folder_create = folder_subparsers.add_parser("create", help="create a workspace folder")
    folder_create.add_argument("name")
    folder_create.add_argument("--workspace", type=Path)
    folder_create.set_defaults(func=cmd_folder_create)
    folder_delete = folder_subparsers.add_parser("delete", help="delete a workspace folder")
    folder_delete.add_argument("name")
    folder_delete.add_argument("--workspace", type=Path)
    folder_delete.add_argument("--yes", action="store_true", help="confirm recursive deletion")
    folder_delete.set_defaults(func=cmd_folder_delete)

    problem_parser = subparsers.add_parser("problem", help="create or delete workspace problems")
    problem_subparsers = problem_parser.add_subparsers(dest="problem_command")
    problem_create = problem_subparsers.add_parser("create", help="create an empty problem")
    problem_create.add_argument("problem_key")
    problem_create.add_argument("--name")
    problem_create.add_argument("--url")
    problem_create.add_argument("--folder")
    problem_create.add_argument("--workspace", type=Path)
    problem_create.set_defaults(func=cmd_problem_create)
    problem_delete = problem_subparsers.add_parser("delete", help="delete a problem folder")
    problem_delete.add_argument("problem_key")
    problem_delete.add_argument("--workspace", type=Path)
    problem_delete.add_argument("--yes", action="store_true", help="confirm recursive deletion")
    problem_delete.set_defaults(func=cmd_problem_delete)

    status_parser = subparsers.add_parser("status", help="show recent Codeforces submissions")
    status_parser.add_argument("handle", nargs="?")
    status_parser.add_argument("--limit", type=int, default=10)
    status_parser.set_defaults(func=cmd_status)

    sync_parser = subparsers.add_parser("sync-solved", help="save solved Codeforces problems from recent submissions")
    sync_parser.add_argument("--handle")
    sync_parser.add_argument("--limit", type=int, default=500)
    sync_parser.add_argument("--workspace", type=Path)
    sync_parser.add_argument("--source", default="main.cpp")
    sync_parser.set_defaults(func=cmd_sync_solved)

    doctor_parser = subparsers.add_parser("doctor", help="check local tools and optional API connectivity")
    doctor_parser.add_argument("--online", action="store_true", help="call the official Codeforces API")
    doctor_parser.add_argument(
        "--handle",
        default="tourist",
        help="public handle used for the online API smoke check",
    )
    doctor_parser.set_defaults(func=cmd_doctor)

    return parser


def cmd_init(args: argparse.Namespace) -> int:
    config = init_project(Path.cwd())
    print(f"Config: {config.root / '.cfw' / 'config.json'}")
    print(f"Template: {config.template}")
    print(f"Workspace: {config.workspace}")
    return 0


def cmd_config_init(args: argparse.Namespace) -> int:
    path = init_user_config(force=args.force)
    print(f"Config: {path}")
    return 0


def cmd_config_codeforces(args: argparse.Namespace) -> int:
    api_key = args.api_key
    api_secret = args.api_secret
    if api_key is None:
        api_key = getpass.getpass("Codeforces API key (blank to skip): ").strip() or None
    if api_secret is None:
        api_secret = getpass.getpass("Codeforces API secret (blank to skip): ").strip() or None
    path = save_codeforces_credentials(handle=args.handle, api_key=api_key, api_secret=api_secret)
    print(f"Config: {path}")
    print(f"Codeforces handle: {args.handle}")
    if args.check:
        api = CodeforcesAPI(api_key=api_key, api_secret=api_secret)
        api.check_auth()
        print("Codeforces API credentials: OK")
    return 0


def cmd_listen(args: argparse.Namespace) -> int:
    config = load_config(Path.cwd())
    if args.workspace:
        config.workspace = args.workspace.resolve()
    ensure_runtime_files(config)
    run_server(config, host=args.host, port=args.port or config.port)
    return 0


def cmd_capture_file(args: argparse.Namespace) -> int:
    config = load_config(Path.cwd())
    if args.workspace:
        config.workspace = args.workspace.resolve()
    ensure_runtime_files(config)
    workspace = config.workspace.resolve()
    with args.payload.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    stored = save_capture(
        payload,
        workspace=workspace,
        template_path=config.template,
        force_template=args.force_template,
        judge_subdir=config.judge_subdir,
    )
    print(f"Imported Codeforces problem: {stored.problem_key}")
    print(f"Path: {stored.path}")
    print(f"Samples: {stored.samples}")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    config = load_config(args.path)
    if args.workspace:
        config.workspace = args.workspace.resolve()
    problem_dir = _resolve_problem_dir(config, args.problem_key, args.path)
    compare_mode = args.compare or ("tokens" if args.tokens else config.compare_mode)
    result = run_problem_tests(
        problem_dir,
        source_name=args.source,
        configured_compiler=config.compiler,
        compare_mode=compare_mode,  # type: ignore[arg-type]
        timeout_seconds=args.timeout,
        force_interactive=args.force,
    )
    _print_run_result(result)
    return 0 if result.success else 1


def cmd_add_test(args: argparse.Namespace) -> int:
    problem_dir = find_problem_root(args.path)
    input_text = args.input_file.read_text(encoding="utf-8")
    output_text = args.output_file.read_text(encoding="utf-8")
    case = add_custom_test(problem_dir, input_text, output_text)
    print(f"Added test {case.number}: {case.input_path} / {case.answer_path}")
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    config = load_config(args.path)
    if args.workspace:
        config.workspace = args.workspace.resolve()
    problem_dir = _resolve_problem_dir(config, args.problem_key, args.path)
    if args.open_browser or args.prefill:
        problem_key = args.problem_key or _problem_key_from_dir(problem_dir)
        return open_submit_page_after_tests(
            problem_dir,
            problem_key=problem_key,
            source_name=args.source,
            language=args.language or config.language,
            configured_compiler=config.compiler,
            compare_mode=args.compare or ("tokens" if args.tokens else config.compare_mode),
            timeout_seconds=args.timeout,
            force_interactive=args.force,
            force_after_failed_tests=args.force_after_failed_tests,
            prefill=args.prefill,
            prefill_timeout_seconds=args.prefill_timeout,
            submit_url_override=args.submit_url,
        )
    problem = _load_problem(problem_dir)
    return submit_problem(
        problem,
        problem_dir,
        source_name=args.source,
        language=args.language or config.language,
        configured_compiler=config.compiler,
        tokens=args.tokens,
        force_after_failed_tests=args.force_after_failed_tests,
    )


def cmd_status(args: argparse.Namespace) -> int:
    config = load_config(Path.cwd())
    handle = args.handle or config.codeforces_handle
    if not handle:
        raise ValueError("Codeforces handle is required; pass one or run cfw config codeforces --handle HANDLE")
    api = CodeforcesAPI(
        min_interval_seconds=config.api_min_interval_seconds,
        api_key=config.codeforces_api_key,
        api_secret=config.codeforces_api_secret,
    )
    submissions = api.user_status(handle, count=args.limit)
    for submission in submissions:
        problem = submission.get("problem", {})
        problem_name = problem.get("name", "?")
        verdict = submission.get("verdict", "TESTING")
        language = submission.get("programmingLanguage", "?")
        time_ms = submission.get("timeConsumedMillis", "?")
        memory = submission.get("memoryConsumedBytes", "?")
        submission_id = submission.get("id", "?")
        print(
            f"{submission_id} | {verdict} | {language} | "
            f"{time_ms} ms | {memory} bytes | {problem_name}"
        )
    return 0


def cmd_sync_solved(args: argparse.Namespace) -> int:
    config = load_config(Path.cwd())
    if args.workspace:
        config.workspace = args.workspace.resolve()
    handle = args.handle or config.codeforces_handle
    if not handle:
        raise ValueError("Codeforces handle is required; pass --handle or run cfw config codeforces --handle HANDLE")
    api = CodeforcesAPI(
        min_interval_seconds=config.api_min_interval_seconds,
        api_key=config.codeforces_api_key,
        api_secret=config.codeforces_api_secret,
    )
    result = sync_solved_submissions(
        api,
        handle=handle,
        workspace=config.workspace,
        judge_subdir=config.judge_subdir,
        count=args.limit,
        source_name=args.source,
    )
    print(f"Handle: {result.handle}")
    print(f"Fetched submissions: {result.fetched}")
    print(f"Accepted problems: {result.accepted}")
    print(f"Local problems updated: {result.local_updated}")
    print(f"Solution snapshots saved: {result.solution_snapshots}")
    print(f"Solved index: {result.index_path}")
    return 0


def cmd_open(args: argparse.Namespace) -> int:
    config = load_config(Path.cwd())
    if args.workspace:
        config.workspace = args.workspace.resolve()
    problem_dir = resolve_problem_path(config.workspace, args.problem_key, judge_subdir=config.judge_subdir)
    with (problem_dir / "problem.json").open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    url = str(data.get("url", ""))
    print(f"Problem: {args.problem_key}")
    print(f"Folder: {problem_dir}")
    print(f"URL: {url}")
    open_browser = args.browser
    open_folder = args.folder or not args.browser
    if open_folder:
        _open_folder(problem_dir)
    if open_browser and url:
        webbrowser.open(url)
    return 0


def cmd_folder_create(args: argparse.Namespace) -> int:
    config = load_config(Path.cwd())
    if args.workspace:
        config.workspace = args.workspace.resolve()
    ensure_runtime_files(config)
    path = create_folder(config.workspace, args.name, judge_subdir=config.judge_subdir)
    print(f"Created folder: {path}")
    return 0


def cmd_folder_delete(args: argparse.Namespace) -> int:
    if not args.yes:
        raise ValueError("folder delete requires --yes")
    config = load_config(Path.cwd())
    if args.workspace:
        config.workspace = args.workspace.resolve()
    path = delete_folder(config.workspace, args.name, judge_subdir=config.judge_subdir)
    print(f"Deleted folder: {path}")
    return 0


def cmd_problem_create(args: argparse.Namespace) -> int:
    config = load_config(Path.cwd())
    if args.workspace:
        config.workspace = args.workspace.resolve()
    ensure_runtime_files(config)
    created = create_problem(
        config.workspace,
        args.problem_key,
        name=args.name,
        url=args.url,
        folder=args.folder,
        template_path=config.template,
        judge_subdir=config.judge_subdir,
    )
    print(f"Created problem: {created.problem_key}")
    print(f"Path: {created.path}")
    return 0


def cmd_problem_delete(args: argparse.Namespace) -> int:
    if not args.yes:
        raise ValueError("problem delete requires --yes")
    config = load_config(Path.cwd())
    if args.workspace:
        config.workspace = args.workspace.resolve()
    path = delete_problem(config.workspace, args.problem_key, judge_subdir=config.judge_subdir)
    print(f"Deleted problem: {path}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    config = load_config(Path.cwd())
    results = run_doctor(config, online=args.online, api_handle=args.handle)
    print(format_doctor_results(results))
    return 0 if all(result.status != "FAIL" for result in results) else 1


def _load_problem(problem_dir: Path) -> Problem:
    with (problem_dir / "problem.json").open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return Problem.from_companion_payload(data)


def _resolve_problem_dir(config, problem_key: str | None, start: Path) -> Path:
    if problem_key:
        return resolve_problem_path(config.workspace, problem_key, judge_subdir=config.judge_subdir)
    return find_problem_root(start)


def _problem_key_from_dir(problem_dir: Path) -> str:
    with (problem_dir / "problem.json").open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    value = data.get("problemKey")
    return str(value) if value else problem_dir.name


def _open_folder(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        import subprocess

        subprocess.Popen(["open", str(path)])
    else:
        import subprocess

        subprocess.Popen(["xdg-open", str(path)])


def _print_run_result(result) -> None:
    if result.skipped_reason:
        print(f"SKIP: {result.skipped_reason}")
        return
    print(f"Compile: {'OK' if result.compile_result.success else 'CE'}")
    if result.compile_result.command:
        print(f"Command: {' '.join(result.compile_result.command)}")
    if result.compile_result.warning:
        print(f"Warning: {result.compile_result.warning}")
    if result.compile_result.stdout:
        print("Compiler stdout:")
        print(_limit_output(result.compile_result.stdout).rstrip())
    if result.compile_result.stderr:
        print("Compiler stderr:")
        print(_limit_output(result.compile_result.stderr).rstrip())
    if not result.compile_result.success:
        return
    if not result.cases:
        print("No tests found.")
        return
    for case in result.cases:
        name = case.case.name or f"case_{case.case.number}"
        elapsed = "" if case.elapsed_ms is None else f"   {case.elapsed_ms} ms"
        print(f"{name}: {case.status}{elapsed}")
        if case.status != "AC":
            if case.returncode is not None:
                print(f"Return code: {case.returncode}")
            if case.stderr:
                print("stderr:")
                print(_limit_output(case.stderr).rstrip())
            print("Expected:")
            print(case.expected.rstrip())
            print("Actual:")
            print(case.actual.rstrip())
            if case.diff:
                print("Diff:")
                print(case.diff)


def _limit_output(value: str, *, max_lines: int = 80, max_chars: int = 12000) -> str:
    if len(value) <= max_chars and value.count("\n") <= max_lines:
        return value
    lines = value.splitlines()
    kept_lines = lines[:max_lines]
    truncated = "\n".join(kept_lines)
    if len(truncated) > max_chars:
        truncated = truncated[:max_chars].rstrip()
    omitted_lines = max(0, len(lines) - len(kept_lines))
    omitted_chars = max(0, len(value) - len(truncated))
    return (
        f"{truncated}\n"
        f"... output truncated ({omitted_lines} more line(s), {omitted_chars} more char(s))"
    )


if __name__ == "__main__":
    raise SystemExit(main())
