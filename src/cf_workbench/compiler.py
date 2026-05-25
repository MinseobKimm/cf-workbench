from __future__ import annotations

import platform
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompilerInfo:
    path: str
    warning: str | None = None


@dataclass
class CompileResult:
    success: bool
    command: list[str]
    executable: Path
    returncode: int
    stdout: str
    stderr: str
    warning: str | None = None


def detect_compiler(configured: str | None = None) -> CompilerInfo:
    if configured:
        resolved = shutil.which(configured) or configured
        return CompilerInfo(path=resolved, warning=_compiler_path_warning(resolved))

    msys2 = Path(r"C:\msys64\ucrt64\bin\g++.exe")
    if platform.system() == "Windows" and msys2.exists():
        return CompilerInfo(path=str(msys2), warning=None)

    gpp = shutil.which("g++")
    if gpp:
        return CompilerInfo(path=gpp, warning=_compiler_path_warning(gpp))

    raise FileNotFoundError(
        "g++ not found. Install GCC/MSYS2 or set compiler in .cfw/config.json."
    )


def compile_solution(
    problem_dir: Path,
    source: Path,
    *,
    compiler_path: str | None = None,
    configured_compiler: str | None = None,
    timeout_seconds: float = 30.0,
) -> CompileResult:
    problem_dir = problem_dir.resolve()
    source = source.resolve()
    build_dir = problem_dir / ".cfw" / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    executable = build_dir / ("main.exe" if platform.system() == "Windows" else "main")

    compiler = CompilerInfo(compiler_path) if compiler_path else detect_compiler(configured_compiler)
    source_arg = _relative_or_absolute(source, problem_dir)
    output_arg = _relative_or_absolute(executable, problem_dir)
    command = [
        compiler.path,
        "-std=gnu++17",
        "-O2",
        "-pipe",
        "-Wall",
        "-Wextra",
        "-Wshadow",
        source_arg,
        "-o",
        output_arg,
    ]
    env = os.environ.copy()
    env["TMP"] = str(build_dir)
    env["TEMP"] = str(build_dir)
    env["TMPDIR"] = str(build_dir)
    compiler_dir = str(Path(compiler.path).resolve().parent)
    env["PATH"] = f"{compiler_dir}{os.pathsep}{env.get('PATH', '')}"
    try:
        completed = subprocess.run(
            command,
            cwd=problem_dir,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return CompileResult(
            success=False,
            command=command,
            executable=executable,
            returncode=-1,
            stdout=_process_text(exc.stdout),
            stderr=f"Compiler timed out after {timeout_seconds:g} seconds.\n{_process_text(exc.stderr)}".rstrip(),
            warning=compiler.warning,
        )
    except OSError as exc:
        return CompileResult(
            success=False,
            command=command,
            executable=executable,
            returncode=-1,
            stdout="",
            stderr=f"Failed to start compiler: {exc}",
            warning=compiler.warning,
        )
    warning = compiler.warning or _compiler_version_warning(compiler.path)
    return CompileResult(
        success=completed.returncode == 0,
        command=command,
        executable=executable,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        warning=warning,
    )


def _process_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _compiler_path_warning(path: str) -> str | None:
    lowered = path.lower().replace("/", "\\")
    if r"c:\mingw64" in lowered:
        recommendation = ""
        msys2 = Path(r"C:\msys64\ucrt64\bin\g++.exe")
        if platform.system() == "Windows" and msys2.exists():
            recommendation = f" Set compiler to {msys2} in .cfw/config.json."
        return (
            "This compiler appears to be under C:\\mingw64. Old MinGW builds, "
            "especially GCC 8.1.0, may break with C++17 and <bits/stdc++.h>."
            f"{recommendation}"
        )
    return None


def _compiler_version_warning(path: str) -> str | None:
    try:
        completed = subprocess.run(
            [path, "--version"],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    version_text = f"{completed.stdout}\n{completed.stderr}"
    if "8.1.0" in version_text and "mingw" in version_text.lower():
        return (
            "Detected MinGW GCC 8.1.0. This compiler may break with C++17 "
            "and <bits/stdc++.h>; MSYS2 UCRT64 GCC is recommended on Windows."
        )
    return None
