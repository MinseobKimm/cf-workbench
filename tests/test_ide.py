import io
import json
import subprocess

import pytest

import cf_workbench.ide as ide_module
from cf_workbench.ide import (
    WebSocketClosed,
    detect_clangd,
    hidden_subprocess_kwargs,
    parse_gcc_diagnostics,
    read_lsp_message,
    read_websocket_frame,
    websocket_accept_key,
    write_compile_commands,
    write_lsp_message,
    write_websocket_frame,
)


def test_detect_clangd_uses_configured_path(tmp_path):
    clangd = tmp_path / "clangd"
    clangd.write_text("", encoding="utf-8")

    detected = detect_clangd(str(clangd))

    assert detected.path == str(clangd)


def test_detect_clangd_missing_configured_path_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="clangd not found"):
        detect_clangd(str(tmp_path / "missing-clangd"))


def test_hidden_subprocess_kwargs_hide_console_on_windows(monkeypatch):
    monkeypatch.setattr(ide_module.os, "name", "nt")
    kwargs = hidden_subprocess_kwargs()

    if not hasattr(subprocess, "STARTUPINFO"):
        assert kwargs == {}
        return
    assert kwargs["creationflags"] == getattr(subprocess, "CREATE_NO_WINDOW", 0)
    assert kwargs["startupinfo"].dwFlags & subprocess.STARTF_USESHOWWINDOW


def test_hidden_subprocess_kwargs_empty_off_windows(monkeypatch):
    monkeypatch.setattr(ide_module.os, "name", "posix")

    assert hidden_subprocess_kwargs() == {}


def test_write_compile_commands_uses_gnu17_and_selected_source(tmp_path, monkeypatch):
    source = tmp_path / "alt.cpp"
    source.write_text("int main() {}", encoding="utf-8")
    monkeypatch.setattr(
        "cf_workbench.ide.detect_compiler",
        lambda configured=None: type("Compiler", (), {"path": "g++"})(),
    )

    path = write_compile_commands(tmp_path, source, configured_compiler="g++")

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["directory"] == str(tmp_path.resolve())
    assert "-std=gnu++17" in data[0]["arguments"]
    assert str(source.resolve()) in data[0]["arguments"]
    assert data[0]["file"] == str(source.resolve())


def test_lsp_content_length_round_trip():
    stream = io.BytesIO()
    write_lsp_message(stream, '{"jsonrpc":"2.0"}')
    stream.seek(0)

    assert read_lsp_message(stream) == b'{"jsonrpc":"2.0"}'


def test_websocket_frame_round_trip_unmasked():
    class Socket:
        def __init__(self):
            self.buffer = bytearray()

        def sendall(self, payload):
            self.buffer.extend(payload)

    sock = Socket()
    write_websocket_frame(sock, "hello")
    frame = read_websocket_frame(io.BytesIO(sock.buffer))

    assert frame.opcode == 1
    assert frame.payload == b"hello"


def test_websocket_frame_short_read_closes():
    with pytest.raises(WebSocketClosed):
        read_websocket_frame(io.BytesIO(b"\x81"))


def test_websocket_accept_key_matches_rfc_example():
    assert websocket_accept_key("dGhlIHNhbXBsZSBub25jZQ==") == "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="


def test_parse_gcc_diagnostics_extracts_markers():
    diagnostics = parse_gcc_diagnostics(
        "C:/tmp/main.cpp:3:7: error: expected ';' before '}' token\n"
        "C:/tmp/main.cpp:4:1: warning: no return statement in function returning non-void\n"
    )

    assert diagnostics == [
        {"line": 3, "column": 7, "severity": "error", "message": "expected ';' before '}' token"},
        {
            "line": 4,
            "column": 1,
            "severity": "warning",
            "message": "no return statement in function returning non-void",
        },
    ]
