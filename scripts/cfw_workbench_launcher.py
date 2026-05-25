from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PORT = 27121
BASE_URL = f"http://{HOST}:{PORT}/"
HEALTH_URL = f"{BASE_URL}health"
SHUTDOWN_URL = f"{BASE_URL}shutdown"
LOG_DIR = ROOT / ".cfw" / "logs"
PID_FILE = LOG_DIR / "cfw-workbench.pid"
OUT_LOG = LOG_DIR / "cfw-workbench.out.log"
ERR_LOG = LOG_DIR / "cfw-workbench.err.log"
PROXY_ENV_VARS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy",
)


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 11):
        print("Python 3.11 or newer is required to run cf-workbench.", file=sys.stderr)
        return 1

    argv = argv or sys.argv[1:]
    no_browser = "--no-browser" in argv

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stop_previous_server()
    if is_cfw_server_running():
        if not no_browser:
            open_workbench(BASE_URL)
        return 0

    process = start_server()
    write_pid_file(process.pid)

    if not wait_for_server():
        print(f"cf-workbench did not start on {BASE_URL}", file=sys.stderr)
        print(f"stderr log: {ERR_LOG}", file=sys.stderr)
        return 1

    if not no_browser:
        open_workbench(BASE_URL)
    return 0


def stop_previous_server() -> None:
    try:
        pid = int(PID_FILE.read_text(encoding="ascii").strip())
    except (FileNotFoundError, ValueError):
        return

    if request_server_shutdown():
        for _ in range(50):
            if not is_process_running(pid):
                remove_pid_file()
                return
            time.sleep(0.1)

    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        try:
            os.kill(pid, 15)
        except OSError:
            pass

    for _ in range(20):
        if not is_process_running(pid):
            break
        time.sleep(0.1)
    if not is_process_running(pid):
        remove_pid_file()


def start_server() -> subprocess.Popen[bytes]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    sanitize_network_env(env)
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    ucrt64_bin = Path(r"C:\msys64\ucrt64\bin")
    if (ucrt64_bin / "g++.exe").is_file():
        env["PATH"] = str(ucrt64_bin) + os.pathsep + env.get("PATH", "")

    creationflags = 0
    if os.name == "nt":
        creationflags = (
            subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_NO_WINDOW
            | subprocess.DETACHED_PROCESS
        )

    out_log = OUT_LOG.open("ab")
    err_log = ERR_LOG.open("ab")
    try:
        return subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-m",
                "cf_workbench",
                "listen",
                "--host",
                HOST,
                "--port",
                str(PORT),
            ],
            cwd=ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=out_log,
            stderr=err_log,
            creationflags=creationflags,
        )
    finally:
        out_log.close()
        err_log.close()


def sanitize_network_env(env: dict[str, str]) -> None:
    for name in PROXY_ENV_VARS:
        env.pop(name, None)
    env["NO_PROXY"] = "localhost,127.0.0.1,::1"
    env["no_proxy"] = env["NO_PROXY"]


def open_workbench(url: str) -> bool:
    if os.name == "nt":
        chrome = find_chrome_executable()
        if chrome:
            try:
                subprocess.Popen(
                    chrome_open_args(chrome, url),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                return True
            except OSError:
                pass
    return bool(webbrowser.open(url))


def chrome_open_args(chrome: str, url: str) -> list[str]:
    return [
        chrome,
        "--new-tab",
        url,
    ]


def find_chrome_executable() -> str | None:
    if os.name == "nt":
        running = running_chrome_executable()
        if running:
            return running

    for candidate in chrome_executable_candidates():
        if candidate and Path(candidate).is_file():
            return str(candidate)
    which = shutil.which("chrome") or shutil.which("chrome.exe") or shutil.which("google-chrome")
    return which


def running_chrome_executable() -> str | None:
    powershell = shutil.which("powershell") or shutil.which("powershell.exe")
    if not powershell:
        return None
    command = (
        "$p = Get-CimInstance Win32_Process -Filter \"Name = 'chrome.exe'\" "
        "| Select-Object -First 1; if ($p) { $p.ExecutablePath }"
    )
    try:
        completed = subprocess.run(
            [powershell, "-NoProfile", "-Command", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    path = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else ""
    return path if path and Path(path).is_file() else None


def chrome_executable_candidates() -> list[Path]:
    candidates: list[Path] = []
    for env_name in ("LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)"):
        base = os.environ.get(env_name)
        if base:
            candidates.append(Path(base) / "Google" / "Chrome" / "Application" / "chrome.exe")
    return candidates


def write_pid_file(pid: int) -> None:
    for _ in range(10):
        try:
            PID_FILE.write_text(str(pid), encoding="ascii")
            return
        except PermissionError:
            time.sleep(0.1)
    PID_FILE.write_text(str(pid), encoding="ascii")


def remove_pid_file() -> None:
    for _ in range(10):
        try:
            PID_FILE.unlink(missing_ok=True)
            return
        except PermissionError:
            time.sleep(0.1)


def wait_for_server() -> bool:
    for _ in range(40):
        if is_cfw_server_running():
            return True
        time.sleep(0.25)
    return False


def request_server_shutdown() -> bool:
    try:
        request = urllib.request.Request(
            SHUTDOWN_URL,
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=1.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
        return False
    return bool(payload.get("ok") is True and payload.get("shuttingDown") is True)


def is_cfw_server_running() -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=1.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
        return False
    return bool(payload.get("ok") is True and payload.get("name") == "cf-workbench")


def is_process_running(pid: int) -> bool:
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
