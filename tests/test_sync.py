import json

from cf_workbench.storage import create_problem
from cf_workbench.sync import sync_solved_submissions


class FakeAPI:
    def user_status(self, handle, *, count=10):
        assert handle == "alice"
        assert count == 3
        return [
            {
                "id": 1002,
                "verdict": "OK",
                "programmingLanguage": "GNU C++17",
                "creationTimeSeconds": 1710000000,
                "timeConsumedMillis": 31,
                "memoryConsumedBytes": 102400,
                "problem": {"contestId": 1999, "index": "A", "name": "A. Example"},
            },
            {
                "id": 1001,
                "verdict": "WRONG_ANSWER",
                "problem": {"contestId": 1999, "index": "B", "name": "B. Example"},
            },
            {
                "id": 1000,
                "verdict": "OK",
                "programmingLanguage": "GNU C++17",
                "creationTimeSeconds": 1700000000,
                "problem": {"contestId": 1999, "index": "A", "name": "A. Example"},
            },
        ]


def test_sync_solved_writes_index_and_local_solution_snapshot(tmp_path):
    workspace = tmp_path / "cp"
    created = create_problem(workspace, "1999A", name="A. Example")
    (created.path / "main.cpp").write_text("// accepted locally\n", encoding="utf-8")

    result = sync_solved_submissions(FakeAPI(), handle="alice", workspace=workspace, count=3)

    assert result.fetched == 3
    assert result.accepted == 1
    assert result.local_updated == 1
    assert result.solution_snapshots == 1
    index = json.loads((workspace / "codeforces" / ".cfw" / "solved.json").read_text(encoding="utf-8"))
    assert index["handle"] == "alice"
    assert index["problems"][0]["problemKey"] == "1999A"
    problem = json.loads((created.path / "problem.json").read_text(encoding="utf-8"))
    assert problem["solved"]["submissionId"] == 1002
    assert (created.path / "solutions" / "1002.cpp").read_text(encoding="utf-8") == "// accepted locally\n"
