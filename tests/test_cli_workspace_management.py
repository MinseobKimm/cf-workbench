from cf_workbench.cli import main


def test_cli_creates_and_deletes_folder_and_problem(tmp_path):
    workspace = tmp_path / "workspace"

    assert main(["folder", "create", "practice", "--workspace", str(workspace)]) == 0
    assert (
        main(
            [
                "problem",
                "create",
                "1999A",
                "--name",
                "A. Example",
                "--folder",
                "practice",
                "--workspace",
                str(workspace),
            ]
        )
        == 0
    )

    problem_dir = workspace / "codeforces" / "practice" / "1999A"
    assert (problem_dir / "problem.json").is_file()
    assert (problem_dir / "main.cpp").is_file()

    assert main(["problem", "delete", "1999A", "--workspace", str(workspace), "--yes"]) == 0
    assert main(["folder", "delete", "practice", "--workspace", str(workspace), "--yes"]) == 0
    assert not (workspace / "codeforces" / "practice").exists()
