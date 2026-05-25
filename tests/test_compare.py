from cf_workbench.compare import compare_outputs


def test_exact_normalizes_crlf_only():
    assert compare_outputs("a\r\nb\n", "a\nb\n", mode="exact").ok
    assert not compare_outputs("a\n", "a\n\n", mode="exact").ok


def test_trim_ignores_trailing_line_space_and_final_blank_lines():
    assert compare_outputs("1  \n2\n\n", "1\n2\n", mode="trim").ok


def test_tokens_default_ignores_whitespace_layout():
    assert compare_outputs("1 2\n3", "1\n2 3\n").ok
