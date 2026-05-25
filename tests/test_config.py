import json

from cf_workbench.config import Config, ensure_runtime_files, load_config, save_codeforces_credentials, save_ui_settings


def test_codeforces_credentials_merge_from_user_config_with_project_config(tmp_path, monkeypatch):
    home = tmp_path / "home"
    project = tmp_path / "project"
    (project / ".cfw").mkdir(parents=True)
    (project / ".cfw" / "config.json").write_text(
        json.dumps({"workspace": "workspace", "template": ".cfw/templates/main.cpp"}),
        encoding="utf-8",
    )
    monkeypatch.setattr("pathlib.Path.home", lambda: home)

    save_codeforces_credentials(handle="alice", api_key="key", api_secret="secret")
    config = load_config(project)

    assert config.workspace == project / "workspace"
    assert config.codeforces_handle == "alice"
    assert config.codeforces_api_key == "key"
    assert config.codeforces_api_secret == "secret"


def test_ide_clangd_path_loads_from_project_config(tmp_path, monkeypatch):
    home = tmp_path / "home"
    project = tmp_path / "project"
    (project / ".cfw").mkdir(parents=True)
    (project / ".cfw" / "config.json").write_text(
        json.dumps(
            {
                "workspace": "workspace",
                "template": ".cfw/templates/main.cpp",
                "ide": {"clangd": "C:\\Program Files\\LLVM\\bin\\clangd.exe"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("pathlib.Path.home", lambda: home)

    config = load_config(project)

    assert config.ide_clangd == "C:\\Program Files\\LLVM\\bin\\clangd.exe"


def test_ensure_runtime_files_creates_template_and_workspace(tmp_path):
    config = Config(
        root=tmp_path,
        workspace=tmp_path / "workspace",
        template=tmp_path / ".cfw" / "templates" / "main.cpp",
    )

    ensure_runtime_files(config)

    assert (tmp_path / "workspace" / "codeforces").is_dir()
    assert config.template.is_file()
    assert "#include" in config.template.read_text(encoding="utf-8")


def test_load_config_without_project_keeps_root_at_current_folder(tmp_path, monkeypatch):
    home = tmp_path / "home"
    project = tmp_path / "downloaded"
    project.mkdir()
    (home / ".cfw").mkdir(parents=True)
    (home / ".cfw" / "config.json").write_text(
        json.dumps(
            {
                "workspaceRoot": "workspace",
                "template": ".cfw/templates/main.cpp",
                "codeforces": {"handle": "alice"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("pathlib.Path.home", lambda: home)

    config = load_config(project)

    assert config.root == project
    assert config.workspace == project / "workspace"
    assert config.template == project / ".cfw" / "templates" / "main.cpp"
    assert config.codeforces_handle == "alice"


def test_ui_language_defaults_to_english(tmp_path, monkeypatch):
    home = tmp_path / "home"
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setattr("pathlib.Path.home", lambda: home)

    config = load_config(project)

    assert config.ui_language == "en"


def test_ui_language_loads_from_user_config(tmp_path, monkeypatch):
    home = tmp_path / "home"
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setattr("pathlib.Path.home", lambda: home)

    save_ui_settings(ui_language="ko")
    config = load_config(project)

    assert config.ui_language == "ko"
