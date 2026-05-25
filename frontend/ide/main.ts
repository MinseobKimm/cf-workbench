import * as monaco from "monaco-editor";
import "monaco-editor/esm/vs/basic-languages/cpp/cpp.contribution";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";

type StatusFn = (message: string) => void;

type MountOptions = {
  container: HTMLElement | null;
  textarea: HTMLTextAreaElement | null;
  setStatus?: StatusFn;
  onInput?: () => void;
  onSave?: () => void;
  onRun?: () => void;
};

type DocumentOptions = {
  value: string;
  language?: string;
  readOnly?: boolean;
  fileUri?: string;
  rootUri?: string;
  lspUrl?: string;
  diagnosticsUrl?: string;
  sourceName?: string;
  clangdAvailable?: boolean;
  documentId?: string;
};

type ViewportSnapshot = {
  uri: string;
  viewState: monaco.editor.ICodeEditorViewState | null;
};

type LspPosition = { line: number; character: number };
type LspRange = { start: LspPosition; end: LspPosition };
type LspLocation = { uri: string; range: LspRange };
type LspDiagnostic = { range: LspRange; severity?: number; message: string; source?: string; code?: string | number };
type LspCompletionItem = {
  label: string | { label: string };
  kind?: number;
  detail?: string;
  documentation?: string | { kind?: string; value?: string };
  insertText?: string;
  insertTextFormat?: number;
  textEdit?: { range: LspRange; newText: string };
};

declare global {
  interface Window {
    cfwIde: CfwIdeApi;
    MonacoEnvironment?: unknown;
  }
}

window.MonacoEnvironment = {
  getWorker() {
    return new editorWorker();
  },
};

class LspClient {
  private socket: WebSocket | null = null;
  private nextId = 1;
  private pending = new Map<number, { resolve: (value: unknown) => void; reject: (reason: unknown) => void }>();
  private version = 1;
  private ready = false;
  private opened = false;

  constructor(
    private readonly url: string,
    private readonly rootUri: string,
    private readonly fileUri: string,
    private text: string,
    private readonly setStatus: StatusFn,
  ) {}

  connect(): void {
    this.socket = new WebSocket(toWebSocketUrl(this.url));
    this.socket.onopen = () => {
      this.initialize().catch((error) => this.setStatus(`clangd initialize failed: ${error.message || String(error)}`));
    };
    this.socket.onmessage = (event) => this.handleMessage(String(event.data));
    this.socket.onerror = () => this.setStatus("clangd connection error");
    this.socket.onclose = () => {
      this.ready = false;
      this.opened = false;
    };
  }

  close(): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN && this.opened) {
      this.sendNotification("textDocument/didClose", { textDocument: { uri: this.fileUri } });
    }
    this.pending.forEach((item) => item.reject(new Error("clangd connection closed")));
    this.pending.clear();
    this.socket?.close();
    this.socket = null;
  }

  updateText(text: string): void {
    this.text = text;
    if (!this.ready || !this.opened) return;
    this.version += 1;
    this.sendNotification("textDocument/didChange", {
      textDocument: { uri: this.fileUri, version: this.version },
      contentChanges: [{ text }],
    });
  }

  request(method: string, params: unknown): Promise<unknown> {
    if (!this.ready || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return Promise.reject(new Error("clangd is not ready"));
    }
    return this.sendRequest(method, params);
  }

  private async initialize(): Promise<void> {
    await this.sendRequest("initialize", {
      processId: null,
      rootUri: this.rootUri,
      workspaceFolders: [{ uri: this.rootUri, name: "problem" }],
      capabilities: {
        textDocument: {
          synchronization: { dynamicRegistration: false, didSave: false },
          completion: { completionItem: { snippetSupport: true, documentationFormat: ["markdown", "plaintext"] } },
          hover: { contentFormat: ["markdown", "plaintext"] },
          definition: {},
          publishDiagnostics: { relatedInformation: true },
        },
        workspace: { workspaceFolders: true, configuration: false },
      },
    });
    this.ready = true;
    this.sendNotification("initialized", {});
    this.sendNotification("textDocument/didOpen", {
      textDocument: {
        uri: this.fileUri,
        languageId: "cpp",
        version: this.version,
        text: this.text,
      },
    });
    this.opened = true;
    this.setStatus("clangd ready");
  }

  private sendRequest(method: string, params: unknown): Promise<unknown> {
    const socket = this.socket;
    if (!socket || socket.readyState !== WebSocket.OPEN) return Promise.reject(new Error("clangd socket is closed"));
    const id = this.nextId++;
    socket.send(JSON.stringify({ jsonrpc: "2.0", id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      window.setTimeout(() => {
        const pending = this.pending.get(id);
        if (!pending) return;
        this.pending.delete(id);
        pending.reject(new Error(`${method} timed out`));
      }, 8000);
    });
  }

  private sendNotification(method: string, params: unknown): void {
    const socket = this.socket;
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    socket.send(JSON.stringify({ jsonrpc: "2.0", method, params }));
  }

  private sendResponse(id: number, result: unknown): void {
    const socket = this.socket;
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    socket.send(JSON.stringify({ jsonrpc: "2.0", id, result }));
  }

  private handleMessage(raw: string): void {
    let message: { id?: number; method?: string; params?: unknown; result?: unknown; error?: unknown };
    try {
      message = JSON.parse(raw);
    } catch {
      return;
    }
    if (typeof message.id === "number" && message.method) {
      this.sendResponse(message.id, null);
      return;
    }
    if (typeof message.id === "number") {
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      if (message.error) pending.reject(message.error);
      else pending.resolve(message.result);
      return;
    }
    if (message.method === "textDocument/publishDiagnostics") {
      applyDiagnostics(message.params);
    }
  }
}

class CompilerDiagnosticsClient {
  private requestId = 0;

  constructor(
    private readonly url: string,
    private readonly sourceName: string,
    private readonly setStatus: StatusFn,
  ) {}

  async check(model: monaco.editor.ITextModel): Promise<void> {
    const id = ++this.requestId;
    try {
      const response = await fetch(this.url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sourceName: this.sourceName, source: model.getValue() }),
      });
      if (id !== this.requestId) return;
      const payload = await response.json();
      if (!response.ok || !payload.ok) throw new Error(payload.error || "diagnostics failed");
      const markers = (payload.diagnostics || []).map((item: { line: number; column: number; severity: string; message: string }) => ({
        startLineNumber: Math.max(1, Number(item.line) || 1),
        startColumn: Math.max(1, Number(item.column) || 1),
        endLineNumber: Math.max(1, Number(item.line) || 1),
        endColumn: Math.max(2, (Number(item.column) || 1) + 1),
        severity: compilerSeverity(item.severity),
        message: item.message,
        source: "g++",
      }));
      monaco.editor.setModelMarkers(model, "g++", markers);
      if (markers.length) this.setStatus(`${markers.length} diagnostic(s)`);
    } catch (error) {
      if (id !== this.requestId) return;
      this.setStatus(`diagnostics failed: ${(error as Error).message || String(error)}`);
    }
  }
}

class CfwIdeApi {
  private editor: monaco.editor.IStandaloneCodeEditor | null = null;
  private textarea: HTMLTextAreaElement | null = null;
  private model: monaco.editor.ITextModel | null = null;
  private client: LspClient | null = null;
  private fallbackDiagnostics: CompilerDiagnosticsClient | null = null;
  private currentUri = "";
  private suppressChange = false;
  private onInput: (() => void) | null = null;
  private setStatus: StatusFn = () => undefined;
  private changeTimer = 0;

  isReady(): boolean {
    return Boolean(this.editor);
  }

  mount(options: MountOptions): void {
    if (!options.container || !options.textarea) throw new Error("missing Monaco mount target");
    if (this.editor) return;
    this.textarea = options.textarea;
    this.onInput = options.onInput || null;
    this.setStatus = options.setStatus || (() => undefined);
    this.editor = monaco.editor.create(options.container, {
      automaticLayout: true,
      fontFamily: '"Cascadia Code", Consolas, monospace',
      fontLigatures: false,
      fontSize: 14,
      lineHeight: 22,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      tabSize: 4,
      insertSpaces: true,
      detectIndentation: false,
      theme: "vs-dark",
      wordWrap: "off",
    });
    this.editor.addAction({
      id: "cfw-save",
      label: "Save",
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS],
      run: () => options.onSave?.(),
    });
    this.editor.addAction({
      id: "cfw-run",
      label: "Run samples",
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter],
      run: () => options.onRun?.(),
    });
    this.editor.onDidChangeModelContent(() => {
      if (this.suppressChange) return;
      this.syncTextarea();
      window.clearTimeout(this.changeTimer);
      this.changeTimer = window.setTimeout(() => {
        if (this.model) this.client?.updateText(this.model.getValue());
        if (this.model) this.fallbackDiagnostics?.check(this.model);
      }, 150);
      this.onInput?.();
    });
    registerLanguageProviders(() => this.client, this.setStatus);
  }

  setDocument(options: DocumentOptions): void {
    if (!this.editor) return;
    const language = options.language || "cpp";
    const uri = options.fileUri || `inmemory://cfw/${encodeURIComponent(options.documentId || "scratch.cpp")}`;
    const value = options.value || "";
    if (!this.model || this.currentUri !== uri) {
      this.client?.close();
      this.fallbackDiagnostics = null;
      this.model?.dispose();
      this.currentUri = uri;
      this.model = monaco.editor.createModel(value, language, monaco.Uri.parse(uri));
      this.editor.setModel(this.model);
      if (options.clangdAvailable && options.lspUrl && options.fileUri && options.rootUri) {
        this.client = new LspClient(options.lspUrl, options.rootUri, options.fileUri, value, this.setStatus);
        this.client.connect();
      } else {
        this.client = null;
        if (options.diagnosticsUrl && options.fileUri) {
          this.fallbackDiagnostics = new CompilerDiagnosticsClient(
            options.diagnosticsUrl,
            options.sourceName || "main.cpp",
            this.setStatus,
          );
          this.fallbackDiagnostics.check(this.model);
        }
        if (options.fileUri) this.setStatus("clangd unavailable");
      }
    } else if (this.model.getValue() !== value) {
      this.suppressChange = true;
      this.model.setValue(value);
      this.suppressChange = false;
      this.client?.updateText(value);
      this.fallbackDiagnostics?.check(this.model);
    }
    this.editor.updateOptions({ readOnly: Boolean(options.readOnly) });
    this.syncTextarea();
    this.editor.layout();
  }

  getValue(): string {
    return this.model?.getValue() || this.textarea?.value || "";
  }

  captureViewport(): ViewportSnapshot | null {
    if (!this.editor) return null;
    return { uri: this.currentUri, viewState: this.editor.saveViewState() };
  }

  restoreViewport(snapshot: ViewportSnapshot | null): void {
    if (!this.editor || !snapshot || snapshot.uri !== this.currentUri) return;
    if (snapshot.viewState) this.editor.restoreViewState(snapshot.viewState);
    this.editor.focus();
  }

  layout(): void {
    this.editor?.layout();
  }

  private syncTextarea(): void {
    if (this.textarea && this.model) this.textarea.value = this.model.getValue();
  }
}

function registerLanguageProviders(getClient: () => LspClient | null, setStatus: StatusFn): void {
  monaco.languages.registerCompletionItemProvider("cpp", {
    triggerCharacters: [".", ">", ":", "#", "<", '"', "/"],
    async provideCompletionItems(model, position) {
      const client = getClient();
      if (!client) return { suggestions: [] };
      try {
        const result = await client.request("textDocument/completion", {
          textDocument: { uri: model.uri.toString() },
          position: toLspPosition(position),
        });
        return { suggestions: toCompletionItems(result, model, position) };
      } catch {
        return { suggestions: [] };
      }
    },
  });
  monaco.languages.registerHoverProvider("cpp", {
    async provideHover(model, position) {
      const client = getClient();
      if (!client) return null;
      try {
        const result = await client.request("textDocument/hover", {
          textDocument: { uri: model.uri.toString() },
          position: toLspPosition(position),
        });
        return toHover(result);
      } catch {
        return null;
      }
    },
  });
  monaco.languages.registerDefinitionProvider("cpp", {
    async provideDefinition(model, position) {
      const client = getClient();
      if (!client) return [];
      try {
        const result = await client.request("textDocument/definition", {
          textDocument: { uri: model.uri.toString() },
          position: toLspPosition(position),
        });
        return toLocations(result);
      } catch (error) {
        setStatus(`definition failed: ${(error as Error).message || String(error)}`);
        return [];
      }
    },
  });
}

function toCompletionItems(
  result: unknown,
  model: monaco.editor.ITextModel,
  position: monaco.Position,
): monaco.languages.CompletionItem[] {
  const items = Array.isArray(result)
    ? result
    : result && typeof result === "object" && Array.isArray((result as { items?: unknown }).items)
      ? (result as { items: unknown[] }).items
      : [];
  const word = model.getWordUntilPosition(position);
  const fallbackRange = new monaco.Range(position.lineNumber, word.startColumn, position.lineNumber, word.endColumn);
  return items.map((raw) => {
    const item = raw as LspCompletionItem;
    const label = typeof item.label === "string" ? item.label : item.label.label;
    const textEdit = item.textEdit;
    return {
      label,
      kind: completionKind(item.kind),
      detail: item.detail,
      documentation: markupToMarkdown(item.documentation),
      insertText: textEdit ? textEdit.newText : item.insertText || label,
      insertTextRules: item.insertTextFormat === 2 ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet : undefined,
      range: textEdit ? toMonacoRange(textEdit.range) : fallbackRange,
    };
  });
}

function toHover(result: unknown): monaco.languages.Hover | null {
  const contents = result && typeof result === "object" ? (result as { contents?: unknown }).contents : null;
  const value = markupToMarkdown(contents);
  return value ? { contents: [value] } : null;
}

function toLocations(result: unknown): monaco.languages.Location[] {
  const values = Array.isArray(result) ? result : result ? [result] : [];
  return values
    .map((item) => item as LspLocation)
    .filter((item) => item.uri && item.range)
    .map((item) => ({ uri: monaco.Uri.parse(item.uri), range: toMonacoRange(item.range) }));
}

function applyDiagnostics(params: unknown): void {
  const payload = params as { uri?: string; diagnostics?: LspDiagnostic[] };
  if (!payload.uri) return;
  const model = monaco.editor.getModel(monaco.Uri.parse(payload.uri));
  if (!model) return;
  const markers = (payload.diagnostics || []).map((diagnostic) => ({
    severity: diagnosticSeverity(diagnostic.severity),
    message: diagnostic.message,
    source: diagnostic.source,
    code: diagnostic.code ? String(diagnostic.code) : undefined,
    ...rangeToMarker(diagnostic.range),
  }));
  monaco.editor.setModelMarkers(model, "clangd", markers);
}

function toLspPosition(position: monaco.Position): LspPosition {
  return { line: position.lineNumber - 1, character: position.column - 1 };
}

function toMonacoRange(range: LspRange): monaco.Range {
  return new monaco.Range(
    range.start.line + 1,
    range.start.character + 1,
    range.end.line + 1,
    range.end.character + 1,
  );
}

function rangeToMarker(range: LspRange): Pick<monaco.editor.IMarkerData, "startLineNumber" | "startColumn" | "endLineNumber" | "endColumn"> {
  return {
    startLineNumber: range.start.line + 1,
    startColumn: range.start.character + 1,
    endLineNumber: range.end.line + 1,
    endColumn: range.end.character + 1,
  };
}

function diagnosticSeverity(severity = 1): monaco.MarkerSeverity {
  if (severity === 2) return monaco.MarkerSeverity.Warning;
  if (severity === 3) return monaco.MarkerSeverity.Info;
  if (severity === 4) return monaco.MarkerSeverity.Hint;
  return monaco.MarkerSeverity.Error;
}

function compilerSeverity(severity: string): monaco.MarkerSeverity {
  if (severity === "warning") return monaco.MarkerSeverity.Warning;
  if (severity === "info") return monaco.MarkerSeverity.Info;
  return monaco.MarkerSeverity.Error;
}

function completionKind(kind = 1): monaco.languages.CompletionItemKind {
  const mapping: Record<number, monaco.languages.CompletionItemKind> = {
    2: monaco.languages.CompletionItemKind.Method,
    3: monaco.languages.CompletionItemKind.Function,
    4: monaco.languages.CompletionItemKind.Constructor,
    5: monaco.languages.CompletionItemKind.Field,
    6: monaco.languages.CompletionItemKind.Variable,
    7: monaco.languages.CompletionItemKind.Class,
    8: monaco.languages.CompletionItemKind.Interface,
    9: monaco.languages.CompletionItemKind.Module,
    10: monaco.languages.CompletionItemKind.Property,
    11: monaco.languages.CompletionItemKind.Unit,
    12: monaco.languages.CompletionItemKind.Value,
    13: monaco.languages.CompletionItemKind.Enum,
    14: monaco.languages.CompletionItemKind.Keyword,
    15: monaco.languages.CompletionItemKind.Snippet,
    17: monaco.languages.CompletionItemKind.File,
    18: monaco.languages.CompletionItemKind.Reference,
    20: monaco.languages.CompletionItemKind.Folder,
    21: monaco.languages.CompletionItemKind.EnumMember,
    22: monaco.languages.CompletionItemKind.Constant,
    23: monaco.languages.CompletionItemKind.Struct,
    24: monaco.languages.CompletionItemKind.Event,
    25: monaco.languages.CompletionItemKind.Operator,
  };
  return mapping[kind] || monaco.languages.CompletionItemKind.Text;
}

function markupToMarkdown(value: unknown): monaco.IMarkdownString | undefined {
  if (!value) return undefined;
  if (typeof value === "string") return { value };
  if (Array.isArray(value)) {
    const text = value.map((item) => markupToText(item)).filter(Boolean).join("\n\n");
    return text ? { value: text } : undefined;
  }
  if (typeof value === "object") {
    const object = value as { value?: unknown; language?: unknown };
    if (typeof object.value === "string") {
      if (typeof object.language === "string") return { value: `\`\`\`${object.language}\n${object.value}\n\`\`\`` };
      return { value: object.value };
    }
  }
  return undefined;
}

function markupToText(value: unknown): string {
  const markdown = markupToMarkdown(value);
  return markdown ? markdown.value : "";
}

function toWebSocketUrl(path: string): string {
  const url = new URL(path, window.location.href);
  url.protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
}

window.cfwIde = new CfwIdeApi();
