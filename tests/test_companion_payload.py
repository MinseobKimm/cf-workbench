import json

from cf_workbench.companion_server import save_problem_from_payload


def test_save_companion_payload_creates_problem_files(tmp_path):
    template = tmp_path / "template.cpp"
    template.write_text("// template\n", encoding="utf-8")
    payload = {
        "name": "A. Example Problem",
        "group": "Codeforces Round",
        "url": "https://codeforces.com/contest/1999/problem/A",
        "interactive": False,
        "memoryLimit": 256,
        "timeLimit": 1000,
        "tests": [
            {"input": "1\n", "output": "1\n"},
            {"input": "2\n", "output": "2\n"},
        ],
        "unknownField": {"keep": True},
    }

    saved = save_problem_from_payload(
        payload,
        workspace=tmp_path / "workspace",
        template_path=template,
    )

    assert saved == tmp_path / "workspace" / "codeforces" / "1999" / "A"
    assert (saved / "main.cpp").read_text(encoding="utf-8") == "// template\n"
    assert (saved / "tests" / "1.in").read_text(encoding="utf-8") == "1\n"
    assert (saved / "tests" / "2.ans").read_text(encoding="utf-8") == "2\n"

    data = json.loads((saved / "problem.json").read_text(encoding="utf-8"))
    assert data["unknownField"] == {"keep": True}
    assert data["name"] == "A. Example Problem"


def test_save_payload_does_not_overwrite_existing_solution(tmp_path):
    payload = {
        "name": "A. Example Problem",
        "url": "https://codeforces.com/contest/1999/problem/A",
        "tests": [{"input": "", "output": ""}],
    }
    saved = save_problem_from_payload(payload, workspace=tmp_path / "workspace")
    (saved / "main.cpp").write_text("// user solution\n", encoding="utf-8")

    save_problem_from_payload(payload, workspace=tmp_path / "workspace")

    assert (saved / "main.cpp").read_text(encoding="utf-8") == "// user solution\n"
