from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .schema import parse_codeforces_url
from .schema import NormalizedProblem, normalize_companion_payload


@dataclass(frozen=True)
class StoredProblem:
    problem: NormalizedProblem
    path: Path

    @property
    def problem_key(self) -> str:
        return self.problem.problem_key

    @property
    def samples(self) -> int:
        return len(self.problem.samples)


@dataclass(frozen=True)
class CreatedProblem:
    problem_key: str
    path: Path


@dataclass(frozen=True)
class WorkspaceFolder:
    name: str
    path: Path


def save_capture(
    payload: Mapping[str, Any],
    *,
    workspace: Path,
    template_path: Path | None = None,
    force_template: bool = False,
    judge_subdir: str = "codeforces",
) -> StoredProblem:
    problem = normalize_companion_payload(payload)
    problem_dir = find_problem_path(workspace, problem.problem_key, judge_subdir=judge_subdir)
    if problem_dir is None:
        problem_dir = _capture_problem_path(workspace, problem, judge_subdir=judge_subdir)
    _ensure_inside(workspace, problem_dir)

    tests_dir = problem_dir / "tests"
    local_cfw_dir = problem_dir / ".cfw"
    build_dir = local_cfw_dir / "build"
    runs_dir = local_cfw_dir / "runs"
    tests_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    problem_data = problem.to_problem_json()
    problem_data.setdefault("contestIncluded", False)
    _atomic_write_json(problem_dir / "problem.json", problem_data)
    _atomic_write_text(problem_dir / "README.md", _problem_readme(problem))
    for sample in problem.samples:
        _atomic_write_text(tests_dir / f"{sample.name}.in", sample.input)
        _atomic_write_text(tests_dir / f"{sample.name}.out", sample.output)

    source_path = problem_dir / "main.cpp"
    if force_template or not source_path.exists():
        template = template_path if template_path and template_path.exists() else _package_template()
        template_text = template.read_text(encoding="utf-8")
        _atomic_write_text(source_path, _source_from_template(problem, template_text))

    return StoredProblem(problem=problem, path=problem_dir)


def create_folder(workspace: Path, folder: str, *, judge_subdir: str = "codeforces") -> Path:
    root = judge_root(workspace, judge_subdir=judge_subdir)
    folder_path = root / _safe_relative_path(folder, fallback="folder")
    _ensure_inside(root, folder_path)
    _ensure_not_inside_problem(root, folder_path)
    if (folder_path / "problem.json").is_file():
        raise ValueError(f"path is a problem, not a folder: {folder}")
    if folder_path.exists():
        raise FileExistsError(f"folder already exists: {folder}")
    folder_path.mkdir(parents=True)
    return folder_path


def delete_folder(workspace: Path, folder: str, *, judge_subdir: str = "codeforces") -> Path:
    root = judge_root(workspace, judge_subdir=judge_subdir)
    folder_path = root / _safe_relative_path(folder, fallback="folder")
    _ensure_inside(root, folder_path)
    _ensure_not_inside_problem(root, folder_path)
    if not folder_path.is_dir():
        raise FileNotFoundError(f"folder not found: {folder}")
    if (folder_path / "problem.json").is_file():
        raise ValueError(f"use problem delete for problem folders: {folder}")
    shutil.rmtree(folder_path)
    return folder_path


def rename_folder(
    workspace: Path,
    folder: str,
    new_folder: str,
    *,
    judge_subdir: str = "codeforces",
) -> Path:
    root = judge_root(workspace, judge_subdir=judge_subdir)
    source = root / _safe_relative_path(folder, fallback="folder")
    target = root / _safe_relative_path(new_folder, fallback="folder")
    _ensure_inside(root, source)
    _ensure_inside(root, target)
    _ensure_not_inside_problem(root, source)
    _ensure_not_inside_problem(root, target)
    if not source.is_dir():
        raise FileNotFoundError(f"folder not found: {folder}")
    if (source / "problem.json").is_file():
        raise ValueError(f"use problem rename for problem folders: {folder}")
    source_resolved = source.resolve()
    target_resolved = target.resolve()
    if target_resolved == source_resolved:
        return source
    if _is_relative_to(target_resolved, source_resolved):
        raise ValueError("cannot move a folder inside itself")
    if target.exists():
        raise FileExistsError(f"folder already exists: {new_folder}")
    target.parent.mkdir(parents=True, exist_ok=True)
    source.rename(target)
    return target


def create_problem(
    workspace: Path,
    problem_key: str,
    *,
    name: str | None = None,
    url: str | None = None,
    folder: str | None = None,
    template_path: Path | None = None,
    judge_subdir: str = "codeforces",
) -> CreatedProblem:
    safe_key = _safe_path_part(problem_key, fallback="problem")
    if find_problem_path(workspace, safe_key, judge_subdir=judge_subdir) is not None:
        raise FileExistsError(f"problem already exists: {safe_key}")

    root = judge_root(workspace, judge_subdir=judge_subdir)
    parent = root
    if folder:
        parent = root / _safe_relative_path(folder, fallback="folder")
    _ensure_not_inside_problem(root, parent)
    if folder:
        problem_dir = parent / safe_key
    else:
        problem_dir = _manual_problem_path(workspace, safe_key, url, judge_subdir=judge_subdir)
    _ensure_inside(root, problem_dir)
    if problem_dir.exists():
        raise FileExistsError(f"path already exists: {problem_dir}")

    tests_dir = problem_dir / "tests"
    build_dir = problem_dir / ".cfw" / "build"
    runs_dir = problem_dir / ".cfw" / "runs"
    tests_dir.mkdir(parents=True)
    build_dir.mkdir(parents=True)
    runs_dir.mkdir(parents=True)

    problem_name = (name or safe_key).strip() or safe_key
    problem_url = (url or _url_from_problem_key(safe_key) or "").strip()
    data = _manual_problem_json(safe_key, problem_name, problem_url)
    _atomic_write_json(problem_dir / "problem.json", data)

    template = template_path if template_path and template_path.exists() else _package_template()
    template_text = template.read_text(encoding="utf-8")
    _atomic_write_text(problem_dir / "main.cpp", _manual_source(safe_key, problem_name, problem_url, template_text))
    _atomic_write_text(problem_dir / "README.md", _manual_problem_readme(safe_key, problem_name, problem_url))
    return CreatedProblem(problem_key=safe_key, path=problem_dir)


def delete_problem(workspace: Path, problem_key: str, *, judge_subdir: str = "codeforces") -> Path:
    problem_dir = resolve_problem_path(workspace, problem_key, judge_subdir=judge_subdir)
    root = judge_root(workspace, judge_subdir=judge_subdir)
    _ensure_inside(root, problem_dir)
    shutil.rmtree(problem_dir)
    return problem_dir


def rename_problem(
    workspace: Path,
    problem_key: str,
    name: str,
    *,
    judge_subdir: str = "codeforces",
) -> dict[str, Any]:
    new_name = name.strip()
    if not new_name:
        raise ValueError("problem name must be a non-empty string")
    problem_dir = resolve_problem_path(workspace, problem_key, judge_subdir=judge_subdir)
    root = judge_root(workspace, judge_subdir=judge_subdir)
    _ensure_inside(root, problem_dir)
    data = load_problem_json(problem_dir)
    data["name"] = new_name
    _atomic_write_json(problem_dir / "problem.json", data)
    return data


def judge_root(workspace: Path, *, judge_subdir: str = "codeforces") -> Path:
    root = workspace.resolve() / judge_subdir
    _ensure_inside(workspace, root)
    return root


def problem_path(workspace: Path, problem_key: str, *, judge_subdir: str = "codeforces") -> Path:
    safe_key = _safe_path_part(problem_key, fallback="problem")
    return judge_root(workspace, judge_subdir=judge_subdir) / safe_key


def find_problem_path(workspace: Path, problem_key: str, *, judge_subdir: str = "codeforces") -> Path | None:
    safe_key = _safe_path_part(problem_key, fallback="problem")
    root = judge_root(workspace, judge_subdir=judge_subdir)
    matches: list[Path] = []
    flat = root / safe_key
    if (flat / "problem.json").is_file():
        matches.append(flat)
    if root.is_dir():
        for problem_dir in iter_problem_dirs(workspace, judge_subdir=judge_subdir):
            if problem_dir == flat:
                continue
            try:
                data = load_problem_json(problem_dir)
            except (OSError, json.JSONDecodeError):
                continue
            key = str(data.get("problemKey") or problem_dir.name)
            if key == problem_key or _safe_path_part(key, fallback="problem") == safe_key:
                matches.append(problem_dir)
    if not matches:
        return None
    unique = sorted({path.resolve() for path in matches}, key=str)
    if len(unique) > 1:
        joined = ", ".join(str(path) for path in unique)
        raise ValueError(f"problem key is ambiguous: {problem_key} ({joined})")
    return unique[0]


def resolve_problem_path(workspace: Path, problem_key: str, *, judge_subdir: str = "codeforces") -> Path:
    problem_dir = find_problem_path(workspace, problem_key, judge_subdir=judge_subdir)
    if problem_dir is None:
        raise FileNotFoundError(f"problem not found: {problem_key} under {workspace}")
    return problem_dir


def iter_problem_dirs(workspace: Path, *, judge_subdir: str = "codeforces") -> list[Path]:
    root = judge_root(workspace, judge_subdir=judge_subdir)
    return _iter_problem_dirs_from_root(root)


def _iter_problem_dirs_from_root(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    problem_dirs: list[Path] = []
    for problem_json in root.rglob("problem.json"):
        try:
            relative = problem_json.relative_to(root)
        except ValueError:
            continue
        if any(part.startswith(".") for part in relative.parts):
            continue
        problem_dirs.append(problem_json.parent)
    return sorted(problem_dirs, key=lambda path: str(path.relative_to(root)).lower())


def list_workspace_folders(workspace: Path, *, judge_subdir: str = "codeforces") -> list[WorkspaceFolder]:
    root = judge_root(workspace, judge_subdir=judge_subdir)
    if not root.is_dir():
        return []
    problem_dirs = [path.resolve() for path in iter_problem_dirs(workspace, judge_subdir=judge_subdir)]
    folders: list[WorkspaceFolder] = []
    for folder_path in root.rglob("*"):
        if not folder_path.is_dir():
            continue
        resolved = folder_path.resolve()
        rel = folder_path.relative_to(root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if rel.parts and rel.parts[0] == "contests":
            continue
        if any(resolved == problem_dir or _is_relative_to(resolved, problem_dir) for problem_dir in problem_dirs):
            continue
        folders.append(WorkspaceFolder(name=rel.as_posix(), path=folder_path))
    return sorted(folders, key=lambda item: item.name.lower())


def _capture_problem_path(
    workspace: Path,
    problem: NormalizedProblem,
    *,
    judge_subdir: str = "codeforces",
) -> Path:
    parsed = parse_codeforces_url(problem.url)
    if parsed and parsed.source in {"contest", "gym", "group"}:
        return _contest_problem_path(
            workspace,
            problem.problem_key,
            source=parsed.source,
            contest_id=str(parsed.contest_id),
            index=parsed.index,
            group_code=parsed.group_code,
            judge_subdir=judge_subdir,
        )
    return problem_path(workspace, problem.problem_key, judge_subdir=judge_subdir)


def _manual_problem_path(
    workspace: Path,
    problem_key: str,
    url: str | None,
    *,
    judge_subdir: str = "codeforces",
) -> Path:
    parsed = parse_codeforces_url(url or "")
    if parsed and parsed.source in {"contest", "gym", "group"}:
        return _contest_problem_path(
            workspace,
            problem_key,
            source=parsed.source,
            contest_id=str(parsed.contest_id),
            index=parsed.index,
            group_code=parsed.group_code,
            judge_subdir=judge_subdir,
        )
    return problem_path(workspace, problem_key, judge_subdir=judge_subdir)


def _contest_problem_path(
    workspace: Path,
    problem_key: str,
    *,
    source: str,
    contest_id: str,
    index: str,
    group_code: str | None = None,
    judge_subdir: str = "codeforces",
) -> Path:
    if source == "gym":
        contest_folder = f"gym-{contest_id}"
    elif source == "group":
        contest_folder = f"group-{group_code or 'group'}-{contest_id}"
    else:
        contest_folder = contest_id
    return (
        judge_root(workspace, judge_subdir=judge_subdir)
        / "contests"
        / _safe_path_part(contest_folder, fallback="contest")
        / _safe_path_part(problem_key or index, fallback="problem")
    )


def load_problem_json(problem_dir: Path) -> dict[str, Any]:
    with (problem_dir / "problem.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _source_from_template(problem: NormalizedProblem, template_text: str) -> str:
    header = f"// Problem: {problem.problem_key} - {problem.name}\n// URL: {problem.url}\n\n"
    return header + template_text.lstrip()


def _problem_readme(problem: NormalizedProblem) -> str:
    return (
        f"# {problem.problem_key} - {problem.name}\n\n"
        f"- URL: {problem.url}\n"
        f"- Group: {problem.group or 'unknown'}\n"
        f"- Time limit: {problem.time_limit_ms} ms\n"
        f"- Memory limit: {problem.memory_limit_mb} MB\n"
        f"- Samples: {len(problem.samples)}\n\n"
        "Run local tests from this folder with:\n\n"
        "```bash\n"
        "cfw test\n"
        "```\n"
    )


def _manual_problem_json(problem_key: str, name: str, url: str) -> dict[str, Any]:
    parsed = parse_codeforces_url(url) if url else None
    inferred = _problem_parts_from_key(problem_key)
    return {
        "schemaVersion": 1,
        "judge": "codeforces",
        "problemKey": problem_key,
        "contestId": parsed.contest_id if parsed else inferred[0],
        "index": parsed.index if parsed else inferred[1],
        "name": name,
        "group": None,
        "url": url,
        "interactive": False,
        "timeLimitMs": 1000,
        "memoryLimitMb": 256,
        "testType": "single",
        "input": {"type": "stdin"},
        "output": {"type": "stdout"},
        "tests": [],
        "contestIncluded": False,
        "source": {
            "kind": "manual",
            "createdAt": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        },
    }


def _manual_source(problem_key: str, name: str, url: str, template_text: str) -> str:
    lines = [f"// Problem: {problem_key} - {name}"]
    if url:
        lines.append(f"// URL: {url}")
    return "\n".join(lines) + "\n\n" + template_text.lstrip()


def _manual_problem_readme(problem_key: str, name: str, url: str) -> str:
    lines = [
        f"# {problem_key} - {name}",
        "",
    ]
    if url:
        lines.append(f"- URL: {url}")
    lines.extend(
        [
            "- Samples: 0",
            "",
            "Run local tests from this folder with:",
            "",
            "```bash",
            "cfw test",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    _atomic_write_text(path, text)


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    try:
        os.replace(tmp, path)
    except PermissionError:
        path.write_text(text, encoding="utf-8", newline="\n")


def _ensure_inside(root: Path, target: Path) -> None:
    root_resolved = root.resolve()
    target_resolved = target.resolve()
    try:
        target_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"refusing to write outside workspace: {target_resolved}") from exc


def _package_template() -> Path:
    root_template = Path(__file__).resolve().parents[2] / "templates" / "main.cpp"
    if root_template.exists():
        return root_template
    return Path(__file__).parent / "templates" / "main.cpp"


def _safe_path_part(value: str, fallback: str = "problem") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    cleaned = cleaned.strip("-._")
    return cleaned or fallback


def _safe_relative_path(value: str, *, fallback: str) -> Path:
    if Path(value).is_absolute():
        raise ValueError(f"absolute paths are not allowed: {value}")
    parts: list[str] = []
    for raw_part in re.split(r"[\\/]+", value.strip()):
        part = raw_part.strip()
        if not part or part == ".":
            continue
        if part == "..":
            raise ValueError(f"parent paths are not allowed: {value}")
        parts.append(_safe_path_part(part, fallback=fallback))
    if not parts:
        parts.append(fallback)
    return Path(*parts)


def _problem_parts_from_key(problem_key: str) -> tuple[int | None, str | None]:
    match = re.fullmatch(r"(?:gym-)?(\d+)([A-Za-z][A-Za-z0-9]*)", problem_key)
    if not match:
        return None, None
    return int(match.group(1)), match.group(2)


def _url_from_problem_key(problem_key: str) -> str | None:
    contest_id, index = _problem_parts_from_key(problem_key)
    if contest_id is None or index is None:
        return None
    if problem_key.startswith("gym-"):
        return f"https://codeforces.com/gym/{contest_id}/problem/{index}"
    return f"https://codeforces.com/problemset/problem/{contest_id}/{index}"


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _ensure_not_inside_problem(root: Path, target: Path) -> None:
    resolved = target.resolve()
    for problem_dir in _iter_problem_dirs_from_root(root):
        problem_resolved = problem_dir.resolve()
        if resolved == problem_resolved or _is_relative_to(resolved, problem_resolved):
            raise ValueError(f"path is inside a problem folder: {target}")
