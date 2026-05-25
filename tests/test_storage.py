import json

import pytest

from cf_workbench.storage import (
    create_folder,
    create_problem,
    delete_folder,
    delete_problem,
    rename_folder,
    rename_problem,
    resolve_problem_path,
    save_capture,
)


def test_storage_writes_plan_layout(tmp_path):
    template = tmp_path / "main.cpp"
    template.write_text("int main() { return 0; }\n", encoding="utf-8")
    payload = {
        "name": "G. Castle Defense",
        "url": "https://codeforces.com/problemset/problem/954/G",
        "tests": [{"input": "1", "output": "2"}],
    }

    stored = save_capture(payload, workspace=tmp_path / "cp", template_path=template)

    assert stored.path == tmp_path / "cp" / "codeforces" / "954G"
    assert (stored.path / "tests" / "sample_1.in").read_text(encoding="utf-8") == "1\n"
    assert (stored.path / "tests" / "sample_1.out").read_text(encoding="utf-8") == "2\n"
    assert (stored.path / ".cfw" / "build").is_dir()
    data = json.loads((stored.path / "problem.json").read_text(encoding="utf-8"))
    assert data["schemaVersion"] == 1
    assert data["tests"][0]["inputFile"] == "tests/sample_1.in"
    assert data["contestIncluded"] is False


def test_storage_does_not_overwrite_main_without_force(tmp_path):
    payload = {
        "name": "A. Example",
        "url": "https://codeforces.com/contest/1999/problem/A",
        "tests": [{"input": "", "output": ""}],
    }
    stored = save_capture(payload, workspace=tmp_path / "cp")
    (stored.path / "main.cpp").write_text("// user\n", encoding="utf-8")

    save_capture(payload, workspace=tmp_path / "cp")

    assert (stored.path / "main.cpp").read_text(encoding="utf-8") == "// user\n"


def test_contest_capture_is_stored_under_contest_folder(tmp_path):
    payload = {
        "name": "A. Example",
        "url": "https://codeforces.com/contest/1999/problem/A",
        "tests": [{"input": "1", "output": "1"}],
    }

    stored = save_capture(payload, workspace=tmp_path / "cp")

    assert stored.path == tmp_path / "cp" / "codeforces" / "contests" / "1999" / "1999A"
    assert resolve_problem_path(tmp_path / "cp", "1999A") == stored.path


def test_manual_problem_with_contest_url_is_stored_under_contest_folder(tmp_path):
    workspace = tmp_path / "cp"

    created = create_problem(
        workspace,
        "1999A",
        name="A. Manual",
        url="https://codeforces.com/contest/1999/problem/A",
    )

    assert created.path == workspace / "codeforces" / "contests" / "1999" / "1999A"


def test_create_and_delete_workspace_folder(tmp_path):
    workspace = tmp_path / "cp"

    folder = create_folder(workspace, "practice/dp")

    assert folder == workspace / "codeforces" / "practice" / "dp"
    assert folder.is_dir()

    deleted = delete_folder(workspace, "practice/dp")

    assert deleted == folder
    assert not folder.exists()


def test_rename_workspace_folder_moves_nested_problems(tmp_path):
    workspace = tmp_path / "cp"
    create_folder(workspace, "practice/dp")
    created = create_problem(workspace, "1999A", name="A. Manual", folder="practice/dp")

    renamed = rename_folder(workspace, "practice", "training")

    assert renamed == workspace / "codeforces" / "training"
    assert not (workspace / "codeforces" / "practice").exists()
    assert resolve_problem_path(workspace, "1999A") == workspace / "codeforces" / "training" / "dp" / "1999A"
    assert not created.path.exists()


def test_rename_problem_updates_display_name(tmp_path):
    workspace = tmp_path / "cp"
    created = create_problem(workspace, "1999A", name="Old name")

    data = rename_problem(workspace, "1999A", "New name")

    assert data["name"] == "New name"
    stored = json.loads((created.path / "problem.json").read_text(encoding="utf-8"))
    assert stored["name"] == "New name"


def test_folder_creation_rejects_parent_paths(tmp_path):
    with pytest.raises(ValueError):
        create_folder(tmp_path / "cp", "../outside")


def test_create_and_delete_manual_problem_in_folder(tmp_path):
    workspace = tmp_path / "cp"
    template = tmp_path / "main.cpp"
    template.write_text("int main() { return 0; }\n", encoding="utf-8")

    created = create_problem(
        workspace,
        "1999A",
        name="A. Manual",
        folder="practice",
        template_path=template,
    )

    assert created.path == workspace / "codeforces" / "practice" / "1999A"
    assert resolve_problem_path(workspace, "1999A") == created.path
    assert (created.path / "tests").is_dir()
    assert (created.path / ".cfw" / "build").is_dir()
    assert "int main()" in (created.path / "main.cpp").read_text(encoding="utf-8")
    data = json.loads((created.path / "problem.json").read_text(encoding="utf-8"))
    assert data["problemKey"] == "1999A"
    assert data["name"] == "A. Manual"
    assert data["tests"] == []
    assert data["contestIncluded"] is False

    deleted = delete_problem(workspace, "1999A")

    assert deleted == created.path
    assert not created.path.exists()
    assert (workspace / "codeforces" / "practice").is_dir()


def test_create_problem_rejects_duplicate_keys_across_folders(tmp_path):
    workspace = tmp_path / "cp"
    create_problem(workspace, "1999A", folder="one")

    with pytest.raises(FileExistsError):
        create_problem(workspace, "1999A", folder="two")


def test_folder_operations_do_not_target_problem_internals(tmp_path):
    workspace = tmp_path / "cp"
    create_problem(workspace, "1999A")

    with pytest.raises(ValueError):
        create_folder(workspace, "1999A/tests/custom")
    with pytest.raises(ValueError):
        delete_folder(workspace, "1999A/tests")
    with pytest.raises(ValueError):
        create_problem(workspace, "2000A", folder="1999A/tests")


def test_save_capture_reuses_existing_problem_folder(tmp_path):
    workspace = tmp_path / "cp"
    created = create_problem(workspace, "1999A", folder="practice")
    payload = {
        "name": "A. Example",
        "url": "https://codeforces.com/contest/1999/problem/A",
        "tests": [{"input": "1", "output": "1"}],
    }

    stored = save_capture(payload, workspace=workspace)

    assert stored.path == created.path
    assert (workspace / "codeforces" / "1999A").exists() is False
