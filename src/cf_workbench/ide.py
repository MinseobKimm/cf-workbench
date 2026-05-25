from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import re
import shutil
import struct
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

from .compiler import detect_compiler


@dataclass(frozen=True)
class ClangdInfo:
    path: str
    warning: str | None = None


@dataclass(frozen=True)
class WebSocketFrame:
    opcode: int
    payload: bytes


class WebSocketClosed(Exception):
    pass


def detect_clangd(configured: str | None = None) -> ClangdInfo:
    if configured:
        resolved = shutil.which(configured) or configured
        if Path(resolved).exists() or shutil.which(resolved):
            return ClangdInfo(path=resolved)
        raise FileNotFoundError(f"clangd not found: {configured}")

    path = shutil.which("clangd")
    if path:
        return ClangdInfo(path=path)

    candidates: list[Path] = []
    if platform.system() == "Windows":
        candidates.extend(
            [
                Path(r"C:\msys64\ucrt64\bin\clangd.exe"),
                Path(r"C:\Program Files\LLVM\bin\clangd.exe"),
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return ClangdInfo(path=str(candidate))

    raise FileNotFoundError("clangd not found. Install LLVM clangd or set ide.clangd in .cfw/config.json.")


def clangd_status(configured: str | None = None) -> dict[str, str | bool | None]:
    try:
        clangd = detect_clangd(configured)
    except FileNotFoundError as exc:
        return {"available": False, "path": None, "version": None, "error": str(exc)}
    return {
        "available": True,
        "path": clangd.path,
        "version": clangd_version(clangd.path),
        "error": None,
    }


def clangd_version(path: str) -> str:
    try:
        completed = subprocess.run(
            [path, "--version"],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=5,
            **hidden_subprocess_kwargs(),
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    first_line = (completed.stdout or completed.stderr).splitlines()
    return first_line[0].strip() if first_line else ""


def write_compile_commands(
    problem_dir: Path,
    source_path: Path,
    *,
    configured_compiler: str | None = None,
) -> Path:
    problem_dir = problem_dir.resolve()
    source_path = source_path.resolve()
    compiler = detect_compiler(configured_compiler)
    build_dir = problem_dir / ".cfw" / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    output = build_dir / f"{source_path.stem}.o"
    arguments = [
        compiler.path,
        "-std=gnu++17",
        "-O2",
        "-pipe",
        "-Wall",
        "-Wextra",
        "-Wshadow",
        "-c",
        str(source_path),
        "-o",
        str(output),
    ]
    payload = [
        {
            "directory": str(problem_dir),
            "arguments": arguments,
            "file": str(source_path),
        }
    ]
    path = problem_dir / "compile_commands.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def compiler_syntax_diagnostics(
    problem_dir: Path,
    source_name: str,
    source: str,
    *,
    configured_compiler: str | None = None,
    timeout_seconds: float = 6.0,
) -> list[dict[str, int | str]]:
    problem_dir = problem_dir.resolve()
    diagnostics_dir = problem_dir / ".cfw" / "diagnostics"
    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(source_name or "main.cpp").name
    source_path = diagnostics_dir / safe_name
    source_path.write_text(source, encoding="utf-8", newline="\n")
    compiler = detect_compiler(configured_compiler)
    command = [
        compiler.path,
        "-std=gnu++17",
        "-Wall",
        "-Wextra",
        "-Wshadow",
        "-fsyntax-only",
        str(source_path),
    ]
    env = os.environ.copy()
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
            **hidden_subprocess_kwargs(),
        )
    except subprocess.TimeoutExpired:
        return [
            {
                "line": 1,
                "column": 1,
                "severity": "warning",
                "message": f"syntax check timed out after {timeout_seconds:g} seconds",
            }
        ]
    except OSError as exc:
        return [{"line": 1, "column": 1, "severity": "error", "message": f"compiler failed: {exc}"}]
    return parse_gcc_diagnostics(completed.stderr)


def parse_gcc_diagnostics(text: str) -> list[dict[str, int | str]]:
    diagnostics: list[dict[str, int | str]] = []
    for line in text.splitlines():
        match = re.match(r"^.*:(\d+):(\d+):\s+(fatal error|error|warning|note):\s+(.*)$", line)
        if not match:
            continue
        line_number = int(match.group(1))
        column = int(match.group(2))
        kind = match.group(3)
        message = match.group(4).strip()
        severity = "error" if kind in {"fatal error", "error"} else ("warning" if kind == "warning" else "info")
        diagnostics.append({"line": line_number, "column": column, "severity": severity, "message": message})
    return diagnostics


def clangd_process_args(
    problem_dir: Path,
    *,
    configured_clangd: str | None = None,
    configured_compiler: str | None = None,
) -> list[str]:
    clangd = detect_clangd(configured_clangd)
    args = [clangd.path, f"--compile-commands-dir={problem_dir.resolve()}"]
    try:
        compiler = detect_compiler(configured_compiler)
    except FileNotFoundError:
        compiler = None
    if compiler is not None:
        args.append(f"--query-driver={compiler.path}")
    return args


def websocket_accept_key(client_key: str) -> str:
    digest = hashlib.sha1((client_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()
    return base64.b64encode(digest).decode("ascii")


def read_websocket_frame(stream: BinaryIO) -> WebSocketFrame:
    header = _read_exact(stream, 2)
    if not header:
        raise WebSocketClosed()
    first, second = header[0], header[1]
    opcode = first & 0x0F
    masked = bool(second & 0x80)
    length = second & 0x7F
    if length == 126:
        length = struct.unpack("!H", _read_exact(stream, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", _read_exact(stream, 8))[0]
    mask = _read_exact(stream, 4) if masked else b""
    payload = _read_exact(stream, length) if length else b""
    if masked:
        payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    return WebSocketFrame(opcode=opcode, payload=payload)


def write_websocket_frame(sock, payload: bytes | str, *, opcode: int = 1) -> None:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    length = len(payload)
    header = bytearray([0x80 | opcode])
    if length < 126:
        header.append(length)
    elif length <= 0xFFFF:
        header.append(126)
        header.extend(struct.pack("!H", length))
    else:
        header.append(127)
        header.extend(struct.pack("!Q", length))
    sock.sendall(bytes(header) + payload)


def read_lsp_message(stream: BinaryIO) -> bytes | None:
    headers: dict[str, str] = {}
    while True:
        line = stream.readline()
        if line == b"":
            return None
        if line in {b"\r\n", b"\n"}:
            break
        name, sep, value = line.decode("ascii", errors="replace").partition(":")
        if sep:
            headers[name.strip().lower()] = value.strip()
    length_text = headers.get("content-length")
    if not length_text:
        return None
    return _read_exact(stream, int(length_text))


def write_lsp_message(stream: BinaryIO, payload: bytes | str) -> None:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    stream.write(f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii") + payload)
    stream.flush()


def run_lsp_websocket_proxy(
    *,
    sock,
    stream: BinaryIO,
    problem_dir: Path,
    source_path: Path,
    configured_clangd: str | None = None,
    configured_compiler: str | None = None,
) -> None:
    write_compile_commands(problem_dir, source_path, configured_compiler=configured_compiler)
    args = clangd_process_args(
        problem_dir,
        configured_clangd=configured_clangd,
        configured_compiler=configured_compiler,
    )
    env = os.environ.copy()
    if configured_compiler:
        compiler_dir = str(Path(configured_compiler).resolve().parent)
        env["PATH"] = f"{compiler_dir}{os.pathsep}{env.get('PATH', '')}"
    process = subprocess.Popen(
        args,
        cwd=problem_dir,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        **hidden_subprocess_kwargs(),
    )
    assert process.stdin is not None
    assert process.stdout is not None
    send_lock = threading.Lock()
    closed = threading.Event()

    def send_to_client(payload: bytes, *, opcode: int = 1) -> None:
        if closed.is_set():
            return
        with send_lock:
            write_websocket_frame(sock, payload, opcode=opcode)

    def stdout_loop() -> None:
        try:
            while not closed.is_set():
                message = read_lsp_message(process.stdout)
                if message is None:
                    break
                send_to_client(message)
        finally:
            closed.set()

    def stderr_loop() -> None:
        if process.stderr is None:
            return
        for _line in iter(process.stderr.readline, b""):
            if closed.is_set():
                break

    stdout_thread = threading.Thread(target=stdout_loop, daemon=True)
    stderr_thread = threading.Thread(target=stderr_loop, daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    try:
        while not closed.is_set():
            frame = read_websocket_frame(stream)
            if frame.opcode == 0x8:
                break
            if frame.opcode == 0x9:
                send_to_client(frame.payload, opcode=0xA)
                continue
            if frame.opcode not in {0x1, 0x2}:
                continue
            write_lsp_message(process.stdin, frame.payload)
    finally:
        closed.set()
        try:
            send_to_client(b"", opcode=0x8)
        except OSError:
            pass
        _terminate_process(process)
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        _close_process_pipe(process.stdin)
        _close_process_pipe(process.stdout)
        _close_process_pipe(process.stderr)
        return
    try:
        _close_process_pipe(process.stdin)
        process.wait(timeout=0.5)
        return
    except (OSError, subprocess.SubprocessError):
        pass
    finally:
        if process.poll() is not None:
            _close_process_pipe(process.stdout)
            _close_process_pipe(process.stderr)
    try:
        process.terminate()
        process.wait(timeout=2)
    except (OSError, subprocess.SubprocessError):
        _kill_process_tree(process)
    finally:
        _close_process_pipe(process.stdout)
        _close_process_pipe(process.stderr)


def hidden_subprocess_kwargs() -> dict[str, Any]:
    if os.name != "nt" or not hasattr(subprocess, "STARTUPINFO"):
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
    return {
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
        "startupinfo": startupinfo,
    }


def _close_process_pipe(pipe: Any) -> None:
    if pipe is None:
        return
    try:
        pipe.close()
    except OSError:
        pass


def _kill_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3,
                **hidden_subprocess_kwargs(),
            )
            process.wait(timeout=1)
            return
        except (OSError, subprocess.SubprocessError):
            pass
    try:
        process.kill()
        process.wait(timeout=1)
    except (OSError, subprocess.SubprocessError):
        pass


def _read_exact(stream: BinaryIO, length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = length
    while remaining:
        chunk = stream.read(remaining)
        if not chunk:
            raise WebSocketClosed()
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)
