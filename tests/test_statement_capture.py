import json

from cf_workbench.statement_capture import sanitize_statement_html, save_statement_capture
from cf_workbench.storage import create_problem


def test_sanitize_statement_html_removes_scripts_and_event_handlers():
    html = (
        '<div class="problem-statement" onclick="bad()">'
        '<script>alert(1)</script>'
        '<p data-x="1">Hello</p>'
        '<a href="javascript:alert(1)">bad</a>'
        "</div>"
    )

    sanitized = sanitize_statement_html(html)

    assert "<script" not in sanitized
    assert "onclick" not in sanitized
    assert "javascript:" not in sanitized
    assert '<p data-x="1">Hello</p>' in sanitized


def test_sanitize_statement_html_keeps_mathjax_markup():
    html = (
        '<div class="problem-statement">'
        '<span class="MathJax_Preview">x &lt; y</span>'
        '<span class="MathJax" id="MathJax-Element-1-Frame"></span>'
        "</div>"
    )

    sanitized = sanitize_statement_html(html)

    assert "MathJax_Preview" in sanitized
    assert "x &lt; y" in sanitized
    assert "MathJax-Element-1-Frame" in sanitized


def test_save_statement_capture_creates_problem_when_samples_are_in_payload(tmp_path):
    template = tmp_path / "main.cpp"
    template.write_text("// template\n", encoding="utf-8")
    payload = {
        "url": "https://codeforces.com/contest/1999/problem/A",
        "problemName": "A. Example",
        "timeLimitMs": 1000,
        "memoryLimitMb": 256,
        "html": '<div class="problem-statement"><div class="title">A. Example</div></div>',
        "text": "A. Example",
        "tests": [{"input": "1", "output": "2"}],
    }

    stored = save_statement_capture(
        payload,
        workspace=tmp_path / "workspace",
        template_path=template,
    )

    assert stored.problem_key == "1999A"
    assert stored.created_problem is True
    assert (stored.path / "statement.html").read_text(encoding="utf-8").startswith(
        '<div class="problem-statement">'
    )
    assert (stored.path / "tests" / "sample_1.in").read_text(encoding="utf-8") == "1\n"
    data = json.loads((stored.path / "problem.json").read_text(encoding="utf-8"))
    assert data["statementCapture"]["kind"] == "browser-dom"
    assert data["statementCapture"]["htmlFile"] == "statement.html"


def test_save_statement_capture_recovers_sample_line_breaks_from_html(tmp_path):
    html = (
        '<div class="problem-statement">'
        '<div class="sample-test">'
        '<div class="input"><div class="title">Input</div><pre>'
        '<div class="test-example-line">5</div>'
        '<div class="test-example-line">3 10 8 6 11</div>'
        '<div class="test-example-line">4</div>'
        '<div class="test-example-line">1</div>'
        '<div class="test-example-line">10</div>'
        '<div class="test-example-line">3</div>'
        '<div class="test-example-line">11 </div>'
        '</pre></div>'
        '<div class="output"><div class="title">Output</div><pre>'
        '<div class="test-example-line">1</div>'
        '<div class="test-example-line">2</div>'
        '<div class="test-example-line">5</div>'
        '</pre></div>'
        '</div>'
        '</div>'
    )
    payload = {
        "url": "https://codeforces.com/contest/1999/problem/A",
        "problemName": "A. Example",
        "html": html,
        "text": "A. Example",
        "tests": [{"input": "53 10 8 6 114110311", "output": "125"}],
    }

    stored = save_statement_capture(payload, workspace=tmp_path / "workspace")

    assert (stored.path / "tests" / "sample_1.in").read_text(encoding="utf-8") == (
        "5\n"
        "3 10 8 6 11\n"
        "4\n"
        "1\n"
        "10\n"
        "3\n"
        "11 \n"
    )
    assert (stored.path / "tests" / "sample_1.out").read_text(encoding="utf-8") == "1\n2\n5\n"


def test_save_statement_capture_updates_existing_problem_without_overwriting_source(tmp_path):
    first = {
        "url": "https://codeforces.com/contest/1999/problem/A",
        "problemName": "A. Example",
        "html": '<div class="problem-statement">first</div>',
        "text": "first",
        "tests": [{"input": "1", "output": "2"}],
    }
    stored = save_statement_capture(first, workspace=tmp_path / "workspace")
    (stored.path / "main.cpp").write_text("// user solution\n", encoding="utf-8")

    second = {
        "url": "https://codeforces.com/contest/1999/problem/A",
        "problemName": "A. Example",
        "html": '<div class="problem-statement">second</div>',
        "text": "second",
        "tests": [{"input": "3", "output": "4"}],
    }
    save_statement_capture(second, workspace=tmp_path / "workspace")

    assert (stored.path / "main.cpp").read_text(encoding="utf-8") == "// user solution\n"
    assert "second" in (stored.path / "statement.html").read_text(encoding="utf-8")
    assert (stored.path / "tests" / "sample_1.in").read_text(encoding="utf-8") == "1\n"


def test_save_statement_capture_reuses_problem_inside_folder(tmp_path):
    workspace = tmp_path / "workspace"
    created = create_problem(workspace, "1999A", folder="practice")
    payload = {
        "url": "https://codeforces.com/contest/1999/problem/A",
        "problemName": "A. Example",
        "html": '<div class="problem-statement">statement</div>',
        "text": "statement",
        "tests": [{"input": "1", "output": "2"}],
    }

    stored = save_statement_capture(payload, workspace=workspace)

    assert stored.path == created.path
    assert not (workspace / "codeforces" / "1999A").exists()
