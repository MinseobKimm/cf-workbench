from __future__ import annotations

import subprocess
import sys
import platform
import socket
from dataclasses import dataclass
from pathlib import Path

from .codeforces_api import CodeforcesAPI, CodeforcesAPIError
from .compiler import detect_compiler
from .config import Config
from .ide import detect_clangd, clangd_version
from .submit import find_cf_tool


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    detail: str


def run_doctor(
    config: Config,
    *,
    online: bool = False,
    api_handle: str = "tourist",
) -> list[CheckResult]:
    results = [
        CheckResult("Python", "OK", sys.version.split()[0]),
        CheckResult("OS", "OK", platform.platform()),
        _path_check("config root", config.root, should_exist=True),
        _path_check("workspace", config.workspace, should_exist=False),
        _path_check("template", config.template, should_exist=True),
        CheckResult("port", "OK" if _port_available(config.port) else "WARN", f"127.0.0.1:{config.port}"),
        _where_gpp_check(),
        _compiler_check(config.compiler),
        _clangd_check(config.ide_clangd),
        _cf_tool_check(),
    ]
    if online:
        results.append(_api_check(config.api_min_interval_seconds, api_handle))
    else:
        results.append(
            CheckResult(
                "Codeforces API",
                "SKIP",
                "not checked; pass --online to call the official /api/user.status endpoint",
            )
        )
    return results


def format_doctor_results(results: list[CheckResult]) -> str:
    width = max(len(result.name) for result in results) if results else 0
    return "\n".join(
        f"{result.status:<4} {result.name:<{width}}  {result.detail}" for result in results
    )


def _path_check(name: str, path: Path, *, should_exist: bool) -> CheckResult:
    if path.exists():
        return CheckResult(name, "OK", str(path))
    status = "WARN" if not should_exist else "FAIL"
    detail = f"{path} does not exist"
    if name == "workspace":
        detail += "; run cfw init or import a problem"
    return CheckResult(name, status, detail)


def _compiler_check(configured_compiler: str | None) -> CheckResult:
    try:
        compiler = detect_compiler(configured_compiler)
    except FileNotFoundError as exc:
        return CheckResult("compiler", "FAIL", str(exc))

    version = _compiler_version(compiler.path)
    detail = compiler.path
    if version:
        detail = f"{detail} ({version})"
    if compiler.warning:
        return CheckResult("compiler", "WARN", f"{detail}; {compiler.warning}")
    return CheckResult("compiler", "OK", detail)


def _where_gpp_check() -> CheckResult:
    command = ["where", "g++"] if platform.system() == "Windows" else ["which", "g++"]
    try:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return CheckResult("PATH g++", "WARN", "could not inspect PATH")
    paths = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if not paths:
        return CheckResult("PATH g++", "WARN", "g++ not found on PATH")
    first = paths[0]
    if platform.system() == "Windows" and first.lower().startswith(r"c:\mingw64\bin"):
        detail = (
            f"{first}; old MinGW may fail on C++17 with #include <bits/stdc++.h>. "
            r"Recommended: C:\msys64\ucrt64\bin\g++.exe"
        )
        return CheckResult("PATH g++", "WARN", detail)
    return CheckResult("PATH g++", "OK", first)


def _clangd_check(configured_clangd: str | None) -> CheckResult:
    try:
        clangd = detect_clangd(configured_clangd)
    except FileNotFoundError as exc:
        return CheckResult("clangd", "WARN", str(exc))
    version = clangd_version(clangd.path)
    detail = clangd.path
    if version:
        detail = f"{detail} ({version})"
    return CheckResult("clangd", "OK", detail)


def _compiler_version(path: str) -> str:
    try:
        completed = subprocess.run(
            [path, "--version"],
            text=True,
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    first_line = (completed.stdout or completed.stderr).splitlines()
    return first_line[0].strip() if first_line else ""


def _cf_tool_check() -> CheckResult:
    executable = find_cf_tool()
    if executable:
        return CheckResult("cf-tool", "OK", executable)
    return CheckResult(
        "cf-tool",
        "WARN",
        "not found; cfw submit will open a manual submit page after confirmation",
    )


def _port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def _api_check(min_interval_seconds: float, handle: str) -> CheckResult:
    api = CodeforcesAPI(min_interval_seconds=min_interval_seconds)
    try:
        submissions = api.user_status(handle, count=1)
    except CodeforcesAPIError as exc:
        return CheckResult("Codeforces API", "FAIL", str(exc))
    except OSError as exc:
        return CheckResult("Codeforces API", "FAIL", str(exc))
    return CheckResult(
        "Codeforces API",
        "OK",
        f"official user.status reachable; {handle} returned {len(submissions)} item(s)",
    )
