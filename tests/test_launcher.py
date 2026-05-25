import importlib.util
from pathlib import Path


def load_launcher_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "cfw_workbench_launcher.py"
    spec = importlib.util.spec_from_file_location("cfw_workbench_launcher", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_launcher_sanitizes_dead_proxy_environment():
    launcher = load_launcher_module()
    env = {
        "HTTP_PROXY": "http://127.0.0.1:9",
        "HTTPS_PROXY": "http://127.0.0.1:9",
        "ALL_PROXY": "http://127.0.0.1:9",
        "PATH": "C:\\Windows",
    }

    launcher.sanitize_network_env(env)

    assert "HTTP_PROXY" not in env
    assert "HTTPS_PROXY" not in env
    assert "ALL_PROXY" not in env
    assert env["NO_PROXY"] == "localhost,127.0.0.1,::1"
    assert env["no_proxy"] == env["NO_PROXY"]
    assert env["PATH"] == "C:\\Windows"


def test_launcher_opens_chrome_new_tab(monkeypatch):
    launcher = load_launcher_module()
    calls = {}

    monkeypatch.setattr(launcher.os, "name", "nt")
    monkeypatch.setattr(launcher, "find_chrome_executable", lambda: "C:\\Chrome\\chrome.exe")

    def fake_popen(args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs

    monkeypatch.setattr(launcher.subprocess, "Popen", fake_popen)

    assert launcher.open_workbench("http://127.0.0.1:27121/") is True

    assert calls["args"] == [
        "C:\\Chrome\\chrome.exe",
        "--new-tab",
        "http://127.0.0.1:27121/",
    ]
    assert calls["kwargs"]["stdin"] is launcher.subprocess.DEVNULL
    assert calls["kwargs"]["creationflags"] == getattr(launcher.subprocess, "CREATE_NO_WINDOW", 0)


def test_launcher_falls_back_to_webbrowser_when_chrome_launch_fails(monkeypatch):
    launcher = load_launcher_module()
    calls = {}

    monkeypatch.setattr(launcher.os, "name", "nt")
    monkeypatch.setattr(launcher, "find_chrome_executable", lambda: "C:\\Chrome\\chrome.exe")

    def fail_popen(*args, **kwargs):
        raise OSError("no chrome")

    monkeypatch.setattr(launcher.subprocess, "Popen", fail_popen)
    monkeypatch.setattr(launcher.webbrowser, "open", lambda url: calls.setdefault("url", url) or True)

    assert launcher.open_workbench("http://127.0.0.1:27121/") is True
    assert calls["url"] == "http://127.0.0.1:27121/"
