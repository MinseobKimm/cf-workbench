from __future__ import annotations

import json
import os
import platform
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_DIR = ".cfw"
CONFIG_FILE = "config.json"


@dataclass
class Config:
    root: Path
    workspace: Path
    template: Path
    compiler: str | None = None
    language: str = "cpp17"
    api_min_interval_seconds: float = 2.2
    port: int = 27121
    judge_subdir: str = "codeforces"
    compare_mode: str = "tokens"
    timeout_margin_seconds: float = 1.0
    codeforces_handle: str | None = None
    codeforces_api_key: str | None = None
    codeforces_api_secret: str | None = None
    ide_clangd: str | None = None
    ui_language: str = "en"


def find_config_file(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    home_roots = _home_roots()
    for candidate in [current, *current.parents]:
        if candidate in home_roots:
            continue
        config_path = candidate / CONFIG_DIR / CONFIG_FILE
        if config_path.is_file():
            return config_path
    return None


def default_config(root: Path | None = None) -> Config:
    base = (root or Path.cwd()).resolve()
    return Config(
        root=base,
        workspace=default_workspace(),
        template=base / CONFIG_DIR / "templates" / "main.cpp",
        compiler=_recommended_compiler() or "g++",
    )


def load_config(start: Path | None = None) -> Config:
    config_path = find_config_file(start)
    user_data = _read_json_file(user_config_file())
    if config_path is None:
        config = default_config(start or Path.cwd())
        _apply_default_settings(config, user_data)
        _apply_codeforces_credentials(config, user_data)
        return config

    root = config_path.parent.parent
    with config_path.open("r", encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)

    compiler_value = data.get("compiler")
    if isinstance(compiler_value, dict):
        compiler = compiler_value.get("cxx")
        standard = str(compiler_value.get("standard", "gnu++17"))
    else:
        compiler = compiler_value
        standard = str(data.get("language", "cpp17"))

    workspace_value = data.get("workspaceRoot", data.get("workspace", str(default_workspace())))
    runner = data.get("runner") if isinstance(data.get("runner"), dict) else {}
    ide = data.get("ide") if isinstance(data.get("ide"), dict) else {}

    config = Config(
        root=root,
        workspace=_resolve(root, workspace_value),
        template=_resolve(root, data.get("template", f"{CONFIG_DIR}/templates/main.cpp")),
        compiler=str(compiler) if compiler else None,
        language=standard,
        api_min_interval_seconds=float(data.get("api_min_interval_seconds", 2.2)),
        port=int(data.get("port", 27121)),
        judge_subdir=str(data.get("judgeSubdir", "codeforces")),
        compare_mode=str(runner.get("compareMode", data.get("compareMode", "tokens"))),
        timeout_margin_seconds=float(runner.get("timeoutMarginSeconds", 1.0)),
        ide_clangd=_env_or_value("CFW_CLANGD", ide.get("clangd")),
        ui_language=_ui_language(data.get("uiLanguage", user_data.get("uiLanguage", "en"))),
    )
    _apply_codeforces_credentials(config, user_data, project_data=data)
    return config


def init_project(root: Path | None = None) -> Config:
    config = default_config(root)
    cfw_dir = config.root / CONFIG_DIR
    templates_dir = cfw_dir / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    (config.workspace / "codeforces").mkdir(parents=True, exist_ok=True)

    if not config.template.exists():
        shutil.copyfile(package_template_file(), config.template)

    config_path = cfw_dir / CONFIG_FILE
    if not config_path.exists():
        data = {
            "workspace": "workspace",
            "template": f"{CONFIG_DIR}/templates/main.cpp",
            "compiler": _recommended_compiler(),
            "language": "cpp17",
            "api_min_interval_seconds": 2.2,
            "uiLanguage": "en",
        }
        with config_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
    return load_config(config.root)


def ensure_runtime_files(config: Config) -> Config:
    config.workspace.mkdir(parents=True, exist_ok=True)
    (config.workspace / config.judge_subdir).mkdir(parents=True, exist_ok=True)
    if not config.template.exists():
        config.template.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(package_template_file(), config.template)
    return config


def user_config_file() -> Path:
    return Path.home() / CONFIG_DIR / CONFIG_FILE


def _home_roots() -> set[Path]:
    roots: set[Path] = set()
    for value in (str(Path.home()), os.path.expanduser("~"), os.environ.get("USERPROFILE"), os.environ.get("HOME")):
        if value:
            try:
                roots.add(Path(value).resolve())
            except OSError:
                continue
    return roots


def init_user_config(*, force: bool = False) -> Path:
    config_path = user_config_file()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists() and not force:
        return config_path
    compiler = _recommended_compiler() or "g++"
    data = {
        "workspaceRoot": str(default_workspace()),
        "judgeSubdir": "codeforces",
        "port": 27121,
        "compiler": {
            "cxx": compiler,
            "standard": "gnu++17",
            "flags": ["-O2", "-Wall", "-Wextra", "-Wshadow"],
        },
        "runner": {
            "compareMode": "tokens",
            "timeoutMarginSeconds": 1.0,
        },
        "uiLanguage": "en",
    }
    with config_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    return config_path


def save_codeforces_credentials(
    *,
    handle: str,
    api_key: str | None = None,
    api_secret: str | None = None,
    config_path: Path | None = None,
) -> Path:
    if not handle.strip():
        raise ValueError("Codeforces handle is required")
    path = config_path or user_config_file()
    data = _read_json_file(path)
    codeforces = data.get("codeforces") if isinstance(data.get("codeforces"), dict) else {}
    codeforces["handle"] = handle.strip()
    if api_key is not None:
        codeforces["apiKey"] = api_key.strip()
    if api_secret is not None:
        codeforces["apiSecret"] = api_secret.strip()
    data["codeforces"] = codeforces
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle_file:
        json.dump(data, handle_file, indent=2)
        handle_file.write("\n")
    return path


def save_ui_settings(
    *,
    ui_language: str,
    config_path: Path | None = None,
) -> Path:
    language = _ui_language(ui_language)
    path = config_path or user_config_file()
    data = _read_json_file(path)
    data["uiLanguage"] = language
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle_file:
        json.dump(data, handle_file, indent=2)
        handle_file.write("\n")
    return path


def default_workspace() -> Path:
    if platform.system() == "Windows":
        return Path(r"C:\CP")
    return Path.home() / "cp-workspace"


def _resolve(root: Path, value: Any) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    return (root / path).resolve()


def _recommended_compiler() -> str | None:
    msys2 = Path(r"C:\msys64\ucrt64\bin\g++.exe")
    if msys2.exists():
        return str(msys2)
    return None


def package_template_file() -> Path:
    return Path(__file__).parent / "templates" / "main.cpp"


def _apply_default_settings(config: Config, data: dict[str, Any]) -> None:
    if not data:
        return
    workspace_value = data.get("workspaceRoot", data.get("workspace"))
    if workspace_value:
        config.workspace = _resolve(config.root, workspace_value)
    template_value = data.get("template")
    if template_value:
        config.template = _resolve(config.root, template_value)

    compiler_value = data.get("compiler")
    if isinstance(compiler_value, dict):
        compiler = compiler_value.get("cxx")
        if compiler:
            config.compiler = str(compiler)
        standard = compiler_value.get("standard")
        if standard:
            config.language = str(standard)
    elif compiler_value:
        config.compiler = str(compiler_value)

    if data.get("language"):
        config.language = str(data["language"])
    if data.get("api_min_interval_seconds") is not None:
        config.api_min_interval_seconds = float(data["api_min_interval_seconds"])
    if data.get("port") is not None:
        config.port = int(data["port"])
    if data.get("judgeSubdir"):
        config.judge_subdir = str(data["judgeSubdir"])

    runner = data.get("runner") if isinstance(data.get("runner"), dict) else {}
    if runner.get("compareMode") or data.get("compareMode"):
        config.compare_mode = str(runner.get("compareMode", data.get("compareMode")))
    if runner.get("timeoutMarginSeconds") is not None:
        config.timeout_margin_seconds = float(runner["timeoutMarginSeconds"])

    ide = data.get("ide") if isinstance(data.get("ide"), dict) else {}
    config.ide_clangd = _env_or_value("CFW_CLANGD", ide.get("clangd"))
    config.ui_language = _ui_language(data.get("uiLanguage", config.ui_language))


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _apply_codeforces_credentials(
    config: Config,
    user_data: dict[str, Any],
    *,
    project_data: dict[str, Any] | None = None,
) -> None:
    merged: dict[str, Any] = {}
    user_cf = user_data.get("codeforces")
    project_cf = (project_data or {}).get("codeforces")
    if isinstance(user_cf, dict):
        merged.update(user_cf)
    if isinstance(project_cf, dict):
        merged.update(project_cf)

    config.codeforces_handle = _env_or_value("CFW_CODEFORCES_HANDLE", merged.get("handle"))
    config.codeforces_api_key = _env_or_value("CFW_CODEFORCES_API_KEY", merged.get("apiKey"))
    config.codeforces_api_secret = _env_or_value("CFW_CODEFORCES_API_SECRET", merged.get("apiSecret"))


def _ui_language(value: Any) -> str:
    text = str(value or "en").strip().lower()
    return "ko" if text in {"ko", "kr", "korean", "한국어"} else "en"


def _env_or_value(name: str, value: Any) -> str | None:
    env_value = os.environ.get(name)
    if env_value is not None and env_value.strip():
        return env_value.strip()
    if value is None:
        return None
    text = str(value).strip()
    return text or None
