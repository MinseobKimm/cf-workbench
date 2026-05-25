(() => {
  const PORTS = [27121, 10043, 10045];
  const BUTTON_ID = "cfw-statement-capture-button";

  function readPre(pre) {
    if (!pre) return "";
    const lineNodes = Array.from(pre.querySelectorAll(".test-example-line"));
    const children = lineNodes.length
      ? lineNodes
      : Array.from(pre.children).filter((child) => child.tagName.toLowerCase() === "div");
    const text = children.length
      ? children.map((child) => child.textContent || "").join("\n")
      : pre.innerText || pre.textContent || "";
    return normalizeText(text);
  }

  function normalizeText(value) {
    const normalized = String(value || "")
      .replace(/\u00a0/g, " ")
      .replace(/\r\n/g, "\n")
      .replace(/\r/g, "\n");
    return normalized.endsWith("\n") ? normalized : `${normalized}\n`;
  }

  function parseLimitMs(text) {
    const value = String(text || "").toLowerCase();
    const number = Number((value.match(/([0-9]+(?:\.[0-9]+)?)/) || [])[1]);
    if (!Number.isFinite(number)) return null;
    if (value.includes("second")) return Math.round(number * 1000);
    return Math.round(number);
  }

  function parseMemoryMb(text) {
    const value = String(text || "").toLowerCase();
    const number = Number((value.match(/([0-9]+(?:\.[0-9]+)?)/) || [])[1]);
    if (!Number.isFinite(number)) return null;
    if (value.includes("kilobyte") || value.includes(" kb")) return Math.ceil(number / 1024);
    return Math.round(number);
  }

  function capturePayload(statement = document.querySelector(".problem-statement")) {
    if (!statement) return null;

    const sample = statement.querySelector(".sample-test");
    const inputs = sample ? Array.from(sample.querySelectorAll(".input")) : [];
    const outputs = sample ? Array.from(sample.querySelectorAll(".output")) : [];
    const tests = inputs.map((inputBlock, index) => ({
      input: readPre(inputBlock.querySelector("pre")),
      output: readPre(outputs[index] && outputs[index].querySelector("pre")),
    })).filter((test) => test.input.length > 0 || test.output.length > 0);

    return {
      kind: "codeforces-dom-statement",
      url: location.href,
      title: document.title,
      problemName: (statement.querySelector(".title") || {}).textContent || document.title,
      group: (document.querySelector(".rtable .left") || {}).textContent || "",
      timeLimitMs: parseLimitMs((statement.querySelector(".time-limit") || {}).textContent),
      memoryLimitMb: parseMemoryMb((statement.querySelector(".memory-limit") || {}).textContent),
      html: statementHtmlForWorkbench(statement),
      text: statementTextForWorkbench(statement),
      tests,
    };
  }

  function statementHtmlForWorkbench(statement) {
    const clone = statement.cloneNode(true);
    snapshotMathStyles(statement, clone);
    absolutizeResourceUrls(statement, clone);
    cleanupMathMarkup(clone);
    return clone.outerHTML;
  }

  function absolutizeResourceUrls(sourceRoot, cloneRoot) {
    const sourceNodes = [sourceRoot, ...sourceRoot.querySelectorAll("*")];
    const cloneNodes = [cloneRoot, ...cloneRoot.querySelectorAll("*")];
    for (let index = 0; index < sourceNodes.length && index < cloneNodes.length; index += 1) {
      const source = sourceNodes[index];
      const clone = cloneNodes[index];
      if (source.tagName && source.tagName.toLowerCase() === "img" && source.src) {
        clone.setAttribute("src", source.src);
      }
      if (source.tagName && source.tagName.toLowerCase() === "a" && source.href) {
        clone.setAttribute("href", source.href);
      }
    }
  }

  function statementTextForWorkbench(statement) {
    const clone = statement.cloneNode(true);
    removeMathForText(clone);
    return clone.textContent || "";
  }

  function cleanupMathMarkup(root) {
    root.querySelectorAll(".MathJax_Preview").forEach((preview) => {
      const next = preview.nextElementSibling;
      if (next && (next.matches(".MathJax:not(.MathJax_Processing)") || next.matches("mjx-container"))) {
        preview.remove();
      }
    });
    root.querySelectorAll(".MathJax_Processing").forEach((node) => {
      node.remove();
    });
  }

  function removeMathForText(root) {
    const selectors = [
      ".MathJax",
      ".MathJax_Preview",
      "[class*='MathJax']",
      "mjx-container",
      "script[type^='math/tex']",
    ];
    root.querySelectorAll(selectors.join(",")).forEach((node) => {
      node.replaceWith(document.createTextNode(" "));
    });
  }

  function snapshotMathStyles(sourceRoot, cloneRoot) {
    const sourceNodes = [sourceRoot, ...sourceRoot.querySelectorAll("*")];
    const cloneNodes = [cloneRoot, ...cloneRoot.querySelectorAll("*")];
    for (let index = 0; index < sourceNodes.length && index < cloneNodes.length; index += 1) {
      const source = sourceNodes[index];
      const clone = cloneNodes[index];
      if (!isMathSnapshotNode(source)) continue;
      copyMathComputedStyle(source, clone);
      clone.setAttribute("data-cfw-math-snapshot", "1");
    }
  }

  function isMathSnapshotNode(node) {
    if (!node || !node.matches) return false;
    return Boolean(node.closest([
      ".MathJax",
      ".MathJax_Preview",
      "mjx-container",
      "[class*='MJX']",
      "[class*='mjx']",
    ].join(",")));
  }

  function copyMathComputedStyle(source, target) {
    const computed = getComputedStyle(source);
    const properties = [
      "display",
      "position",
      "float",
      "clear",
      "box-sizing",
      "vertical-align",
      "direction",
      "unicode-bidi",
      "visibility",
      "overflow",
      "overflow-x",
      "overflow-y",
      "white-space",
      "text-align",
      "text-indent",
      "text-transform",
      "letter-spacing",
      "word-spacing",
      "line-height",
      "font",
      "font-family",
      "font-size",
      "font-style",
      "font-weight",
      "font-variant",
      "color",
      "background",
      "background-color",
      "width",
      "height",
      "min-width",
      "min-height",
      "max-width",
      "max-height",
      "margin",
      "margin-top",
      "margin-right",
      "margin-bottom",
      "margin-left",
      "padding",
      "padding-top",
      "padding-right",
      "padding-bottom",
      "padding-left",
      "border",
      "border-collapse",
      "border-spacing",
      "top",
      "right",
      "bottom",
      "left",
      "transform",
      "transform-origin",
    ];
    const rules = properties
      .map((property) => {
        const value = computed.getPropertyValue(property);
        return value ? `${property}:${value}` : "";
      })
      .filter(Boolean)
      .join(";");
    const existing = target.getAttribute("style") || "";
    target.setAttribute("style", existing ? `${existing};${rules}` : rules);
  }

  function hasPendingMath(statement) {
    return Boolean(statement && statement.querySelector(".MathJax_Processing, .MathJax_Preview + .MathJax_Processing"));
  }

  async function waitForStatementReady(timeoutMs = 5000) {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      const statement = document.querySelector(".problem-statement");
      if (!statement) return null;
      if (!hasPendingMath(statement)) return statement;
      await delay(150);
    }
    return document.querySelector(".problem-statement");
  }

  async function postCapture(payload) {
    let lastError = null;
    for (const port of PORTS) {
      try {
        const response = await fetch(`http://127.0.0.1:${port}/capture-statement`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok || data.ok === false) throw new Error(data.error || "capture failed");
        return { port, data };
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError || new Error("cf-workbench is not reachable");
  }

  function ensureButton(title = "Capture this Codeforces statement into cf-workbench") {
    if (document.getElementById(BUTTON_ID)) return document.getElementById(BUTTON_ID);
    const button = document.createElement("button");
    button.id = BUTTON_ID;
    button.type = "button";
    button.textContent = "cfw";
    button.title = title;
    button.style.cssText = [
      "position:fixed",
      "right:14px",
      "bottom:14px",
      "z-index:2147483647",
      "height:34px",
      "min-width:52px",
      "padding:0 10px",
      "border:1px solid #0f766e",
      "border-radius:6px",
      "background:#0f766e",
      "color:#fff",
      "font:700 13px Arial,sans-serif",
      "box-shadow:0 8px 24px rgba(0,0,0,.18)",
      "cursor:pointer",
    ].join(";");
    button.addEventListener("click", () => {
      const prefillInfo = parseSubmitPrefillHash();
      if (prefillInfo) prefillSubmitPage(prefillInfo);
      else captureOnce(false);
    });
    document.documentElement.appendChild(button);
    return button;
  }

  function setButtonStatus(text, ok) {
    const button = ensureButton();
    button.textContent = text;
    button.style.background = ok ? "#137333" : "#b42318";
    button.style.borderColor = ok ? "#137333" : "#b42318";
  }

  async function captureOnce(silent) {
    const statement = await waitForStatementReady(silent ? 5000 : 15000);
    const payload = capturePayload(statement);
    if (!payload) return;
    if (!silent) setButtonStatus("...", true);
    try {
      const result = await postCapture(payload);
      setButtonStatus(`cfw ${result.port}`, true);
    } catch (error) {
      setButtonStatus("cfw off", false);
      if (!silent) console.warn("cf-workbench statement capture failed:", error);
    }
  }

  function parseSubmitPrefillHash() {
    const params = new URLSearchParams(String(location.hash || "").replace(/^#/, ""));
    if (params.get("cfw-submit") !== "1") return null;
    const port = Number(params.get("cfw-port"));
    const token = params.get("cfw-token") || "";
    if (!Number.isInteger(port) || port < 1 || port > 65535 || !token) return null;
    return { port, token };
  }

  async function prefillSubmitPage(info) {
    ensureButton("Fill this Codeforces submit form from cf-workbench");
    setButtonStatus("cfw ...", true);
    try {
      const response = await fetch(`http://127.0.0.1:${info.port}/submit-prefill?token=${encodeURIComponent(info.token)}`);
      const payload = await response.json();
      if (!response.ok || payload.ok === false) throw new Error(payload.error || "prefill failed");
      const result = await fillSubmitFormWithRetry(payload);
      setButtonStatus(result.source ? "cfw filled" : "cfw partial", result.source);
      console.info("cf-workbench submit prefill:", result);
    } catch (error) {
      setButtonStatus("cfw fail", false);
      console.warn("cf-workbench submit prefill failed:", error);
    }
  }

  async function fillSubmitFormWithRetry(payload) {
    let result = fillSubmitForm(payload);
    for (let attempt = 0; attempt < 20 && !result.source; attempt += 1) {
      await delay(250);
      result = fillSubmitForm(payload);
    }
    return result;
  }

  function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function fillSubmitForm(payload) {
    return {
      problem: fillProblem(payload),
      language: fillLanguage(payload),
      source: fillSource(payload),
    };
  }

  function fillProblem(payload) {
    const problemIndex = String(payload.problemIndex || "").trim();
    const problemKey = String(payload.problemKey || "").trim();
    const contestId = String(payload.contestId || "").trim();
    const candidates = uniqueValues([
      problemIndex,
      problemKey,
      contestId && problemIndex ? `${contestId}${problemIndex}` : "",
      contestId && problemIndex ? `${contestId} ${problemIndex}` : "",
    ]);

    for (const select of document.querySelectorAll('select[name*="problem" i], select[id*="problem" i]')) {
      if (chooseOption(select, candidates, { startsWith: true })) return true;
    }

    for (const input of document.querySelectorAll('input[name*="problem" i], input[id*="problem" i]')) {
      if (input.type === "hidden") continue;
      setNativeValue(input, problemKey || (contestId && problemIndex ? `${contestId}${problemIndex}` : problemIndex));
      dispatchChanged(input);
      return true;
    }
    return false;
  }

  function fillLanguage(payload) {
    const language = String(payload.language || "").toLowerCase();
    const candidates = languageCandidates(language);
    if (!candidates.length) return false;
    const selectors = [
      'select[name="programTypeId"]',
      'select[id*="programType" i]',
      'select[name*="program" i]',
      'select[id*="language" i]',
      'select[name*="language" i]',
    ].join(", ");
    for (const select of document.querySelectorAll(selectors)) {
      if (chooseOption(select, candidates, { startsWith: false })) return true;
    }
    return false;
  }

  function fillSource(payload) {
    const source = String(payload.source || "");
    if (!source) return false;

    for (const wrapper of document.querySelectorAll(".CodeMirror")) {
      if (wrapper.CodeMirror && typeof wrapper.CodeMirror.setValue === "function") {
        wrapper.CodeMirror.setValue(source);
        if (typeof wrapper.CodeMirror.save === "function") wrapper.CodeMirror.save();
        return true;
      }
    }

    const selectors = [
      'textarea[name="source"]',
      "textarea#sourceCodeTextarea",
      'textarea[name*="source" i]',
      'textarea[id*="source" i]',
      "textarea",
    ].join(", ");
    const textarea = document.querySelector(selectors);
    if (!textarea) return false;
    setNativeValue(textarea, source);
    dispatchChanged(textarea);
    return true;
  }

  function chooseOption(select, candidates, options) {
    const normalizedCandidates = candidates.map((candidate) => normalizeChoice(candidate)).filter(Boolean);
    if (!normalizedCandidates.length) return false;

    for (const option of Array.from(select.options || [])) {
      const value = normalizeChoice(option.value);
      const text = normalizeChoice(option.textContent || "");
      if (normalizedCandidates.some((candidate) => value === candidate || text === candidate)) {
        select.value = option.value;
        dispatchChanged(select);
        return true;
      }
    }

    for (const option of Array.from(select.options || [])) {
      const text = normalizeChoice(option.textContent || "");
      const matched = normalizedCandidates.some((candidate) => (
        options.startsWith ? text.startsWith(candidate) : text.includes(candidate)
      ));
      if (matched) {
        select.value = option.value;
        dispatchChanged(select);
        return true;
      }
    }
    return false;
  }

  function languageCandidates(language) {
    if (language.includes("20")) return ["gnu c++20", "g++20", "c++20"];
    if (language.includes("23")) return ["gnu c++23", "g++23", "c++23"];
    if (language.includes("14")) return ["gnu c++14", "g++14", "c++14"];
    if (language.includes("11")) return ["gnu c++11", "g++11", "c++11"];
    if (language.includes("py") || language.includes("python")) return ["pypy 3", "python 3"];
    if (language.includes("java")) return ["java"];
    if (language.includes("kotlin")) return ["kotlin"];
    if (language.includes("rust")) return ["rust"];
    if (language.includes("go")) return ["go"];
    if (language.includes("cpp") || language.includes("c++") || language.includes("gnu++")) {
      return ["gnu c++17", "g++17", "c++17"];
    }
    return [language];
  }

  function setNativeValue(element, value) {
    const prototype = element instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
    if (descriptor && descriptor.set) descriptor.set.call(element, value);
    else element.value = value;
  }

  function dispatchChanged(element) {
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function uniqueValues(values) {
    return Array.from(new Set(values.map((value) => String(value || "").trim()).filter(Boolean)));
  }

  function normalizeChoice(value) {
    return String(value || "").toLowerCase().replace(/\s+/g, " ").trim();
  }

  if (document.querySelector(".problem-statement")) {
    ensureButton();
    captureOnce(true);
  }
  const submitPrefillInfo = parseSubmitPrefillHash();
  if (submitPrefillInfo) {
    prefillSubmitPage(submitPrefillInfo);
  }
})();
