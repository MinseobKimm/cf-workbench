from __future__ import annotations


def render_index() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>cf-workbench</title>
  <link rel="stylesheet" href="/static/ide/cf-workbench-ide-assets.css">
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --panel-2: #f1f4f8;
      --line: #d7dde7;
      --line-strong: #aeb8c7;
      --text: #17202f;
      --muted: #657286;
      --accent: #0f766e;
      --accent-2: #2563eb;
      --danger: #b42318;
      --warn: #a15c07;
      --ok: #137333;
      --shadow: 0 10px 28px rgba(23, 32, 47, 0.08);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      height: 100vh;
      overflow: hidden;
    }
    button, input, select, textarea {
      font: inherit;
    }
    button {
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      height: 34px;
      padding: 0 11px;
      border-radius: 6px;
      cursor: pointer;
    }
    button:hover { border-color: var(--line-strong); background: #f9fafc; }
    button:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }
    button.primary {
      background: var(--accent);
      border-color: var(--accent);
      color: white;
    }
    button.blue {
      background: var(--accent-2);
      border-color: var(--accent-2);
      color: white;
    }
    button.danger {
      color: var(--danger);
      border-color: #e8aaa4;
    }
    button.danger:hover {
      background: #fff4f2;
      border-color: var(--danger);
    }
    button.icon {
      width: 34px;
      padding: 0;
      display: inline-grid;
      place-items: center;
    }
    button.sidebar-toggle {
      flex: 0 0 auto;
      font-weight: 800;
      line-height: 1;
    }
    .app {
      --problem-width: 340px;
      --statement-width: 420px;
      --tests-width: 380px;
      --left-sidebar-width: var(--problem-width);
      --right-sidebar-width: var(--tests-width);
      --side-resizer-width: 6px;
      --results-resizer-width: 6px;
      display: grid;
      grid-template-columns: var(--left-sidebar-width) var(--side-resizer-width) minmax(860px, 1fr) var(--results-resizer-width) var(--right-sidebar-width);
      grid-template-rows: 48px minmax(0, 1fr);
      height: 100vh;
    }
    .app.left-sidebar-collapsed {
      --left-sidebar-width: 42px;
      --side-resizer-width: 0px;
    }
    .app.right-sidebar-collapsed {
      --right-sidebar-width: 42px;
      --results-resizer-width: 0px;
    }
    header {
      grid-column: 1 / -1;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 0 14px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    .brand {
      display: flex;
      align-items: baseline;
      gap: 10px;
      min-width: 0;
    }
    .brand strong {
      font-size: 15px;
      letter-spacing: 0;
    }
    .brand span, .status {
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }
    .top-menu {
      display: flex;
      align-items: center;
      gap: 4px;
      min-width: 0;
      margin-right: auto;
    }
    .menu-tab {
      height: 32px;
      min-width: 76px;
      border-color: transparent;
      background: transparent;
      font-weight: 700;
      color: var(--muted);
    }
    .menu-tab.active {
      color: var(--text);
      border-color: var(--line);
      background: var(--panel-2);
    }
    .header-tools {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }
    .toolbar {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }
    .app:not([data-view="code"]) .code-toolbar {
      display: none;
    }
    select, input {
      height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 0 9px;
      background: white;
      min-width: 0;
    }
    aside, main, section.results {
      min-height: 0;
      overflow: hidden;
      grid-row: 2;
    }
    aside {
      grid-column: 1;
      border-right: 1px solid var(--line);
      background: var(--panel);
      display: flex;
      flex-direction: column;
    }
    .resizer {
      min-width: 6px;
      min-height: 0;
      background: var(--bg);
      border-left: 1px solid transparent;
      border-right: 1px solid transparent;
      cursor: col-resize;
      touch-action: none;
    }
    .resizer:hover,
    .resizer.dragging {
      background: #e7edf5;
      border-color: var(--line-strong);
    }
    body.resizing {
      cursor: col-resize;
      user-select: none;
    }
    #sideResizer {
      grid-column: 2;
      grid-row: 2;
    }
    #resultsResizer {
      grid-column: 4;
      grid-row: 2;
    }
    .app.left-sidebar-collapsed #sideResizer,
    .app.right-sidebar-collapsed #resultsResizer {
      display: none;
    }
    .app[data-view="account"] aside,
    .app[data-view="account"] main,
    .app[data-view="account"] .resizer,
    .app[data-view="account"] section.results,
    .app[data-view="settings"] aside,
    .app[data-view="settings"] main,
    .app[data-view="settings"] .resizer,
    .app[data-view="settings"] section.results,
    .app[data-view="stats"] aside,
    .app[data-view="stats"] main,
    .app[data-view="stats"] .resizer,
    .app[data-view="stats"] section.results {
      display: none;
    }
    .side-head {
      display: flex;
      gap: 8px;
      align-items: center;
      padding: 10px;
      border-bottom: 1px solid var(--line);
    }
    .side-collapse-toggle {
      width: 30px;
      height: 30px;
    }
    .app.left-sidebar-collapsed aside {
      overflow: hidden;
    }
    .app.left-sidebar-collapsed .side-head {
      justify-content: center;
      padding: 8px 4px;
      border-bottom: 0;
    }
    .app.left-sidebar-collapsed #filter,
    .app.left-sidebar-collapsed .side-actions,
    .app.left-sidebar-collapsed .problems {
      display: none;
    }
    .search {
      flex: 1;
    }
    .side-actions {
      display: flex;
      gap: 6px;
      flex: 0 0 auto;
    }
    .mode-toggle {
      min-width: 44px;
      padding: 0 8px;
      font-size: 12px;
      font-weight: 800;
    }
    .mode-toggle.active {
      color: white;
      border-color: var(--accent);
      background: var(--accent);
    }
    .problems {
      overflow: auto;
      padding: 8px 8px 12px;
    }
    .folder {
      margin-bottom: 10px;
    }
    .folder-root {
      margin-bottom: 16px;
    }
    details.folder-root > summary {
      list-style: none;
      cursor: pointer;
    }
    details.folder-root > summary::-webkit-details-marker {
      display: none;
    }
    details.folder > summary {
      list-style: none;
      cursor: pointer;
    }
    details.folder > summary::-webkit-details-marker {
      display: none;
    }
    .folder-root-title {
      position: sticky;
      top: 0;
      z-index: 1;
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 32px;
      padding: 0 8px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      color: var(--text);
      font-size: 13px;
      font-weight: 800;
    }
    .root-actions {
      margin-left: auto;
      display: inline-flex;
      gap: 5px;
    }
    .root-actions button {
      width: 26px;
      height: 24px;
      padding: 0;
      font-size: 11px;
    }
    .template-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      align-items: center;
    }
    .sidebar-draggable-row,
    .folder[draggable="true"] > .folder-head {
      cursor: grab;
    }
    .problems.sidebar-dragging .sidebar-draggable-row,
    .problems.sidebar-dragging .folder[draggable="true"] > .folder-head {
      cursor: grabbing;
    }
    .sidebar-dragging-item {
      opacity: 0.45;
    }
    .sidebar-drop-before {
      box-shadow: inset 0 3px 0 var(--accent-2);
    }
    .sidebar-drop-after {
      box-shadow: inset 0 -3px 0 var(--accent-2);
    }
    .template-item {
      width: 100%;
      min-height: 34px;
      text-align: left;
      border-color: transparent;
      background: transparent;
      padding: 6px 8px;
    }
    .template-item.active {
      border-color: var(--accent-2);
      background: #eef4ff;
    }
    .template-item .name {
      color: var(--text);
      font-size: 12px;
      font-weight: 700;
      margin: 0;
      display: block;
      -webkit-line-clamp: 1;
    }
    .folder-head {
      display: flex;
      align-items: center;
      gap: 7px;
      min-height: 28px;
      padding: 0 7px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }
    .folder-head::before {
      content: "";
      width: 13px;
      height: 10px;
      border: 1px solid var(--line-strong);
      border-top-width: 3px;
      border-radius: 3px 3px 2px 2px;
      background: var(--panel-2);
      flex: 0 0 auto;
    }
    .folder-name {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .folder-count {
      margin-left: auto;
      color: var(--muted);
      font-weight: 600;
    }
    .folder-delete {
      width: 26px;
      height: 26px;
      padding: 0;
      margin-left: 3px;
      font-size: 11px;
      flex: 0 0 auto;
    }
    .folder-items {
      display: grid;
      gap: 3px;
      margin-left: 13px;
      padding-left: 10px;
      border-left: 1px solid var(--line);
    }
    .problem-row {
      display: grid;
      grid-template-columns: 14px minmax(0, 1fr);
      gap: 3px;
      align-items: center;
    }
    .problem-drag-handle {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      line-height: 1;
      text-align: center;
      opacity: 0.72;
      user-select: none;
    }
    .problem {
      width: 100%;
      height: auto;
      min-height: 46px;
      display: block;
      text-align: left;
      border-color: transparent;
      border-radius: 6px;
      padding: 7px 8px;
      background: transparent;
    }
    .problem.active {
      border-color: var(--accent);
      background: #edf7f5;
    }
    .problem .key {
      font-weight: 700;
      font-size: 13px;
    }
    .problem .name {
      color: var(--muted);
      font-size: 12px;
      margin-top: 3px;
      line-height: 1.3;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    .problem-tags {
      display: flex;
      gap: 5px;
      margin-top: 6px;
      min-height: 18px;
    }
    .problem-tag {
      display: inline-flex;
      align-items: center;
      height: 18px;
      padding: 0 6px;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1;
    }
    .problem-tag.statement {
      border-color: #9bd0c9;
      background: #edf7f5;
      color: var(--accent);
      font-weight: 700;
    }
    .problem-tag.solved {
      border-color: #99d6ad;
      background: #edf8f0;
      color: var(--ok);
      font-weight: 800;
    }
    .problem-tag.contest {
      border-color: #a8bdd9;
      background: #eef4fb;
      color: #315a89;
      font-weight: 800;
    }
    .context-menu {
      position: fixed;
      z-index: 1000;
      min-width: 148px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: var(--panel);
      box-shadow: 0 14px 34px rgba(23, 32, 47, 0.16);
    }
    .context-menu[hidden] {
      display: none;
    }
    .context-menu button {
      width: 100%;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: flex-start;
      border-color: transparent;
      background: transparent;
      padding: 0 9px;
      text-align: left;
      font-size: 13px;
    }
    .context-menu button:hover {
      border-color: var(--line);
      background: #f7f9fc;
    }
    .context-menu button.danger {
      color: var(--danger);
    }
    main {
      grid-column: 3;
      display: grid;
      grid-template-columns: minmax(280px, var(--statement-width)) 6px minmax(420px, 1fr);
      grid-template-rows: 44px minmax(0, 1fr);
      background: #fbfcfe;
    }
    #codeResizer {
      grid-column: 2;
      grid-row: 2;
    }
    .editor-head {
      grid-column: 1 / -1;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 0 12px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      min-width: 0;
    }
    .title {
      min-width: 0;
      font-weight: 700;
      font-size: 14px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .pane {
      min-height: 0;
    }
    .hidden {
      display: none !important;
    }
    .editor-wrap {
      grid-column: 3;
      grid-row: 2;
      min-height: 0;
      padding: 10px;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      border-left: 1px solid var(--line);
    }
    .editor-tabs {
      display: flex;
      align-items: end;
      gap: 2px;
      min-width: 0;
      overflow-x: auto;
      padding: 0 2px;
    }
    .editor-tab {
      height: 31px;
      max-width: 180px;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      border-color: var(--line);
      border-bottom-color: transparent;
      border-radius: 6px 6px 0 0;
      background: #edf1f7;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }
    .editor-tab.active {
      background: #0e1525;
      color: #e9eef9;
      border-color: #0e1525;
    }
    .editor-tab-add {
      width: 31px;
      justify-content: center;
      padding: 0;
      font-size: 16px;
      flex: 0 0 auto;
    }
    .editor-tab-name {
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .editor-tab-close {
      width: 18px;
      height: 18px;
      display: inline-grid;
      place-items: center;
      border: 0;
      border-radius: 4px;
      background: transparent;
      color: inherit;
      padding: 0;
      font-size: 14px;
      line-height: 1;
    }
    .editor-tab-close:hover {
      background: rgba(255, 255, 255, 0.16);
    }
    .code-editor {
      --code-font-size: 14px;
      --code-line-height: 22px;
      --code-gutter-width: 46px;
      position: relative;
      min-height: 0;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 0 7px 7px 7px;
      background: #0e1525;
      box-shadow: var(--shadow);
    }
    .monaco-editor-host {
      position: absolute;
      inset: 0;
      display: none;
      z-index: 4;
    }
    .code-editor.monaco-ready .monaco-editor-host {
      display: block;
    }
    .code-editor.monaco-ready .code-line-numbers,
    .code-editor.monaco-ready .code-highlight,
    .code-editor.monaco-ready textarea.code {
      display: none;
    }
    .code-line-numbers,
    .code-highlight,
    textarea.code {
      font-family: "Cascadia Code", "Consolas", ui-monospace, monospace;
      font-variant-ligatures: none;
      font-feature-settings: "liga" 0, "calt" 0;
      font-kerning: none;
      font-synthesis: none;
      font-size: var(--code-font-size);
      line-height: var(--code-line-height);
      letter-spacing: 0;
      word-spacing: 0;
      text-rendering: geometricPrecision;
      tab-size: 4;
      white-space: pre;
      word-break: normal;
      overflow-wrap: normal;
    }
    .code-highlight,
    textarea.code {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      margin: 0;
      padding: 13px 14px 13px calc(var(--code-gutter-width) + 14px);
    }
    .code-line-numbers {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      width: var(--code-gutter-width);
      margin: 0;
      padding: 13px 8px 72px 0;
      overflow: hidden;
      border-right: 1px solid rgba(124, 138, 165, 0.2);
      background: #0b1220;
      color: #64748b;
      text-align: right;
      user-select: none;
      pointer-events: none;
      z-index: 3;
    }
    .code-highlight {
      overflow: hidden;
      color: #d8deea;
      padding-bottom: 72px;
      z-index: 1;
      pointer-events: none;
    }
    .code-highlight span {
      font: inherit;
      font-variant-ligatures: inherit;
      font-feature-settings: inherit;
      letter-spacing: inherit;
      line-height: inherit;
      margin: 0;
      padding: 0;
      border: 0;
    }
    textarea.code {
      resize: none;
      border: 0;
      background: transparent;
      color: transparent;
      caret-color: #e9eef9;
      outline: none;
      overflow: auto;
      padding-bottom: 72px;
      scroll-padding: 18px 18px 72px calc(var(--code-gutter-width) + 18px);
      z-index: 2;
    }
    textarea.code::selection {
      background: rgba(134, 168, 255, 0.38);
      color: transparent;
    }
    textarea.code:focus { box-shadow: inset 0 0 0 1px #86a8ff; }
    textarea.code[readonly] {
      cursor: default;
    }
    .tok-keyword { color: #7dd3fc; }
    .tok-type { color: #86efac; }
    .tok-literal { color: #f0abfc; }
    .tok-string { color: #fbbf24; }
    .tok-number { color: #fdba74; }
    .tok-comment { color: #7c8aa5; }
    .tok-preprocessor { color: #c4b5fd; }
    .tok-operator { color: #93c5fd; }
    .tok-bracket {
      border-radius: 3px;
    }
    .tok-bracket-match {
      background: rgba(250, 204, 21, 0.32);
      color: #fde68a;
      box-shadow: inset 0 0 0 1px rgba(250, 204, 21, 0.55);
    }
    .tok-bracket-unmatched {
      background: rgba(248, 113, 113, 0.28);
      color: #fecaca;
      box-shadow: inset 0 -2px 0 #ef4444;
    }
    .statement-wrap {
      grid-column: 1;
      grid-row: 2;
      overflow: auto;
      padding: 14px;
      background: #fbfcfe;
    }
    .statement-shell {
      width: 100%;
      max-width: none;
      margin: 0 auto;
      display: grid;
      gap: 14px;
    }
    .statement-title {
      border-bottom: 1px solid var(--line);
      padding-bottom: 12px;
    }
    .statement-title h1 {
      font-size: 22px;
      line-height: 1.25;
      margin: 0 0 8px;
    }
    .statement-facts {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
    }
    .statement-facts span {
      background: white;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 8px;
    }
    .statement-section h2 {
      font-size: 16px;
      margin: 0 0 7px;
    }
    .statement-section p {
      margin: 0;
      white-space: pre-wrap;
      line-height: 1.55;
      font-size: 14px;
    }
    math.statement-math {
      display: inline-block;
      direction: ltr;
      unicode-bidi: isolate;
      font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif;
      font-size: 1.18em;
      color: #111827;
      vertical-align: -0.12em;
      margin: 0 0.12em;
    }
    math.statement-math mi {
      font-style: italic;
    }
    math.statement-math mtext,
    math.statement-math mn,
    math.statement-math mo {
      font-style: normal;
    }
    .captured-statement-shell {
      width: 100%;
      max-width: none;
      height: 100%;
      min-height: 680px;
      margin: 0 auto;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: white;
      overflow: hidden;
      box-shadow: var(--shadow);
    }
    .statement-frame {
      width: 100%;
      height: 100%;
      min-height: 680px;
      border: 0;
      display: block;
      background: white;
    }
    .sample-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .sample-block {
      border: 1px solid var(--line);
      border-radius: 7px;
      background: white;
      overflow: hidden;
    }
    .sample-block strong {
      display: block;
      padding: 8px 10px;
      border-bottom: 1px solid var(--line);
      font-size: 12px;
      color: var(--muted);
    }
    section.results {
      grid-column: 5;
      border-left: 1px solid var(--line);
      background: var(--panel);
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr) auto;
    }
    .results-head {
      min-width: 0;
      min-height: 42px;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 10px;
      border-bottom: 1px solid var(--line);
    }
    .results-head-title {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .results-collapse-toggle {
      width: 30px;
      height: 30px;
    }
    .app.right-sidebar-collapsed section.results {
      grid-template-rows: auto;
      overflow: hidden;
    }
    .app.right-sidebar-collapsed .results-head {
      justify-content: center;
      padding: 8px 4px;
      border-bottom: 0;
    }
    .app.right-sidebar-collapsed .results-head-title,
    .app.right-sidebar-collapsed .meta,
    .app.right-sidebar-collapsed .output,
    .app.right-sidebar-collapsed .custom {
      display: none;
    }
    .meta {
      padding: 12px;
      border-bottom: 1px solid var(--line);
    }
    .meta h2 {
      font-size: 15px;
      margin: 0 0 7px;
      line-height: 1.35;
    }
    .meta-row {
      display: grid;
      grid-template-columns: 92px minmax(0, 1fr);
      gap: 8px;
      font-size: 12px;
      color: var(--muted);
      margin-top: 5px;
    }
    .meta-row a {
      color: var(--accent-2);
      text-decoration: none;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .output {
      overflow: auto;
      padding: 10px 12px;
      background: #fbfcfe;
    }
    .case {
      border: 1px solid var(--line);
      border-radius: 7px;
      background: white;
      margin-bottom: 9px;
      overflow: hidden;
    }
    .case-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 8px 10px;
      border-bottom: 1px solid var(--line);
      font-size: 13px;
      font-weight: 700;
    }
    .case-actions {
      display: flex;
      align-items: center;
      gap: 6px;
      flex: 0 0 auto;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 42px;
      height: 22px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
      color: white;
      background: var(--muted);
    }
    .badge.TEST { background: var(--muted); }
    .badge.AC { background: var(--ok); }
    .badge.WA, .badge.RE, .badge.CE { background: var(--danger); }
    .badge.TLE, .badge.SKIP { background: var(--warn); }
    .case-body {
      display: grid;
      gap: 8px;
      padding: 8px;
    }
    .submit-link {
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      padding: 0 10px;
      border: 1px solid #1d4ed8;
      border-radius: 6px;
      color: #1d4ed8;
      background: #eff6ff;
      font-weight: 700;
      text-decoration: none;
    }
    .submit-link:hover {
      background: #dbeafe;
    }
    .case-part {
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
      background: #fbfcfe;
    }
    .case-part strong {
      display: block;
      padding: 6px 8px;
      border-bottom: 1px solid var(--line);
      color: var(--muted);
      font-size: 11px;
      line-height: 1;
    }
    pre {
      margin: 0;
      padding: 9px 10px;
      overflow: auto;
      font-family: "Cascadia Code", "Consolas", ui-monospace, monospace;
      font-variant-ligatures: none;
      font-feature-settings: "liga" 0, "calt" 0;
      font-size: 12px;
      line-height: 1.45;
      white-space: pre-wrap;
    }
    .custom {
      border-top: 1px solid var(--line);
      padding: 10px 12px;
      background: var(--panel);
      display: grid;
      gap: 8px;
    }
    .custom textarea {
      width: 100%;
      height: 78px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      font-family: "Cascadia Code", "Consolas", ui-monospace, monospace;
      font-size: 12px;
    }
    .custom-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .empty {
      padding: 18px;
      color: var(--muted);
      font-size: 14px;
    }
    .page-view {
      grid-column: 1 / -1;
      grid-row: 2;
      min-height: 0;
      overflow: auto;
      display: none;
      background: #f7f8fb;
      padding: 18px;
    }
    .app[data-view="account"] #accountView,
    .app[data-view="settings"] #settingsView,
    .app[data-view="stats"] #statsView {
      display: block;
    }
    .page-shell {
      max-width: 1280px;
      margin: 0 auto;
      display: grid;
      gap: 14px;
    }
    .page-head {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 12px;
      padding: 2px 0 8px;
      border-bottom: 1px solid var(--line);
    }
    .page-head h1 {
      margin: 0;
      font-size: 24px;
      line-height: 1.2;
    }
    .page-head p {
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 13px;
    }
    .page-actions {
      display: flex;
      gap: 8px;
      align-items: center;
      flex: 0 0 auto;
    }
    .account-form {
      display: grid;
      grid-template-columns: minmax(180px, 1fr) minmax(180px, 1fr) minmax(180px, 1fr) auto;
      gap: 10px;
      align-items: end;
    }
    .account-form label {
      display: grid;
      gap: 5px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }
    .account-form input,
    .account-form select {
      width: 100%;
    }
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(150px, 1fr));
      gap: 10px;
    }
    .metric-card,
    .panel {
      border: 1px solid var(--line);
      border-radius: 7px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }
    .metric-card {
      padding: 12px;
      display: grid;
      gap: 5px;
      min-height: 82px;
    }
    .metric-card span {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .metric-card strong {
      font-size: 25px;
      line-height: 1.1;
    }
    .panel {
      padding: 14px;
      min-width: 0;
    }
    .panel h2 {
      margin: 0 0 10px;
      font-size: 16px;
    }
    .page-grid-2 {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(320px, 0.8fr);
      gap: 14px;
    }
    .profile-card {
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      gap: 14px;
      align-items: center;
    }
    .avatar {
      width: 86px;
      height: 86px;
      border-radius: 7px;
      object-fit: cover;
      border: 1px solid var(--line);
      background: var(--panel-2);
    }
    .avatar-fallback {
      display: grid;
      place-items: center;
      font-size: 30px;
      font-weight: 800;
      color: var(--accent);
    }
    .profile-title {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 8px;
    }
    .profile-title h2 {
      margin: 0;
      font-size: 22px;
    }
    .rank-pill,
    .table-pill {
      display: inline-flex;
      align-items: center;
      height: 23px;
      padding: 0 8px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #f8fafc;
      font-size: 12px;
      font-weight: 800;
      color: var(--muted);
      white-space: nowrap;
    }
    .fact-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(130px, 1fr));
      gap: 7px 14px;
    }
    .fact {
      display: grid;
      gap: 2px;
      min-width: 0;
    }
    .fact span {
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .fact strong {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 13px;
      font-weight: 700;
    }
    .chart-bars {
      display: grid;
      gap: 8px;
    }
    .bar-row {
      display: grid;
      grid-template-columns: 140px minmax(120px, 1fr) 44px;
      gap: 9px;
      align-items: center;
      font-size: 12px;
    }
    .bar-label {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: var(--muted);
      font-weight: 700;
    }
    .bar-track {
      height: 12px;
      border-radius: 999px;
      background: #e8edf5;
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      min-width: 2px;
      background: var(--accent);
    }
    .bar-fill.blue { background: var(--accent-2); }
    .rating-chart {
      width: 100%;
      min-height: 220px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #fbfcfe;
    }
    .data-table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: white;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .data-table th,
    .data-table td {
      padding: 8px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: middle;
      white-space: nowrap;
    }
    .data-table th {
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      background: #f8fafc;
      position: sticky;
      top: 0;
      z-index: 1;
    }
    .data-table tr:last-child td {
      border-bottom: 0;
    }
    .problem-link {
      height: auto;
      min-height: 28px;
      max-width: 360px;
      padding: 4px 7px;
      border-color: transparent;
      background: transparent;
      color: var(--accent-2);
      font-weight: 700;
      text-align: left;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .problem-link:hover {
      border-color: var(--line);
      background: #eff6ff;
    }
    .tag-list {
      display: flex;
      gap: 5px;
      flex-wrap: wrap;
      max-width: 360px;
    }
    .small-muted {
      color: var(--muted);
      font-size: 12px;
    }
    .split-panels {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 14px;
    }
    @media (max-width: 1380px) {
      .app {
        grid-template-columns: var(--left-sidebar-width) var(--side-resizer-width) minmax(760px, 1fr);
      }
      main { grid-column: 3; }
      #resultsResizer {
        display: none;
      }
      section.results {
        display: none;
      }
      .metric-grid {
        grid-template-columns: repeat(2, minmax(150px, 1fr));
      }
      .page-grid-2,
      .split-panels {
        grid-template-columns: 1fr;
      }
      .account-form {
        grid-template-columns: repeat(2, minmax(180px, 1fr));
      }
    }
    @media (max-width: 760px) {
      body { overflow: auto; }
      .app {
        height: auto;
        min-height: 100vh;
        grid-template-columns: 1fr;
        grid-template-rows: auto auto auto auto;
      }
      header, aside, main, section.results {
        grid-column: 1;
      }
      header {
        height: auto;
        min-height: 48px;
        flex-wrap: wrap;
        padding: 8px 10px;
      }
      .top-menu {
        order: 3;
        width: 100%;
      }
      .menu-tab {
        flex: 1;
        min-width: 0;
      }
      .header-tools {
        margin-left: auto;
      }
      .resizer {
        display: none;
      }
      main {
        grid-template-columns: 1fr;
        grid-template-rows: auto 60vh 70vh;
      }
      .statement-wrap,
      .editor-wrap {
        grid-column: 1;
      }
      .statement-wrap { grid-row: 2; }
      .editor-wrap {
        grid-row: 3;
        border-left: 0;
        border-top: 1px solid var(--line);
      }
      section.results {
        display: grid;
        min-height: 520px;
      }
      .sample-grid {
        grid-template-columns: 1fr;
      }
      .page-view {
        padding: 12px;
      }
      .metric-grid,
      .fact-grid,
      .account-form {
        grid-template-columns: 1fr;
      }
      .profile-card {
        grid-template-columns: 1fr;
      }
      .bar-row {
        grid-template-columns: 96px minmax(80px, 1fr) 36px;
      }
    }
  </style>
</head>
<body>
  <div class="app" data-view="code">
    <header>
      <div class="brand"><strong>cf-workbench</strong><span id="workspace"></span></div>
      <nav class="top-menu" aria-label="Primary">
        <button class="menu-tab active" data-view-target="code">Code</button>
        <button class="menu-tab" data-view-target="account">Account</button>
        <button class="menu-tab" data-view-target="stats">Stats</button>
        <button class="menu-tab" data-view-target="settings">Settings</button>
      </nav>
      <div class="header-tools">
        <div class="toolbar code-toolbar" id="codeToolbar">
          <select id="compare" title="Compare mode">
            <option value="tokens">tokens</option>
            <option value="trim">trim</option>
            <option value="exact">exact</option>
          </select>
          <button id="save" class="blue" title="Save source">Save</button>
          <button id="copy" title="Copy editor contents">Copy</button>
          <button id="run" class="primary" title="Run samples (Ctrl+Enter)">Run</button>
          <button id="submit" title="Open submit page with source prefill">Submit</button>
        </div>
        <span class="status" id="status">Ready</span>
      </div>
    </header>
    <aside id="problemSidebar">
      <div class="side-head">
        <button id="toggleProblemSidebar" class="icon sidebar-toggle side-collapse-toggle" type="button" title="Collapse problem list" aria-label="Collapse problem list" aria-controls="problemSidebar" aria-expanded="true">&lt;</button>
        <input id="filter" class="search" placeholder="Search" aria-label="Search problems">
        <div class="side-actions">
          <button id="contestModeToggle" class="mode-toggle" type="button" title="Contest mode" aria-pressed="false">Contest</button>
          <button id="newFolder" class="icon" title="New folder">F+</button>
          <button id="newProblem" class="icon" title="New problem">P+</button>
          <button id="refresh" class="icon" title="Refresh">R</button>
        </div>
      </div>
      <div class="problems" id="problems"></div>
    </aside>
    <div id="sideResizer" class="resizer" title="Resize problem list"></div>
    <main>
      <div class="editor-head">
        <div class="title" id="title">No problem selected</div>
        <div class="toolbar">
          <button id="openCf" title="Open Codeforces">CF</button>
        </div>
      </div>
      <div id="statementPane" class="pane statement-wrap"></div>
      <div id="codeResizer" class="resizer" title="Resize statement and code panes"></div>
      <div id="editorPane" class="pane editor-wrap">
        <div id="editorTabs" class="editor-tabs"></div>
        <div class="code-editor">
          <div id="monacoEditor" class="monaco-editor-host" aria-label="Source code editor"></div>
          <pre id="codeLineNumbers" class="code-line-numbers" aria-hidden="true">1</pre>
          <pre id="codeHighlight" class="code-highlight" aria-hidden="true"></pre>
          <textarea id="code" class="code" spellcheck="false" wrap="off" aria-label="Source code editor"></textarea>
        </div>
      </div>
    </main>
    <div id="resultsResizer" class="resizer" title="Resize tests pane"></div>
    <section class="results" id="resultsSidebar">
      <div class="results-head">
        <button id="toggleResultsSidebar" class="icon sidebar-toggle results-collapse-toggle" type="button" title="Collapse tests pane" aria-label="Collapse tests pane" aria-controls="resultsSidebar" aria-expanded="true">&gt;</button>
        <span class="results-head-title">Tests</span>
      </div>
      <div class="meta" id="meta"></div>
      <div class="output" id="output"></div>
      <div class="custom">
        <div class="custom-grid">
          <textarea id="customInput" placeholder="input"></textarea>
          <textarea id="customOutput" placeholder="expected output"></textarea>
        </div>
        <button id="addTest" title="Add custom test">Add Test</button>
      </div>
    </section>
    <section id="accountView" class="page-view account-view"></section>
    <section id="statsView" class="page-view stats-view"></section>
    <section id="settingsView" class="page-view settings-view"></section>
  </div>
  <div id="contextMenu" class="context-menu" hidden></div>
  <script src="/static/ide/cfw-ide.iife.js"></script>
  <script>
    const DETAILS_STORAGE_KEY = "cfw.openDetails.v2";
    const SIDEBAR_ORDER_STORAGE_KEY = "cfw.sidebarOrder.v1";
    const LEFT_SIDEBAR_COLLAPSED_STORAGE_KEY = "cfw.leftSidebarCollapsed";
    const RIGHT_SIDEBAR_COLLAPSED_STORAGE_KEY = "cfw.rightSidebarCollapsed";
    const EDITOR_DRAFTS_STORAGE_KEY = "cfw.editorDrafts";
    const LAST_EDITOR_DOCUMENT_STORAGE_KEY = "cfw.lastEditorDocument";
    const CONTEST_MODE_STORAGE_KEY = "cfw.contestMode";
    const SOURCE_SELECTION_STORAGE_KEY = "cfw.problemSourceSelection.v1";
    const AUTO_SAVE_DELAY_MS = 900;
    const DRAFT_SAVE_DELAY_MS = 350;
    const MAX_EDITOR_DRAFTS = 50;
    const state = {
      view: "code",
      problems: [],
      folders: [],
      knownProblemKeys: null,
      contestMode: loadContestMode(),
      recentlyLoadedProblemKeys: new Set(),
      current: null,
      currentTemplate: null,
      dirty: false,
      autoSaveTimer: null,
      draftSaveTimer: null,
      caretScrollFrame: null,
      codeHighlightFrame: null,
      lastSavedSource: "",
      sourceBuffer: "",
      editorTab: "source",
      sourceSelections: loadSourceSelections(),
      templates: [],
      account: null,
      stats: null,
      settings: { uiLanguage: "en" },
      openDetails: loadOpenDetails(),
      sidebarOrder: loadSidebarOrder(),
      sidebarDrag: null,
      leftSidebarCollapsed: loadCollapsedState(LEFT_SIDEBAR_COLLAPSED_STORAGE_KEY),
      rightSidebarCollapsed: loadCollapsedState(RIGHT_SIDEBAR_COLLAPSED_STORAGE_KEY),
    };
    const $ = (id) => document.getElementById(id);

    const UI_STRINGS = {
      en: {
        tabCode: "Code",
        tabAccount: "Account",
        tabStats: "Stats",
        tabSettings: "Settings",
        save: "Save",
        saveSource: "Save source",
        copy: "Copy",
        copyEditor: "Copy editor contents",
        run: "Run",
        runSamples: "Run samples (Ctrl+Enter)",
        submit: "Submit",
        submitPrefill: "Open submit page with source prefill",
        compareMode: "Compare mode",
        search: "Search",
        searchProblems: "Search problems",
        contestShort: "Contest",
        contestModeOn: "Contest mode on",
        contestModeOff: "Contest mode off",
        newFolder: "New folder",
        newProblem: "New problem",
        refresh: "Refresh",
        tests: "Tests",
        input: "input",
        expectedOutput: "expected output",
        addTest: "Add Test",
        addCustomTest: "Add custom test",
        problemList: "problem list",
        testsPane: "tests pane",
        collapse: "Collapse",
        expand: "Expand",
        rootFolders: "Folders",
        rootContest: "Contest",
        rootDifficulty: "Difficulty",
        rootTags: "Tags",
        rootTemplates: "Templates",
        recentlyLoaded: "Newly loaded",
        noMatches: "No matches",
        noTemplates: "No templates",
        untagged: "Untagged",
        unratedDifficulty: "Unrated",
        settingsTitle: "Settings",
        settingsDescription: "Adjust local UI preferences for this workbench.",
        uiLanguage: "UI language",
        english: "English",
        korean: "Korean",
        saveSettings: "Save settings",
        savingSettings: "Saving settings",
        settingsReady: "Settings ready",
        settingsSaved: "Settings saved",
        settingsFailed: "Settings failed to load",
        accountTitle: "Account",
        accountFailed: "Account failed to load",
        accountNotConfigured: "Codeforces handle is not configured.",
        codeforcesProfile: "Codeforces Profile",
        handle: "Handle",
        apiKey: "API key",
        apiSecret: "API secret",
        configured: "Configured",
        optional: "Optional",
        rating: "Rating",
        maxRating: "Max rating",
        solvedIndex: "Solved index",
        fetchedAC: "Fetched AC",
        contribution: "Contribution",
        friends: "Friends",
        organization: "Organization",
        country: "Country",
        registered: "Registered",
        lastOnline: "Last online",
        submissionMix: "Submission Mix",
        ratingHistory: "Rating History",
        languages: "Languages",
        recentSubmissions: "Recent Submissions",
        statsTitle: "Stats",
        statsFailed: "Stats failed to load",
        noHandle: "No handle",
        synced: "Synced",
        noAcSync: "No AC sync yet",
        solved: "Solved",
        imported: "Imported",
        rated: "Rated",
        avgRating: "Avg rating",
        noSolvedProblems: "No solved problems",
        noTags: "No tags",
        language: "Language",
        recentAC: "Recent AC",
        acceptedProblems: "Accepted Problems",
        noLanguageData: "No language data",
      },
      ko: {
        tabCode: "코드",
        tabAccount: "계정",
        tabStats: "통계",
        tabSettings: "설정",
        save: "저장",
        saveSource: "소스 저장",
        copy: "복사",
        copyEditor: "에디터 내용 복사",
        run: "실행",
        runSamples: "샘플 실행 (Ctrl+Enter)",
        submit: "제출",
        submitPrefill: "제출 페이지를 열고 소스 자동 입력",
        compareMode: "비교 방식",
        search: "검색",
        searchProblems: "문제 검색",
        contestShort: "대회",
        contestModeOn: "대회 모드 켜짐",
        contestModeOff: "대회 모드 꺼짐",
        newFolder: "새 폴더",
        newProblem: "새 문제",
        refresh: "새로고침",
        tests: "테스트",
        input: "입력",
        expectedOutput: "예상 출력",
        addTest: "테스트 추가",
        addCustomTest: "커스텀 테스트 추가",
        problemList: "문제 목록",
        testsPane: "테스트 패널",
        collapse: "접기",
        expand: "펼치기",
        rootFolders: "폴더",
        rootContest: "대회",
        rootDifficulty: "난이도",
        rootTags: "태그",
        rootTemplates: "템플릿",
        recentlyLoaded: "최근 가져온 문제",
        noMatches: "일치하는 항목 없음",
        noTemplates: "템플릿 없음",
        untagged: "태그 없음",
        unratedDifficulty: "난이도 미분류",
        settingsTitle: "설정",
        settingsDescription: "로컬 워크벤치의 UI 표시 설정을 변경합니다.",
        uiLanguage: "UI 언어",
        english: "영어",
        korean: "한국어",
        saveSettings: "설정 저장",
        savingSettings: "설정 저장 중",
        settingsReady: "설정 준비됨",
        settingsSaved: "설정 저장됨",
        settingsFailed: "설정을 불러오지 못했습니다",
        accountTitle: "계정",
        accountFailed: "계정을 불러오지 못했습니다",
        accountNotConfigured: "Codeforces handle이 설정되지 않았습니다.",
        codeforcesProfile: "Codeforces 프로필",
        handle: "Handle",
        apiKey: "API key",
        apiSecret: "API secret",
        configured: "설정됨",
        optional: "선택 사항",
        rating: "레이팅",
        maxRating: "최고 레이팅",
        solvedIndex: "맞힌 문제 기록",
        fetchedAC: "가져온 AC",
        contribution: "기여도",
        friends: "친구",
        organization: "소속",
        country: "국가",
        registered: "가입일",
        lastOnline: "마지막 접속",
        submissionMix: "제출 분포",
        ratingHistory: "레이팅 기록",
        languages: "언어",
        recentSubmissions: "최근 제출",
        statsTitle: "통계",
        statsFailed: "통계를 불러오지 못했습니다",
        noHandle: "Handle 없음",
        synced: "동기화됨",
        noAcSync: "AC 동기화 없음",
        solved: "맞힌 문제",
        imported: "가져온 문제",
        rated: "레이팅 있음",
        avgRating: "평균 레이팅",
        noSolvedProblems: "맞힌 문제가 없습니다",
        noTags: "태그 없음",
        language: "언어",
        recentAC: "최근 AC",
        acceptedProblems: "맞힌 문제 목록",
        noLanguageData: "언어 데이터 없음",
      },
    };

    function currentUiLanguage() {
      return normalizeUiLanguage(state.settings && state.settings.uiLanguage);
    }

    function normalizeUiLanguage(value) {
      const text = String(value || "en").trim().toLowerCase();
      return ["ko", "kr", "korean", "한국어"].includes(text) ? "ko" : "en";
    }

    function t(key, fallback = "") {
      const language = currentUiLanguage();
      return (UI_STRINGS[language] && UI_STRINGS[language][key]) || UI_STRINGS.en[key] || fallback || key;
    }

    function setText(id, value) {
      const element = $(id);
      if (element) element.textContent = value;
    }

    function setTitle(id, value) {
      const element = $(id);
      if (element) element.title = value;
    }

    function applyUiLanguage() {
      document.documentElement.lang = currentUiLanguage() === "ko" ? "ko" : "en";
      document.querySelectorAll("[data-view-target]").forEach((button) => {
        const key = `tab${button.dataset.viewTarget.charAt(0).toUpperCase()}${button.dataset.viewTarget.slice(1)}`;
        button.textContent = t(key, button.textContent);
      });
      setText("save", t("save"));
      setTitle("save", t("saveSource"));
      setText("copy", t("copy"));
      setTitle("copy", t("copyEditor"));
      setText("run", t("run"));
      setTitle("run", t("runSamples"));
      setText("submit", t("submit"));
      setTitle("submit", t("submitPrefill"));
      setTitle("compare", t("compareMode"));
      const filter = $("filter");
      if (filter) {
        filter.placeholder = t("search");
        filter.setAttribute("aria-label", t("searchProblems"));
      }
      setText("contestModeToggle", t("contestShort"));
      setTitle("newFolder", t("newFolder"));
      setTitle("newProblem", t("newProblem"));
      setTitle("refresh", t("refresh"));
      const resultsTitle = document.querySelector(".results-head-title");
      if (resultsTitle) resultsTitle.textContent = t("tests");
      const customInput = $("customInput");
      if (customInput) customInput.placeholder = t("input");
      const customOutput = $("customOutput");
      if (customOutput) customOutput.placeholder = t("expectedOutput");
      setText("addTest", t("addTest"));
      setTitle("addTest", t("addCustomTest"));
      updateContestModeToggle();
      applySidebarCollapseState();
      updateToolbarMode();
    }

    function setStatus(text) { $("status").textContent = text; }

    function monacoIde() {
      return window.cfwIde && typeof window.cfwIde.isReady === "function" && window.cfwIde.isReady()
        ? window.cfwIde
        : null;
    }

    function initializeMonacoEditor() {
      if (!window.cfwIde || typeof window.cfwIde.mount !== "function") {
        setStatus("Monaco unavailable; using basic editor");
        return;
      }
      try {
        window.cfwIde.mount({
          container: $("monacoEditor"),
          textarea: $("code"),
          setStatus,
          onInput: () => markCodeDirty(),
          onSave: () => saveFromCodeShortcut().catch((error) => setStatus(error.message)),
          onRun: () => {
            if (state.editorTab === "source") runTests().catch((error) => setStatus(error.message));
          },
        });
        const host = $("monacoEditor");
        if (host && host.closest(".code-editor")) host.closest(".code-editor").classList.add("monaco-ready");
      } catch (error) {
        setStatus(`Monaco failed: ${error.message || String(error)}`);
      }
    }

    function currentIdeDocumentDescriptor(options = {}) {
      const sourceTab = state.editorTab === "source";
      const problemSource = sourceTab && state.current && !state.currentTemplate;
      const ide = problemSource && state.current.ide ? state.current.ide : {};
      return {
        language: "cpp",
        readOnly: Boolean(options.readOnly),
        fileUri: problemSource ? state.current.fileUri || "" : "",
        rootUri: problemSource ? state.current.rootUri || "" : "",
        lspUrl: problemSource ? state.current.lspUrl || "" : "",
        diagnosticsUrl: problemSource ? state.current.diagnosticsUrl || "" : "",
        sourceName: problemSource ? currentSourceName() : "",
        clangdAvailable: Boolean(problemSource && ide && ide.available),
        documentId: currentEditorDocumentId(),
      };
    }

    function setCodeEditorText(text, options = {}) {
      const normalized = normalizeEditorText(text);
      const code = $("code");
      code.readOnly = Boolean(options.readOnly);
      code.value = normalized;
      const ide = monacoIde();
      if (ide) {
        ide.setDocument({
          ...currentIdeDocumentDescriptor(options),
          value: normalized,
        });
      } else {
        updateCodeHighlight();
      }
    }

    function codeEditorValue() {
      const ide = monacoIde();
      return ide ? ide.getValue() : $("code").value;
    }

    function layoutCodeEditor() {
      const ide = monacoIde();
      if (ide && typeof ide.layout === "function") ide.layout();
    }

    function loadCollapsedState(storageKey) {
      try {
        return localStorage.getItem(storageKey) === "1";
      } catch (error) {
        return false;
      }
    }

    function saveCollapsedState(storageKey, collapsed) {
      try {
        localStorage.setItem(storageKey, collapsed ? "1" : "0");
      } catch (error) {
        // Layout persistence is optional.
      }
    }

    function updateSidebarToggle(id, collapsed, label, collapseIcon, expandIcon) {
      const button = $(id);
      if (!button) return;
      const action = collapsed ? t("expand") : t("collapse");
      button.textContent = collapsed ? expandIcon : collapseIcon;
      button.title = `${action} ${label}`;
      button.setAttribute("aria-label", `${action} ${label}`);
      button.setAttribute("aria-expanded", collapsed ? "false" : "true");
    }

    function applySidebarCollapseState() {
      const app = document.querySelector(".app");
      if (!app) return;
      app.classList.toggle("left-sidebar-collapsed", state.leftSidebarCollapsed);
      app.classList.toggle("right-sidebar-collapsed", state.rightSidebarCollapsed);
      updateSidebarToggle("toggleProblemSidebar", state.leftSidebarCollapsed, t("problemList"), "<", ">");
      updateSidebarToggle("toggleResultsSidebar", state.rightSidebarCollapsed, t("testsPane"), ">", "<");
      updateCodeLineNumbers();
      syncCodeScroll();
      scheduleEnsureCodeCaretVisible();
      layoutCodeEditor();
    }

    function toggleProblemSidebar() {
      state.leftSidebarCollapsed = !state.leftSidebarCollapsed;
      saveCollapsedState(LEFT_SIDEBAR_COLLAPSED_STORAGE_KEY, state.leftSidebarCollapsed);
      applySidebarCollapseState();
      setStatus(state.leftSidebarCollapsed ? "Problem list collapsed" : "Problem list expanded");
    }

    function toggleResultsSidebar() {
      state.rightSidebarCollapsed = !state.rightSidebarCollapsed;
      saveCollapsedState(RIGHT_SIDEBAR_COLLAPSED_STORAGE_KEY, state.rightSidebarCollapsed);
      applySidebarCollapseState();
      setStatus(state.rightSidebarCollapsed ? "Tests pane collapsed" : "Tests pane expanded");
    }

    function loadContestMode() {
      try {
        return localStorage.getItem(CONTEST_MODE_STORAGE_KEY) === "1";
      } catch (error) {
        return false;
      }
    }

    function saveContestMode() {
      try {
        localStorage.setItem(CONTEST_MODE_STORAGE_KEY, state.contestMode ? "1" : "0");
      } catch (error) {
        // Contest mode persistence is optional.
      }
    }

    function updateContestModeToggle() {
      const button = $("contestModeToggle");
      if (!button) return;
      button.classList.toggle("active", state.contestMode);
      button.setAttribute("aria-pressed", state.contestMode ? "true" : "false");
      button.textContent = t("contestShort");
      button.title = state.contestMode ? t("contestModeOn") : t("contestModeOff");
    }

    function toggleContestMode() {
      state.contestMode = !state.contestMode;
      saveContestMode();
      updateContestModeToggle();
      renderProblems();
      setStatus(state.contestMode ? t("contestModeOn") : t("contestModeOff"));
    }

    function loadOpenDetails() {
      try {
        const parsed = JSON.parse(localStorage.getItem(DETAILS_STORAGE_KEY) || "{}");
        return parsed && typeof parsed === "object" ? parsed : {};
      } catch (error) {
        return {};
      }
    }

    function loadSidebarOrder() {
      try {
        const parsed = JSON.parse(localStorage.getItem(SIDEBAR_ORDER_STORAGE_KEY) || "{}");
        if (!parsed || typeof parsed !== "object") return {};
        const order = {};
        for (const [key, value] of Object.entries(parsed)) {
          if (Array.isArray(value)) order[key] = value.map((item) => String(item));
        }
        return order;
      } catch (error) {
        return {};
      }
    }

    function saveSidebarOrder() {
      try {
        localStorage.setItem(SIDEBAR_ORDER_STORAGE_KEY, JSON.stringify(state.sidebarOrder));
      } catch (error) {
        // Sidebar ordering is optional.
      }
    }

    function loadSourceSelections() {
      try {
        const parsed = JSON.parse(localStorage.getItem(SOURCE_SELECTION_STORAGE_KEY) || "{}");
        if (!parsed || typeof parsed !== "object") return {};
        const selections = {};
        for (const [key, value] of Object.entries(parsed)) {
          const sourceName = String(value || "");
          if (sourceName) selections[String(key)] = sourceName;
        }
        return selections;
      } catch (error) {
        return {};
      }
    }

    function rememberProblemSource(problemKey, sourceName) {
      const key = String(problemKey || "");
      const name = String(sourceName || "");
      if (!key || !name) return;
      state.sourceSelections[key] = name;
      try {
        localStorage.setItem(SOURCE_SELECTION_STORAGE_KEY, JSON.stringify(state.sourceSelections));
      } catch (error) {
        // Source selection persistence is optional.
      }
    }

    function isDetailsOpen(key) {
      if (Object.prototype.hasOwnProperty.call(state.openDetails, key)) {
        return state.openDetails[key] === true;
      }
      return defaultDetailsOpen(key);
    }

    function defaultDetailsOpen(key) {
      const value = String(key || "");
      return value === "root:workspace" ||
        value.startsWith("root:workspace:folder:") ||
        value === "root:recently-loaded" ||
        value === "root:contest" ||
        value.startsWith("root:contest:folder:");
    }

    function setDetailsOpen(key, open) {
      state.openDetails[key] = Boolean(open);
      try {
        localStorage.setItem(DETAILS_STORAGE_KEY, JSON.stringify(state.openDetails));
      } catch (error) {
        // Persisting sidebar state is optional.
      }
    }

    function detailsOpenAttr(key) {
      return isDetailsOpen(key) ? " open" : "";
    }

    function initializeResizers() {
      const app = document.querySelector(".app");
      applySavedSize("--problem-width", "cfw.problemWidth", 260, 560);
      applySavedSize("--statement-width", "cfw.statementWidth", 280, 1200);
      applySavedSize("--tests-width", "cfw.testsWidth", 300, 640);
      bindResizer("sideResizer", (event) => {
        const rect = app.getBoundingClientRect();
        setPaneSize("--problem-width", "cfw.problemWidth", event.clientX - rect.left, 260, 560);
      });
      bindResizer("codeResizer", (event) => {
        const main = document.querySelector("main");
        const rect = main.getBoundingClientRect();
        setPaneSize("--statement-width", "cfw.statementWidth", event.clientX - rect.left, 280, Math.max(280, rect.width - 360));
      });
      bindResizer("resultsResizer", (event) => {
        const rect = app.getBoundingClientRect();
        setPaneSize("--tests-width", "cfw.testsWidth", rect.right - event.clientX, 300, 640);
      });
    }

    function applySavedSize(cssName, storageKey, min, max) {
      const value = Number(localStorage.getItem(storageKey));
      if (Number.isFinite(value)) setPaneSize(cssName, storageKey, value, min, max, false);
    }

    function setPaneSize(cssName, storageKey, value, min, max, persist = true) {
      const size = Math.round(Math.max(min, Math.min(max, value)));
      document.querySelector(".app").style.setProperty(cssName, `${size}px`);
      if (persist) localStorage.setItem(storageKey, String(size));
      layoutCodeEditor();
    }

    function bindResizer(id, onMove) {
      const handle = $(id);
      if (!handle) return;
      handle.addEventListener("pointerdown", (event) => {
        event.preventDefault();
        handle.classList.add("dragging");
        document.body.classList.add("resizing");
        handle.setPointerCapture(event.pointerId);
        const move = (moveEvent) => onMove(moveEvent);
        const up = () => {
          handle.classList.remove("dragging");
          document.body.classList.remove("resizing");
          window.removeEventListener("pointermove", move);
          window.removeEventListener("pointerup", up);
        };
        window.addEventListener("pointermove", move);
        window.addEventListener("pointerup", up);
      });
    }

    async function api(path, options = {}) {
      let response;
      try {
        response = await fetch(path, {
          ...options,
          headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        });
      } catch (error) {
        throw new Error("Server connection failed. Refresh and retry.");
      }
      const text = await response.text();
      let data = {};
      try {
        data = text ? JSON.parse(text) : {};
      } catch (error) {
        throw new Error(text || "invalid server response");
      }
      if (!response.ok || data.ok === false) {
        const error = new Error(data.error || `request failed (${response.status})`);
        error.status = response.status;
        error.payload = data;
        throw error;
      }
      return data;
    }

    function delay(ms) {
      return new Promise((resolve) => window.setTimeout(resolve, ms));
    }

    function switchView(view) {
      state.view = view;
      document.querySelector(".app").dataset.view = view;
      document.querySelectorAll(".menu-tab").forEach((button) => {
        button.classList.toggle("active", button.dataset.viewTarget === view);
      });
      if (view === "account" && !state.account) {
        loadAccount().catch((error) => {
          renderAccountError(error.message);
          setStatus(error.message);
        });
      }
      if (view === "stats" && !state.stats) {
        loadStats().catch((error) => {
          renderStatsError(error.message);
          setStatus(error.message);
        });
      }
      if (view === "settings") {
        renderSettings(state.settings);
      }
      updateToolbarMode();
    }

    function currentEditorDocumentId() {
      if (state.currentTemplate) {
        return `template:${state.currentTemplate.algorithm}\n${state.currentTemplate.name}`;
      }
      if (state.current) {
        return problemEditorDocumentId(state.current.problem.problemKey, currentSourceName());
      }
      return "";
    }

    function problemEditorDocumentId(problemKey, sourceName = "main.cpp") {
      return `problem:${String(problemKey || "")}\n${String(sourceName || "main.cpp")}`;
    }

    function parseProblemEditorDocumentId(documentId) {
      const raw = String(documentId || "");
      if (!raw.startsWith("problem:")) return null;
      const body = raw.slice("problem:".length);
      const newline = body.indexOf("\\n");
      if (newline === -1) {
        return { problemKey: body, sourceName: "" };
      }
      return {
        problemKey: body.slice(0, newline),
        sourceName: body.slice(newline + 1) || "main.cpp",
      };
    }

    function currentSourceName() {
      return state.current && state.current.sourceName ? String(state.current.sourceName) : "main.cpp";
    }

    function applyCurrentIdePayload(data) {
      if (!state.current || !data) return;
      state.current.fileUri = data.fileUri || "";
      state.current.rootUri = data.rootUri || "";
      state.current.lspUrl = data.lspUrl || "";
      state.current.diagnosticsUrl = data.diagnosticsUrl || "";
      state.current.ide = data.ide || null;
    }

    function problemSourceFiles(problem) {
      const files = problem && Array.isArray(problem.sourceFiles) ? problem.sourceFiles : [];
      const normalized = files
        .map((file) => ({ ...file, name: String(file.name || file.path || "") }))
        .filter((file) => file.name);
      if (normalized.length) return normalized;
      return [{ name: "main.cpp", path: "main.cpp", primary: true }];
    }

    function sourceFileExists(problem, sourceName) {
      const name = String(sourceName || "");
      return problemSourceFiles(problem).some((file) => file.name === name);
    }

    function selectedSourceForProblem(problemKey, explicitSourceName = "") {
      const key = String(problemKey || "");
      const problem = state.problems.find((item) => item.problemKey === key) ||
        (state.current && state.current.problem && state.current.problem.problemKey === key ? state.current.problem : null);
      const requested = String(explicitSourceName || "").trim();
      if (requested && (!problem || sourceFileExists(problem, requested))) return requested;
      const remembered = String(state.sourceSelections[key] || "").trim();
      if (remembered && (!problem || sourceFileExists(problem, remembered))) return remembered;
      const first = problemSourceFiles(problem)[0];
      return first ? first.name : "main.cpp";
    }

    function mergeProblemIntoList(problem) {
      if (!problem || !problem.problemKey) return;
      state.problems = state.problems.map((item) => (
        item.problemKey === problem.problemKey ? { ...item, ...problem } : item
      ));
    }

    function rememberCurrentEditorDocument() {
      const documentId = currentEditorDocumentId();
      if (!documentId) return;
      try {
        localStorage.setItem(LAST_EDITOR_DOCUMENT_STORAGE_KEY, documentId);
      } catch (error) {
        // Remembering the last editor is optional.
      }
    }

    function forgetCurrentEditorDocument() {
      try {
        localStorage.removeItem(LAST_EDITOR_DOCUMENT_STORAGE_KEY);
      } catch (error) {
        // Remembering the last editor is optional.
      }
    }

    function readEditorDrafts() {
      try {
        const parsed = JSON.parse(localStorage.getItem(EDITOR_DRAFTS_STORAGE_KEY) || "{}");
        return parsed && typeof parsed === "object" ? parsed : {};
      } catch (error) {
        return {};
      }
    }

    function writeEditorDrafts(drafts) {
      try {
        localStorage.setItem(EDITOR_DRAFTS_STORAGE_KEY, JSON.stringify(drafts));
      } catch (error) {
        // Draft persistence is a best-effort safety net.
      }
    }

    function pruneEditorDrafts(drafts) {
      const entries = Object.entries(drafts)
        .filter(([, draft]) => draft && typeof draft === "object")
        .sort((a, b) => Number(b[1].updatedAt || 0) - Number(a[1].updatedAt || 0))
        .slice(0, MAX_EDITOR_DRAFTS);
      return Object.fromEntries(entries);
    }

    function saveEditorDraft(source = mainSourceValue(), options = {}) {
      const documentId = options.documentId || currentEditorDocumentId();
      if (!documentId) return;
      const drafts = readEditorDrafts();
      drafts[documentId] = {
        source,
        savedSource: Object.prototype.hasOwnProperty.call(options, "savedSource") ? options.savedSource : state.lastSavedSource,
        updatedAt: Date.now(),
      };
      writeEditorDrafts(pruneEditorDrafts(drafts));
    }

    function cancelDraftSave() {
      if (state.draftSaveTimer) {
        clearTimeout(state.draftSaveTimer);
        state.draftSaveTimer = null;
      }
    }

    function scheduleEditorDraftSave(source = mainSourceValue()) {
      const documentId = currentEditorDocumentId();
      if (!documentId) return;
      const savedSource = state.lastSavedSource;
      cancelDraftSave();
      state.draftSaveTimer = setTimeout(() => {
        state.draftSaveTimer = null;
        if (currentEditorDocumentId() !== documentId) return;
        saveEditorDraft(source, { documentId, savedSource });
      }, DRAFT_SAVE_DELAY_MS);
    }

    function editorDraft(documentId) {
      const draft = readEditorDrafts()[documentId];
      return draft && typeof draft.source === "string" ? draft : null;
    }

    function clearEditorDraft(documentId = currentEditorDocumentId()) {
      if (!documentId) return;
      const drafts = readEditorDrafts();
      if (!Object.prototype.hasOwnProperty.call(drafts, documentId)) return;
      delete drafts[documentId];
      writeEditorDrafts(drafts);
    }

    function restoredEditorSource(documentId, savedSource) {
      const draft = editorDraft(documentId);
      if (!draft || draft.source === savedSource) {
        clearEditorDraft(documentId);
        return { source: savedSource, restored: false };
      }
      return { source: draft.source, restored: true };
    }

    function cancelAutoSave() {
      if (state.autoSaveTimer) {
        clearTimeout(state.autoSaveTimer);
        state.autoSaveTimer = null;
      }
    }

    function scheduleAutoSave() {
      cancelAutoSave();
      const documentId = currentEditorDocumentId();
      if (!documentId) return;
      state.autoSaveTimer = setTimeout(() => {
        state.autoSaveTimer = null;
        saveSource({ autosave: true, expectedDocumentId: documentId }).catch((error) => {
          if (currentEditorDocumentId() === documentId) {
            setStatus(`Autosave failed: ${error.message}`);
          }
        });
      }, AUTO_SAVE_DELAY_MS);
    }

    async function saveDirtyEditorBeforeSwitch() {
      captureCurrentEditorBuffer();
      if (!state.dirty) {
        cancelDraftSave();
        cancelAutoSave();
        return true;
      }
      const documentId = currentEditorDocumentId();
      if (!documentId) return true;
      cancelDraftSave();
      cancelAutoSave();
      captureSourceBuffer();
      saveEditorDraft(mainSourceValue());
      try {
        for (let attempt = 0; attempt < 2; attempt += 1) {
          await saveSource({ autosave: true, expectedDocumentId: documentId, source: mainSourceValue() });
          if (!state.dirty || currentEditorDocumentId() !== documentId) return true;
        }
        return !state.dirty || currentEditorDocumentId() !== documentId;
      } catch (error) {
        setStatus(`Autosave failed: ${error.message}`);
        return confirm("Autosave failed. Discard changes?");
      }
    }

    function keepaliveSaveCurrentEditor() {
      const documentId = currentEditorDocumentId();
      if (!documentId) return false;
      captureSourceBuffer();
      const source = mainSourceValue();
      let path = "";
      let payload = null;
      if (state.currentTemplate) {
        const selected = state.currentTemplate;
        path = "/api/templates";
        payload = {
          kind: "template",
          algorithm: selected.algorithm,
          name: selected.name,
          source,
          extension: sourceExtensionFromTemplate(selected),
        };
      } else if (state.current) {
        path = `/api/problems/${encodeURIComponent(state.current.problem.problemKey)}/source`;
        payload = { source, sourceName: currentSourceName() };
      }
      if (!path || !payload) return false;
      const body = JSON.stringify(payload);
      if (navigator.sendBeacon) {
        return navigator.sendBeacon(path, new Blob([body], { type: "application/json" }));
      }
      fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        keepalive: true,
      }).catch(() => {});
      return true;
    }

    function preserveDirtyEditorForUnload(event) {
      captureCurrentEditorBuffer();
      if (!state.dirty) return;
      cancelDraftSave();
      captureSourceBuffer();
      saveEditorDraft(mainSourceValue());
      keepaliveSaveCurrentEditor();
      event.preventDefault();
      event.returnValue = "";
    }

    async function loadProblems(options = {}) {
      const syncSolved = Boolean(options.syncSolved);
      const resetRecentlyLoaded = Boolean(options.resetRecentlyLoaded);
      setStatus(syncSolved ? "Syncing AC" : "Loading");
      const data = await api(syncSolved ? "/api/problems?syncSolved=1" : "/api/problems");
      const syncStatus = solvedSyncStatus(data.solvedSync);
      let nextProblems = data.problems || [];
      if (resetRecentlyLoaded) state.recentlyLoadedProblemKeys.clear();
      nextProblems = await applyContestModeDefaults(nextProblems);
      state.problems = nextProblems;
      state.folders = data.folders || [];
      pruneRecentlyLoadedProblemKeys();
      await loadTemplates();
      if (state.currentTemplate && !state.dirty) refreshCurrentTemplateFromStore();
      $("workspace").textContent = data.workspace;
      renderProblems();
      if (state.current && !state.dirty) {
        const latest = state.problems.find((problem) => problem.problemKey === state.current.problem.problemKey);
        if (latest && latest.updated !== state.current.problem.updated) {
          await selectProblem(latest.problemKey, { preserveEditorTab: true, sourceName: currentSourceName() });
          if (syncStatus && !state.dirty) setStatus(syncStatus);
          return;
        }
        if (!latest) {
          clearCurrentProblem();
        }
      }
      if (!state.current && !state.currentTemplate) {
        await restoreLastEditorDocument();
      }
      if (!state.current && !state.currentTemplate && state.problems.length) {
        await selectProblem(state.problems[0].problemKey, { sourceName: selectedSourceForProblem(state.problems[0].problemKey) });
      }
      if (!state.problems.length && !state.currentTemplate) {
        renderProblems();
        clearCurrentProblem();
      }
      updateToolbarMode();
      setStatus(state.dirty ? "Unsaved" : (syncStatus || "Ready"));
    }

    function setupServerEvents() {
      if (!("EventSource" in window)) return;
      const source = new EventSource("/api/events");
      source.addEventListener("statement-captured", (event) => {
        handleProblemServerEvent(event, "Statement captured").catch((error) => setStatus(error.message));
      });
      source.addEventListener("problem-imported", (event) => {
        handleProblemServerEvent(event, "Problem imported").catch((error) => setStatus(error.message));
      });
    }

    function parseServerEvent(event) {
      try {
        return JSON.parse(event.data || "{}");
      } catch (error) {
        return {};
      }
    }

    async function handleProblemServerEvent(event, statusText) {
      const payload = parseServerEvent(event);
      const problemKey = String(payload.problemKey || "");
      if (!problemKey) return;
      const currentKey = state.current && state.current.problem && state.current.problem.problemKey;
      const preserveEditor = currentKey === problemKey && state.dirty;
      await loadProblems();
      if (preserveEditor && state.current && state.current.problem.problemKey === problemKey) {
        await refreshCurrentProblemWithoutEditor();
      }
      if (state.current && state.current.problem.problemKey === problemKey) {
        setStatus(preserveEditor ? `${statusText}; unsaved code kept` : statusText);
      }
    }

    async function refreshCurrentProblemWithoutEditor() {
      if (!state.current || !state.current.problem) return false;
      const key = state.current.problem.problemKey;
      const data = await api(`/api/problems/${encodeURIComponent(key)}?sourceName=${encodeURIComponent(currentSourceName())}`);
      if (!state.current || !state.current.problem || state.current.problem.problemKey !== key) return false;
      state.current.problem = data.problem;
      mergeProblemIntoList(data.problem);
      state.current.sourceName = data.sourceName || currentSourceName();
      state.current.source = data.source;
      applyCurrentIdePayload(data);
      rememberProblemSource(key, state.current.sourceName);
      renderMeta(data.problem);
      renderStatement(data.problem);
      renderProblems();
      updateToolbarMode();
      return true;
    }

    function solvedSyncStatus(sync) {
      if (!sync) return "";
      if (sync.ok) {
        const localUpdated = Number(sync.localUpdated || 0);
        const accepted = Number(sync.accepted || 0);
        return `AC synced ${localUpdated}/${accepted}`;
      }
      if (sync.skipped) return "Set Codeforces handle to sync AC";
      return sync.error ? `AC sync failed: ${sync.error}` : "AC sync failed";
    }

    async function applyContestModeDefaults(nextProblems) {
      const nextKeys = new Set(nextProblems.map((problem) => String(problem.problemKey || "")).filter(Boolean));
      if (state.knownProblemKeys === null) {
        state.knownProblemKeys = nextKeys;
        return nextProblems;
      }
      const newProblems = nextProblems.filter((problem) => {
        const key = String(problem.problemKey || "");
        return key && !state.knownProblemKeys.has(key);
      });
      if (state.contestMode) {
        const updatedByKey = new Map();
        for (const problem of newProblems) {
          const updated = await saveProblemContestIncluded(problem.problemKey, true);
          if (updated && updated.problemKey) updatedByKey.set(String(updated.problemKey), updated);
        }
        state.knownProblemKeys = nextKeys;
        if (!updatedByKey.size) return nextProblems;
        return nextProblems.map((problem) => updatedByKey.get(String(problem.problemKey || "")) || problem);
      } else {
        for (const problem of newProblems) {
          const key = String(problem.problemKey || "");
          if (key) state.recentlyLoadedProblemKeys.add(key);
        }
      }
      state.knownProblemKeys = nextKeys;
      return nextProblems;
    }

    function pruneRecentlyLoadedProblemKeys() {
      const currentKeys = new Set(state.problems.map((problem) => String(problem.problemKey || "")).filter(Boolean));
      for (const key of [...state.recentlyLoadedProblemKeys]) {
        if (!currentKeys.has(key)) state.recentlyLoadedProblemKeys.delete(key);
      }
    }

    async function saveProblemContestIncluded(key, included) {
      if (!key) return null;
      const data = await api(`/api/problems/${encodeURIComponent(key)}/contest`, {
        method: "POST",
        body: JSON.stringify({ contestIncluded: Boolean(included) }),
      });
      return data.problem || { problemKey: key, contestIncluded: Boolean(included) };
    }

    function mergeProblemUpdate(updated) {
      if (!updated || !updated.problemKey) return;
      const key = String(updated.problemKey);
      state.problems = state.problems.map((problem) => problem.problemKey === key ? { ...problem, ...updated } : problem);
      if (state.current && state.current.problem && state.current.problem.problemKey === key) {
        state.current.problem = { ...state.current.problem, ...updated };
        renderMeta(state.current.problem);
        renderStatement(state.current.problem);
      }
    }

    async function setProblemContestIncluded(key, included) {
      if (!key) return;
      const keys = included ? sameContestProblemKeys(key) : [String(key)];
      setStatus(included ? `Adding ${keys.length} to contest` : "Removing from contest");
      const updates = await Promise.all(keys.map((problemKey) => saveProblemContestIncluded(problemKey, included)));
      updates.forEach(mergeProblemUpdate);
      renderProblems();
      setStatus(included ? `Added ${keys.length} to contest` : "Removed from contest");
    }

    function sameContestProblemKeys(key) {
      const target = state.problems.find((problem) => problem.problemKey === key) ||
        (state.current && state.current.problem && state.current.problem.problemKey === key ? state.current.problem : null);
      const contestKey = contestKeyForProblem(target);
      if (!contestKey) return [String(key)];
      const keys = state.problems
        .filter((problem) => contestKeyForProblem(problem) === contestKey)
        .map((problem) => String(problem.problemKey || ""))
        .filter(Boolean);
      return [...new Set(keys.length ? keys : [String(key)])];
    }

    function contestKeyForProblem(problem) {
      return String((problem && problem.contest && problem.contest.key) || "");
    }

    async function loadTemplates() {
      const data = await api("/api/templates");
      state.templates = data.templates || [];
    }

    async function loadSettings() {
      const data = await api("/api/settings");
      state.settings = { uiLanguage: normalizeUiLanguage(data.uiLanguage) };
      applyUiLanguage();
      if (state.view === "settings") renderSettings(state.settings);
      return state.settings;
    }

    function renderSettingsError(message) {
      $("settingsView").innerHTML = `
        <div class="page-shell">
          <div class="page-head">
            <div><h1>${escapeHtml(t("settingsTitle"))}</h1><p>${escapeHtml(message || t("settingsFailed"))}</p></div>
            <div class="page-actions"><button id="refreshSettings" class="primary">${escapeHtml(t("refresh"))}</button></div>
          </div>
        </div>
      `;
      const refresh = $("refreshSettings");
      if (refresh) refresh.addEventListener("click", () => loadSettings().catch((error) => renderSettingsError(error.message)));
    }

    function renderSettings(data = {}) {
      const language = normalizeUiLanguage(data.uiLanguage);
      $("settingsView").innerHTML = `
        <div class="page-shell">
          <div class="page-head">
            <div>
              <h1>${escapeHtml(t("settingsTitle"))}</h1>
              <p>${escapeHtml(t("settingsDescription"))}</p>
            </div>
          </div>
          <div class="panel">
            <form id="settingsForm" class="account-form">
              <label>
                ${escapeHtml(t("uiLanguage"))}
                <select id="uiLanguage" name="uiLanguage">
                  <option value="en"${language === "en" ? " selected" : ""}>${escapeHtml(t("english"))}</option>
                  <option value="ko"${language === "ko" ? " selected" : ""}>${escapeHtml(t("korean"))}</option>
                </select>
              </label>
              <button id="saveSettings" class="primary" type="submit">${escapeHtml(t("saveSettings"))}</button>
            </form>
          </div>
        </div>
      `;
      bindSettingsControls();
    }

    function bindSettingsControls() {
      const form = $("settingsForm");
      if (!form) return;
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        saveSettings().catch((error) => setStatus(error.message || String(error)));
      });
    }

    async function saveSettings() {
      const uiLanguage = normalizeUiLanguage($("uiLanguage").value);
      setStatus(t("savingSettings"));
      const data = await api("/api/settings", {
        method: "POST",
        body: JSON.stringify({ uiLanguage }),
      });
      state.settings = { uiLanguage: normalizeUiLanguage(data.uiLanguage) };
      applyUiLanguage();
      renderSettings(state.settings);
      renderProblems();
      if (state.account) renderAccount(state.account);
      if (state.stats) renderStats(state.stats);
      if (state.current && !state.currentTemplate) {
        renderMeta(state.current.problem);
        renderResults(null);
      }
      setStatus(t("settingsSaved"));
    }

    async function loadAccount() {
      setStatus("Loading account");
      const data = await api("/api/account");
      state.account = data;
      renderAccount(data);
      setStatus(data.profileError || data.submissionError ? "Account partially loaded" : "Account ready");
    }

    function renderAccountError(message) {
      $("accountView").innerHTML = `
        <div class="page-shell">
          <div class="page-head">
            <div><h1>${escapeHtml(t("accountTitle"))}</h1><p>${escapeHtml(message || t("accountFailed"))}</p></div>
            <div class="page-actions"><button id="refreshAccount" class="primary">${escapeHtml(t("refresh"))}</button></div>
          </div>
        </div>
      `;
      $("refreshAccount").addEventListener("click", () => loadAccount().catch((error) => renderAccountError(error.message)));
    }

    function renderAccount(data) {
      if (!data || !data.configured) {
        $("accountView").innerHTML = `
          <div class="page-shell">
            <div class="page-head">
              <div><h1>${escapeHtml(t("accountTitle"))}</h1><p>${escapeHtml(t("accountNotConfigured"))}</p></div>
              <div class="page-actions"><button id="refreshAccount" class="primary">${escapeHtml(t("refresh"))}</button></div>
            </div>
            ${renderAccountForm(data)}
          </div>
        `;
        bindAccountControls();
        return;
      }
      const profile = data.profile || {};
      const summary = data.submissionSummary || {};
      const solvedIndex = data.solvedIndex || {};
      const ratingHistory = data.ratingHistory || [];
      const currentRating = profile.rating || latestRating(ratingHistory) || "-";
      const maxRating = profile.maxRating || maxRatingFromHistory(ratingHistory) || "-";
      const friends = Array.isArray(data.friends) ? data.friends : [];
      $("accountView").innerHTML = `
        <div class="page-shell">
          <div class="page-head">
            <div>
              <h1>${escapeHtml(t("accountTitle"))}</h1>
              <p>${escapeHtml(data.handle)}${data.profileError ? ` · ${escapeHtml(data.profileError)}` : ""}</p>
            </div>
            <div class="page-actions"><button id="refreshAccount" class="primary">${escapeHtml(t("refresh"))}</button></div>
          </div>
          ${renderAccountForm(data)}
          <div class="metric-grid">
            ${renderMetricCard(t("rating"), currentRating)}
            ${renderMetricCard(t("maxRating"), maxRating)}
            ${renderMetricCard(t("solvedIndex"), solvedIndex.count || 0)}
            ${renderMetricCard(t("fetchedAC"), summary.acceptedProblems || 0)}
          </div>
          <div class="page-grid-2">
            <div class="panel profile-card">
              ${renderAvatar(profile)}
              <div>
                <div class="profile-title">
                  <h2>${escapeHtml(profile.handle || data.handle)}</h2>
                  <span class="rank-pill">${escapeHtml(profile.rank || "unrated")}</span>
                </div>
                <div class="fact-grid">
                  ${renderFact(t("contribution"), signedNumber(profile.contribution))}
                  ${renderFact(t("friends"), profile.friendOfCount ?? "-")}
                  ${renderFact(t("organization"), profile.organization || "-")}
                  ${renderFact(t("country"), profile.country || "-")}
                  ${renderFact(t("registered"), formatDateTime(profile.registrationTimeSeconds))}
                  ${renderFact(t("lastOnline"), formatDateTime(profile.lastOnlineTimeSeconds))}
                </div>
              </div>
            </div>
            <div class="panel">
              <h2>${escapeHtml(t("submissionMix"))}</h2>
              ${renderBarChart(entriesFromCounts(summary.verdicts), { empty: "No submissions fetched" })}
            </div>
          </div>
          <div class="page-grid-2">
            <div class="panel">
              <h2>${escapeHtml(t("ratingHistory"))}</h2>
              ${renderRatingChart(ratingHistory)}
              ${renderRatingHistoryTable(ratingHistory)}
            </div>
            <div class="panel">
              <h2>${escapeHtml(t("languages"))}</h2>
              ${renderBarChart(entriesFromCounts(summary.languages), { fillClass: "blue", empty: t("noLanguageData") })}
            </div>
          </div>
          <div class="split-panels">
            <div class="panel">
              <h2>${escapeHtml(t("recentSubmissions"))}</h2>
              ${renderRecentSubmissions(data.recentSubmissions || [])}
            </div>
            <div class="panel">
              <h2>${escapeHtml(t("friends"))}</h2>
              ${renderFriends(friends, data.friendsError)}
            </div>
          </div>
        </div>
      `;
      bindAccountControls();
    }

    function renderAccountForm(data = {}) {
      const auth = data && data.auth ? data.auth : {};
      return `
        <div class="panel">
          <h2>${escapeHtml(t("codeforcesProfile"))}</h2>
          <form id="accountForm" class="account-form">
            <label>
              ${escapeHtml(t("handle"))}
              <input id="accountHandle" name="handle" autocomplete="username" value="${escapeAttr(data && data.handle ? data.handle : "")}" required>
            </label>
            <label>
              ${escapeHtml(t("apiKey"))}
              <input id="accountApiKey" name="apiKey" autocomplete="off" placeholder="${auth.apiKeyConfigured ? t("configured") : t("optional")}">
            </label>
            <label>
              ${escapeHtml(t("apiSecret"))}
              <input id="accountApiSecret" name="apiSecret" type="password" autocomplete="off" placeholder="${auth.apiSecretConfigured ? t("configured") : t("optional")}">
            </label>
            <button id="saveAccount" class="primary" type="submit">${escapeHtml(t("save"))}</button>
          </form>
        </div>
      `;
    }

    function bindAccountControls() {
      const refresh = $("refreshAccount");
      if (refresh) refresh.addEventListener("click", () => loadAccount().catch((error) => renderAccountError(error.message)));
      const form = $("accountForm");
      if (form) form.addEventListener("submit", (event) => {
        event.preventDefault();
        saveAccount().catch((error) => {
          setStatus(error.message || String(error));
        });
      });
    }

    async function saveAccount() {
      const handle = $("accountHandle").value.trim();
      const apiKey = $("accountApiKey").value.trim();
      const apiSecret = $("accountApiSecret").value.trim();
      if (!handle) {
        setStatus("Codeforces handle is required");
        return;
      }
      setStatus("Saving account");
      await api("/api/account", {
        method: "POST",
        body: JSON.stringify({ handle, apiKey, apiSecret }),
      });
      await loadAccount();
      setStatus("Account saved");
    }

    async function loadStats(options = {}) {
      const syncSolved = Boolean(options.syncSolved);
      setStatus(syncSolved ? "Syncing stats" : "Loading stats");
      const data = await api(syncSolved ? "/api/stats?syncSolved=1" : "/api/stats");
      state.stats = data;
      renderStats(data);
      if (syncSolved) {
        await loadProblems();
      }
      setStatus(data.solvedSync ? solvedSyncStatus(data.solvedSync) || "Stats ready" : "Stats ready");
    }

    function renderStatsError(message) {
      $("statsView").innerHTML = `
        <div class="page-shell">
          <div class="page-head">
            <div><h1>${escapeHtml(t("statsTitle"))}</h1><p>${escapeHtml(message || t("statsFailed"))}</p></div>
            <div class="page-actions">
              <button id="refreshStats">${escapeHtml(t("refresh"))}</button>
              <button id="syncStats" class="primary">Sync AC</button>
            </div>
          </div>
        </div>
      `;
      bindStatsActions();
    }

    function renderStats(data) {
      const problems = Array.isArray(data.problems) ? data.problems : [];
      const rated = problems.filter((problem) => Number.isFinite(Number(problem.rating)) && Number(problem.rating) > 0);
      const imported = problems.filter((problem) => problem.local);
      const tagSet = new Set(problems.flatMap((problem) => Array.isArray(problem.tags) ? problem.tags : []));
      const averageRating = rated.length ? Math.round(rated.reduce((sum, problem) => sum + Number(problem.rating), 0) / rated.length) : "-";
      $("statsView").innerHTML = `
        <div class="page-shell">
          <div class="page-head">
            <div>
              <h1>${escapeHtml(t("statsTitle"))}</h1>
              <p>${escapeHtml(data.handle || t("noHandle"))} · ${data.syncedAt ? `${escapeHtml(t("synced"))} ${escapeHtml(formatIso(data.syncedAt))}` : t("noAcSync")}</p>
            </div>
            <div class="page-actions">
              <button id="refreshStats">${escapeHtml(t("refresh"))}</button>
              <button id="syncStats" class="primary">Sync AC</button>
            </div>
          </div>
          <div class="metric-grid">
            ${renderMetricCard(t("solved"), problems.length)}
            ${renderMetricCard(t("imported"), imported.length)}
            ${renderMetricCard(t("rated"), rated.length)}
            ${renderMetricCard(t("avgRating"), averageRating)}
          </div>
          <div class="split-panels">
            <div class="panel">
              <h2>${escapeHtml(t("rootDifficulty"))}</h2>
              ${renderBarChart(entriesFromCounts(countSolvedBy(problems, difficultyLabel)), { empty: t("noSolvedProblems") })}
            </div>
            <div class="panel">
              <h2>${escapeHtml(t("rootTags"))}</h2>
              ${renderBarChart(topEntries(entriesFromCounts(countSolvedTags(problems)), 14), { fillClass: "blue", empty: t("noTags") })}
            </div>
          </div>
          <div class="split-panels">
            <div class="panel">
              <h2>${escapeHtml(t("language"))}</h2>
              ${renderBarChart(topEntries(entriesFromCounts(countSolvedBy(problems, (problem) => problem.programmingLanguage || "Unknown")), 10), { empty: t("noLanguageData") })}
            </div>
            <div class="panel">
              <h2>${escapeHtml(t("recentAC"))}</h2>
              ${renderSolvedTable(problems.slice(0, 8), { compact: true })}
            </div>
          </div>
          <div class="panel">
            <h2>${escapeHtml(t("acceptedProblems"))}</h2>
            ${renderSolvedTable(problems)}
          </div>
        </div>
      `;
      bindStatsActions();
      bindStatsProblemLinks();
    }

    function bindStatsActions() {
      const refresh = $("refreshStats");
      const sync = $("syncStats");
      if (refresh) refresh.addEventListener("click", () => loadStats().catch((error) => renderStatsError(error.message)));
      if (sync) sync.addEventListener("click", () => loadStats({ syncSolved: true }).catch((error) => renderStatsError(error.message)));
    }

    function bindStatsProblemLinks() {
      document.querySelectorAll("[data-stats-problem]").forEach((button) => {
        button.addEventListener("click", () => openStatsProblem(button.dataset.statsProblem).catch((error) => setStatus(error.message)));
      });
    }

    async function openStatsProblem(problemKey) {
      if (!problemKey) return;
      const problem = ((state.stats && state.stats.problems) || []).find((item) => item.problemKey === problemKey) || { problemKey };
      switchView("code");
      await ensureProblemExistsFromStats(problem);
      await selectProblem(problemKey, { sourceName: selectedSourceForProblem(problemKey) });
      setStatus("Problem opened");
    }

    async function ensureProblemExistsFromStats(problem) {
      const key = problem.problemKey;
      if (state.problems.some((item) => item.problemKey === key)) return;
      setStatus("Creating local problem");
      try {
        await api("/api/problems", {
          method: "POST",
          body: JSON.stringify({
            problemKey: key,
            name: problem.name || key,
            url: problem.url || "",
          }),
        });
      } catch (error) {
        if (!String(error.message || error).toLowerCase().includes("already exists")) throw error;
      }
      await loadProblems();
    }

    function renderMetricCard(label, value) {
      return `<div class="metric-card"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`;
    }

    function renderAvatar(profile) {
      const photo = profile.titlePhoto || profile.avatar;
      if (photo) {
        return `<img class="avatar" src="${escapeAttr(photo)}" alt="">`;
      }
      const initial = String(profile.handle || "?").slice(0, 1).toUpperCase();
      return `<div class="avatar avatar-fallback">${escapeHtml(initial)}</div>`;
    }

    function renderFact(label, value) {
      return `<div class="fact"><span>${escapeHtml(label)}</span><strong title="${escapeAttr(value)}">${escapeHtml(value)}</strong></div>`;
    }

    function renderBarChart(entries, options = {}) {
      const list = Array.isArray(entries) ? entries.filter((entry) => Number(entry[1]) > 0) : [];
      if (!list.length) return `<div class="empty">${escapeHtml(options.empty || "No data")}</div>`;
      const max = Math.max(...list.map((entry) => Number(entry[1])));
      return `
        <div class="chart-bars">
          ${list.map(([label, count]) => {
            const width = Math.max(2, Math.round((Number(count) / max) * 100));
            return `
              <div class="bar-row">
                <div class="bar-label" title="${escapeAttr(label)}">${escapeHtml(label)}</div>
                <div class="bar-track"><div class="bar-fill ${options.fillClass || ""}" style="width:${width}%"></div></div>
                <strong>${escapeHtml(count)}</strong>
              </div>
            `;
          }).join("")}
        </div>
      `;
    }

    function renderRatingChart(history) {
      const contests = Array.isArray(history) ? history.filter((item) => Number.isFinite(Number(item.newRating))) : [];
      if (!contests.length) return '<div class="empty">No rated contests</div>';
      const width = 720;
      const height = 220;
      const pad = 28;
      const ratings = contests.map((item) => Number(item.newRating));
      const min = Math.min(...ratings);
      const max = Math.max(...ratings);
      const span = Math.max(1, max - min);
      const points = contests.map((item, index) => {
        const x = pad + (contests.length === 1 ? 0 : (index / (contests.length - 1)) * (width - pad * 2));
        const y = height - pad - ((Number(item.newRating) - min) / span) * (height - pad * 2);
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      }).join(" ");
      const last = contests[contests.length - 1];
      return `
        <svg class="rating-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Rating history">
          <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#d7dde7" />
          <line x1="${pad}" y1="${pad}" x2="${pad}" y2="${height - pad}" stroke="#d7dde7" />
          <text x="${pad}" y="${pad - 8}" fill="#657286" font-size="12">${escapeHtml(max)}</text>
          <text x="${pad}" y="${height - 8}" fill="#657286" font-size="12">${escapeHtml(min)}</text>
          <polyline points="${points}" fill="none" stroke="#2563eb" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" />
          <text x="${width - pad}" y="${pad}" text-anchor="end" fill="#17202f" font-size="13" font-weight="700">${escapeHtml(last.newRating)}</text>
        </svg>
      `;
    }

    function renderRatingHistoryTable(history) {
      const rows = (Array.isArray(history) ? history : [])
        .filter((item) => Number.isFinite(Number(item.newRating)) && Number.isFinite(Number(item.oldRating)))
        .slice()
        .reverse();
      if (!rows.length) return "";
      return `
        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Contest</th>
                <th>Rating</th>
                <th>CF change</th>
                <th>Bonus</th>
                <th>Actual change</th>
              </tr>
            </thead>
            <tbody>
              ${rows.map((item) => {
                const contestNumber = item.contestNumber || "";
                const contest = item.contestName || item.contestId || (contestNumber ? `Contest ${contestNumber}` : "Contest");
                const oldRating = Number(item.oldRating);
                const newRating = Number(item.newRating);
                const ratingChange = Number.isFinite(Number(item.ratingChange))
                  ? Number(item.ratingChange)
                  : newRating - oldRating;
                const bonus = Number.isFinite(Number(item.earlyContestBonus)) ? Number(item.earlyContestBonus) : 0;
                const actualChange = Number.isFinite(Number(item.actualRatingChange))
                  ? Number(item.actualRatingChange)
                  : ratingChange - bonus;
                return `
                  <tr>
                    <td>${escapeHtml(contestNumber || "-")}</td>
                    <td>${escapeHtml(contest)}</td>
                    <td>${escapeHtml(oldRating)} to ${escapeHtml(newRating)}</td>
                    <td>${escapeHtml(signedNumber(ratingChange))}</td>
                    <td>${bonus ? escapeHtml(bonus) : '<span class="small-muted">-</span>'}</td>
                    <td><strong>${escapeHtml(signedNumber(actualChange))}</strong></td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      `;
    }

    function renderRecentSubmissions(submissions) {
      const rows = (Array.isArray(submissions) ? submissions : []).slice(0, 12);
      if (!rows.length) return '<div class="empty">No recent submissions</div>';
      return `
        <div class="data-table-wrap">
          <table class="data-table">
            <thead><tr><th>When</th><th>Problem</th><th>Verdict</th><th>Lang</th></tr></thead>
            <tbody>
              ${rows.map((submission) => {
                const problem = submission.problem || {};
                return `
                  <tr>
                    <td>${escapeHtml(formatDateTime(submission.creationTimeSeconds))}</td>
                    <td>${escapeHtml(problem.problemKey || "")} ${escapeHtml(problem.name || "")}</td>
                    <td><span class="table-pill">${escapeHtml(submission.verdict || "-")}</span></td>
                    <td>${escapeHtml(submission.programmingLanguage || "-")}</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      `;
    }

    function renderFriends(friends, error) {
      if (error) return `<div class="empty">${escapeHtml(error)}</div>`;
      if (!friends.length) return '<div class="empty">No authenticated friend data</div>';
      return `<div class="tag-list">${friends.slice(0, 80).map((friend) => `<span class="table-pill">${escapeHtml(friend)}</span>`).join("")}</div>`;
    }

    function renderSolvedTable(problems, options = {}) {
      const rows = Array.isArray(problems) ? problems : [];
      if (!rows.length) return '<div class="empty">No accepted problems</div>';
      return `
        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Problem</th>
                <th>Rating</th>
                ${options.compact ? "" : "<th>Tags</th>"}
                <th>Lang</th>
                <th>Accepted</th>
                ${options.compact ? "" : "<th>Local</th>"}
              </tr>
            </thead>
            <tbody>
              ${rows.map((problem) => `
                <tr>
                  <td>
                    <button class="problem-link" data-stats-problem="${escapeAttr(problem.problemKey)}" title="${escapeAttr(problem.name || problem.problemKey)}">
                      ${escapeHtml(problem.problemKey)} · ${escapeHtml(problem.name || "")}
                    </button>
                  </td>
                  <td>${escapeHtml(problem.rating || "-")}</td>
                  ${options.compact ? "" : `<td>${renderTagList(problem.tags)}</td>`}
                  <td>${escapeHtml(problem.programmingLanguage || "-")}</td>
                  <td>${escapeHtml(formatDateTime(problem.creationTimeSeconds))}</td>
                  ${options.compact ? "" : `<td>${problem.local ? '<span class="table-pill">Imported</span>' : '<span class="small-muted">API</span>'}</td>`}
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      `;
    }

    function renderTagList(tags) {
      const list = Array.isArray(tags) ? tags : [];
      if (!list.length) return '<span class="small-muted">-</span>';
      return `<div class="tag-list">${list.slice(0, 4).map((tag) => `<span class="table-pill">${escapeHtml(tag)}</span>`).join("")}${list.length > 4 ? `<span class="small-muted">+${list.length - 4}</span>` : ""}</div>`;
    }

    function entriesFromCounts(counts) {
      return Object.entries(counts || {}).sort((a, b) => Number(b[1]) - Number(a[1]) || String(a[0]).localeCompare(String(b[0])));
    }

    function topEntries(entries, limit) {
      return entries.slice(0, limit);
    }

    function countSolvedBy(problems, labeler) {
      const counts = {};
      for (const problem of problems) {
        const label = String(labeler(problem) || "Unknown");
        counts[label] = (counts[label] || 0) + 1;
      }
      return counts;
    }

    function countSolvedTags(problems) {
      const counts = {};
      for (const problem of problems) {
        const tags = Array.isArray(problem.tags) && problem.tags.length ? problem.tags : [t("untagged")];
        for (const tag of tags) {
          const label = String(tag || t("untagged"));
          counts[label] = (counts[label] || 0) + 1;
        }
      }
      return counts;
    }

    function latestRating(history) {
      const list = Array.isArray(history) ? history : [];
      return list.length ? list[list.length - 1].newRating : null;
    }

    function maxRatingFromHistory(history) {
      const ratings = (Array.isArray(history) ? history : []).map((item) => Number(item.newRating)).filter(Number.isFinite);
      return ratings.length ? Math.max(...ratings) : null;
    }

    function signedNumber(value) {
      if (!Number.isFinite(Number(value))) return "-";
      return Number(value) > 0 ? `+${Number(value)}` : String(Number(value));
    }

    function formatDateTime(seconds) {
      const value = Number(seconds);
      if (!Number.isFinite(value) || value <= 0) return "-";
      return new Date(value * 1000).toLocaleString();
    }

    function formatIso(value) {
      if (!value) return "-";
      const date = new Date(value);
      return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
    }

    async function restoreLastEditorDocument() {
      let documentId = "";
      try {
        documentId = localStorage.getItem(LAST_EDITOR_DOCUMENT_STORAGE_KEY) || "";
      } catch (error) {
        return false;
      }
      const problemDocument = parseProblemEditorDocumentId(documentId);
      if (problemDocument) {
        const key = problemDocument.problemKey;
        if (state.problems.some((problem) => problem.problemKey === key)) {
          await selectProblem(key, { sourceName: problemDocument.sourceName });
          return true;
        }
      }
      if (documentId.startsWith("template:")) {
        const parts = documentId.slice("template:".length).split("\\n");
        const algorithm = parts[0] || "";
        const name = parts.slice(1).join("\\n");
        if (algorithm && name && findTemplate(algorithm, name)) {
          await selectTemplate(algorithm, name);
          return true;
        }
      }
      return false;
    }

    function renderProblems() {
      const q = $("filter").value.trim().toLowerCase();
      const list = state.problems.filter((problem) => problemMatchesFilter(problem, q));
      $("problems").innerHTML = renderProblemFolders(list);
      document.querySelectorAll(".problem").forEach((button) => {
        button.addEventListener("click", () => selectProblem(button.dataset.key).catch((error) => setStatus(error.message)));
      });
      document.querySelectorAll(".template-item").forEach((button) => {
        button.addEventListener("click", () => selectTemplate(button.dataset.algorithm, button.dataset.template).catch((error) => setStatus(error.message)));
      });
      document.querySelectorAll("[data-template-action]").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.preventDefault();
          event.stopPropagation();
          if (button.dataset.templateAction === "algorithm") {
            createTemplateAlgorithm().catch((error) => setStatus(error.message));
          } else {
            createTemplateFromPrompt(button.dataset.algorithm || "").catch((error) => setStatus(error.message));
          }
        });
      });
      document.querySelectorAll("#problems details[data-details-key]").forEach((details) => {
        details.addEventListener("toggle", () => setDetailsOpen(details.dataset.detailsKey, details.open));
      });
      setupSidebarDragAndDrop();
    }

    function problemMatchesFilter(problem, query = $("filter").value.trim().toLowerCase()) {
      const haystack = [
        problem.problemKey,
        problem.name,
        contestLabel(problem),
        difficultyLabel(problem),
        ...(problem.tags || []),
      ].join(" ").toLowerCase();
      return !query || haystack.includes(query);
    }

    function renderProblemFolders(list) {
      const workspaceTree = renderWorkspaceFolderRoot(list);
      const recentlyLoadedTree = renderRecentlyLoadedRoot(list);
      const templateTree = renderTemplateRoot();
      const contestTree = list.length ? renderFolderRoot(t("rootContest"), groupByContest(list), { key: "root:contest" }) : "";
      const virtualTrees = list.length
        ? renderFolderRoot(t("rootDifficulty"), groupByDifficulty(list), { key: "root:difficulty", sort: compareDifficultyFolders }) + renderFolderRoot(t("rootTags"), groupByTag(list), { key: "root:tag" })
        : "";
      return workspaceTree + recentlyLoadedTree + templateTree + contestTree + virtualTrees || `<div class="empty">${escapeHtml(t("noMatches"))}</div>`;
    }

    function renderWorkspaceFolderRoot(list) {
      if (!state.folders.length) return "";
      const key = "root:workspace";
      const folderOrderContainer = sidebarOrderContainer(key, "folders");
      return `
        <details class="folder-root" data-details-key="${escapeAttr(key)}"${detailsOpenAttr(key)}>
          <summary class="folder-root-title">${escapeHtml(t("rootFolders"))}</summary>
          ${orderedItemsWithUnclassifiedLast(folderOrderContainer, state.folders, (folder) => folder.name, (folder) => folder.name).map((folder) => {
            const problems = list.filter((problem) => problem.folder === folder.name);
            return renderFolder(folder.name, problems, { deletable: true, key: nestedFolderKey(key, folder.name), orderContainer: folderOrderContainer });
          }).join("")}
        </details>
      `;
    }

    function renderRecentlyLoadedRoot(list) {
      if (state.contestMode || !state.recentlyLoadedProblemKeys.size) return "";
      const problems = list.filter((problem) => state.recentlyLoadedProblemKeys.has(String(problem.problemKey || "")));
      if (!problems.length) return "";
      const key = "root:recently-loaded";
      const problemOrderContainer = sidebarOrderContainer(key, "problems");
      const orderedProblems = orderItems(problemOrderContainer, problems, (problem) => problem.problemKey);
      return `
        <details class="folder-root" data-details-key="${escapeAttr(key)}"${detailsOpenAttr(key)}>
          <summary class="folder-root-title">
            ${escapeHtml(t("recentlyLoaded"))}
            <span class="folder-count">${orderedProblems.length}</span>
          </summary>
          <div class="folder-items">
            ${orderedProblems.map((problem) => renderProblemButton(problem, problemOrderContainer)).join("")}
          </div>
        </details>
      `;
    }

    function renderFolderRoot(title, folders, options = {}) {
      if (!folders || !folders.size) return "";
      const key = options.key || `root:${title}`;
      const folderOrderContainer = sidebarOrderContainer(key, "folders");
      const entries = folderEntriesWithUnclassifiedLast(folders);
      if (typeof options.sort === "function") entries.sort(options.sort);
      const orderedEntries = orderItems(folderOrderContainer, entries, ([folder]) => folder);
      return `
        <details class="folder-root" data-details-key="${escapeAttr(key)}"${detailsOpenAttr(key)}>
          <summary class="folder-root-title">${escapeHtml(title)}</summary>
          ${orderedEntries.map(([folder, problems]) => renderFolder(folder, problems, { key: nestedFolderKey(key, folder), orderContainer: folderOrderContainer })).join("")}
        </details>
      `;
    }

    function renderTemplateRoot() {
      const key = "root:templates";
      const folderOrderContainer = sidebarOrderContainer(key, "folders");
      const algorithms = orderItems(folderOrderContainer, state.templates, (algorithm) => String(algorithm.name || "Algorithm"));
      return `
        <details class="folder-root" data-details-key="${escapeAttr(key)}"${detailsOpenAttr(key)}>
          <summary class="folder-root-title">
            ${escapeHtml(t("rootTemplates"))}
            <span class="root-actions">
              <button data-template-action="algorithm" title="Add algorithm">A+</button>
              <button data-template-action="template" title="Save current source as template">T+</button>
            </span>
          </summary>
          ${algorithms.length ? algorithms.map((algorithm) => renderTemplateAlgorithm(algorithm, { orderContainer: folderOrderContainer })).join("") : `<div class="empty">${escapeHtml(t("noTemplates"))}</div>`}
        </details>
      `;
    }

    function renderTemplateAlgorithm(algorithm, options = {}) {
      const name = String(algorithm.name || "Algorithm");
      const templates = Array.isArray(algorithm.templates) ? algorithm.templates : [];
      const key = nestedFolderKey("root:templates", name);
      const templateOrderContainer = sidebarOrderContainer(key, "templates");
      const dragAttrs = options.orderContainer
        ? ` draggable="true" data-drag-type="folder" data-drag-id="${escapeAttr(name)}" data-drag-container="${escapeAttr(options.orderContainer)}"`
        : "";
      const orderedTemplates = orderItems(templateOrderContainer, templates, (template) => String(template.name || ""));
      return `
        <details class="folder" data-details-key="${escapeAttr(key)}"${detailsOpenAttr(key)} data-context-kind="template-algorithm" data-algorithm="${escapeAttr(name)}"${dragAttrs}>
          <summary class="folder-head" data-context-kind="template-algorithm" data-algorithm="${escapeAttr(name)}">
            <span class="folder-name">${escapeHtml(name)}</span>
            <span class="folder-count">${templates.length}</span>
            <button class="folder-delete" data-template-action="template" data-algorithm="${escapeAttr(name)}" title="Add template">T+</button>
          </summary>
          <div class="folder-items">
            ${orderedTemplates.map((template) => renderTemplateButton(name, template, templateOrderContainer)).join("") || `<div class="empty">${escapeHtml(t("noTemplates"))}</div>`}
          </div>
        </details>
      `;
    }

    function renderTemplateButton(algorithm, template, orderContainer) {
      const name = String(template.name || "");
      const active = state.currentTemplate &&
        state.currentTemplate.algorithm === String(algorithm || "") &&
        state.currentTemplate.name === name;
      return `
        <div class="template-row sidebar-draggable-row" draggable="true" data-drag-type="template" data-drag-id="${escapeAttr(name)}" data-drag-container="${escapeAttr(orderContainer)}" data-context-kind="template" data-algorithm="${escapeAttr(algorithm)}" data-template="${escapeAttr(name)}">
          <button class="template-item ${active ? "active" : ""}" data-algorithm="${escapeAttr(algorithm)}" data-template="${escapeAttr(name)}" title="Edit template">
            <span class="name">${escapeHtml(name || "Template")}</span>
          </button>
        </div>
      `;
    }

    function renderFolder(folder, problems, options = {}) {
      const key = options.key || nestedFolderKey("folder", folder);
      const problemOrderContainer = sidebarOrderContainer(key, "problems");
      const orderedProblems = orderItems(problemOrderContainer, problems, (problem) => problem.problemKey);
      const contextAttrs = options.deletable ? ` data-context-kind="folder" data-folder="${escapeAttr(folder)}"` : "";
      const dragAttrs = options.orderContainer
        ? ` draggable="true" data-drag-type="folder" data-drag-id="${escapeAttr(folder)}" data-drag-container="${escapeAttr(options.orderContainer)}"`
        : "";
      return `
        <details class="folder" data-details-key="${escapeAttr(key)}"${detailsOpenAttr(key)}${contextAttrs}${dragAttrs}>
          <summary class="folder-head"${contextAttrs}>
            <span class="folder-name">${escapeHtml(folder)}</span>
            <span class="folder-count">${problems.length}</span>
          </summary>
          <div class="folder-items">
            ${orderedProblems.map((problem) => renderProblemButton(problem, problemOrderContainer)).join("")}
          </div>
        </details>
      `;
    }

    function nestedFolderKey(parentKey, folder) {
      return `${parentKey}:folder:${String(folder || "")}`;
    }

    function folderEntriesWithUnclassifiedLast(folders) {
      return itemsWithUnclassifiedLast([...folders.entries()], ([folder]) => folder);
    }

    function sidebarOrderContainer(key, kind) {
      return `${kind}:${String(key || "")}`;
    }

    function sidebarOrderList(containerKey) {
      const value = state.sidebarOrder[String(containerKey || "")];
      return Array.isArray(value) ? value.map((item) => String(item)) : [];
    }

    function orderItems(containerKey, items, idForItem) {
      const list = [...items];
      const order = sidebarOrderList(containerKey);
      if (!order.length) return list;
      const positions = new Map(order.map((id, index) => [String(id), index]));
      return list
        .map((item, index) => ({ item, index, id: String(idForItem(item) || "") }))
        .sort((left, right) => {
          const leftRank = positions.has(left.id) ? positions.get(left.id) : Number.MAX_SAFE_INTEGER;
          const rightRank = positions.has(right.id) ? positions.get(right.id) : Number.MAX_SAFE_INTEGER;
          return leftRank - rightRank || left.index - right.index;
        })
        .map((entry) => entry.item);
    }

    function orderedItemsWithUnclassifiedLast(containerKey, items, labelForItem, idForItem = labelForItem) {
      return itemsWithUnclassifiedLast(orderItems(containerKey, items, idForItem), labelForItem);
    }

    function itemsWithUnclassifiedLast(items, labelForItem) {
      const list = [...items];
      const normal = list.filter((item) => !isUnclassifiedFolder(labelForItem(item)));
      const unclassified = list.filter((item) => isUnclassifiedFolder(labelForItem(item)));
      return normal.concat(unclassified);
    }

    function isUnclassifiedFolder(folder) {
      const label = String(folder || "").toLowerCase();
      return label.includes("\\uBBF8\\uBD84\\uB958") ||
        label.includes("unclassified") ||
        label.includes("uncategorized");
    }

    function renderProblemButton(problem, orderContainer) {
      const sourceCount = problemSourceFiles(problem).length;
      return `
        <div class="problem-row sidebar-draggable-row" draggable="true" data-drag-type="problem" data-drag-id="${escapeAttr(problem.problemKey)}" data-drag-container="${escapeAttr(orderContainer)}" data-context-kind="problem" data-key="${escapeAttr(problem.problemKey)}">
          <span class="problem-drag-handle" title="Drag to reorder" aria-hidden="true">::</span>
          <button class="problem ${state.current && state.current.problem.problemKey === problem.problemKey ? "active" : ""}"
            data-key="${escapeAttr(problem.problemKey)}">
            <div class="key">${escapeHtml(problem.problemKey)}</div>
            <div class="name">${escapeHtml(problem.name)}</div>
            ${problem.solved || problem.contestIncluded || sourceCount > 1 ? `
              <div class="problem-tags">
                ${problem.contestIncluded ? '<span class="problem-tag contest">Contest</span>' : ""}
                ${problem.solved ? '<span class="problem-tag solved">AC</span>' : ""}
                ${sourceCount > 1 ? `<span class="problem-tag">${escapeHtml(sourceCount)} files</span>` : ""}
              </div>
            ` : ""}
          </button>
        </div>
      `;
    }

    function handleSidebarContextMenu(event) {
      const target = event.target && event.target.closest ? event.target.closest("[data-context-kind]") : null;
      if (!target || !$("problems").contains(target)) return;
      const items = sidebarContextItems(target);
      if (!items.length) return;
      openContextMenu(event, items);
    }

    function handleOutputContextMenu(event) {
      const target = event.target && event.target.closest ? event.target.closest('[data-context-kind="test"]') : null;
      if (!target || !$("output").contains(target)) return;
      const index = target.dataset.testIndex || "";
      openContextMenu(event, [
        { label: "Rename", action: () => renameTestByIndex(index) },
        { label: "Delete", danger: true, action: () => deleteTestByIndex(index) },
      ]);
    }

    function sidebarContextItems(target) {
      const kind = target.dataset.contextKind || "";
      if (kind === "folder") {
        const folder = target.dataset.folder || "";
        return [
          { label: "Rename", action: () => renameFolderFromPrompt(folder) },
          { label: "Delete", danger: true, action: () => deleteFolder(folder) },
        ];
      }
      if (kind === "problem") {
        const key = target.dataset.key || "";
        const problem = state.problems.find((item) => item.problemKey === key) ||
          (state.current && state.current.problem.problemKey === key ? state.current.problem : null);
        const included = Boolean(problem && problem.contestIncluded);
        return [
          { label: included ? "Remove from contest" : "Add to contest", action: () => setProblemContestIncluded(key, !included) },
          { label: "Rename", action: () => renameProblemFromPrompt(key) },
          { label: "Delete", danger: true, action: () => deleteProblemByKey(key) },
        ];
      }
      if (kind === "template-algorithm") {
        const algorithm = target.dataset.algorithm || "";
        return [
          { label: "Rename", action: () => renameTemplateAlgorithmFromPrompt(algorithm) },
          { label: "Delete", danger: true, action: () => deleteTemplateAlgorithm(algorithm) },
        ];
      }
      if (kind === "template") {
        const algorithm = target.dataset.algorithm || "";
        const template = target.dataset.template || "";
        return [
          { label: "Rename", action: () => renameTemplateFromPrompt(algorithm, template) },
          { label: "Delete", danger: true, action: () => deleteTemplate(algorithm, template) },
        ];
      }
      return [];
    }

    function openContextMenu(event, items) {
      event.preventDefault();
      event.stopPropagation();
      const menu = $("contextMenu");
      if (!menu) return;
      closeContextMenu();
      menu.innerHTML = "";
      for (const item of items) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = item.label;
        if (item.danger) button.classList.add("danger");
        button.addEventListener("click", () => {
          closeContextMenu();
          Promise.resolve(item.action()).catch((error) => setStatus(error.message || String(error)));
        });
        menu.appendChild(button);
      }
      menu.style.left = "0px";
      menu.style.top = "0px";
      menu.hidden = false;
      const rect = menu.getBoundingClientRect();
      const left = Math.max(8, Math.min(event.clientX, window.innerWidth - rect.width - 8));
      const top = Math.max(8, Math.min(event.clientY, window.innerHeight - rect.height - 8));
      menu.style.left = `${left}px`;
      menu.style.top = `${top}px`;
    }

    function closeContextMenu() {
      const menu = $("contextMenu");
      if (!menu) return;
      menu.hidden = true;
      menu.innerHTML = "";
    }

    function setupSidebarDragAndDrop() {
      const root = $("problems");
      if (!root) return;
      root.querySelectorAll('[draggable="true"][data-drag-type]').forEach((item) => {
        item.addEventListener("dragstart", handleSidebarDragStart);
        item.addEventListener("dragover", handleSidebarDragOver);
        item.addEventListener("dragleave", handleSidebarDragLeave);
        item.addEventListener("drop", handleSidebarDrop);
        item.addEventListener("dragend", handleSidebarDragEnd);
      });
    }

    function handleSidebarDragStart(event) {
      if (event.target.closest("[data-template-action], input, textarea, select, a")) {
        event.preventDefault();
        return;
      }
      const item = event.currentTarget;
      state.sidebarDrag = {
        type: item.dataset.dragType || "",
        id: item.dataset.dragId || "",
        container: item.dataset.dragContainer || "",
      };
      if (!state.sidebarDrag.type || !state.sidebarDrag.id || !state.sidebarDrag.container) {
        state.sidebarDrag = null;
        event.preventDefault();
        return;
      }
      item.classList.add("sidebar-dragging-item");
      $("problems").classList.add("sidebar-dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", state.sidebarDrag.id);
      setStatus("Drag to reorder");
    }

    function handleSidebarDragOver(event) {
      const target = event.currentTarget;
      const placement = sidebarDropPlacement(target, event);
      if (!placement) return;
      event.preventDefault();
      event.stopPropagation();
      clearSidebarDropPreview();
      target.classList.add(placement === "before" ? "sidebar-drop-before" : "sidebar-drop-after");
      event.dataTransfer.dropEffect = "move";
    }

    function handleSidebarDragLeave(event) {
      if (event.currentTarget.contains(event.relatedTarget)) return;
      event.currentTarget.classList.remove("sidebar-drop-before", "sidebar-drop-after");
    }

    function handleSidebarDrop(event) {
      const target = event.currentTarget;
      const placement = sidebarDropPlacement(target, event);
      if (!placement || !state.sidebarDrag) return;
      event.preventDefault();
      event.stopPropagation();
      reorderSidebarItem(
        state.sidebarDrag.container,
        state.sidebarDrag.type,
        state.sidebarDrag.id,
        target.dataset.dragId || "",
        placement,
      );
      clearSidebarDropPreview();
      state.sidebarDrag = null;
    }

    function handleSidebarDragEnd() {
      document.querySelectorAll(".sidebar-dragging-item").forEach((item) => item.classList.remove("sidebar-dragging-item"));
      const root = $("problems");
      if (root) root.classList.remove("sidebar-dragging");
      clearSidebarDropPreview();
      state.sidebarDrag = null;
    }

    function sidebarDropPlacement(target, event) {
      const drag = state.sidebarDrag;
      if (!drag) return "";
      if ((target.dataset.dragType || "") !== drag.type) return "";
      if ((target.dataset.dragContainer || "") !== drag.container) return "";
      if ((target.dataset.dragId || "") === drag.id) return "";
      const rect = target.getBoundingClientRect();
      const midpoint = rect.top + rect.height / 2;
      return event.clientY < midpoint ? "before" : "after";
    }

    function clearSidebarDropPreview() {
      document.querySelectorAll(".sidebar-drop-before, .sidebar-drop-after").forEach((item) => {
        item.classList.remove("sidebar-drop-before", "sidebar-drop-after");
      });
    }

    function reorderSidebarItem(containerKey, type, draggedId, targetId, placement) {
      const ids = sidebarVisibleDragIds(containerKey, type);
      const from = ids.indexOf(draggedId);
      if (from === -1 || !targetId) return;
      ids.splice(from, 1);
      const targetIndex = ids.indexOf(targetId);
      if (targetIndex === -1) return;
      ids.splice(targetIndex + (placement === "after" ? 1 : 0), 0, draggedId);
      const previousHidden = sidebarOrderList(containerKey).filter((id) => !ids.includes(id));
      state.sidebarOrder[containerKey] = ids.concat(previousHidden);
      saveSidebarOrder();
      renderProblems();
      setStatus("Order saved");
    }

    function sidebarVisibleDragIds(containerKey, type) {
      const root = $("problems");
      if (!root) return [];
      return [...root.querySelectorAll(`[data-drag-type="${type}"]`)]
        .filter((item) => (item.dataset.dragContainer || "") === containerKey)
        .map((item) => item.dataset.dragId || "")
        .filter(Boolean);
    }

    async function createTemplateAlgorithm() {
      const algorithm = prompt("Algorithm name");
      if (!algorithm || !algorithm.trim()) return;
      setStatus("Saving template");
      const data = await api("/api/templates", {
        method: "POST",
        body: JSON.stringify({ kind: "algorithm", algorithm }),
      });
      state.templates = data.templates || [];
      renderProblems();
      setStatus("Template saved");
    }

    async function createTemplateFromPrompt(defaultAlgorithm = "") {
      const algorithm = prompt("Algorithm", defaultAlgorithm || "");
      if (!algorithm || !algorithm.trim()) return;
      const name = prompt("Template name");
      if (!name || !name.trim()) return;
      setStatus("Saving template");
      const data = await api("/api/templates", {
        method: "POST",
        body: JSON.stringify({ kind: "template", algorithm, name, source: "", extension: ".cpp" }),
      });
      state.templates = data.templates || [];
      renderProblems();
      await selectTemplate(algorithm.trim(), name.trim());
      setStatus("New template ready");
    }

    async function renameTemplateAlgorithmFromPrompt(algorithm) {
      if (!algorithm) return;
      const name = prompt("Algorithm name", algorithm);
      if (!name || !name.trim() || name.trim() === algorithm) return;
      setStatus("Renaming template folder");
      const data = await api("/api/templates/rename", {
        method: "POST",
        body: JSON.stringify({ kind: "algorithm", algorithm, name }),
      });
      state.templates = data.templates || [];
      if (state.currentTemplate && state.currentTemplate.algorithm === algorithm) {
        state.currentTemplate.algorithm = name.trim();
        const selected = findTemplate(state.currentTemplate.algorithm, state.currentTemplate.name);
        if (selected) state.currentTemplate.file = selected.template.file || state.currentTemplate.file;
        $("title").textContent = templateTitle(state.currentTemplate);
        renderTemplateStatement(state.currentTemplate);
        renderTemplateMeta(state.currentTemplate);
        rememberCurrentEditorDocument();
      }
      renderProblems();
      setStatus("Template folder renamed");
    }

    async function renameTemplateFromPrompt(algorithm, templateName) {
      if (!algorithm || !templateName) return;
      const name = prompt("Template name", templateName);
      if (!name || !name.trim() || name.trim() === templateName) return;
      setStatus("Renaming template");
      const data = await api("/api/templates/rename", {
        method: "POST",
        body: JSON.stringify({ kind: "template", algorithm, template: templateName, name }),
      });
      state.templates = data.templates || [];
      if (state.currentTemplate &&
        state.currentTemplate.algorithm === algorithm &&
        state.currentTemplate.name === templateName) {
        state.currentTemplate.name = name.trim();
        const selected = findTemplate(algorithm, state.currentTemplate.name);
        if (selected) state.currentTemplate.file = selected.template.file || state.currentTemplate.file;
        $("title").textContent = templateTitle(state.currentTemplate);
        renderTemplateStatement(state.currentTemplate);
        renderTemplateMeta(state.currentTemplate);
        rememberCurrentEditorDocument();
      }
      renderProblems();
      setStatus("Template renamed");
    }

    async function deleteTemplate(algorithm, templateName) {
      if (!algorithm || !templateName) return;
      if (!confirm(`Delete template "${algorithm} / ${templateName}"?`)) return;
      setStatus("Deleting template");
      const data = await api(`/api/templates?kind=template&algorithm=${encodeURIComponent(algorithm)}&name=${encodeURIComponent(templateName)}`, {
        method: "DELETE",
      });
      state.templates = removeDeletedTemplateFromState(data.templates || state.templates, algorithm, templateName);
      if (state.currentTemplate &&
        state.currentTemplate.algorithm === algorithm &&
        state.currentTemplate.name === templateName) {
        clearCurrentProblem();
      } else {
        renderProblems();
      }
      setStatus("Template deleted");
    }

    async function deleteTemplateAlgorithm(algorithm) {
      if (!algorithm) return;
      if (!confirm(`Delete all templates in "${algorithm}"?`)) return;
      setStatus("Deleting templates");
      const data = await api(`/api/templates?kind=algorithm&algorithm=${encodeURIComponent(algorithm)}`, {
        method: "DELETE",
      });
      state.templates = removeDeletedTemplateAlgorithmFromState(data.templates || state.templates, algorithm);
      if (state.currentTemplate && state.currentTemplate.algorithm === algorithm) {
        clearCurrentProblem();
      } else {
        renderProblems();
      }
      setStatus("Templates deleted");
    }

    function removeDeletedTemplateFromState(templates, algorithm, templateName) {
      const algorithmKey = String(algorithm || "").trim().toLowerCase();
      const templateKey = String(templateName || "").trim().toLowerCase();
      return (Array.isArray(templates) ? templates : []).map((item) => {
        if (String(item.name || "").trim().toLowerCase() !== algorithmKey) return item;
        const nextTemplates = (Array.isArray(item.templates) ? item.templates : [])
          .filter((template) => String(template.name || "").trim().toLowerCase() !== templateKey);
        return nextTemplates.length ? { ...item, templates: nextTemplates } : null;
      }).filter(Boolean);
    }

    function removeDeletedTemplateAlgorithmFromState(templates, algorithm) {
      const algorithmKey = String(algorithm || "").trim().toLowerCase();
      return (Array.isArray(templates) ? templates : [])
        .filter((item) => String(item.name || "").trim().toLowerCase() !== algorithmKey);
    }

    function sourceExtensionFromTemplate(template) {
      const file = String((template && template.file) || "");
      const match = file.match(/(\\.[A-Za-z0-9_+-]+)$/);
      return match ? match[1] : ".cpp";
    }

    function findTemplate(algorithmName, templateName) {
      const algorithm = state.templates.find((item) => String(item.name || "") === String(algorithmName || ""));
      const templates = algorithm && Array.isArray(algorithm.templates) ? algorithm.templates : [];
      const template = templates.find((item) => String(item.name || "") === String(templateName || ""));
      return template ? { algorithm: String(algorithm.name || ""), template } : null;
    }

    function templateEditorState(algorithmName, template) {
      return {
        algorithm: String(algorithmName || ""),
        name: String(template.name || "Template"),
        file: String(template.file || ""),
        source: normalizeEditorText(template.source),
      };
    }

    function resetEditorTabs(source) {
      state.sourceBuffer = normalizeEditorText(source);
      state.editorTab = "source";
      showEditorText(state.sourceBuffer, { readOnly: false });
      renderEditorTabs();
    }

    function showEditorText(text, options = {}) {
      setCodeEditorText(text, options);
    }

    function normalizeEditorText(text) {
      return String(text || "").replace(/\t/g, "    ");
    }

    function normalizeCodeValueTabs(code) {
      if (!code || !code.value.includes("\t")) return false;
      const start = code.selectionStart;
      const end = code.selectionEnd;
      const beforeStart = code.value.slice(0, start);
      const beforeEnd = code.value.slice(0, end);
      code.value = normalizeEditorText(code.value);
      code.selectionStart = normalizeEditorText(beforeStart).length;
      code.selectionEnd = normalizeEditorText(beforeEnd).length;
      return true;
    }

    function captureCodeViewport() {
      const ide = monacoIde();
      if (ide && typeof ide.captureViewport === "function") {
        return {
          kind: "monaco",
          documentId: currentEditorDocumentId(),
          editorTab: state.editorTab,
          snapshot: ide.captureViewport(),
        };
      }
      const code = $("code");
      if (!code) return null;
      return {
        documentId: currentEditorDocumentId(),
        editorTab: state.editorTab,
        active: document.activeElement === code,
        value: code.value,
        selectionStart: code.selectionStart,
        selectionEnd: code.selectionEnd,
        scrollTop: code.scrollTop,
        scrollLeft: code.scrollLeft,
      };
    }

    function restoreCodeViewport(snapshot) {
      if (snapshot && snapshot.kind === "monaco") {
        const ide = monacoIde();
        if (!ide || snapshot.documentId !== currentEditorDocumentId()) return;
        if (snapshot.editorTab !== state.editorTab) return;
        ide.restoreViewport(snapshot.snapshot);
        return;
      }
      const code = $("code");
      if (!code || !snapshot) return;
      if (snapshot.documentId !== currentEditorDocumentId()) return;
      if (snapshot.editorTab !== state.editorTab) return;
      const normalizedSnapshot = normalizeEditorText(snapshot.value);
      if (code.value !== snapshot.value && code.value !== normalizedSnapshot) return;
      const start = clampEditorIndex(snapshot.selectionStart, code.value.length);
      const end = clampEditorIndex(snapshot.selectionEnd, code.value.length);
      if (snapshot.active) code.focus({ preventScroll: true });
      code.selectionStart = start;
      code.selectionEnd = end;
      code.scrollTop = snapshot.scrollTop;
      code.scrollLeft = snapshot.scrollLeft;
      updateCodeHighlight();
      code.scrollTop = snapshot.scrollTop;
      code.scrollLeft = snapshot.scrollLeft;
      syncCodeScroll();
    }

    function restoreCodeViewportAfterLayout(snapshot) {
      restoreCodeViewport(snapshot);
      requestAnimationFrame(() => restoreCodeViewport(snapshot));
    }

    async function saveFromCodeShortcut() {
      const snapshot = captureCodeViewport();
      try {
        await saveSource();
      } finally {
        restoreCodeViewportAfterLayout(snapshot);
      }
    }

    function mainSourceValue() {
      return state.editorTab === "source" ? codeEditorValue() : state.sourceBuffer;
    }

    function captureSourceBuffer() {
      if (state.editorTab === "source") state.sourceBuffer = codeEditorValue();
    }

    function captureCurrentEditorBuffer() {
      if (state.editorTab === "source") {
        state.sourceBuffer = codeEditorValue();
      }
    }

    function renderEditorTabs() {
      const tabs = $("editorTabs");
      const sourceTabs = state.currentTemplate
        ? [{ id: "source", type: "source", label: state.currentTemplate.file || state.currentTemplate.name || "template", closeable: false }]
        : (state.current
          ? problemSourceFiles(state.current.problem).map((file) => ({
              id: `source:${file.name}`,
              type: "source",
              sourceName: file.name,
              label: file.name,
              closeable: false,
            }))
          : [{ id: "source", type: "source", label: "main.cpp", closeable: false }]);
      const visibleTabs = sourceTabs;
      tabs.innerHTML = visibleTabs.map((tab) => {
        const label = `${tab.label}${tab.dirty ? " *" : ""}`;
        const title = tab.path ? `${tab.label} - ${tab.path}` : tab.label;
        const active = tab.type === "source"
          ? state.editorTab === "source" && (!tab.sourceName || tab.sourceName === currentSourceName())
          : state.editorTab === tab.id;
        return `
        <button class="editor-tab ${active ? "active" : ""}" data-editor-tab="${escapeAttr(tab.id)}"${tab.sourceName ? ` data-source-name="${escapeAttr(tab.sourceName)}"` : ""} title="${escapeAttr(title)}">
          <span class="editor-tab-name">${escapeHtml(label)}</span>
        </button>
      `;
      }).join("") + (state.current && !state.currentTemplate ? '<button class="editor-tab editor-tab-add" data-add-source title="New source file">+</button>' : "");
      tabs.querySelectorAll("[data-editor-tab]").forEach((button) => {
        button.addEventListener("click", (event) => {
          if (event.target.closest("[data-close-editor-tab]")) return;
          Promise.resolve(selectEditorTab(button.dataset.editorTab)).catch((error) => setStatus(error.message));
        });
        button.addEventListener("contextmenu", (event) => {
          const sourceName = button.dataset.sourceName || "";
          if (!sourceName || state.currentTemplate) return;
          openContextMenu(event, [
            { label: "Delete", danger: true, action: () => deleteSourceFile(sourceName) },
          ]);
        });
      });
      tabs.querySelectorAll("[data-add-source]").forEach((button) => {
        button.addEventListener("click", () => createSourceFileFromPrompt().catch((error) => setStatus(error.message)));
      });
    }

    async function selectEditorTab(tabId) {
      if (!tabId) return;
      if (tabId.startsWith("source:")) {
        const sourceName = tabId.slice("source:".length);
        if (!sourceName || sourceName === currentSourceName()) return;
        await selectProblemSource(sourceName);
        return;
      }
      if (tabId === state.editorTab) return;
      captureCurrentEditorBuffer();
      if (tabId === "source") {
        state.editorTab = "source";
        showEditorText(state.sourceBuffer, { readOnly: false });
      }
      renderEditorTabs();
      updateToolbarMode();
    }

    function refreshCurrentTemplateFromStore() {
      const selected = findTemplate(state.currentTemplate.algorithm, state.currentTemplate.name);
      if (!selected) {
        clearCurrentProblem();
        return;
      }
      state.currentTemplate = templateEditorState(selected.algorithm, selected.template);
      state.lastSavedSource = normalizeEditorText(state.currentTemplate.source);
      $("title").textContent = templateTitle(state.currentTemplate);
      resetEditorTabs(state.currentTemplate.source);
      renderTemplateStatement(state.currentTemplate);
      renderTemplateMeta(state.currentTemplate);
    }

    async function selectTemplate(algorithmName, templateName) {
      if (!(await saveDirtyEditorBeforeSwitch())) return;
      const selected = findTemplate(algorithmName, templateName);
      if (!selected) return;
      state.current = null;
      state.currentTemplate = templateEditorState(selected.algorithm, selected.template);
      rememberCurrentEditorDocument();
      const documentId = currentEditorDocumentId();
      const restored = restoredEditorSource(documentId, state.currentTemplate.source);
      state.dirty = restored.restored;
      state.lastSavedSource = normalizeEditorText(state.currentTemplate.source);
      $("title").textContent = templateTitle(state.currentTemplate);
      resetEditorTabs(restored.source);
      renderTemplateStatement(state.currentTemplate);
      renderTemplateMeta(state.currentTemplate);
      renderResults(null);
      renderProblems();
      updateToolbarMode();
      if (state.dirty) {
        setStatus("Draft restored");
        scheduleAutoSave();
      } else {
        setStatus("Template ready");
      }
    }

    function templateTitle(template) {
      return `Template - ${template.algorithm} / ${template.name}`;
    }

    function renderTemplateStatement(template) {
      $("statementPane").innerHTML = `
        <div class="statement-shell">
          <div class="statement-title">
            <h1>${escapeHtml(template.name)}</h1>
            <div class="statement-facts">
              <span>Template</span>
              <span>${escapeHtml(template.algorithm)}</span>
              ${template.file ? `<span>${escapeHtml(template.file)}</span>` : ""}
            </div>
          </div>
        </div>
      `;
    }

    function renderTemplateMeta(template) {
      $("meta").innerHTML = `
        <h2>${escapeHtml(template.name)}</h2>
        <div class="meta-row"><span>Type</span><span>Template</span></div>
        <div class="meta-row"><span>Algorithm</span><span>${escapeHtml(template.algorithm)}</span></div>
        <div class="meta-row"><span>File</span><span>${escapeHtml(template.file || "-")}</span></div>
      `;
    }

    function groupByDifficulty(list) {
      const folders = new Map();
      for (const problem of list) {
        const folder = difficultyLabel(problem);
        if (!folders.has(folder)) folders.set(folder, []);
        folders.get(folder).push(problem);
      }
      return folders;
    }

    function groupByContest(list) {
      const folders = new Map();
      for (const problem of list) {
        const contest = problem.contest || null;
        if (!contest || !contest.key) continue;
        if (!isContestIncludedProblem(problem)) continue;
        const label = contestFolderLabel(contest);
        if (!folders.has(label)) folders.set(label, []);
        folders.get(label).push(problem);
      }
      return folders;
    }

    function isContestIncludedProblem(problem) {
      return Boolean(problem && problem.contestIncluded);
    }

    function groupByTag(list) {
      const folders = new Map();
      for (const problem of list) {
        const tags = Array.isArray(problem.tags) && problem.tags.length ? problem.tags : [t("untagged")];
        for (const tag of tags) {
          const folder = String(tag || t("untagged"));
          if (!folders.has(folder)) folders.set(folder, []);
          folders.get(folder).push(problem);
        }
      }
      return folders;
    }

    function contestLabel(problem) {
      const contest = problem && problem.contest;
      if (contest && contest.label) return String(contest.label);
      if (problem && problem.contestId) return `Contest ${problem.contestId}`;
      return "";
    }

    function contestFolderLabel(contest) {
      const fallback = contest && contest.key ? String(contest.key) : "Contest";
      const raw = String((contest && contest.label) || fallback).trim();
      if (!raw) return fallback;
      const withoutPrefix = raw
        .replace(/^\\d+\\s*-\\s*/, "")
        .replace(/^(?:Codeforces\\s*-\\s*)+/i, "")
        .trim();
      const codeforcesRound = withoutPrefix.match(/^(?:Codeforces\\s+)?(?:(Beta)\\s+)?Round\\s+#?(\\d+)(.*)$/i);
      if (codeforcesRound) {
        return `${codeforcesRound[1] ? "Beta Round" : "Round"} ${codeforcesRound[2]}${codeforcesRound[3] || ""}`.trim();
      }
      const educationalRound = withoutPrefix.match(/^Educational\\s+Codeforces\\s+Round\\s+#?(\\d+)(.*)$/i);
      if (educationalRound) {
        return `Educational Round ${educationalRound[1]}${educationalRound[2] || ""}`.trim();
      }
      return withoutPrefix || raw;
    }

    function difficultyLabel(problem) {
      const rating = Number(problem.rating);
      if (!Number.isFinite(rating) || rating <= 0) return t("unratedDifficulty");
      return `${Math.floor(rating / 100) * 100}`;
    }

    function compareDifficultyFolders(a, b) {
      const left = Number(a[0]);
      const right = Number(b[0]);
      const leftRated = Number.isFinite(left);
      const rightRated = Number.isFinite(right);
      if (leftRated && rightRated) return right - left;
      if (leftRated) return -1;
      if (rightRated) return 1;
      return String(a[0]).localeCompare(String(b[0]));
    }

    async function selectProblem(key, options = {}) {
      if (!(await saveDirtyEditorBeforeSwitch())) return;
      const previousProblemKey = state.current && state.current.problem && state.current.problem.problemKey;
      const preserveEditorTab = Boolean(options.preserveEditorTab) && previousProblemKey === key;
      const previousViewport = preserveEditorTab ? captureCodeViewport() : null;
      const sourceName = selectedSourceForProblem(key, options.sourceName || (preserveEditorTab ? currentSourceName() : ""));
      setStatus("Opening");
      const data = await api(`/api/problems/${encodeURIComponent(key)}?sourceName=${encodeURIComponent(sourceName)}`);
      state.current = data;
      state.current.sourceName = data.sourceName || sourceName || "main.cpp";
      applyCurrentIdePayload(data);
      state.currentTemplate = null;
      mergeProblemIntoList(data.problem);
      rememberProblemSource(key, state.current.sourceName);
      rememberCurrentEditorDocument();
      const documentId = currentEditorDocumentId();
      const restored = restoredEditorSource(documentId, data.source);
      state.dirty = restored.restored;
      state.lastSavedSource = normalizeEditorText(data.source);
      $("title").textContent = `${data.problem.problemKey} - ${data.problem.name}`;
      resetEditorTabs(restored.source);
      renderMeta(data.problem);
      renderStatement(data.problem);
      renderResults(null);
      renderProblems();
      updateToolbarMode();
      if (preserveEditorTab) restoreCodeViewportAfterLayout(previousViewport);
      if (state.dirty) {
        setStatus("Draft restored");
        scheduleAutoSave();
      } else {
        setStatus("Ready");
      }
    }

    async function selectProblemSource(sourceName) {
      if (!state.current || state.currentTemplate) return;
      const key = state.current.problem.problemKey;
      if (!(await saveDirtyEditorBeforeSwitch())) return;
      setStatus("Opening source");
      const data = await api(`/api/problems/${encodeURIComponent(key)}?sourceName=${encodeURIComponent(sourceName)}`);
      if (!state.current || state.current.problem.problemKey !== key) return;
      state.current.problem = data.problem;
      mergeProblemIntoList(data.problem);
      state.current.sourceName = data.sourceName || sourceName;
      state.current.source = data.source;
      applyCurrentIdePayload(data);
      rememberProblemSource(key, state.current.sourceName);
      rememberCurrentEditorDocument();
      const documentId = currentEditorDocumentId();
      const restored = restoredEditorSource(documentId, data.source);
      state.dirty = restored.restored;
      state.lastSavedSource = normalizeEditorText(data.source);
      $("title").textContent = `${data.problem.problemKey} - ${data.problem.name}`;
      resetEditorTabs(restored.source);
      renderMeta(data.problem);
      renderStatement(data.problem);
      renderResults(null);
      renderProblems();
      updateToolbarMode();
      setStatus(state.dirty ? "Draft restored" : `Source: ${state.current.sourceName}`);
      if (state.dirty) scheduleAutoSave();
    }

    async function createSourceFileFromPrompt() {
      if (!state.current || state.currentTemplate) return;
      if (!(await saveDirtyEditorBeforeSwitch())) return;
      const key = state.current.problem.problemKey;
      setStatus("Creating source");
      const data = await api(`/api/problems/${encodeURIComponent(key)}/sources`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      if (!state.current || state.current.problem.problemKey !== key) return;
      state.current.problem = data.problem;
      mergeProblemIntoList(data.problem);
      state.current.sourceName = data.sourceName || "main.cpp";
      state.current.source = data.source;
      applyCurrentIdePayload(data);
      rememberProblemSource(key, state.current.sourceName);
      rememberCurrentEditorDocument();
      state.dirty = false;
      state.lastSavedSource = normalizeEditorText(data.source);
      resetEditorTabs(data.source);
      renderMeta(data.problem);
      renderStatement(data.problem);
      renderResults(null);
      renderProblems();
      updateToolbarMode();
      setStatus(`Created ${state.current.sourceName}`);
    }

    async function deleteSourceFile(sourceName) {
      if (!state.current || state.currentTemplate || !sourceName) return;
      const key = state.current.problem.problemKey;
      const deletingCurrent = sourceName === currentSourceName();
      const suffix = deletingCurrent && state.dirty ? " Unsaved edits will be discarded." : "";
      if (!confirm(`Delete source file "${sourceName}"?${suffix}`)) return;
      if ((!deletingCurrent || state.editorTab !== "source") && !(await saveDirtyEditorBeforeSwitch())) return;
      cancelDraftSave();
      cancelAutoSave();
      setStatus("Deleting source");
      const data = await api(`/api/problems/${encodeURIComponent(key)}/sources?sourceName=${encodeURIComponent(sourceName)}`, {
        method: "DELETE",
      });
      if (!state.current || state.current.problem.problemKey !== key) return;
      if (!deletingCurrent) {
        captureSourceBuffer();
        state.current.problem = data.problem;
        mergeProblemIntoList(data.problem);
        rememberCurrentEditorDocument();
        renderMeta(data.problem);
        renderEditorTabs();
        renderProblems();
        updateToolbarMode();
        setStatus(`Deleted ${sourceName}`);
        return;
      }
      state.current.problem = data.problem;
      mergeProblemIntoList(data.problem);
      state.current.sourceName = data.sourceName || selectedSourceForProblem(key);
      state.current.source = data.source;
      applyCurrentIdePayload(data);
      rememberProblemSource(key, state.current.sourceName);
      rememberCurrentEditorDocument();
      state.dirty = false;
      state.lastSavedSource = normalizeEditorText(data.source);
      resetEditorTabs(data.source);
      renderMeta(data.problem);
      renderStatement(data.problem);
      renderResults(null);
      renderProblems();
      updateToolbarMode();
      setStatus(`Deleted ${sourceName}`);
    }

    function clearCurrentProblem() {
      cancelAutoSave();
      state.current = null;
      state.currentTemplate = null;
      state.dirty = false;
      state.lastSavedSource = "";
      state.sourceBuffer = "";
      state.editorTab = "source";
      forgetCurrentEditorDocument();
      $("title").textContent = "No problem selected";
      showEditorText("", { readOnly: false });
      renderEditorTabs();
      $("meta").innerHTML = '<h2>No problem selected</h2>';
      $("output").innerHTML = "";
      $("statementPane").innerHTML = "";
      renderProblems();
      updateToolbarMode();
    }

    function renderMeta(problem) {
      $("meta").innerHTML = `
        <h2>${escapeHtml(problem.name)}</h2>
        <div class="meta-row"><span>Key</span><span>${escapeHtml(problem.problemKey)}</span></div>
        ${problem.contest ? `<div class="meta-row"><span>Contest</span><span>${escapeHtml(problem.contest.label || problem.contest.key)}</span></div>` : ""}
        ${problem.solved ? `<div class="meta-row"><span>Status</span><span>AC ${escapeHtml(problem.solved.submissionId || "")}</span></div>` : ""}
        <div class="meta-row"><span>Source</span><span>${escapeHtml(currentSourceName())}</span></div>
        <div class="meta-row"><span>Limit</span><span>${problem.timeLimitMs || "?"} ms / ${problem.memoryLimitMb || "?"} MB</span></div>
        <div class="meta-row"><span>Samples</span><span>${problem.tests.length}</span></div>
        <div class="meta-row"><span>URL</span><a href="${escapeAttr(problem.url)}" target="_blank">${escapeHtml(problem.url)}</a></div>
      `;
    }

    function renderStatement(problem) {
      const capturedHtml = problem.statement && problem.statement.capture && problem.statement.capture.html;
      if (capturedHtml) {
        $("statementPane").innerHTML = `
          <div class="statement-shell">
            <div class="captured-statement-shell">
              <iframe id="statementFrame" class="statement-frame" sandbox referrerpolicy="no-referrer"></iframe>
            </div>
          </div>
        `;
        $("statementFrame").srcdoc = buildCapturedStatementDoc(capturedHtml);
        return;
      }
      const sections = (problem.statement && problem.statement.sections) || [];
      const statementSections = sections.length
        ? sections.map((section) => `
            <div class="statement-section">
              <h2>${escapeHtml(section.title)}</h2>
              <p>${renderStatementText(section.text)}</p>
            </div>
          `).join("")
        : `<div class="statement-section"><h2>Statement</h2><p>Competitive Companion's standard payload does not include the full statement text or original page HTML. Open CF for the original problem page.</p></div>`;
      $("statementPane").innerHTML = `
        <div class="statement-shell">
          <div class="statement-title">
            <h1>${escapeHtml(problem.name)}</h1>
            <div class="statement-facts">
              <span>${escapeHtml(problem.problemKey)}</span>
              <span>${problem.timeLimitMs || "?"} ms</span>
              <span>${problem.memoryLimitMb || "?"} MB</span>
              ${problem.group ? `<span>${escapeHtml(problem.group)}</span>` : ""}
            </div>
          </div>
          ${statementSections}
        </div>
      `;
    }

    function renderStatementText(text) {
      const source = String(text || "");
      const parts = [];
      let cursor = 0;
      source.replace(/\\$([^$\\n]{1,500})\\$/g, (match, math, offset) => {
        if (offset > cursor) parts.push(escapeHtml(source.slice(cursor, offset)));
        parts.push(renderStatementMath(math));
        cursor = offset + match.length;
        return match;
      });
      if (cursor < source.length) parts.push(escapeHtml(source.slice(cursor)));
      return parts.join("");
    }

    function renderStatementMath(math) {
      const normalized = String(math || "").trim();
      if (!normalized) return "";
      return `<math class="statement-math" xmlns="http://www.w3.org/1998/Math/MathML"><mrow>${renderMathMlTokens(normalized)}</mrow></math>`;
    }

    function renderMathMlTokens(value) {
      const atoms = [];
      for (let index = 0; index < value.length; index += 1) {
        const char = value[index];
        if (char === "\\\\" && index + 1 < value.length) {
          const command = readMathCommand(value, index + 1);
          if (command) {
            if (command.name === "frac") {
              const numerator = readMathGroup(value, command.end);
              const denominator = numerator ? readMathGroup(value, numerator.end) : null;
              if (numerator && denominator) {
                atoms.push(mathAtom(`<mfrac><mrow>${renderMathMlTokens(numerator.value)}</mrow><mrow>${renderMathMlTokens(denominator.value)}</mrow></mfrac>`));
                index = denominator.end - 1;
                continue;
              }
            }
            if (command.name === "sqrt") {
              const radicand = readMathGroup(value, command.end);
              if (radicand) {
                atoms.push(mathAtom(`<msqrt><mrow>${renderMathMlTokens(radicand.value)}</mrow></msqrt>`));
                index = radicand.end - 1;
                continue;
              }
            }
            atoms.push(mathAtom(renderMathCommand(command.name)));
            index = command.end - 1;
            continue;
          }
        }
        if ((char === "_" || char === "^") && atoms.length) {
          const group = readMathGroup(value, index + 1);
          if (group) {
            const script = `<mrow>${renderMathMlTokens(group.value)}</mrow>`;
            const atom = atoms[atoms.length - 1];
            if (char === "_") atom.sub = script;
            else atom.sup = script;
            index = group.end - 1;
            continue;
          }
        }
        if (/\\d/.test(char)) {
          const number = readWhile(value, index, /[0-9.]/);
          atoms.push(mathAtom(`<mn>${escapeHtml(number.value)}</mn>`));
          index = number.end - 1;
          continue;
        }
        if (/[+\\-=<>\\u2264\\u2265\\u00d7\\u00f7,.;:()\\[\\]{}|]/.test(char)) {
          atoms.push(mathAtom(`<mo>${escapeHtml(char)}</mo>`));
          continue;
        }
        if (/\\s/.test(char)) {
          atoms.push(mathAtom("<mspace width='0.28em'></mspace>"));
          continue;
        }
        atoms.push(mathAtom(`<mi>${escapeHtml(char)}</mi>`));
      }
      return atoms.map(renderMathAtom).join("");
    }

    function mathAtom(base) {
      return { base, sub: "", sup: "" };
    }

    function renderMathAtom(atom) {
      if (atom.sub && atom.sup) return `<msubsup>${atom.base}${atom.sub}${atom.sup}</msubsup>`;
      if (atom.sub) return `<msub>${atom.base}${atom.sub}</msub>`;
      if (atom.sup) return `<msup>${atom.base}${atom.sup}</msup>`;
      return atom.base;
    }

    function readMathCommand(value, start) {
      const match = /^[A-Za-z]+/.exec(value.slice(start));
      if (!match) return null;
      return { name: match[0], end: start + match[0].length };
    }

    function renderMathCommand(name) {
      const symbols = {
        le: ["mo", "\\u2264"],
        leq: ["mo", "\\u2264"],
        ge: ["mo", "\\u2265"],
        geq: ["mo", "\\u2265"],
        neq: ["mo", "\\u2260"],
        ne: ["mo", "\\u2260"],
        cdot: ["mo", "\\u00b7"],
        times: ["mo", "\\u00d7"],
        div: ["mo", "\\u00f7"],
        dots: ["mo", "\\u2026"],
        ldots: ["mo", "\\u2026"],
        infty: ["mo", "\\u221e"],
        alpha: ["mi", "\\u03b1"],
        beta: ["mi", "\\u03b2"],
        gamma: ["mi", "\\u03b3"],
        delta: ["mi", "\\u03b4"],
        epsilon: ["mi", "\\u03b5"],
        lambda: ["mi", "\\u03bb"],
        mu: ["mi", "\\u03bc"],
        pi: ["mi", "\\u03c0"],
        sigma: ["mi", "\\u03c3"],
      };
      const symbol = symbols[name];
      if (symbol) return `<${symbol[0]}>${escapeHtml(symbol[1])}</${symbol[0]}>`;
      return `<mtext>${escapeHtml(name)}</mtext>`;
    }

    function readMathGroup(value, start) {
      if (start >= value.length) return null;
      if (value[start] === "{") {
        let depth = 1;
        for (let index = start + 1; index < value.length; index += 1) {
          if (value[index] === "{") depth += 1;
          if (value[index] === "}") depth -= 1;
          if (depth === 0) {
            return { value: value.slice(start + 1, index), end: index + 1 };
          }
        }
        return null;
      }
      if (value[start] === "\\\\") {
        const command = readMathCommand(value, start + 1);
        if (command) return { value: value.slice(start, command.end), end: command.end };
      }
      return { value: value[start], end: start + 1 };
    }

    function readWhile(value, start, pattern) {
      let end = start;
      while (end < value.length && pattern.test(value[end])) end += 1;
      return { value: value.slice(start, end), end };
    }

    function prepareCapturedStatementFragment(fragment) {
      const template = document.createElement("template");
      template.innerHTML = fragment || "";
      cleanupCapturedMath(template.content);
      return template.innerHTML;
    }

    function cleanupCapturedMath(root) {
      root.querySelectorAll(".MathJax_Preview").forEach((preview) => {
        const next = preview.nextElementSibling;
        if (next && (next.matches(".MathJax:not(.MathJax_Processing)") || next.matches("mjx-container"))) {
          preview.remove();
        }
      });
      root.querySelectorAll(".MathJax_Processing").forEach((node) => node.remove());
    }

    function buildCapturedStatementDoc(fragment) {
      const preparedFragment = prepareCapturedStatementFragment(fragment);
      return `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <base target="_blank">
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 20px 24px 28px;
      background: #fff;
      color: #222;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 14px;
      line-height: 1.45;
    }
    a { color: #1f4f9a; }
    .problem-statement {
      width: 100%;
      max-width: none;
      margin: 0;
    }
    .problem-statement .header { margin-bottom: 1.1em; }
    .problem-statement .title {
      margin: 0.25em 0 0.8em;
      text-align: center;
      font-size: 1.55em;
      font-weight: 700;
      line-height: 1.25;
    }
    .problem-statement .time-limit,
    .problem-statement .memory-limit {
      text-align: center;
      font-size: 0.92em;
      color: #333;
      margin: 0.2em 0;
    }
    .problem-statement .input-file,
    .problem-statement .output-file,
    .problem-statement .sample-test {
      display: none !important;
    }
    .problem-statement .sample-test:first-child,
    .problem-statement .section-title:has(+ .sample-test) {
      display: none !important;
    }
    .problem-statement .section-title {
      margin: 1.1em 0 0.55em;
      font-size: 1.15em;
      font-weight: 700;
    }
    .problem-statement p { margin: 0.65em 0; }
    .problem-statement .tex-span {
      display: inline-block;
      margin: 0 0.1em;
      color: #111827;
      font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif;
      font-size: 1.16em;
      line-height: 1;
      white-space: nowrap;
      vertical-align: -0.08em;
    }
    .problem-statement .tex-span i {
      font-style: italic;
    }
    .problem-statement .tex-span sup,
    .problem-statement .tex-span sub {
      font-size: 0.72em;
      line-height: 0;
    }
    .problem-statement ul,
    .problem-statement ol { padding-left: 1.8em; }
    .problem-statement table {
      border-collapse: collapse;
      margin: 0.8em 0;
      width: auto;
      max-width: 100%;
    }
    .problem-statement th,
    .problem-statement td {
      border: 1px solid #d7d7d7;
      padding: 0.35em 0.5em;
      vertical-align: top;
    }
    .problem-statement .sample-test {
      margin-top: 1em;
    }
    .problem-statement .sample-test .input,
    .problem-statement .sample-test .output {
      border: 1px solid #cfcfcf;
      border-radius: 3px;
      margin: 0.7em 0;
      overflow: hidden;
      background: #fafafa;
    }
    .problem-statement .sample-test .title {
      margin: 0;
      padding: 0.35em 0.55em;
      text-align: left;
      font-size: 0.9em;
      font-weight: 700;
      background: #f1f1f1;
      border-bottom: 1px solid #d7d7d7;
    }
    .problem-statement pre {
      margin: 0;
      padding: 0.65em 0.75em;
      white-space: pre-wrap;
      overflow: auto;
      font-family: "Cascadia Code", "Consolas", monospace;
      font-size: 0.95em;
      line-height: 1.4;
      background: #fff;
    }
    .problem-statement img,
    .problem-statement svg {
      max-width: 100%;
      height: auto;
    }
    .problem-statement .MathJax_Processing {
      display: none !important;
    }
    .problem-statement .MathJax:not([data-cfw-math-snapshot]),
    .problem-statement .MathJax_Preview:not([data-cfw-math-snapshot]) {
      color: inherit;
      font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif;
      font-size: 1.16em !important;
      line-height: normal;
      margin: 0 0.12em;
      vertical-align: -0.08em;
    }
    .problem-statement .MathJax_Display {
      display: block;
      text-align: center;
      margin: 1em 0;
    }
    .problem-statement .MJX_Assistive_MathML {
      position: absolute !important;
      width: 1px !important;
      height: 1px !important;
      overflow: hidden !important;
      clip: rect(1px, 1px, 1px, 1px) !important;
      white-space: nowrap !important;
    }
    .problem-statement .MJXp-math:not([data-cfw-math-snapshot]) {
      display: inline-block;
      white-space: nowrap;
      border-collapse: collapse;
      line-height: 1.2;
      text-indent: 0;
      font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif;
      font-size: 1.12em !important;
    }
    .problem-statement .MJXp-mi,
    .problem-statement .MJXp-mo,
    .problem-statement .MJXp-mn,
    .problem-statement .MJXp-mtext,
    .problem-statement .MJXp-mrow,
    .problem-statement .MJXp-msubsup {
      display: inline-block;
    }
    .problem-statement .MJXp-italic {
      font-style: italic;
    }
    .problem-statement .MJXp-script {
      font-size: 0.75em !important;
      line-height: 0;
    }
    .problem-statement [data-cfw-math-snapshot] {
      max-width: none;
    }
    .problem-statement .MJXp-script:not([data-cfw-math-snapshot]) {
      font-size: 0.75em !important;
    }
    mjx-container { overflow-x: auto; overflow-y: hidden; max-width: 100%; }
  </style>
</head>
<body>${preparedFragment}</body>
</html>`;
    }

    async function saveSource(options = {}) {
      const autosave = Boolean(options.autosave);
      const expectedDocumentId = options.expectedDocumentId || "";
      if (!autosave) cancelAutoSave();
      if (state.currentTemplate) {
        await saveTemplateSource(options);
        return;
      }
      if (!state.current) return;
      const problemKey = state.current.problem.problemKey;
      const sourceName = currentSourceName();
      const documentId = problemEditorDocumentId(problemKey, sourceName);
      if (expectedDocumentId && expectedDocumentId !== documentId) return;
      captureSourceBuffer();
      const source = Object.prototype.hasOwnProperty.call(options, "source") ? options.source : mainSourceValue();
      if (source === state.lastSavedSource && state.dirty) {
        state.dirty = false;
        state.sourceBuffer = source;
        cancelDraftSave();
        clearEditorDraft(documentId);
        setStatus(autosave ? "Autosaved" : "Saved");
        return;
      }
      setStatus(autosave ? "Autosaving" : "Saving");
      const saved = await api(`/api/problems/${encodeURIComponent(problemKey)}/source`, {
        method: "POST",
        body: JSON.stringify({ source, sourceName }),
      });
      if (currentEditorDocumentId() === documentId) {
        if (Array.isArray(saved.sourceFiles)) {
          state.current.problem.sourceFiles = saved.sourceFiles;
          mergeProblemIntoList(state.current.problem);
        }
        state.lastSavedSource = source;
        state.current.source = source;
        state.sourceBuffer = source;
        state.dirty = mainSourceValue() !== source;
        if (!state.dirty) {
          cancelDraftSave();
          clearEditorDraft(documentId);
        } else {
          scheduleEditorDraftSave(mainSourceValue());
        }
        setStatus(state.dirty ? "Unsaved" : (autosave ? "Autosaved" : "Saved"));
        if (state.dirty && autosave) scheduleAutoSave();
      }
    }

    async function saveTemplateSource(options = {}) {
      if (!state.currentTemplate) return;
      const autosave = Boolean(options.autosave);
      const expectedDocumentId = options.expectedDocumentId || "";
      const selected = state.currentTemplate;
      const documentId = `template:${selected.algorithm}\n${selected.name}`;
      if (expectedDocumentId && expectedDocumentId !== documentId) return;
      captureSourceBuffer();
      const source = Object.prototype.hasOwnProperty.call(options, "source") ? options.source : mainSourceValue();
      if (source === state.lastSavedSource && state.dirty) {
        state.dirty = false;
        state.sourceBuffer = source;
        cancelDraftSave();
        clearEditorDraft(documentId);
        setStatus(autosave ? "Autosaved" : "Template saved");
        return;
      }
      setStatus(autosave ? "Autosaving" : "Saving template");
      const data = await api("/api/templates", {
        method: "POST",
        body: JSON.stringify({
          kind: "template",
          algorithm: selected.algorithm,
          name: selected.name,
          source,
          extension: sourceExtensionFromTemplate(selected),
        }),
      });
      state.templates = data.templates || [];
      renderProblems();
      if (currentEditorDocumentId() === documentId) {
        const latest = findTemplate(selected.algorithm, selected.name);
        state.currentTemplate = latest
          ? templateEditorState(latest.algorithm, latest.template)
          : { ...selected, source };
        state.currentTemplate.source = mainSourceValue();
        state.lastSavedSource = source;
        state.sourceBuffer = mainSourceValue();
        state.dirty = mainSourceValue() !== source;
        if (!state.dirty) {
          cancelDraftSave();
          clearEditorDraft(documentId);
        } else {
          scheduleEditorDraftSave(mainSourceValue());
        }
        $("title").textContent = templateTitle(state.currentTemplate);
        renderTemplateStatement(state.currentTemplate);
        renderTemplateMeta(state.currentTemplate);
        updateToolbarMode();
        setStatus(state.dirty ? "Unsaved" : (autosave ? "Autosaved" : "Template saved"));
        if (state.dirty && autosave) scheduleAutoSave();
      }
    }

    async function copyEditorSource() {
      const code = $("code");
      const text = codeEditorValue() || "";
      await copyPlainText(text, code);
      setStatus("Copied");
    }

    async function copyPlainText(text, fallbackElement = null) {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const target = fallbackElement || document.createElement("textarea");
        if (!fallbackElement) {
          target.value = text;
          target.style.position = "fixed";
          target.style.left = "-9999px";
          document.body.appendChild(target);
        }
        target.focus();
        target.select();
        document.execCommand("copy");
        if (!fallbackElement) target.remove();
      }
    }


    async function runTests() {
      if (state.currentTemplate) {
        setStatus("Select a problem first");
        return;
      }
      if (!state.current) return;
      if (state.editorTab !== "source") {
        setStatus("Select a source file first");
        return;
      }
      try {
        await saveSource();
        setStatus("Running");
        renderResults({ running: true });
        const result = await api(`/api/problems/${encodeURIComponent(state.current.problem.problemKey)}/test`, {
          method: "POST",
          body: JSON.stringify({ compare: $("compare").value, sourceName: currentSourceName() }),
        });
        renderResults(result);
        setStatus(result.success ? "AC" : "Failed");
      } catch (error) {
        renderRunError(error);
        setStatus(error.message || "Run failed");
      }
    }

    async function submitCurrentProblem() {
      if (state.currentTemplate) {
        setStatus("Select a problem first");
        return;
      }
      if (!state.current) return;
      if (state.editorTab !== "source") {
        setStatus("Select a source file first");
        return;
      }
      try {
        await saveSource();
        const key = state.current.problem.problemKey;
        setStatus("Testing");
        renderResults({ running: true });
        const result = await api(`/api/problems/${encodeURIComponent(key)}/test`, {
          method: "POST",
          body: JSON.stringify({ compare: $("compare").value, sourceName: currentSourceName() }),
        });
        renderResults(result);
        if (!result.success) {
          const proceed = confirm("Local tests failed. Open submit page anyway?");
          if (!proceed) {
            setStatus("Tests failed");
            return;
          }
        }
        setStatus("Preparing submit");
        const prefill = await api(`/api/problems/${encodeURIComponent(key)}/submit-prefill`, {
          method: "POST",
          body: JSON.stringify({ sourceName: currentSourceName() }),
        });
        renderSubmitLink(prefill.url, prefill.submitUrl);
        const opened = window.open(prefill.url, "_blank", "noopener");
        setStatus(opened ? "Review submit" : "Click submit link");
      } catch (error) {
        renderRunError(error);
        setStatus(error.message || "Submit failed");
      }
    }

    function renderSubmitLink(url, submitUrl = "") {
      const output = $("output");
      const existing = output.querySelector(".submit-open");
      if (existing) existing.remove();
      const block = document.createElement("div");
      block.className = "case submit-open";
      block.innerHTML = `
        <div class="case-head"><span>Submit</span><span class="badge TEST">OPEN</span></div>
        <div class="case-body">
          <a class="submit-link" href="${escapeAttr(url)}" target="_blank" rel="noopener">Open Codeforces submit</a>
          ${submitUrl ? `<div class="empty">${escapeHtml(submitUrl)}</div>` : ""}
        </div>
      `;
      output.prepend(block);
      return block;
    }

    function renderRunError(error) {
      const message = error && error.message ? error.message : String(error || "Run failed");
      const status = error && error.status ? `HTTP ${error.status}` : "ERROR";
      $("output").innerHTML = `
        <div class="case">
          <div class="case-head"><span>Run failed</span><span class="badge RE">${escapeHtml(status)}</span></div>
          <div class="case-body">
            <div class="case-part">
              <strong>Error</strong>
              <pre>${escapeHtml(message)}</pre>
            </div>
          </div>
        </div>
      ` + renderProblemTestCards();
    }

    function renderResults(result) {
      const output = $("output");
      if (state.currentTemplate) {
        output.innerHTML = "";
        return;
      }
      if (!state.current) {
        output.innerHTML = "";
        return;
      }
      if (!result) {
        output.innerHTML = renderProblemTestCards();
        return;
      }
      if (result.running) {
        output.innerHTML = '<div class="empty">Running</div>' + renderProblemTestCards();
        return;
      }
      if (result.skippedReason) {
        output.innerHTML = `<div class="case"><div class="case-head"><span>SKIP</span><span class="badge SKIP">SKIP</span></div><pre>${escapeHtml(result.skippedReason)}</pre></div>` + renderProblemTestCards();
        return;
      }
      const compileBlock = result.compile.success ? "" : renderCompileError(result.compile);
      const cases = result.cases.length ? result.cases.map((testCase, index) => {
        const sourceTest = findProblemTest(testCase, index);
        return renderProblemTestCard(sourceTest, index, testCase);
      }).join("") : renderProblemTestCards();
      output.innerHTML = compileBlock + (cases || '<div class="empty">No tests</div>');
    }

    function renderCompileError(compile) {
      const command = Array.isArray(compile.command) && compile.command.length
        ? `<div class="case-part"><strong>Command</strong><pre>${escapeHtml(compile.command.join(" "))}</pre></div>`
        : "";
      const code = compile.returncode != null ? `exit code: ${compile.returncode}` : "compile failed";
      const stderr = compile.stderr ? `
        <div class="case-part">
          <strong>Compiler stderr</strong>
          <pre>${escapeHtml(compile.stderr)}</pre>
        </div>
      ` : "";
      const stdout = compile.stdout ? `
        <div class="case-part">
          <strong>Compiler stdout</strong>
          <pre>${escapeHtml(compile.stdout)}</pre>
        </div>
      ` : "";
      const fallback = !stderr && !stdout ? `
        <div class="case-part">
          <strong>Error</strong>
          <pre>${escapeHtml("compile failed")}</pre>
        </div>
      ` : "";
      return `
        <div class="case">
          <div class="case-head"><span>Compile</span><span class="badge CE">CE</span></div>
          <div class="case-body">
            <div class="case-part"><strong>Status</strong><pre>${escapeHtml(code)}</pre></div>
            ${command}
            ${stderr}
            ${stdout}
            ${fallback}
          </div>
        </div>`;
    }

    function renderProblemTestCards() {
      const tests = (state.current && state.current.problem && state.current.problem.tests) || [];
      return tests.map((testCase, index) => renderProblemTestCard(testCase, index)).join("") || '<div class="empty">No tests</div>';
    }

    function findProblemTest(resultCase, index) {
      const tests = (state.current && state.current.problem && state.current.problem.tests) || [];
      return tests[index] || tests.find((testCase) => testCase.name === resultCase.name) || {};
    }

    function renderProblemTestCard(testCase, index, resultCase = null) {
      const name = (resultCase && resultCase.name) || testCase.name || `sample_${index + 1}`;
      const status = resultCase ? resultCase.status : "TEST";
      const elapsed = resultCase && resultCase.elapsedMs != null ? ` ${resultCase.elapsedMs} ms` : "";
      const expected = resultCase ? resultCase.expected : testCase.output;
      const message = resultCaseMessage(resultCase);
      const statusMessage = message ? `
        <div class="case-part">
          <strong>Message</strong>
          <pre>${escapeHtml(message)}</pre>
        </div>
      ` : "";
      const actual = resultCase ? `
        <div class="case-part">
          <strong>Actual</strong>
          <pre>${escapeHtml(resultCase.actual || "")}</pre>
        </div>
      ` : "";
      const stderr = resultCase && resultCase.stderr ? `
        <div class="case-part">
          <strong>stderr</strong>
          <pre>${escapeHtml(resultCase.stderr)}</pre>
        </div>
      ` : "";
      const diff = resultCase && resultCase.diff ? `
        <div class="case-part">
          <strong>Diff</strong>
          <pre>${escapeHtml(resultCase.diff)}</pre>
        </div>
      ` : "";
      return `
        <div class="case"${testCase ? ` data-context-kind="test" data-test-index="${index + 1}"` : ""}>
          <div class="case-head">
            <span>${escapeHtml(name)}${escapeHtml(elapsed)}</span>
            <span class="case-actions">
              <span class="badge ${escapeHtml(status)}">${escapeHtml(status)}</span>
            </span>
          </div>
          <div class="case-body">
            <div class="case-part">
              <strong>Input</strong>
              <pre>${escapeHtml(testCase.input || "")}</pre>
            </div>
            <div class="case-part">
              <strong>Expected</strong>
              <pre>${escapeHtml(expected || "")}</pre>
            </div>
            ${statusMessage}
            ${actual}
            ${stderr}
            ${diff}
          </div>
        </div>
      `;
    }

    function resultCaseMessage(resultCase) {
      if (!resultCase) return "";
      if (resultCase.status === "RE") {
        return resultCase.returncode != null
          ? `Runtime error (exit code ${resultCase.returncode})`
          : "Runtime error";
      }
      if (resultCase.status === "TLE") {
        return resultCase.elapsedMs != null
          ? `Time limit exceeded after ${resultCase.elapsedMs} ms`
          : "Time limit exceeded";
      }
      return "";
    }

    async function addCustomTest() {
      if (state.currentTemplate) {
        setStatus("Select a problem first");
        return;
      }
      if (!state.current) return;
      const key = state.current.problem.problemKey;
      const input = $("customInput").value;
      const output = $("customOutput").value;
      setStatus("Adding");
      const created = await api(`/api/problems/${encodeURIComponent(key)}/tests`, {
        method: "POST",
        body: JSON.stringify({ input, output }),
      });
      $("customInput").value = "";
      $("customOutput").value = "";
      if (state.current && state.current.problem.problemKey === key) {
        state.current.problem.tests = [
          ...(state.current.problem.tests || []),
          {
            name: created.name || `test_${(state.current.problem.tests || []).length + 1}`,
            inputFile: created.inputFile,
            outputFile: created.outputFile,
            input,
            output,
          },
        ];
        renderMeta(state.current.problem);
        renderResults(null);
      }
      if (!state.dirty) {
        try {
          await selectProblem(key, { sourceName: currentSourceName() });
        } catch (error) {
          setStatus("Added; refresh failed");
          return;
        }
      }
      setStatus("Added");
    }

    async function renameTestByIndex(index) {
      if (!state.current) return;
      const numericIndex = Number(index);
      const test = state.current.problem.tests[numericIndex - 1];
      if (!test) return;
      const key = state.current.problem.problemKey;
      const currentName = test.name || `test_${numericIndex}`;
      const name = prompt("Test name", currentName);
      if (!name || !name.trim() || name.trim() === currentName) return;
      setStatus("Renaming test");
      await api(`/api/problems/${encodeURIComponent(key)}/tests/${encodeURIComponent(String(numericIndex))}/rename`, {
        method: "POST",
        body: JSON.stringify({ name }),
      });
      const data = await api(`/api/problems/${encodeURIComponent(key)}?sourceName=${encodeURIComponent(currentSourceName())}`);
      state.current.problem = data.problem;
      mergeProblemIntoList(data.problem);
      state.current.sourceName = data.sourceName || currentSourceName();
      state.current.source = data.source;
      applyCurrentIdePayload(data);
      rememberProblemSource(key, state.current.sourceName);
      if (!state.dirty) {
        resetEditorTabs(data.source);
      }
      renderMeta(data.problem);
      renderStatement(data.problem);
      renderResults(null);
      renderProblems();
      setStatus("Test renamed");
    }

    async function deleteTestByIndex(index) {
      if (!state.current) return;
      const numericIndex = Number(index);
      const test = state.current.problem.tests[numericIndex - 1];
      if (!test) return;
      const key = state.current.problem.problemKey;
      const label = test.name || `test ${numericIndex}`;
      if (!confirm(`Delete test "${label}" files?`)) return;
      setStatus("Deleting test");
      await api(`/api/problems/${encodeURIComponent(key)}/tests/${encodeURIComponent(String(numericIndex))}`, {
        method: "DELETE",
      });
      const data = await api(`/api/problems/${encodeURIComponent(key)}?sourceName=${encodeURIComponent(currentSourceName())}`);
      state.current.problem = data.problem;
      mergeProblemIntoList(data.problem);
      state.current.sourceName = data.sourceName || currentSourceName();
      state.current.source = data.source;
      applyCurrentIdePayload(data);
      rememberProblemSource(key, state.current.sourceName);
      if (!state.dirty) {
        resetEditorTabs(data.source);
      }
      renderMeta(data.problem);
      renderStatement(data.problem);
      renderResults(null);
      renderProblems();
      setStatus("Test deleted");
    }

    async function createFolderFromPrompt() {
      const name = prompt("Folder name");
      if (!name || !name.trim()) return;
      setStatus("Creating folder");
      await api("/api/folders", {
        method: "POST",
        body: JSON.stringify({ name }),
      });
      await loadProblems();
      setStatus("Folder created");
    }

    async function renameFolderFromPrompt(folder) {
      if (!folder) return;
      const name = prompt("Folder name", folder);
      if (!name || !name.trim() || normalizeFolderPath(name) === normalizeFolderPath(folder)) return;
      setStatus("Renaming folder");
      const data = await api(`/api/folders/${encodeURIComponent(folder)}/rename`, {
        method: "POST",
        body: JSON.stringify({ name }),
      });
      const nextFolder = data.folder && data.folder.name ? data.folder.name : name.trim();
      replaceFolderInState(folder, nextFolder);
      renderProblems();
      setStatus("Folder renamed");
      await loadProblems();
    }

    async function deleteFolder(folder) {
      if (!folder) return;
      if (!confirm(`Delete folder "${folder}" and everything inside it?`)) return;
      setStatus("Deleting folder");
      await api(`/api/folders/${encodeURIComponent(folder)}`, { method: "DELETE" });
      const deletedCurrent = state.current && folderContainsPath(folder, state.current.problem.folder || "");
      removeDeletedFolderFromState(folder);
      if (deletedCurrent) {
        clearCurrentProblem();
      } else {
        renderProblems();
      }
      setStatus("Folder deleted");
      await loadProblems();
    }

    function replaceFolderInState(folder, nextFolder) {
      state.folders = state.folders.map((item) => (
        folderContainsPath(folder, item.name || "") ? { ...item, name: replaceFolderPrefix(folder, nextFolder, item.name || "") } : item
      ));
      state.problems = state.problems.map((problem) => (
        folderContainsPath(folder, problem.folder || "") ? { ...problem, folder: replaceFolderPrefix(folder, nextFolder, problem.folder || "") } : problem
      ));
      if (state.current && folderContainsPath(folder, state.current.problem.folder || "")) {
        state.current.problem.folder = replaceFolderPrefix(folder, nextFolder, state.current.problem.folder || "");
      }
    }

    function replaceFolderPrefix(folder, nextFolder, candidate) {
      const parent = normalizeFolderPath(folder);
      const child = normalizeFolderPath(candidate);
      const replacement = normalizeFolderPath(nextFolder);
      if (!parent || !child) return candidate;
      if (child === parent) return replacement;
      if (child.startsWith(`${parent}/`)) return `${replacement}/${child.slice(parent.length + 1)}`;
      return candidate;
    }

    function removeDeletedFolderFromState(folder) {
      state.folders = state.folders.filter((item) => !folderContainsPath(folder, item.name || ""));
      state.problems = state.problems.filter((problem) => !folderContainsPath(folder, problem.folder || ""));
    }

    function folderContainsPath(folder, candidate) {
      const parent = normalizeFolderPath(folder);
      const child = normalizeFolderPath(candidate);
      return Boolean(parent && (child === parent || child.startsWith(`${parent}/`)));
    }

    function normalizeFolderPath(value) {
      return String(value || "").replace(/\\\\/g, "/").replace(/^\\/+|\\/+$/g, "");
    }

    async function createProblemFromPrompt() {
      const problemKey = prompt("Problem key");
      if (!problemKey || !problemKey.trim()) return;
      const name = prompt("Problem name", problemKey.trim()) || problemKey.trim();
      const defaultFolder = state.current && state.current.problem.folder ? state.current.problem.folder : "";
      const folder = prompt("Folder", defaultFolder) || "";
      const url = prompt("URL", "") || "";
      setStatus("Creating problem");
      const created = await api("/api/problems", {
        method: "POST",
        body: JSON.stringify({ problemKey, name, folder, url }),
      });
      await loadProblems();
      await selectProblem(created.problemKey, { sourceName: "main.cpp" });
      setStatus("Problem created");
    }

    async function renameProblemFromPrompt(key) {
      if (!key) return;
      const problem = state.problems.find((item) => item.problemKey === key) ||
        (state.current && state.current.problem.problemKey === key ? state.current.problem : null);
      const currentName = problem && problem.name ? problem.name : key;
      const name = prompt("Problem name", currentName);
      if (!name || !name.trim() || name.trim() === currentName) return;
      setStatus("Renaming problem");
      const data = await api(`/api/problems/${encodeURIComponent(key)}/rename`, {
        method: "POST",
        body: JSON.stringify({ name }),
      });
      const renamed = data.problem || { name: name.trim() };
      state.problems = state.problems.map((item) => item.problemKey === key ? { ...item, name: renamed.name || name.trim() } : item);
      if (state.current && state.current.problem.problemKey === key) {
        state.current.problem = { ...state.current.problem, name: renamed.name || name.trim() };
        $("title").textContent = `${state.current.problem.problemKey} - ${state.current.problem.name}`;
        renderMeta(state.current.problem);
        renderStatement(state.current.problem);
      }
      renderProblems();
      setStatus("Problem renamed");
    }

    async function deleteCurrentProblem() {
      if (state.currentTemplate) {
        await deleteTemplate(state.currentTemplate.algorithm, state.currentTemplate.name);
        return;
      }
      if (!state.current) return;
      await deleteProblemByKey(state.current.problem.problemKey);
    }

    async function deleteProblemByKey(key) {
      if (!key) return;
      if (!confirm(`Delete problem "${key}"?`)) return;
      setStatus("Deleting problem");
      await api(`/api/problems/${encodeURIComponent(key)}`, { method: "DELETE" });
      const deletedCurrent = state.current && state.current.problem.problemKey === key;
      state.problems = state.problems.filter((problem) => problem.problemKey !== key);
      if (deletedCurrent) {
        clearCurrentProblem();
      } else {
        renderProblems();
      }
      await loadProblems();
      setStatus("Problem deleted");
    }

    const cppKeywords = new Set([
      "alignas", "alignof", "asm", "auto", "break", "case", "catch", "class", "concept",
      "const", "consteval", "constexpr", "constinit", "continue", "decltype", "default",
      "delete", "do", "else", "enum", "explicit", "export", "extern", "for", "friend",
      "goto", "if", "inline", "mutable", "namespace", "new", "noexcept", "operator",
      "private", "protected", "public", "requires", "return", "sizeof", "static",
      "static_assert", "struct", "switch", "template", "this", "throw", "try", "typedef",
      "typename", "using", "virtual", "while"
    ]);
    const cppTypes = new Set([
      "bool", "char", "char8_t", "char16_t", "char32_t", "double", "float", "int",
      "long", "short", "signed", "unsigned", "void", "wchar_t", "size_t", "string",
      "vector", "pair", "tuple", "array", "deque", "queue", "priority_queue", "stack",
      "set", "multiset", "map", "multimap", "unordered_set", "unordered_map", "ll"
    ]);
    const cppLiterals = new Set(["true", "false", "nullptr", "NULL"]);
    const autoClosingPairs = { "(": ")", "[": "]", "{": "}", '"': '"', "'": "'" };
    const closingPairs = { ")": "(", "]": "[", "}": "{" };
    const editorBracketPairs = { "(": ")", "[": "]", "{": "}" };

    function updateCodeHighlight() {
      if (monacoIde()) return;
      const code = $("code");
      const layer = $("codeHighlight");
      if (!code || !layer) return;
      const cppMode = true;
      updateCodeLineNumbers(code);
      layer.innerHTML = editorHighlightHtml(code.value, cppMode, code.selectionStart, code.selectionEnd);
      syncCodeScroll();
    }

    function editorHighlightHtml(source, cppMode, selectionStart = 0, selectionEnd = selectionStart) {
      const value = String(source || "");
      const bracketMarks = analyzeEditorBrackets(value, selectionStart, selectionEnd, cppMode);
      let html = cppMode ? highlightCpp(value || " ", bracketMarks) : highlightPlainText(value || " ", bracketMarks);
      if (value.endsWith("\\n")) html += " ";
      return html;
    }

    function scheduleCodeHighlightUpdate() {
      if (monacoIde()) return;
      if (state.codeHighlightFrame) cancelAnimationFrame(state.codeHighlightFrame);
      state.codeHighlightFrame = requestAnimationFrame(() => {
        state.codeHighlightFrame = null;
        updateCodeHighlight();
      });
    }

    function syncCodeScroll() {
      if (monacoIde()) return;
      const code = $("code");
      const layer = $("codeHighlight");
      if (!code || !layer) return;
      layer.scrollTop = code.scrollTop;
      layer.scrollLeft = code.scrollLeft;
      const numbers = $("codeLineNumbers");
      if (numbers) numbers.scrollTop = code.scrollTop;
    }

    function updateCodeLineNumbers(code = $("code")) {
      if (monacoIde()) return;
      const numbers = $("codeLineNumbers");
      if (!code || !numbers) return;
      const lineCount = countCodeLines(code.value);
      numbers.textContent = codeLineNumberText(lineCount);
      updateCodeGutterWidth(code, lineCount);
    }

    function countCodeLines(value) {
      return countNewlinesBefore(String(value || ""), String(value || "").length) + 1;
    }

    function codeLineNumberText(lineCount) {
      const lines = [];
      for (let i = 1; i <= Math.max(1, lineCount); i += 1) lines.push(String(i));
      return lines.join("\\n");
    }

    function updateCodeGutterWidth(code, lineCount) {
      const editor = code.closest(".code-editor");
      if (!editor) return;
      const digits = String(Math.max(1, lineCount)).length;
      const characterWidth = measureCodeCharacterWidth(code);
      const gutterWidth = Math.max(46, Math.ceil(digits * characterWidth + 24));
      editor.style.setProperty("--code-gutter-width", `${gutterWidth}px`);
    }

    function scheduleEnsureCodeCaretVisible() {
      if (monacoIde()) return;
      const code = $("code");
      if (!code || document.activeElement !== code) return;
      if (state.caretScrollFrame) cancelAnimationFrame(state.caretScrollFrame);
      state.caretScrollFrame = requestAnimationFrame(() => {
        state.caretScrollFrame = null;
        ensureCodeCaretVisible();
      });
    }

    function ensureCodeCaretVisible() {
      if (monacoIde()) return;
      const code = $("code");
      if (!code) return;
      const style = getComputedStyle(code);
      const caretBox = measureCodeCaretBox(code);
      if (!caretBox) return;
      const paddingTop = cssPixels(style.paddingTop, 0);
      const paddingBottom = cssPixels(style.paddingBottom, 0);
      const paddingLeft = cssPixels(style.paddingLeft, 0);
      const paddingRight = cssPixels(style.paddingRight, 0);
      const lineHeight = caretBox.lineHeight;
      const topMargin = Math.max(lineHeight, paddingTop);
      const bottomMargin = Math.max(lineHeight * 2.5, paddingBottom);
      const visibleTop = code.scrollTop;
      const visibleBottom = code.scrollTop + code.clientHeight;
      const maxScrollTop = Math.max(0, code.scrollHeight - code.clientHeight);
      if (caretBox.bottom > visibleBottom - bottomMargin) {
        code.scrollTop = Math.min(maxScrollTop, caretBox.bottom - code.clientHeight + bottomMargin);
      } else if (caretBox.top < visibleTop + topMargin) {
        code.scrollTop = Math.max(0, caretBox.top - topMargin);
      }

      const horizontalMargin = Math.max(measureCodeCharacterWidth(code, style), paddingLeft, paddingRight);
      const visibleLeft = code.scrollLeft;
      const visibleRight = code.scrollLeft + code.clientWidth;
      const maxScrollLeft = Math.max(0, code.scrollWidth - code.clientWidth);
      if (maxScrollLeft > 0 && caretBox.right > visibleRight - horizontalMargin) {
        code.scrollLeft = Math.min(maxScrollLeft, caretBox.right - code.clientWidth + horizontalMargin);
      } else if (maxScrollLeft > 0 && caretBox.left < visibleLeft + horizontalMargin) {
        code.scrollLeft = Math.max(0, caretBox.left - horizontalMargin);
      }
      syncCodeScroll();
    }

    function measureCodeCaretBox(code) {
      const style = getComputedStyle(code);
      const mirror = document.createElement("div");
      const marker = document.createElement("span");
      const caretIndex = Math.min(code.value.length, Math.max(0, code.selectionEnd || 0));
      mirror.style.position = "absolute";
      mirror.style.visibility = "hidden";
      mirror.style.left = "-100000px";
      mirror.style.top = "0";
      mirror.style.margin = "0";
      mirror.style.border = "0";
      mirror.style.padding = style.padding;
      mirror.style.fontFamily = style.fontFamily;
      mirror.style.fontSize = style.fontSize;
      mirror.style.fontStyle = style.fontStyle;
      mirror.style.fontWeight = style.fontWeight;
      mirror.style.fontVariantLigatures = style.fontVariantLigatures;
      mirror.style.fontFeatureSettings = style.fontFeatureSettings;
      mirror.style.letterSpacing = style.letterSpacing;
      mirror.style.lineHeight = style.lineHeight;
      mirror.style.tabSize = style.tabSize;
      mirror.style.whiteSpace = "pre";
      mirror.style.wordBreak = "normal";
      mirror.style.overflowWrap = "normal";
      mirror.style.overflow = "visible";
      mirror.textContent = code.value.slice(0, caretIndex);
      marker.textContent = "\\u200b";
      mirror.appendChild(marker);
      document.body.appendChild(mirror);
      const mirrorRect = mirror.getBoundingClientRect();
      const markerRect = marker.getBoundingClientRect();
      const lineHeight = Math.max(markerRect.height, measuredCodeLineHeight(code, style));
      const box = {
        top: markerRect.top - mirrorRect.top,
        bottom: markerRect.top - mirrorRect.top + lineHeight,
        left: markerRect.left - mirrorRect.left,
        right: markerRect.left - mirrorRect.left + 1,
        lineHeight,
      };
      mirror.remove();
      return box;
    }

    function measuredCodeLineHeight(code, style = getComputedStyle(code)) {
      const fontSize = cssPixels(style.fontSize, 14);
      const fallback = fontSize * 1.55;
      const lineHeightValue = String(style.lineHeight || "");
      const parsed = Number.parseFloat(lineHeightValue);
      if (Number.isFinite(parsed) && parsed > 0) {
        return lineHeightValue.trim().endsWith("px") ? parsed : parsed * fontSize;
      }
      const probe = document.createElement("span");
      probe.style.position = "absolute";
      probe.style.visibility = "hidden";
      probe.style.fontFamily = style.fontFamily;
      probe.style.fontSize = style.fontSize;
      probe.style.fontStyle = style.fontStyle;
      probe.style.fontWeight = style.fontWeight;
      probe.style.lineHeight = style.lineHeight;
      probe.textContent = "M";
      document.body.appendChild(probe);
      const height = probe.getBoundingClientRect().height;
      probe.remove();
      return height || fallback;
    }

    function measureCodeCharacterWidth(code, style = getComputedStyle(code)) {
      const probe = document.createElement("span");
      probe.style.position = "absolute";
      probe.style.visibility = "hidden";
      probe.style.fontFamily = style.fontFamily;
      probe.style.fontSize = style.fontSize;
      probe.style.fontStyle = style.fontStyle;
      probe.style.fontWeight = style.fontWeight;
      probe.style.letterSpacing = style.letterSpacing;
      probe.textContent = "M";
      document.body.appendChild(probe);
      const width = probe.getBoundingClientRect().width;
      probe.remove();
      return width || cssPixels(style.fontSize, 14);
    }

    function cssPixels(value, fallback) {
      const number = Number.parseFloat(value);
      return Number.isFinite(number) ? number : fallback;
    }

    function countNewlinesBefore(value, end) {
      let count = 0;
      const stop = Math.min(value.length, Math.max(0, end));
      for (let i = 0; i < stop; i += 1) {
        if (value.charCodeAt(i) === 10) count += 1;
      }
      return count;
    }

    function highlightCpp(source, bracketMarks = new Map()) {
      let html = "";
      let i = 0;
      while (i < source.length) {
        const ch = source[i];
        const next = source[i + 1];

        if (ch === "/" && next === "/") {
          const end = readUntilLineEnd(source, i + 2);
          html += token("comment", source.slice(i, end));
          i = end;
          continue;
        }
        if (ch === "/" && next === "*") {
          const end = source.indexOf("*/", i + 2);
          const stop = end === -1 ? source.length : end + 2;
          html += token("comment", source.slice(i, stop));
          i = stop;
          continue;
        }
        if (ch === '"' || ch === "'") {
          const end = readQuoted(source, i, ch);
          html += token("string", source.slice(i, end));
          i = end;
          continue;
        }
        if (ch === "#" && isLinePrefixOnlyWhitespace(source, i)) {
          const end = readUntilLineEnd(source, i + 1);
          html += token("preprocessor", source.slice(i, end), i, bracketMarks);
          i = end;
          continue;
        }
        if (/[0-9]/.test(ch)) {
          const match = source.slice(i).match(/^(?:0[xX][0-9a-fA-F']+|\\d[\\d']*(?:\\.\\d[\\d']*)?(?:[eE][+-]?\\d+)?)(?:[uUlLfF]*)/);
          if (match) {
            html += token("number", match[0]);
            i += match[0].length;
            continue;
          }
        }
        if (/[A-Za-z_]/.test(ch)) {
          const match = source.slice(i).match(/^[A-Za-z_][A-Za-z0-9_]*/);
          const word = match ? match[0] : ch;
          if (cppKeywords.has(word)) html += token("keyword", word);
          else if (cppTypes.has(word)) html += token("type", word);
          else if (cppLiterals.has(word)) html += token("literal", word);
          else html += escapeHtml(word);
          i += word.length;
          continue;
        }
        if ("+-*/%=!<>&|^~?:.".includes(ch)) {
          html += token("operator", ch);
          i += 1;
          continue;
        }
        html += highlightBracketSegment(ch, i, bracketMarks);
        i += 1;
      }
      return html || " ";
    }

    function highlightPlainText(source, bracketMarks = new Map()) {
      return highlightBracketSegment(source, 0, bracketMarks) || " ";
    }

    function token(kind, value, offset = -1, bracketMarks = null) {
      const html = bracketMarks && offset >= 0
        ? highlightBracketSegment(value, offset, bracketMarks)
        : escapeHtml(value);
      return `<span class="tok-${kind}">${html}</span>`;
    }

    function highlightBracketSegment(value, offset, bracketMarks) {
      let html = "";
      for (let i = 0; i < value.length; i += 1) {
        const mark = bracketMarks && bracketMarks.get(offset + i);
        if (mark) {
          html += `<span class="tok-bracket tok-bracket-${mark}">${escapeHtml(value[i])}</span>`;
        } else {
          html += escapeHtml(value[i]);
        }
      }
      return html;
    }

    function analyzeEditorBrackets(source, selectionStart = 0, selectionEnd = selectionStart, cppMode = true) {
      const value = String(source || "");
      const tokens = collectEditorBracketTokens(value, cppMode);
      const tokenByIndex = new Map(tokens.map((item) => [item.index, item]));
      const pairByIndex = new Map();
      const unmatched = new Set();
      const stack = [];
      tokens.forEach((item) => {
        if (editorBracketPairs[item.ch]) {
          stack.push(item);
          return;
        }
        const opening = closingPairs[item.ch];
        const top = stack[stack.length - 1];
        if (top && top.ch === opening) {
          stack.pop();
          pairByIndex.set(top.index, item.index);
          pairByIndex.set(item.index, top.index);
        } else {
          unmatched.add(item.index);
        }
      });
      stack.forEach((item) => unmatched.add(item.index));

      const marks = new Map();
      unmatched.forEach((index) => marks.set(index, "unmatched"));
      const active = activeEditorBracketIndex(value, selectionStart, selectionEnd, tokenByIndex);
      if (active !== -1) {
        const pair = pairByIndex.get(active);
        if (pair == null) {
          marks.set(active, "unmatched");
        } else {
          marks.set(active, "match");
          marks.set(pair, "match");
        }
      }
      return marks;
    }

    function collectEditorBracketTokens(source, cppMode = true) {
      const tokens = [];
      let i = 0;
      while (i < source.length) {
        const ch = source[i];
        const next = source[i + 1];
        if (cppMode && ch === "/" && next === "/") {
          i = readUntilLineEnd(source, i + 2);
          continue;
        }
        if (cppMode && ch === "/" && next === "*") {
          const end = source.indexOf("*/", i + 2);
          i = end === -1 ? source.length : end + 2;
          continue;
        }
        if (cppMode && (ch === '"' || ch === "'")) {
          i = readQuoted(source, i, ch);
          continue;
        }
        if (isEditorBracket(ch)) tokens.push({ index: i, ch });
        i += 1;
      }
      return tokens;
    }

    function activeEditorBracketIndex(source, selectionStart, selectionEnd, tokenByIndex) {
      const start = clampEditorIndex(selectionStart, source.length);
      const end = clampEditorIndex(selectionEnd, source.length);
      if (start !== end) return -1;
      if (tokenByIndex.has(start)) return start;
      if (start > 0 && tokenByIndex.has(start - 1)) return start - 1;
      return -1;
    }

    function clampEditorIndex(index, length) {
      const number = Number(index);
      if (!Number.isFinite(number)) return 0;
      return Math.min(length, Math.max(0, number));
    }

    function isEditorBracket(ch) {
      return Boolean(editorBracketPairs[ch] || closingPairs[ch]);
    }

    function readUntilLineEnd(source, index) {
      const end = source.indexOf("\\n", index);
      return end === -1 ? source.length : end;
    }

    function readQuoted(source, start, quote) {
      let i = start + 1;
      while (i < source.length) {
        if (source[i] === "\\\\") {
          i += 2;
          continue;
        }
        if (source[i] === quote) return i + 1;
        if (source[i] === "\\n") return i;
        i += 1;
      }
      return source.length;
    }

    function isLinePrefixOnlyWhitespace(source, index) {
      let i = index - 1;
      while (i >= 0 && source[i] !== "\\n") {
        if (source[i] !== " " && source[i] !== "\\t") return false;
        i -= 1;
      }
      return true;
    }

    function markCodeDirty() {
      const code = $("code");
      if (!monacoIde()) normalizeCodeValueTabs(code);
      scheduleCodeHighlightUpdate();
      scheduleEnsureCodeCaretVisible();
      if (!currentEditorDocumentId()) return;
      state.sourceBuffer = codeEditorValue();
      state.dirty = state.sourceBuffer !== state.lastSavedSource;
      if (state.dirty) {
        scheduleEditorDraftSave(state.sourceBuffer);
        setStatus("Unsaved");
        scheduleAutoSave();
      } else {
        cancelDraftSave();
        cancelAutoSave();
        clearEditorDraft();
        setStatus("Saved");
      }
    }

    function updateToolbarMode() {
      const templateMode = Boolean(state.currentTemplate);
      const hasEditorDocument = Boolean(state.current || state.currentTemplate);
      const sourceTab = state.editorTab === "source";
      $("save").textContent = templateMode ? "Save Template" : t("save");
      $("save").title = templateMode ? "Save template" : t("saveSource");
      $("save").disabled = !hasEditorDocument;
      $("copy").disabled = !hasEditorDocument;
      $("run").disabled = templateMode || !state.current || !sourceTab;
      $("submit").disabled = templateMode || !state.current || !sourceTab;
      const deleteButton = $("deleteProblem");
      if (deleteButton) {
        deleteButton.title = templateMode ? "Delete template" : "Delete problem";
        deleteButton.disabled = templateMode ? !state.currentTemplate : !state.current;
      }
      $("openCf").disabled = templateMode || !state.current || !state.current.problem.url;
      $("addTest").disabled = templateMode || !state.current;
    }

    function replaceCodeSelection(text, cursorOffset = text.length, selectLength = 0) {
      const code = $("code");
      const start = code.selectionStart;
      const end = code.selectionEnd;
      code.value = code.value.slice(0, start) + text + code.value.slice(end);
      code.selectionStart = start + cursorOffset;
      code.selectionEnd = start + cursorOffset + selectLength;
      markCodeDirty();
    }

    function handleCodeKeydown(event) {
      const code = $("code");
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        event.stopPropagation();
        saveFromCodeShortcut().catch((error) => setStatus(error.message));
        return;
      }
      if (state.editorTab === "source" && (event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        event.stopPropagation();
        runTests().catch((error) => setStatus(error.message));
        return;
      }
      if (event.key === "Tab") {
        event.preventDefault();
        handleTabKey(event.shiftKey);
        return;
      }
      if (event.key === "Enter") {
        event.preventDefault();
        insertIndentedNewline();
        return;
      }
      if (event.key === "}" && handleClosingBraceKey(event)) {
        return;
      }
      if (event.key === "Backspace" && code.selectionStart === code.selectionEnd) {
        const before = code.value[code.selectionStart - 1];
        const after = code.value[code.selectionStart];
        if (autoClosingPairs[before] === after) {
          event.preventDefault();
          code.selectionStart -= 1;
          code.selectionEnd += 1;
          replaceCodeSelection("", 0);
        }
        return;
      }
      if (autoClosingPairs[event.key] && !event.ctrlKey && !event.altKey && !event.metaKey) {
        event.preventDefault();
        const start = code.selectionStart;
        const end = code.selectionEnd;
        const selected = code.value.slice(start, end);
        const close = autoClosingPairs[event.key];
        if ((event.key === '"' || event.key === "'") && isEscapedAt(code.value, start)) {
          replaceCodeSelection(event.key);
          return;
        }
        replaceCodeSelection(event.key + selected + close, 1, selected.length);
        return;
      }
      if (closingPairs[event.key] && code.selectionStart === code.selectionEnd) {
        if (code.value[code.selectionStart] === event.key) {
          event.preventDefault();
          code.selectionStart += 1;
          code.selectionEnd = code.selectionStart;
          scheduleEnsureCodeCaretVisible();
        }
      }
    }

    function handleClosingBraceKey(event) {
      if (event.ctrlKey || event.altKey || event.metaKey) return false;
      const code = $("code");
      if (code.selectionStart !== code.selectionEnd) return false;
      const source = code.value;
      const start = code.selectionStart;
      const lineStart = source.lastIndexOf("\\n", start - 1) + 1;
      const prefix = source.slice(lineStart, start);
      if (!/^[ \\t]*$/.test(prefix)) return false;
      const indent = matchingOpeningBraceIndent(source, start);
      if (indent === null) return false;
      event.preventDefault();
      const existingClose = nextWhitespaceOnlyClosingBrace(source, start);
      if (existingClose !== -1) {
        code.value = source.slice(0, lineStart) + indent + source.slice(existingClose);
      } else {
        code.value = source.slice(0, lineStart) + indent + "}" + source.slice(start);
      }
      code.selectionStart = code.selectionEnd = lineStart + indent.length + 1;
      markCodeDirty();
      return true;
    }

    function matchingOpeningBraceIndent(source, cursor) {
      const stack = [];
      let i = 0;
      while (i < cursor) {
        const ch = source[i];
        const next = source[i + 1];
        if (ch === "/" && next === "/") {
          i = readUntilLineEnd(source, i + 2);
          continue;
        }
        if (ch === "/" && next === "*") {
          const end = source.indexOf("*/", i + 2);
          i = end === -1 ? source.length : end + 2;
          continue;
        }
        if (ch === '"' || ch === "'") {
          i = readQuoted(source, i, ch);
          continue;
        }
        if (ch === "{") stack.push(i);
        else if (ch === "}" && stack.length) stack.pop();
        i += 1;
      }
      const opening = stack.length ? stack[stack.length - 1] : -1;
      return opening === -1 ? null : lineIndentAt(source, opening);
    }

    function lineIndentAt(source, index) {
      const lineStart = source.lastIndexOf("\\n", Math.max(0, index - 1)) + 1;
      const line = source.slice(lineStart, index);
      const indent = (line.match(/^[ \\t]*/) || [""])[0];
      return indent.replace(/\\t/g, "    ");
    }

    function nextWhitespaceOnlyClosingBrace(source, start) {
      let i = start;
      while (i < source.length && /[ \\t\\r\\n]/.test(source[i])) i += 1;
      return source[i] === "}" ? i : -1;
    }

    function handleTabKey(outdent) {
      const code = $("code");
      const start = code.selectionStart;
      const end = code.selectionEnd;
      if (start === end) {
        if (outdent) outdentCurrentLine();
        else replaceCodeSelection("    ");
        return;
      }
      const lineStart = code.value.lastIndexOf("\\n", start - 1) + 1;
      const lineEnd = code.value.indexOf("\\n", end);
      const blockEnd = lineEnd === -1 ? code.value.length : lineEnd;
      const before = code.value.slice(0, lineStart);
      const block = code.value.slice(lineStart, blockEnd);
      const after = code.value.slice(blockEnd);
      const lines = block.split("\\n");
      let changedChars = 0;
      const updated = lines.map((line) => {
        if (!outdent) {
          changedChars += 4;
          return "    " + line;
        }
        if (line.startsWith("    ")) {
          changedChars -= 4;
          return line.slice(4);
        }
        if (line.startsWith("\\t")) {
          changedChars -= 1;
          return line.slice(1);
        }
        return line;
      }).join("\\n");
      code.value = before + updated + after;
      code.selectionStart = outdent ? Math.max(lineStart, start - 4) : start + 4;
      code.selectionEnd = Math.max(code.selectionStart, end + changedChars);
      markCodeDirty();
    }

    function outdentCurrentLine() {
      const code = $("code");
      const start = code.selectionStart;
      const lineStart = code.value.lastIndexOf("\\n", start - 1) + 1;
      const line = code.value.slice(lineStart, code.value.indexOf("\\n", lineStart) === -1 ? code.value.length : code.value.indexOf("\\n", lineStart));
      let remove = 0;
      if (line.startsWith("    ")) remove = 4;
      else if (line.startsWith("\\t")) remove = 1;
      if (!remove) return;
      code.value = code.value.slice(0, lineStart) + code.value.slice(lineStart + remove);
      code.selectionStart = code.selectionEnd = Math.max(lineStart, start - remove);
      markCodeDirty();
    }

    function insertIndentedNewline() {
      const code = $("code");
      const start = code.selectionStart;
      const before = code.value.slice(0, start);
      const after = code.value.slice(code.selectionEnd);
      const lineStart = before.lastIndexOf("\\n") + 1;
      const currentLine = before.slice(lineStart);
      const indent = (currentLine.match(/^\\s*/) || [""])[0].replace(/\\t/g, "    ");
      const trimmedBefore = before.replace(/\\s+$/g, "");
      const previousChar = trimmedBefore[trimmedBefore.length - 1] || "";
      const nextChar = after.replace(/^\\s+/g, "")[0] || "";
      const shouldIndent = ["{", "(", "["].includes(previousChar);
      const closesBlock = (previousChar === "{" && nextChar === "}") ||
        (previousChar === "(" && nextChar === ")") ||
        (previousChar === "[" && nextChar === "]");
      if (shouldIndent && closesBlock) {
        const innerIndent = indent + "    ";
        replaceCodeSelection("\\n" + innerIndent + "\\n" + indent, innerIndent.length + 1);
        return;
      }
      replaceCodeSelection("\\n" + indent + (shouldIndent ? "    " : ""));
    }

    function isEscapedAt(value, index) {
      let slashes = 0;
      for (let i = index - 1; i >= 0 && value[i] === "\\\\"; i -= 1) slashes += 1;
      return slashes % 2 === 1;
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
    }
    function escapeAttr(value) { return escapeHtml(value).replace(/`/g, "&#96;"); }

    document.querySelectorAll("[data-view-target]").forEach((button) => {
      button.addEventListener("click", () => switchView(button.dataset.viewTarget || "code"));
    });
    $("toggleProblemSidebar").addEventListener("click", toggleProblemSidebar);
    $("toggleResultsSidebar").addEventListener("click", toggleResultsSidebar);
    $("contestModeToggle").addEventListener("click", toggleContestMode);
    $("refresh").addEventListener("click", () => loadProblems({ resetRecentlyLoaded: true }).catch((error) => setStatus(error.message)));
    $("newFolder").addEventListener("click", () => createFolderFromPrompt().catch((error) => setStatus(error.message)));
    $("newProblem").addEventListener("click", () => createProblemFromPrompt().catch((error) => setStatus(error.message)));
    $("filter").addEventListener("input", renderProblems);
    $("problems").addEventListener("contextmenu", handleSidebarContextMenu);
    $("save").addEventListener("click", () => saveSource().catch((error) => setStatus(error.message)));
    $("copy").addEventListener("click", () => copyEditorSource().catch((error) => setStatus(error.message)));
    $("run").addEventListener("click", () => runTests().catch((error) => setStatus(error.message)));
    $("submit").addEventListener("click", () => submitCurrentProblem().catch((error) => setStatus(error.message)));
    $("addTest").addEventListener("click", () => addCustomTest().catch((error) => setStatus(error.message)));
    $("output").addEventListener("contextmenu", handleOutputContextMenu);
    if ($("deleteProblem")) $("deleteProblem").addEventListener("click", () => deleteCurrentProblem().catch((error) => setStatus(error.message)));
    $("openCf").addEventListener("click", () => {
      if (!state.currentTemplate && state.current && state.current.problem.url) window.open(state.current.problem.url, "_blank");
    });
    $("code").addEventListener("input", markCodeDirty);
    $("code").addEventListener("scroll", syncCodeScroll);
    $("code").addEventListener("keydown", handleCodeKeydown);
    $("code").addEventListener("keyup", () => {
      scheduleCodeHighlightUpdate();
      scheduleEnsureCodeCaretVisible();
    });
    $("code").addEventListener("mouseup", () => {
      scheduleCodeHighlightUpdate();
      scheduleEnsureCodeCaretVisible();
    });
    $("code").addEventListener("focus", () => {
      scheduleCodeHighlightUpdate();
      scheduleEnsureCodeCaretVisible();
    });
    $("code").addEventListener("compositionend", () => {
      scheduleCodeHighlightUpdate();
      scheduleEnsureCodeCaretVisible();
    });
    document.addEventListener("selectionchange", () => {
      if (document.activeElement === $("code")) {
        scheduleCodeHighlightUpdate();
        scheduleEnsureCodeCaretVisible();
      }
    });
    document.addEventListener("click", closeContextMenu);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeContextMenu();
    });
    window.addEventListener("resize", () => {
      closeContextMenu();
      updateCodeLineNumbers();
      syncCodeScroll();
      scheduleEnsureCodeCaretVisible();
    });
    if (document.fonts && typeof document.fonts.addEventListener === "function") {
      document.fonts.addEventListener("loadingdone", () => {
        updateCodeLineNumbers();
        syncCodeScroll();
        scheduleEnsureCodeCaretVisible();
      });
    }
    window.addEventListener("beforeunload", preserveDirtyEditorForUnload);
    window.addEventListener("resize", layoutCodeEditor);
    window.addEventListener("pagehide", () => {
      captureCurrentEditorBuffer();
      if (state.dirty) {
        cancelDraftSave();
        captureSourceBuffer();
        saveEditorDraft(mainSourceValue());
        keepaliveSaveCurrentEditor();
      }
    });
    document.addEventListener("visibilitychange", () => {
      captureCurrentEditorBuffer();
      if (document.visibilityState === "hidden" && state.dirty) {
        cancelDraftSave();
        captureSourceBuffer();
        saveEditorDraft(mainSourceValue());
        keepaliveSaveCurrentEditor();
      }
    });
    document.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        if (state.view === "code") runTests().catch((error) => setStatus(error.message));
      }
    });
    initializeResizers();
    initializeMonacoEditor();
    applyUiLanguage();
    applySidebarCollapseState();
    updateCodeHighlight();
    updateContestModeToggle();
    updateToolbarMode();
    setupServerEvents();
    loadSettings()
      .catch((error) => {
        setStatus(error.message);
        state.settings = { uiLanguage: "en" };
        applyUiLanguage();
      })
      .finally(() => {
        loadProblems({ syncSolved: true }).catch((error) => setStatus(error.message));
      });
  </script>
</body>
</html>"""
