from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .codeforces_api import CodeforcesAPI
from .storage import find_problem_path, judge_root, load_problem_json


@dataclass(frozen=True)
class SyncSolvedResult:
    handle: str
    fetched: int
    accepted: int
    local_updated: int
    solution_snapshots: int
    index_path: Path


def sync_solved_submissions(
    api: CodeforcesAPI,
    *,
    handle: str,
    workspace: Path,
    judge_subdir: str = "codeforces",
    count: int = 500,
    source_name: str = "main.cpp",
) -> SyncSolvedResult:
    submissions = api.user_status(handle, count=count)
    accepted = _latest_accepted_by_problem(submissions)
    root = judge_root(workspace, judge_subdir=judge_subdir)
    cfw_dir = root / ".cfw"
    cfw_dir.mkdir(parents=True, exist_ok=True)
    index_path = cfw_dir / "solved.json"
    synced_at = _utc_now()

    records = [_solved_record(problem_key, submission) for problem_key, submission in accepted.items()]
    _atomic_write_json(
        index_path,
        {
            "schemaVersion": 1,
            "handle": handle,
            "syncedAt": synced_at,
            "count": len(records),
            "problems": sorted(records, key=lambda item: item["problemKey"]),
        },
    )

    local_updated = 0
    solution_snapshots = 0
    for problem_key, submission in accepted.items():
        problem_dir = find_problem_path(workspace, problem_key, judge_subdir=judge_subdir)
        if problem_dir is None:
            continue
        if _update_problem_solved_metadata(problem_dir, problem_key, submission, handle, synced_at):
            local_updated += 1
        if _snapshot_local_solution(problem_dir, submission, source_name=source_name):
            solution_snapshots += 1

    return SyncSolvedResult(
        handle=handle,
        fetched=len(submissions),
        accepted=len(accepted),
        local_updated=local_updated,
        solution_snapshots=solution_snapshots,
        index_path=index_path,
    )


def _latest_accepted_by_problem(submissions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    accepted: dict[str, dict[str, Any]] = {}
    for submission in submissions:
        if submission.get("verdict") != "OK":
            continue
        problem_key = _problem_key_from_submission(submission)
        if not problem_key or problem_key in accepted:
            continue
        accepted[problem_key] = submission
    return accepted


def _problem_key_from_submission(submission: dict[str, Any]) -> str | None:
    problem = submission.get("problem")
    if not isinstance(problem, dict):
        return None
    contest_id = problem.get("contestId")
    index = problem.get("index")
    if contest_id is None or index is None:
        return None
    return f"{contest_id}{index}"


def _solved_record(problem_key: str, submission: dict[str, Any]) -> dict[str, Any]:
    problem = submission.get("problem") if isinstance(submission.get("problem"), dict) else {}
    record = {
        "problemKey": problem_key,
        "contestId": problem.get("contestId"),
        "index": problem.get("index"),
        "name": problem.get("name"),
        "submissionId": submission.get("id"),
        "programmingLanguage": submission.get("programmingLanguage"),
        "creationTimeSeconds": submission.get("creationTimeSeconds"),
        "timeConsumedMillis": submission.get("timeConsumedMillis"),
        "memoryConsumedBytes": submission.get("memoryConsumedBytes"),
    }
    if isinstance(problem.get("rating"), int):
        record["rating"] = problem["rating"]
    if isinstance(problem.get("tags"), list):
        record["tags"] = [str(tag) for tag in problem["tags"]]
    return record


def _update_problem_solved_metadata(
    problem_dir: Path,
    problem_key: str,
    submission: dict[str, Any],
    handle: str,
    synced_at: str,
) -> bool:
    problem_json = problem_dir / "problem.json"
    data = load_problem_json(problem_dir)
    solved = {
        **_solved_record(problem_key, submission),
        "handle": handle,
        "verdict": "OK",
        "syncedAt": synced_at,
    }
    if data.get("solved") == solved:
        return False
    data["solved"] = solved
    _atomic_write_json(problem_json, data)
    return True


def _snapshot_local_solution(problem_dir: Path, submission: dict[str, Any], *, source_name: str) -> bool:
    source_path = problem_dir / source_name
    if not source_path.is_file():
        return False
    submission_id = submission.get("id")
    if submission_id is None:
        return False
    suffix = source_path.suffix or ".txt"
    destination = problem_dir / "solutions" / f"{submission_id}{suffix}"
    if destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, destination)
    return True


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    try:
        os.replace(tmp, path)
    except PermissionError:
        path.write_text(text, encoding="utf-8", newline="\n")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
