from datetime import datetime, timezone

from cf_workbench.schema import normalize_companion_payload, parse_codeforces_url


def _payload(url: str, **overrides):
    data = {
        "name": "G. Castle Defense",
        "group": "Codeforces Round",
        "url": url,
        "timeLimit": 1500,
        "memoryLimit": 256,
        "tests": [{"input": "1", "output": "2"}],
    }
    data.update(overrides)
    return data


def test_problemset_url_normalization():
    problem = normalize_companion_payload(
        _payload("https://codeforces.com/problemset/problem/954/G"),
        captured_at=datetime(2026, 4, 29, tzinfo=timezone.utc),
    )
    assert problem.problem_key == "954G"
    assert problem.contest_id == 954
    assert problem.index == "G"
    assert problem.samples[0].input.endswith("\n")
    assert problem.to_problem_json()["source"]["capturedAt"] == "2026-04-29T00:00:00Z"


def test_contest_gym_and_group_urls():
    assert parse_codeforces_url("https://codeforces.com/contest/1999/problem/A").problem_key == "1999A"
    assert parse_codeforces_url("https://codeforces.com/gym/104000/problem/B").problem_key == "gym-104000B"
    group = parse_codeforces_url("https://codeforces.com/group/abc123/contest/777/problem/C")
    assert group.problem_key == "777C"
    assert group.group_code == "abc123"


def test_missing_optional_interactive_defaults_false():
    problem = normalize_companion_payload(_payload("https://codeforces.com/contest/1999/problem/A"))
    assert problem.interactive is False


def test_unknown_url_fallback_key():
    problem = normalize_companion_payload(_payload("https://example.com/problem/foo"))
    assert problem.problem_key.startswith("unknown-g-castle-defense-")
