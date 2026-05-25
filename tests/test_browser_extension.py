import json
from pathlib import Path


def test_content_script_stabilizes_mathjax_before_capture():
    source = Path("browser-extension/content-script.js").read_text(encoding="utf-8")

    assert "statementHtmlForWorkbench(statement)" in source
    assert "snapshotMathStyles" in source
    assert "absolutizeResourceUrls" in source
    assert "copyMathComputedStyle" in source
    assert "data-cfw-math-snapshot" in source
    assert "cleanupMathMarkup" in source
    assert 'querySelectorAll(".test-example-line")' in source
    assert "pre.innerText || pre.textContent" in source
    assert '".MathJax_Processing"' in source
    assert "node.remove()" in source
    assert "cfw-math-inline" not in source
    assert "texToInlineText" not in source
    assert "waitForStatementReady(silent ? 5000 : 15000)" in source


def test_content_script_stays_codeforces_only():
    manifest = json.loads(Path("browser-extension/manifest.json").read_text(encoding="utf-8"))
    matches = manifest["content_scripts"][0]["matches"]

    assert matches
    assert all(match.startswith("https://codeforces.com/") for match in matches)
