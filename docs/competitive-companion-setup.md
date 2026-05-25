# Competitive Companion Setup

Competitive Companion is an optional browser extension that sends Codeforces
problem data to a local tool. cf-workbench accepts that standard payload format
and creates a local problem folder with samples and a starter source file.

You can use Competitive Companion for problem import, or you can use the
included `browser-extension/`. You do not need both for importing problems.

## 1. Install Competitive Companion

Install Competitive Companion from your browser's extension store.

Supported browsers:

- Chrome or Chromium-based browsers
- Firefox

## 2. Start cf-workbench

Start cf-workbench with the normal app launcher, then keep the browser UI open.

On Windows, you can double-click `cf-workbench.cmd` from the repository folder.

Expected output:

```text
CF Workbench listening on http://127.0.0.1:27121
Workspace: .\workspace
Waiting for Competitive Companion payloads...
```

Keep this terminal open while importing problems.

## 3. Import One Problem

1. Open a Codeforces problem page.
2. Click the Competitive Companion button.
3. Return to cf-workbench.
4. Confirm that the problem appears in the local UI.

Imported files are written under:

```text
workspace/codeforces/{problemKey}/
```

## 4. Import a Contest

Open a Codeforces contest problem list and click the Competitive Companion
button. Competitive Companion may send one payload per problem. cf-workbench
stores each payload as its own problem folder.

## Notes

- The server binds to `127.0.0.1` only.
- Competitive Companion is only needed for importing problem statements and
  samples.
- Submit prefill uses the included `browser-extension/`, not Competitive
  Companion.
