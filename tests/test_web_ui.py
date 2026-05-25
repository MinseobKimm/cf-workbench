import json
from queue import Queue

import pytest

from cf_workbench.companion_server import CompetitiveCompanionHandler
from cf_workbench.storage import create_folder, create_problem, save_capture
from cf_workbench.web_ui import render_index


def test_render_index_contains_ide_entry_points():
    html = render_index()
    assert "cf-workbench" in html
    assert 'data-view-target="code"' in html
    assert 'data-view-target="account"' in html
    assert 'data-view-target="stats"' in html
    assert 'data-view-target="settings"' in html
    assert "/api/account" in html
    assert "/api/settings" in html
    assert "/api/stats" in html
    assert "openStatsProblem" in html
    assert "/api/problems" in html
    assert "textarea" in html
    assert "Run" in html
    assert ">Contest</button>" in html
    assert 'lang="en"' in html
    assert "Problem" in html
    assert "statementPane" in html
    assert "editorPane" in html
    assert "font-variant-ligatures: none" in html
    assert '"liga" 0, "calt" 0' in html
    assert 'id="codeLineNumbers"' in html
    assert ".code-line-numbers" in html
    assert "--code-gutter-width" in html
    assert ".code-highlight {\n      overflow: hidden;\n      color: #d8deea;\n      padding-bottom: 72px;" in html
    assert ".code-highlight span {\n      font: inherit;" in html
    assert "font-feature-settings: inherit;\n      letter-spacing: inherit;" in html
    assert "line-height: inherit;\n      margin: 0;\n      padding: 0;\n      border: 0;" in html
    assert "textarea.code {\n      resize: none;\n      border: 0;\n      background: transparent;\n      color: transparent;" in html
    assert "font-kerning: none" in html
    assert "font-synthesis: none" in html
    assert "--code-line-height: 22px" in html
    assert "text-rendering: geometricPrecision" in html
    assert "word-spacing: 0" in html
    assert "renderRatingHistoryTable" in html
    assert "Actual change" in html
    assert "word-break: normal" in html
    assert "overflow-wrap: normal" in html
    assert "textarea.code::selection {\n      background: rgba(134, 168, 255, 0.38);\n      color: transparent;" in html
    assert "function normalizeEditorText" in html
    assert 'replace(/\\t/g, "    ")' in html
    assert "normalizeCodeValueTabs(code)" in html
    assert "padding-bottom: 72px" in html
    assert ".tok-keyword { color: #7dd3fc; }" in html
    assert ".tok-comment { color: #7c8aa5; }" in html
    assert "font-weight: 700; }\n    .tok-type" not in html
    assert ".tok-comment { color: #7c8aa5; font-style: italic; }" not in html
    assert "layer.innerHTML = editorHighlightHtml(code.value, cppMode, code.selectionStart, code.selectionEnd)" in html
    assert "function editorHighlightHtml" in html
    assert ".tok-bracket-match" in html
    assert ".tok-bracket-unmatched" in html
    assert ".tok-bracket {\n      border-radius: 3px;\n      padding" not in html
    assert "function analyzeEditorBrackets" in html
    assert "function collectEditorBracketTokens" in html
    assert "function activeEditorBracketIndex" in html
    assert "function highlightBracketSegment" in html
    assert 'marks.set(index, "unmatched")' in html
    assert 'marks.set(active, "match")' in html
    assert 'marks.set(pair, "match")' in html
    assert 'if (value.endsWith("\\n")) html += " "' in html
    assert "scheduleCodeHighlightUpdate" in html
    assert "scheduleEnsureCodeCaretVisible" in html
    assert "ensureCodeCaretVisible" in html
    assert "captureCodeViewport" in html
    assert "restoreCodeViewportAfterLayout" in html
    assert "saveFromCodeShortcut" in html
    assert "saveFromCodeShortcut().catch" in html
    assert "event.stopPropagation()" in html
    assert "measureCodeCaretBox" in html
    assert "measuredCodeLineHeight" in html
    assert "measureCodeCharacterWidth" in html
    assert "--code-font-size" in html
    assert "updateCodeLineNumbers" in html
    assert "countCodeLines" in html
    assert "codeLineNumberText" in html
    assert "updateCodeGutterWidth" in html
    assert "countNewlinesBefore" in html
    assert 'if (event.key === "Tab")' in html
    assert 'handleTabKey(event.shiftKey)' in html
    assert 'if (event.key === "}" && handleClosingBraceKey(event))' in html
    assert "function handleClosingBraceKey" in html
    assert "function matchingOpeningBraceIndent" in html
    assert "function lineIndentAt" in html
    assert "function nextWhitespaceOnlyClosingBrace" in html
    assert "DRAFT_SAVE_DELAY_MS" in html
    assert "PROBLEM_REFRESH_INTERVAL_MS" not in html
    assert "SOLVED_SYNC_INTERVAL_MS" not in html
    assert "scheduleEditorDraftSave(state.sourceBuffer)" in html
    assert "function refreshProblemsRoutine" not in html
    assert "function shouldRoutineSyncSolved" not in html
    assert "markSolvedSyncAttempt" not in html
    assert "state.problemRefreshInFlight" not in html
    assert "loadProblems({ routine: true })" not in html
    assert "function problemListSignature" not in html
    assert "setInterval(() => refreshProblemsRoutine()" not in html
    assert "selectProblem(latest.problemKey, { preserveEditorTab: true, sourceName: currentSourceName() })" in html
    assert "restoreCodeViewportAfterLayout(previousViewport)" in html
    assert "folder-head" in html
    assert "renderProblemFolders" in html
    assert "groupByContest" in html
    assert "contestModeToggle" in html
    assert "toggleProblemSidebar" in html
    assert "toggleResultsSidebar" in html
    assert 'LEFT_SIDEBAR_COLLAPSED_STORAGE_KEY = "cfw.leftSidebarCollapsed"' in html
    assert 'RIGHT_SIDEBAR_COLLAPSED_STORAGE_KEY = "cfw.rightSidebarCollapsed"' in html
    assert "applySidebarCollapseState" in html
    assert "CONTEST_MODE_STORAGE_KEY" in html
    assert "CONTEST_MODE_PROBLEMS_STORAGE_KEY" not in html
    assert "applyContestModeDefaults" in html
    assert "isContestIncludedProblem" in html
    assert "setProblemContestIncluded" in html
    assert "sameContestProblemKeys" in html
    assert "contestKeyForProblem" in html
    assert "contestIncluded" in html
    assert "recentlyLoadedProblemKeys: new Set()" in html
    assert "renderRecentlyLoadedRoot" in html
    assert "workspaceTree + recentlyLoadedTree + templateTree" in html
    assert 'key = "root:recently-loaded"' in html
    assert "state.recentlyLoadedProblemKeys.add(key)" in html
    assert "resetRecentlyLoaded" in html
    assert "toggleContestMode" in html
    assert "REQUIRED_CONTEST_INDEXES" not in html
    assert "hasRequiredContestIndexes" not in html
    assert "contestProblemIndex" not in html
    assert "contestLabel" in html
    assert "contestFolderLabel" in html
    assert "Codeforces\\s*-\\s*" in html
    assert '${codeforcesRound[1] ? "Beta Round" : "Round"}' in html
    assert "Educational Round ${educationalRound[1]}" in html
    assert "compareDifficultyFolders" in html
    assert 'key: "root:difficulty", sort: compareDifficultyFolders' in html
    assert "return right - left" in html
    assert "rootContest" in html
    assert "renderProblemTestCards" in html
    assert "case-part" in html
    assert "sample-grid" in html
    assert "standard payload does not include the full statement" in html
    assert "statementFrame" in html
    assert "buildCapturedStatementDoc" in html
    assert 'new EventSource("/api/events")' in html
    assert "statement-captured" in html
    assert "refreshCurrentProblemWithoutEditor" in html
    assert "trans" + "lationPanel" not in html
    assert "trans" + "lateAndSave" not in html
    assert ".MathJax_Preview" in html
    assert ".MathJax_Processing" in html
    assert ".MJXp-math" in html
    assert ".problem-statement .tex-span" in html
    assert 'font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif;' in html
    assert "font-size: 1.18em" in html
    assert "data-cfw-math-snapshot" in html
    assert ".problem-statement .MathJax:not([data-cfw-math-snapshot])" in html
    assert ".problem-statement .MJXp-math:not([data-cfw-math-snapshot])" in html
    assert ".problem-statement .MJXp-script:not([data-cfw-math-snapshot])" in html
    assert "font-family: inherit !important;" not in html
    assert "font-size: inherit !important;" not in html
    assert "prepareCapturedStatementFragment" in html
    assert "cleanupCapturedMath" in html
    assert "texToInlineMathText" not in html
    assert "renderStatementText" in html
    assert "renderStatementMath" in html
    assert "statement-math" in html
    assert "renderMathMlTokens" in html
    assert "<msub>" in html
    assert "<mfrac>" in html
    assert "background: #f5fbfa;" not in html
    assert ".MJX_Assistive_MathML" in html
    assert "cleanupCapturedMath(root)" in html
    assert "escapeHtml(paragraph)" not in html
    assert "ensureProblemTranslation" not in html
    assert "/trans" + "lation" not in html
    assert "/api/folders" in html
    assert "createProblemFromPrompt" in html
    assert "deleteCurrentProblem" in html
    assert "deleteProblemByKey" in html
    assert "renameProblemFromPrompt" in html
    assert 'data-context-kind="problem"' in html
    assert "state.problems = state.problems.filter((problem) => problem.problemKey !== key)" in html
    assert "deleteFolder" in html
    assert "renameFolderFromPrompt" in html
    assert "removeDeletedFolderFromState" in html
    assert "folderContainsPath" in html
    assert "handleOutputContextMenu" in html
    assert "renameTestByIndex" in html
    assert "deleteTestByIndex" in html
    assert "Submit" in html
    assert "submitCurrentProblem" in html
    assert "Local tests failed. Open submit page anyway?" in html
    assert "renderSubmitLink" in html
    assert "Open Codeforces submit" in html
    assert "Click submit link" in html
    assert "renderRunError" in html
    assert "renderCompileError" in html
    assert "Compiler stderr" in html
    assert "Runtime error (exit code" in html
    assert "Time limit exceeded" in html
    assert 'window.open("", "_blank")' not in html
    assert "submit-prefill" in html
    assert "/api/templates" in html
    assert "renderTemplateRoot" in html
    assert '<details class="folder-root" open>' not in html
    assert "data-details-key" in html
    assert '<details class="folder" data-details-key=' in html
    assert 'key = "root:templates"' in html
    assert "nestedFolderKey" in html
    assert "itemsWithUnclassifiedLast" in html
    assert "folderEntriesWithUnclassifiedLast" in html
    assert "isUnclassifiedFolder" in html
    assert "loadOpenDetails" in html
    assert 'SIDEBAR_ORDER_STORAGE_KEY = "cfw.sidebarOrder.v1"' in html
    assert "loadSidebarOrder" in html
    assert "saveSidebarOrder" in html
    assert "setupSidebarDragAndDrop" in html
    assert "handleSidebarDragStart" in html
    assert "handleSidebarDragOver" in html
    assert "reorderSidebarItem" in html
    assert "sidebar-drop-before" in html
    assert "sidebar-drop-after" in html
    assert "sidebar-draggable-row" in html
    assert 'data-drag-type="problem"' in html
    assert 'data-drag-type="folder"' in html
    assert "setDetailsOpen" in html
    assert "detailsOpenAttr" in html
    assert 'DETAILS_STORAGE_KEY = "cfw.openDetails.v2"' in html
    assert "defaultDetailsOpen" in html
    assert "createTemplateFromPrompt" in html
    assert 'body: JSON.stringify({ kind: "template", algorithm, name, source: "", extension: ".cpp" })' in html
    assert 'await selectTemplate(algorithm.trim(), name.trim())' in html
    assert "New template ready" in html
    assert "Template source" not in html
    assert "selectTemplate" in html
    assert "saveTemplateSource" in html
    assert "deleteTemplate" in html
    assert "deleteTemplateAlgorithm" in html
    assert "renameTemplateFromPrompt" in html
    assert "renameTemplateAlgorithmFromPrompt" in html
    assert "removeDeletedTemplateFromState" in html
    assert "removeDeletedTemplateAlgorithmFromState" in html
    assert "deleteTemplate(state.currentTemplate.algorithm, state.currentTemplate.name)" in html
    assert 'id="contextMenu"' in html
    assert "handleSidebarContextMenu" in html
    assert "/api/templates?kind=template" in html
    assert "/api/templates?kind=algorithm" in html
    assert "AUTO_SAVE_DELAY_MS" in html
    assert "EDITOR_DRAFTS_STORAGE_KEY" in html
    assert "LAST_EDITOR_DOCUMENT_STORAGE_KEY" in html
    assert "scheduleAutoSave" in html
    assert "saveEditorDraft" in html
    assert "restoreLastEditorDocument" in html
    assert "preserveDirtyEditorForUnload" in html
    assert "keepaliveSaveCurrentEditor" in html
    assert "sendBeacon" in html
    assert "saveDirtyEditorBeforeSwitch" in html
    assert "expectedDocumentId" in html
    assert "Autosaved" in html
    assert "Unsaved changes will be discarded" not in html
    assert "copyEditorSource" in html
    assert 'id="deleteProblem"' not in html
    assert 'id="editorTabs"' in html
    assert "renderEditorTabs" in html
    assert "selectEditorTab" in html
    assert "resetEditorTabs(source)" in html
    assert "closeEditorTab" not in html
    assert "Edit template" in html
    assert "Copy" in html
    assert 'window.addEventListener("resize"' in html
    assert 'document.fonts.addEventListener("loadingdone"' in html
    assert "createSourceFromTemplate" not in html
    assert "Create source file from template" not in html
    assert "Replace current source" not in html
    assert "createSourceFileFromPrompt" in html
    assert "deleteSourceFile" in html
    assert "sourceName: currentSourceName()" in html
    assert "data-add-source" in html
    assert "Source file name" not in html


def test_statement_payload_uses_optional_extra_statement_fields(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)

    payload = {
        "extra": {
            "statement": {"text": "Solve the described task."},
            "inputSpecification": "The first line contains n.",
            "outputSpecification": {"plainText": "Print the answer."},
        }
    }

    sections = handler._statement_payload(tmp_path, payload)["sections"]

    assert sections == [
        {"title": "Statement", "text": "Solve the described task."},
        {"title": "Input", "text": "The first line contains n."},
        {"title": "Output", "text": "Print the answer."},
    ]


def test_problem_summary_exposes_group_for_folder_tree(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)

    summary = handler._problem_summary(
        tmp_path,
        {
            "problemKey": "1999A",
            "name": "A. Example",
            "group": "Codeforces Round",
            "url": "https://codeforces.com/contest/1999/problem/A",
            "tests": [{"name": "sample_1"}],
        },
    )

    assert summary["group"] == "Codeforces Round"
    assert summary["contest"]["key"] == "1999"
    assert summary["contest"]["label"] == "1999 - Codeforces Round"
    assert summary["contestIncluded"] is False


def test_problem_summary_exposes_contest_inclusion_flag(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)

    summary = handler._problem_summary(
        tmp_path,
        {
            "problemKey": "1999A",
            "name": "A. Example",
            "contestId": 1999,
            "index": "A",
            "url": "https://codeforces.com/contest/1999/problem/A",
            "tests": [],
            "contestIncluded": True,
        },
    )

    assert summary["contestIncluded"] is True


def test_set_problem_contest_included_persists_to_problem_json(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    (tmp_path / "problem.json").write_text(
        '{"problemKey":"1999A","name":"A. Example","tests":[]}\n',
        encoding="utf-8",
    )

    data = handler._set_problem_contest_included(tmp_path, True)

    stored = json.loads((tmp_path / "problem.json").read_text(encoding="utf-8"))
    assert data["contestIncluded"] is True
    assert stored["contestIncluded"] is True


def test_problem_summary_exposes_gym_contest(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)

    summary = handler._problem_summary(
        tmp_path,
        {
            "problemKey": "gym-104000A",
            "contestId": 104000,
            "index": "A",
            "name": "A. Gym Example",
            "url": "https://codeforces.com/gym/104000/problem/A",
            "tests": [],
        },
    )

    assert summary["contest"]["key"] == "gym-104000"
    assert summary["contest"]["label"] == "Gym 104000"


def test_problem_list_exposes_real_workspace_folders(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    handler._codeforces_problem_metadata = lambda: {}
    create_folder(handler.workspace, "practice")
    problem = create_problem(handler.workspace, "1999A", name="A. Example", folder="practice")

    listing = handler._api_problem_list()

    assert listing["folders"][0]["name"] == "practice"
    assert listing["folders"][0]["problems"] == 1
    assert listing["problems"][0]["problemKey"] == "1999A"
    assert listing["problems"][0]["folder"] == "practice"
    assert listing["problems"][0]["path"] == str(problem.path)


def test_problem_source_versions_can_be_created_selected_and_deleted(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    handler._codeforces_problem_metadata = lambda: {}
    handler.template_path = tmp_path / "template.cpp"
    handler.template_path.write_text("// bare template\n", encoding="utf-8")
    created = create_problem(handler.workspace, "1999A", name="A. Example", template_path=handler.template_path)

    payload = handler._create_problem_source(created.path, "")

    assert payload["sourceName"] == "main2.cpp"
    assert payload["source"] == "// bare template\n"
    assert (created.path / "main2.cpp").read_text(encoding="utf-8") == "// bare template\n"

    payload = handler._create_problem_source(created.path, "alt")

    assert payload["sourceName"] == "alt.cpp"
    assert payload["source"] == "// bare template\n"
    assert (created.path / "alt.cpp").read_text(encoding="utf-8") == "// bare template\n"
    detail = handler._api_problem_detail("1999A", source_name="alt.cpp")
    assert detail["sourceName"] == "alt.cpp"
    assert detail["source"] == "// bare template\n"
    assert [item["name"] for item in detail["problem"]["sourceFiles"]] == ["main.cpp", "main2.cpp", "alt.cpp"]

    deleted = handler._delete_problem_source(created.path, "alt.cpp")

    assert deleted["deletedSourceName"] == "alt.cpp"
    assert deleted["sourceName"] == "main.cpp"
    assert not (created.path / "alt.cpp").exists()
    handler._delete_problem_source(created.path, "main2.cpp")
    with pytest.raises(ValueError, match="only source file"):
        handler._delete_problem_source(created.path, "main.cpp")


def test_static_asset_path_escape_is_rejected():
    handler = object.__new__(CompetitiveCompanionHandler)
    captured = {}

    def fake_send_json(status, payload):
        captured["status"] = status
        captured["payload"] = payload

    handler._send_json = fake_send_json

    handler._send_static_asset("../pyproject.toml")

    assert captured["status"].value == 404
    assert captured["payload"]["error"] == "asset not found"


def test_problem_list_can_sync_solved_from_configured_handle(tmp_path, monkeypatch):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    handler.api_min_interval_seconds = 0.0
    handler.codeforces_handle = "alice"
    handler.codeforces_api_key = "key"
    handler.codeforces_api_secret = "secret"
    handler.solved_sync_limit = 7
    handler._codeforces_problem_metadata = lambda: {}
    create_problem(handler.workspace, "1999A", name="A. Example")
    calls = {}

    class FakeAPI:
        def __init__(self, **kwargs):
            calls["kwargs"] = kwargs

        def user_status(self, handle, *, count=10):
            calls["handle"] = handle
            calls["count"] = count
            return [
                {
                    "id": 1002,
                    "verdict": "OK",
                    "problem": {"contestId": 1999, "index": "A", "name": "A. Example"},
                }
            ]

    monkeypatch.setattr("cf_workbench.companion_server.CodeforcesAPI", FakeAPI)

    listing = handler._api_problem_list(sync_solved=True)

    assert calls == {
        "kwargs": {"min_interval_seconds": 0.0, "api_key": "key", "api_secret": "secret"},
        "handle": "alice",
        "count": 7,
    }
    assert listing["solvedSync"]["ok"] is True
    assert listing["solvedSync"]["localUpdated"] == 1
    assert listing["problems"][0]["solved"]["submissionId"] == 1002


def test_problem_list_solved_sync_skips_without_handle(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    handler._codeforces_problem_metadata = lambda: {}
    create_problem(handler.workspace, "1999A", name="A. Example")

    listing = handler._api_problem_list(sync_solved=True)

    assert listing["solvedSync"]["skipped"] is True
    assert listing["problems"][0]["solved"] is None


def test_problem_list_excludes_contest_storage_from_user_folders(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    handler._codeforces_problem_metadata = lambda: {}
    save_capture(
        {
            "name": "A. Example",
            "url": "https://codeforces.com/contest/1999/problem/A",
            "tests": [{"input": "1", "output": "1"}],
        },
        workspace=handler.workspace,
    )

    listing = handler._api_problem_list()

    assert listing["folders"] == []
    assert listing["problems"][0]["contest"]["key"] == "1999"


def test_account_api_aggregates_profile_rating_and_submissions(tmp_path, monkeypatch):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    handler.api_min_interval_seconds = 0.0
    handler.codeforces_handle = "alice"
    handler.codeforces_api_key = None
    handler.codeforces_api_secret = None
    handler.solved_sync_limit = 2

    class FakeAPI:
        def __init__(self, **kwargs):
            pass

        def user_info(self, handle):
            assert handle == "alice"
            return [{"handle": "alice", "rating": 1234, "rank": "pupil"}]

        def user_rating(self, handle):
            assert handle == "alice"
            return [{"contestId": 1, "oldRating": 1000, "newRating": 1234}]

        def user_status(self, handle, *, count=10):
            assert handle == "alice"
            assert count == 2
            return [
                {
                    "id": 11,
                    "verdict": "OK",
                    "programmingLanguage": "GNU C++17",
                    "problem": {"contestId": 1999, "index": "A", "name": "A. Example"},
                },
                {
                    "id": 10,
                    "verdict": "WRONG_ANSWER",
                    "programmingLanguage": "GNU C++17",
                    "problem": {"contestId": 1999, "index": "B", "name": "B. Example"},
                },
            ]

    monkeypatch.setattr("cf_workbench.companion_server.CodeforcesAPI", FakeAPI)

    account = handler._api_account()

    assert account["configured"] is True
    assert account["profile"]["handle"] == "alice"
    assert account["profile"]["rating"] == 1234
    assert account["ratingHistory"][0]["oldRating"] == 1000
    assert account["ratingHistory"][0]["newRating"] == 1234
    assert account["ratingHistory"][0]["ratingChange"] == 234
    assert account["ratingHistory"][0]["earlyContestBonus"] == 500
    assert account["ratingHistory"][0]["actualRatingChange"] == -266
    assert account["submissionSummary"]["acceptedProblems"] == 1
    assert account["submissionSummary"]["attemptedProblems"] == 2
    assert account["recentSubmissions"][0]["problem"]["problemKey"] == "1999A"


def test_account_api_applies_early_contest_bonuses_to_rating_change_only(tmp_path, monkeypatch):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    handler.api_min_interval_seconds = 0.0
    handler.codeforces_handle = "alice"
    handler.codeforces_api_key = None
    handler.codeforces_api_secret = None
    handler.solved_sync_limit = 1

    class FakeAPI:
        def __init__(self, **kwargs):
            pass

        def user_info(self, handle):
            return [{"handle": handle, "rating": 1300, "maxRating": 1300}]

        def user_rating(self, handle):
            return [
                {"contestId": 1, "oldRating": 0, "newRating": 100},
                {"contestId": 2, "oldRating": 100, "newRating": 300},
                {"contestId": 3, "oldRating": 300, "newRating": 500},
                {"contestId": 4, "oldRating": 500, "newRating": 700},
                {"contestId": 5, "oldRating": 700, "newRating": 900},
                {"contestId": 6, "oldRating": 900, "newRating": 1100},
                {"contestId": 7, "oldRating": 1100, "newRating": 1300},
            ]

        def user_status(self, handle, *, count=10):
            return []

    monkeypatch.setattr("cf_workbench.companion_server.CodeforcesAPI", FakeAPI)

    account = handler._api_account()
    history = account["ratingHistory"]

    assert [item["earlyContestBonus"] for item in history] == [500, 350, 250, 150, 100, 50, 0]
    assert [item["ratingChange"] for item in history] == [100, 200, 200, 200, 200, 200, 200]
    assert [item["actualRatingChange"] for item in history] == [-400, -150, -50, 50, 100, 150, 200]
    assert [item["newRating"] for item in history] == [100, 300, 500, 700, 900, 1100, 1300]
    assert history[1]["oldRating"] == 100
    assert history[6]["oldRating"] == 1100
    assert account["profile"]["rating"] == 1300
    assert account["profile"]["maxRating"] == 1300


def test_stats_api_reads_solved_index_and_marks_local_problems(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    handler.codeforces_handle = "alice"
    handler._codeforces_problem_metadata = lambda: {
        "1999A": {"rating": 800, "tags": ["implementation"]},
        "1999B": {"rating": 900, "tags": ["math"]},
    }
    create_problem(handler.workspace, "1999A", name="A. Local")
    solved_path = handler.workspace / "codeforces" / ".cfw" / "solved.json"
    solved_path.parent.mkdir(parents=True)
    solved_path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "handle": "alice",
                "syncedAt": "2026-04-30T00:00:00Z",
                "problems": [
                    {"problemKey": "1999A", "contestId": 1999, "index": "A", "name": "A. Example"},
                    {"problemKey": "1999B", "contestId": 1999, "index": "B", "name": "B. Example"},
                ],
            }
        ),
        encoding="utf-8",
    )

    stats = handler._api_stats()

    assert stats["solvedCount"] == 2
    by_key = {problem["problemKey"]: problem for problem in stats["problems"]}
    assert by_key["1999A"]["local"] is True
    assert by_key["1999A"]["rating"] == 800
    assert by_key["1999B"]["local"] is False
    assert by_key["1999B"]["url"] == "https://codeforces.com/problemset/problem/1999/B"


def test_delete_problem_test_removes_files_and_metadata(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    stored = save_capture(
        {
            "name": "A. Example",
            "url": "https://codeforces.com/contest/1999/problem/A",
            "tests": [{"input": "1", "output": "2"}],
        },
        workspace=handler.workspace,
    )

    deleted = handler._delete_problem_test(stored.path, "1")

    assert deleted["deletedFiles"] == ["tests/sample_1.in", "tests/sample_1.out"]
    assert not (stored.path / "tests" / "sample_1.in").exists()
    assert not (stored.path / "tests" / "sample_1.out").exists()
    assert '"tests": []' in (stored.path / "problem.json").read_text(encoding="utf-8")


def test_delete_problem_test_keeps_metadata_change_when_file_delete_fails(tmp_path, monkeypatch):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    stored = save_capture(
        {
            "name": "A. Example",
            "url": "https://codeforces.com/contest/1999/problem/A",
            "tests": [{"input": "1", "output": "2"}],
        },
        workspace=handler.workspace,
    )

    def fail_unlink(self):
        raise PermissionError("locked")

    monkeypatch.setattr("pathlib.Path.unlink", fail_unlink)

    deleted = handler._delete_problem_test(stored.path, "1")

    assert deleted["deletedFiles"] == []
    assert deleted["deleteErrors"]
    assert '"tests": []' in (stored.path / "problem.json").read_text(encoding="utf-8")


def test_rename_problem_test_moves_files_and_metadata(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"
    stored = save_capture(
        {
            "name": "A. Example",
            "url": "https://codeforces.com/contest/1999/problem/A",
            "tests": [{"input": "1", "output": "2"}],
        },
        workspace=handler.workspace,
    )

    renamed = handler._rename_problem_test(stored.path, "1", "edge case")

    assert renamed["name"] == "edge-case"
    assert renamed["inputFile"] == "tests/edge-case.in"
    assert renamed["outputFile"] == "tests/edge-case.out"
    assert not (stored.path / "tests" / "sample_1.in").exists()
    assert not (stored.path / "tests" / "sample_1.out").exists()
    assert (stored.path / "tests" / "edge-case.in").read_text(encoding="utf-8") == "1\n"
    assert (stored.path / "tests" / "edge-case.out").read_text(encoding="utf-8") == "2\n"
    data = json.loads((stored.path / "problem.json").read_text(encoding="utf-8"))
    assert data["tests"][0]["name"] == "edge-case"
    assert data["tests"][0]["inputFile"] == "tests/edge-case.in"
    assert data["tests"][0]["outputFile"] == "tests/edge-case.out"


def test_apply_problem_metadata_updates_problem_json(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    problem_json = tmp_path / "problem.json"
    problem_json.write_text(
        '{"problemKey":"112A","name":"A. Petya and Strings","tests":[]}\n',
        encoding="utf-8",
    )
    data = {"problemKey": "112A", "name": "A. Petya and Strings", "tests": []}

    handler._apply_problem_metadata(
        tmp_path,
        data,
        {"112A": {"rating": 800, "tags": ["implementation", "strings"]}},
    )

    assert data["rating"] == 800
    assert data["tags"] == ["implementation", "strings"]
    assert '"rating": 800' in problem_json.read_text(encoding="utf-8")


def test_statement_payload_reads_captured_dom_files(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    (tmp_path / "statement.html").write_text('<div class="problem-statement">Hello</div>', encoding="utf-8")
    (tmp_path / "statement.txt").write_text("Hello", encoding="utf-8")

    payload = {
        "statementCapture": {
            "kind": "browser-dom",
            "capturedAt": "2026-04-29T00:00:00Z",
            "url": "https://codeforces.com/contest/1999/problem/A",
            "htmlFile": "statement.html",
            "textFile": "statement.txt",
        }
    }

    statement = handler._statement_payload(tmp_path, payload)

    assert statement["capture"]["html"] == '<div class="problem-statement">Hello</div>'
    assert statement["capture"]["text"] == "Hello"


def test_problem_events_are_broadcast_to_ui_subscribers(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    events = Queue()
    CompetitiveCompanionHandler.ui_event_queues = []
    CompetitiveCompanionHandler._add_ui_event_queue(events)
    try:
        handler._broadcast_problem_event("statement-captured", "1999A", tmp_path / "1999A")
        event = events.get_nowait()
    finally:
        CompetitiveCompanionHandler._remove_ui_event_queue(events)

    assert event["type"] == "statement-captured"
    assert event["problemKey"] == "1999A"
    assert event["path"] == str(tmp_path / "1999A")


def test_account_config_save_records_codeforces_handle(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setattr("pathlib.Path.home", lambda: home)
    monkeypatch.setattr(CompetitiveCompanionHandler, "codeforces_handle", None)
    monkeypatch.setattr(CompetitiveCompanionHandler, "codeforces_api_key", None)
    monkeypatch.setattr(CompetitiveCompanionHandler, "codeforces_api_secret", None)
    handler = object.__new__(CompetitiveCompanionHandler)

    payload = handler._save_account_config({"handle": "alice", "apiKey": "key", "apiSecret": "secret"})

    assert payload["handle"] == "alice"
    assert payload["auth"]["apiKeyConfigured"] is True
    assert CompetitiveCompanionHandler.codeforces_handle == "alice"
    saved = json.loads((home / ".cfw" / "config.json").read_text(encoding="utf-8"))
    assert saved["codeforces"]["handle"] == "alice"


def test_account_config_save_preserves_configured_api_values(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setattr("pathlib.Path.home", lambda: home)
    monkeypatch.setattr(CompetitiveCompanionHandler, "codeforces_handle", "alice")
    monkeypatch.setattr(CompetitiveCompanionHandler, "codeforces_api_key", "existing-key")
    monkeypatch.setattr(CompetitiveCompanionHandler, "codeforces_api_secret", "existing-secret")
    handler = object.__new__(CompetitiveCompanionHandler)

    payload = handler._save_account_config({"handle": "alice", "apiKey": "", "apiSecret": ""})

    saved = json.loads((home / ".cfw" / "config.json").read_text(encoding="utf-8"))
    assert payload["auth"]["apiKeyConfigured"] is True
    assert payload["auth"]["apiSecretConfigured"] is True
    assert CompetitiveCompanionHandler.codeforces_api_key == "existing-key"
    assert CompetitiveCompanionHandler.codeforces_api_secret == "existing-secret"
    assert saved["codeforces"]["apiKey"] == "existing-key"
    assert saved["codeforces"]["apiSecret"] == "existing-secret"


def test_settings_config_save_records_ui_language(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setattr("pathlib.Path.home", lambda: home)
    monkeypatch.setattr(CompetitiveCompanionHandler, "ui_language", "en")
    handler = object.__new__(CompetitiveCompanionHandler)

    payload = handler._save_settings_config({"uiLanguage": "ko"})

    saved = json.loads((home / ".cfw" / "config.json").read_text(encoding="utf-8"))
    assert payload["uiLanguage"] == "ko"
    assert CompetitiveCompanionHandler.ui_language == "ko"
    assert saved["uiLanguage"] == "ko"


def test_problem_payload_has_no_language_conversion_helpers(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)

    assert not hasattr(handler, "_save_" + "trans" + "lation")
    assert not hasattr(handler, "_trans" + "lation_" + "payload")


def test_template_payload_round_trips_from_workspace_cfw_dir(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"

    handler._save_template_algorithm("graph")
    handler._save_template("graph", "dijkstra", "// dijkstra\n", extension=".cpp")
    templates = handler._api_template_list()["templates"]

    assert templates[0]["name"] == "graph"
    assert templates[0]["templates"][0]["name"] == "dijkstra"
    assert templates[0]["templates"][0]["source"] == "// dijkstra\n"
    assert (handler.workspace / "codeforces" / ".cfw" / "templates.json").is_file()


def test_saving_template_updates_one_existing_template_file(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"

    handler._save_template("graph", "dijkstra", "// first\n", extension=".cpp")
    handler._save_template("graph", "dijkstra", "// second\n", extension=".cpp")
    template_dir = handler.workspace / "codeforces" / ".cfw" / "templates" / "graph"
    files = list(template_dir.glob("*.cpp"))

    assert files == [template_dir / "dijkstra.cpp"]
    assert files[0].read_text(encoding="utf-8") == "// second\n"


def test_renaming_template_moves_file_and_index_entry(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"

    handler._save_template("graph", "dijkstra", "// dijkstra\n", extension=".cpp")
    result = handler._rename_template("graph", "dijkstra", "shortest-path")
    template_dir = handler.workspace / "codeforces" / ".cfw" / "templates" / "graph"

    assert result["template"]["name"] == "shortest-path"
    assert result["template"]["file"] == "templates/graph/shortest-path.cpp"
    assert not (template_dir / "dijkstra.cpp").exists()
    assert (template_dir / "shortest-path.cpp").read_text(encoding="utf-8") == "// dijkstra\n"
    assert handler._api_template_list()["templates"][0]["templates"][0]["name"] == "shortest-path"


def test_renaming_template_algorithm_moves_folder_and_index_entry(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"

    handler._save_template("graph", "dijkstra", "// dijkstra\n", extension=".cpp")
    result = handler._rename_template_algorithm("graph", "shortest")
    template_root = handler.workspace / "codeforces" / ".cfw" / "templates"

    assert result["templates"][0]["name"] == "shortest"
    assert result["templates"][0]["templates"][0]["file"] == "templates/shortest/dijkstra.cpp"
    assert not (template_root / "graph").exists()
    assert (template_root / "shortest" / "dijkstra.cpp").is_file()


def test_deleting_one_template_removes_file_and_index_entry(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"

    handler._save_template("graph", "dijkstra", "// dijkstra\n", extension=".cpp")
    handler._save_template("graph", "dfs", "// dfs\n", extension=".cpp")
    result = handler._delete_template("graph", "dijkstra")
    template_dir = handler.workspace / "codeforces" / ".cfw" / "templates" / "graph"

    assert [item["name"] for item in result["templates"][0]["templates"]] == ["dfs"]
    assert not (template_dir / "dijkstra.cpp").exists()
    assert (template_dir / "dfs.cpp").is_file()
    assert handler._api_template_list()["templates"][0]["templates"][0]["name"] == "dfs"


def test_deleting_last_template_removes_algorithm_entry(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"

    handler._save_template("graph", "dijkstra", "// dijkstra\n", extension=".cpp")
    result = handler._delete_template("graph", "dijkstra")

    template_root = handler.workspace / "codeforces" / ".cfw" / "templates"
    assert result["templates"] == []
    assert not (template_root / "graph" / "dijkstra.cpp").exists()
    assert handler._api_template_list()["templates"] == []


def test_deleting_template_algorithm_removes_files_and_index_entry(tmp_path):
    handler = object.__new__(CompetitiveCompanionHandler)
    handler.workspace = tmp_path / "workspace"
    handler.judge_subdir = "codeforces"

    handler._save_template("graph", "dijkstra", "// dijkstra\n", extension=".cpp")
    handler._save_template("dp", "knapsack", "// knapsack\n", extension=".cpp")
    result = handler._delete_template_algorithm("graph")
    template_root = handler.workspace / "codeforces" / ".cfw" / "templates"

    assert [algorithm["name"] for algorithm in result["templates"]] == ["dp"]
    assert not (template_root / "graph" / "dijkstra.cpp").exists()
    assert (template_root / "dp" / "knapsack.cpp").is_file()
    assert [algorithm["name"] for algorithm in handler._api_template_list()["templates"]] == ["dp"]
