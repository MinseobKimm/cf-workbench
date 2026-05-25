from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse


@dataclass(frozen=True)
class ProblemId:
    source: str
    contest_id: str
    index: str
    group_code: str | None = None

    @property
    def cf_tool_label(self) -> str:
        return f"{self.contest_id}{self.index}"


def parse_codeforces_problem_url(url: str) -> ProblemId | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host and not (host == "codeforces.com" or host.endswith(".codeforces.com")):
        return None

    parts = [unquote(part) for part in parsed.path.strip("/").split("/") if part]
    if len(parts) >= 4 and parts[0] in {"contest", "gym"} and parts[2] == "problem":
        return ProblemId(source=parts[0], contest_id=parts[1], index=parts[3])
    if len(parts) >= 4 and parts[0] == "problemset" and parts[1] == "problem":
        return ProblemId(source="problemset", contest_id=parts[2], index=parts[3])
    if (
        len(parts) >= 6
        and parts[0] == "group"
        and parts[2] == "contest"
        and parts[4] == "problem"
    ):
        return ProblemId(
            source="group",
            contest_id=parts[3],
            index=parts[5],
            group_code=parts[1],
        )
    return None


def safe_slug(value: str, fallback: str = "problem") -> str:
    lowered = value.strip().lower()
    slug = re.sub(r"[^a-z0-9._-]+", "-", lowered)
    slug = slug.strip("-._")
    return slug or fallback


def safe_path_part(value: str, fallback: str = "x") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    cleaned = cleaned.strip("._")
    return cleaned or fallback


def problem_directory(workspace: Path, name: str, url: str) -> Path:
    parsed = parse_codeforces_problem_url(url)
    root = workspace / "codeforces"
    if parsed is None:
        return root / "misc" / safe_slug(name)
    if parsed.source == "gym":
        return root / "gym" / safe_path_part(parsed.contest_id) / safe_path_part(parsed.index)
    return root / safe_path_part(parsed.contest_id) / safe_path_part(parsed.index)


def find_problem_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / "problem.json").is_file():
            return candidate
    raise FileNotFoundError("problem.json not found in current directory or parents")
