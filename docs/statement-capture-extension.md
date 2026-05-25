# Included Chrome Extension

cf-workbench includes a small Chrome extension in `browser-extension/`.

It has two jobs:

- capture a Codeforces problem statement from the page you are viewing,
- fill the Codeforces submit page from a local source file when submit prefill
  is requested.

The extension does not download Codeforces pages by itself. It only reads the
Codeforces page that is already open in your browser and talks to the local
cf-workbench server on `127.0.0.1`.

## 1. Start cf-workbench

Start cf-workbench with the normal app launcher, then keep the browser UI open.
On Windows, you can double-click `cf-workbench.cmd` from the repository folder.

The statement capture endpoint is:

```text
POST http://127.0.0.1:27121/capture-statement
```

## 2. Load the Extension

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Click Load unpacked.
4. Select the repository's `browser-extension/` folder.

Reload the extension after pulling updates or editing extension files.

## 3. Capture a Problem

1. Open a Codeforces problem page.
2. Click the floating `cfw` button near the bottom-right of the page.
3. Return to cf-workbench and confirm that the problem was imported.

The extension tries these local ports in order:

- `27121`
- `10043`
- `10045`

Imported files are written under:

```text
workspace/codeforces/{problemKey}/
|- problem.json
|- statement.html
|- statement.txt
|- main.cpp
`- tests/
```

## When to Use This Extension

Use the included extension when:

- you do not want to install Competitive Companion,
- Competitive Companion fails to capture a statement correctly,
- you want submit prefill support.

For problem import, Competitive Companion and this extension are alternatives.
For submit prefill, this extension is required.
