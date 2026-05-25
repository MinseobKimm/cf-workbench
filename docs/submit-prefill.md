# Submit Prefill

cf-workbench does not submit directly to Codeforces. Instead, it uses a safer
browser-assisted flow:

1. save the current source file,
2. run local tests,
3. open the Codeforces submit page,
4. let the included Chrome extension fill the problem, language, and source,
5. review the page and click Submit yourself.

This keeps the final submission action under your control.

## Requirements

- The included `browser-extension/` is loaded in Chrome.
- You are logged in to Codeforces in that browser.
- The local source file exists and can be read by cf-workbench.
- The Codeforces submit page is under `https://codeforces.com/`.

## Use From the Web UI

In the cf-workbench web UI, click `Submit` in the top toolbar.

The UI saves the editor, runs local tests, opens the Codeforces submit page,
and starts the extension-based prefill flow.

## How It Works

cf-workbench starts a short-lived helper server on `127.0.0.1` and opens
Codeforces with a one-use token in the URL fragment. The Chrome extension reads
that token, fetches the source from localhost, fills the submit form, and leaves
the final Submit click to you.

The token is generated locally and is intended for one prefill request.

## Troubleshooting

If prefill times out or the form is not filled:

- confirm that the updated `browser-extension/` is loaded and enabled,
- confirm that you are logged in to Codeforces,
- reload the Codeforces submit page,
- check that the page did not redirect to login or CAPTCHA,
- make sure cf-workbench or the submit prefill helper is still running,
- reload the extension after updating repository files.

## Contest Rules

cf-workbench is designed as a local practice tool. Use it only in ways that
respect the rules of the contest, practice session, or group you are
participating in.
