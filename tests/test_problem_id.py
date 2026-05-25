from cf_workbench.paths import parse_codeforces_problem_url


def test_parse_contest_problem_url():
    parsed = parse_codeforces_problem_url("https://codeforces.com/contest/1999/problem/A")
    assert parsed is not None
    assert parsed.source == "contest"
    assert parsed.contest_id == "1999"
    assert parsed.index == "A"
    assert parsed.cf_tool_label == "1999A"


def test_parse_problemset_problem_url():
    parsed = parse_codeforces_problem_url("https://codeforces.com/problemset/problem/1999/A")
    assert parsed is not None
    assert parsed.source == "problemset"
    assert parsed.contest_id == "1999"
    assert parsed.index == "A"


def test_parse_gym_problem_url():
    parsed = parse_codeforces_problem_url("https://codeforces.com/gym/104000/problem/B")
    assert parsed is not None
    assert parsed.source == "gym"
    assert parsed.contest_id == "104000"
    assert parsed.index == "B"
