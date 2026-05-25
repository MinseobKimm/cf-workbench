from pathlib import Path
from urllib.request import urlopen

from cf_workbench.models import Problem, ProblemTest
from cf_workbench.submit import (
    build_cf_tool_command,
    build_manual_submit_url,
    build_submit_plan,
    build_submit_url_from_problem_json,
)
from cf_workbench.submit_prefill import (
    SubmitPrefillServer,
    build_submit_prefill_payload,
    build_submit_prefill_url,
    prefill_fetch_url,
)


def test_build_cf_tool_command_includes_problem_label():
    command = build_cf_tool_command(
        "cf",
        "https://codeforces.com/contest/1999/problem/A",
        Path("main.cpp"),
    )
    assert command == ["cf", "submit", "-f", "main.cpp", "1999A"]


def test_build_submit_plan_without_cf_tool_does_not_submit(tmp_path):
    problem = Problem(
        name="A. Example",
        url="https://codeforces.com/contest/1999/problem/A",
        tests=[ProblemTest(input="", output="")],
    )
    plan = build_submit_plan(
        problem,
        tmp_path,
        cf_tool_executable=None,
    )
    assert plan.command is None
    assert plan.manual_submit_url == "https://codeforces.com/contest/1999/submit"
    assert plan.solution_path == (tmp_path / "main.cpp").resolve()


def test_build_manual_submit_url_for_problemset():
    assert (
        build_manual_submit_url("https://codeforces.com/problemset/problem/1999/A")
        == "https://codeforces.com/problemset/submit"
    )


def test_build_manual_submit_url_for_group_and_gym():
    assert (
        build_manual_submit_url("https://codeforces.com/group/abc123/contest/777/problem/C")
        == "https://codeforces.com/group/abc123/contest/777/submit"
    )
    assert (
        build_manual_submit_url("https://codeforces.com/gym/104000/problem/B")
        == "https://codeforces.com/gym/104000/submit"
    )


def test_build_submit_url_from_problem_json_prefers_source_url_kind():
    assert (
        build_submit_url_from_problem_json(
            {
                "problemKey": "104000A",
                "contestId": 104000,
                "url": "https://codeforces.com/gym/104000/problem/A",
            }
        )
        == "https://codeforces.com/gym/104000/submit"
    )
    assert (
        build_submit_url_from_problem_json(
            {
                "problemKey": "777C",
                "contestId": 777,
                "url": "https://codeforces.com/group/abc123/contest/777/problem/C",
            }
        )
        == "https://codeforces.com/group/abc123/contest/777/submit"
    )
    assert (
        build_submit_url_from_problem_json(
            {
                "problemKey": "1999A",
                "contestId": 1999,
                "url": "https://codeforces.com/problemset/problem/1999/A",
            }
        )
        == "https://codeforces.com/problemset/submit"
    )


def test_build_submit_prefill_payload_reads_source_and_normalizes_problem_key(tmp_path):
    source_path = tmp_path / "main.cpp"
    source_path.write_text("int main() { return 0; }\n", encoding="utf-8")

    payload = build_submit_prefill_payload(
        {"url": "https://codeforces.com/problemset/problem/1999/A"},
        problem_key="A",
        source_path=source_path,
        language="cpp17",
        submit_url="https://codeforces.com/problemset/submit",
    )

    assert payload["problemKey"] == "1999A"
    assert payload["contestId"] == "1999"
    assert payload["problemIndex"] == "A"
    assert payload["source"] == "int main() { return 0; }\n"
    assert payload["language"] == "cpp17"
    assert payload["submitUrl"] == "https://codeforces.com/problemset/submit"


def test_build_submit_prefill_url_uses_fragment_token():
    url = build_submit_prefill_url(
        "https://codeforces.com/problemset/submit",
        port=12345,
        token="abc",
    )
    assert url == "https://codeforces.com/problemset/submit#cfw-submit=1&cfw-port=12345&cfw-token=abc"


def test_submit_prefill_server_serves_payload_with_token():
    server = SubmitPrefillServer({"source": "code", "language": "cpp17"})
    server.start()
    try:
        with urlopen(prefill_fetch_url(server.port, server.token), timeout=5) as response:
            body = response.read().decode("utf-8")
    finally:
        server.close()

    assert '"ok": true' in body
    assert '"source": "code"' in body
    assert server.wait_until_delivered(0)
