import cfw.schema


def test_cfw_package_alias_exposes_schema():
    parsed = cfw.schema.parse_codeforces_url("https://codeforces.com/contest/1999/problem/A")
    assert parsed.problem_key == "1999A"
