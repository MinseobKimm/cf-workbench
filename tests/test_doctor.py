from cf_workbench.config import Config
from cf_workbench.doctor import CheckResult, format_doctor_results, run_doctor


def test_format_doctor_results_aligns_statuses():
    output = format_doctor_results(
        [
            CheckResult("compiler", "OK", "g++"),
            CheckResult("Codeforces API", "SKIP", "offline"),
        ]
    )

    assert "OK   compiler" in output
    assert "SKIP Codeforces API" in output


def test_run_doctor_offline_skips_api(tmp_path, monkeypatch):
    template = tmp_path / "template.cpp"
    template.write_text("", encoding="utf-8")
    config = Config(
        root=tmp_path,
        workspace=tmp_path / "workspace",
        template=template,
        compiler=None,
    )

    compiler = type("Compiler", (), {"path": "g++", "warning": None})()
    monkeypatch.setattr("cf_workbench.doctor.detect_compiler", lambda configured: compiler)
    monkeypatch.setattr("cf_workbench.doctor.find_cf_tool", lambda: None)

    results = run_doctor(config, online=False)

    assert any(result.name == "Codeforces API" and result.status == "SKIP" for result in results)
    assert any(result.name == "cf-tool" and result.status == "WARN" for result in results)
