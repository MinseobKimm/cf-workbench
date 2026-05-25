from cf_workbench.diffing import compact_diff, outputs_match


def test_normalized_compare_trims_trailing_spaces_and_final_newlines():
    assert outputs_match("1 2  \n3\n\n", "1 2\n3")


def test_normalized_compare_does_not_ignore_arbitrary_whitespace():
    assert not outputs_match("1 2\n", "1    2\n")


def test_token_compare_ignores_token_spacing():
    assert outputs_match("1 2\n3", "1    2 3\n", tokens=True)


def test_compact_diff_mentions_expected_and_actual():
    diff = compact_diff("1\n", "2\n")
    assert "--- expected" in diff
    assert "+++ actual" in diff
