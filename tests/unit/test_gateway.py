"""Unit tests for lazy-gateway: tokens, JSON-RPC bus, protocol, and server."""
from __future__ import annotations

import json
import socket
import struct
import threading
import time
from pathlib import Path

import pytest

from lazy.gateway.protocol import (
    GatewayProtocolMessage,
    compute_ws_accept,
    decode_ws_frame,
    encode_ws_frame,
)
from lazy.gateway.rpc_bus import JSONRPCError, RPCBus, make_error, make_request, make_response
from lazy.gateway.server import GatewayServer
from lazy.gateway.token import HUDTokenManager


def _make_client_ws_frame(msg: str) -> bytes:
    """Helper to produce RFC 6455 client-masked text frame."""
    payload = msg.encode("utf-8")
    length = len(payload)
    mask = b"\x12\x34\x56\x78"
    if length <= 125:
        header = bytes([0x81, 0x80 | length]) + mask
    elif length <= 65535:
        header = bytes([0x81, 0x80 | 126]) + struct.pack("!H", length) + mask
    else:
        header = bytes([0x81, 0x80 | 127]) + struct.pack("!Q", length) + mask

    masked = bytearray(length)
    for i in range(length):
        masked[i] = payload[i] ^ mask[i % 4]
    return header + bytes(masked)


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestHUDTokenManager:
    def test_random_token_generation(self, tmp_path: Path):
        token_file = tmp_path / "hud_token"
        mgr = HUDTokenManager(token_path=token_file)
        assert len(mgr.token) == 64
        assert token_file.exists()
        assert token_file.read_text(encoding="utf-8") == mgr.token

    def test_explicit_token(self):
        mgr = HUDTokenManager(explicit_token="supersecret123")
        assert mgr.token == "supersecret123"
        assert mgr.validate("supersecret123") is True
        assert mgr.validate("wrongtoken") is False
        assert mgr.validate("") is False

    def test_constant_time_validation(self):
        mgr = HUDTokenManager(explicit_token="fixedtoken456")
        assert mgr.validate("fixedtoken456") is True
        assert mgr.validate("fixedtoken457") is False


class TestRPCBus:
    def test_helpers(self):
        req = make_request("test.method", {"param": 1}, req_id=42)
        assert req["jsonrpc"] == "2.0"
        assert req["id"] == 42
        assert req["method"] == "test.method"

        resp = make_response(42, {"status": "ok"})
        assert resp["result"]["status"] == "ok"

        err = make_error(42, -32600, "Bad Request", {"detail": "syntax"})
        assert err["error"]["code"] == -32600
        assert err["error"]["data"]["detail"] == "syntax"

    def test_local_handler_dispatch(self):
        bus = RPCBus()
        bus.register_local("calc.add", lambda p: p.get("a", 0) + p.get("b", 0))

        raw_req = json.dumps(make_request("calc.add", {"a": 10, "b": 32}, req_id=1))
        raw_resp = bus.dispatch(raw_req)
        resp = json.loads(raw_resp)
        assert resp["id"] == 1
        assert resp["result"] == 42

    def test_invalid_json(self):
        bus = RPCBus()
        res = json.loads(bus.dispatch("not valid json {"))
        assert res["error"]["code"] == -32700

    def test_invalid_request_structure(self):
        bus = RPCBus()
        res = json.loads(bus.dispatch(json.dumps({"wrong": "format"})))
        assert res["error"]["code"] == -32600

    def test_method_not_found(self):
        bus = RPCBus()
        res = json.loads(bus.dispatch(json.dumps(make_request("unknown.method", {}))))
        assert res["error"]["code"] == -32601

    def test_invalid_params_type(self):
        bus = RPCBus()
        res = json.loads(bus.dispatch(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "foo", "params": "not-a-dict"})))
        assert res["error"]["code"] == -32602

    def test_unix_socket_routing(self, tmp_path: Path):
        socket_dir = tmp_path / "run_lazy"
        socket_dir.mkdir(parents=True)
        sock_path = socket_dir / "myservice.sock"

        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.bind(str(sock_path))
        server_sock.listen(1)

        def mock_server():
            conn, _ = server_sock.accept()
            data = conn.recv(4096)
            req = json.loads(data.decode("utf-8"))
            resp = make_response(req["id"], {"greeting": f"Hello {req['params'].get('name')}"})
            conn.sendall(json.dumps(resp).encode("utf-8"))
            conn.close()
            server_sock.close()

        t = threading.Thread(target=mock_server, daemon=True)
        t.start()

        bus = RPCBus(socket_dir=socket_dir)
        raw_req = json.dumps(make_request("myservice.greet", {"name": "LazyOS"}, req_id=99))
        raw_resp = bus.dispatch(raw_req)
        resp = json.loads(raw_resp)
        assert resp["id"] == 99
        assert resp["result"]["greeting"] == "Hello LazyOS"


class TestProtocolFraming:
    def test_compute_ws_accept(self):
        # RFC 6455 section 1.3 test vector
        key = "dGhlIHNhbXBsZSBub25jZQ=="
        expected = "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="
        assert compute_ws_accept(key) == expected

    def test_encode_decode_roundtrip_unmasked(self):
        msg = "Hello Lazy OS HUD"
        frame = encode_ws_frame(msg, is_text=True)
        decoded, remaining, opcode = decode_ws_frame(frame)
        assert decoded == msg
        assert remaining == b""
        assert opcode == 1

    def test_encode_decode_roundtrip_masked(self):
        msg = '{"type": "user_input", "text": "status"}'
        frame = _make_client_ws_frame(msg)
        decoded, remaining, opcode = decode_ws_frame(frame)
        assert decoded == msg
        assert remaining == b""
        assert opcode == 1

    def test_protocol_message_serialization(self):
        msg = GatewayProtocolMessage("task_update", {"task_id": "t-1", "status": "running"})
        raw = msg.to_json()
        parsed = GatewayProtocolMessage.from_json(raw)
        assert parsed.type == "task_update"
        assert parsed.payload["task_id"] == "t-1"

    def test_protocol_message_invalid_json(self):
        with pytest.raises(ValueError):
            GatewayProtocolMessage.from_json('{"no_type": "here"}')


class TestGatewayServer:
    @pytest.fixture
    def test_env(self, tmp_path: Path):
        hud_dir = tmp_path / "hud"
        hud_dir.mkdir()
        (hud_dir / "index.html").write_text("<html><body>LazyHUD</body></html>", encoding="utf-8")
        (hud_dir / "hud.css").write_text("body { background: #000; }", encoding="utf-8")
        (hud_dir / "hud.js").write_text("console.log('hud');", encoding="utf-8")

        port = _get_free_port()
        token_mgr = HUDTokenManager(explicit_token="hud_secret_123")
        bus = RPCBus(socket_dir=tmp_path / "sockets")

        server = GatewayServer(host="127.0.0.1", port=port, token_manager=token_mgr, rpc_bus=bus, hud_dir=hud_dir)
        server.start()
        time.sleep(0.05)
        yield {"server": server, "port": port, "token": "hud_secret_123", "hud_dir": hud_dir}
        server.stop()

    def test_http_static_serving(self, test_env):
        port = test_env["port"]
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))
        client.sendall(b"GET /index.html HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")

        resp = client.recv(4096).decode("utf-8")
        client.close()
        assert "HTTP/1.1 200 OK" in resp
        assert "text/html" in resp
        assert "LazyHUD" in resp

    def test_http_css_and_js_serving(self, test_env):
        port = test_env["port"]
        # CSS
        c1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c1.connect(("127.0.0.1", port))
        c1.sendall(b"GET /hud.css HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        resp1 = c1.recv(4096).decode("utf-8")
        c1.close()
        assert "HTTP/1.1 200 OK" in resp1
        assert "text/css" in resp1

        # JS
        c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c2.connect(("127.0.0.1", port))
        c2.sendall(b"GET /hud.js HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        resp2 = c2.recv(4096).decode("utf-8")
        c2.close()
        assert "HTTP/1.1 200 OK" in resp2
        assert "application/javascript" in resp2

    def test_http_not_found(self, test_env):
        port = test_env["port"]
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))
        client.sendall(b"GET /notfound.html HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")

        resp = client.recv(4096).decode("utf-8")
        client.close()
        assert "HTTP/1.1 404 Not Found" in resp

    def test_websocket_auth_handshake_and_events(self, test_env):
        port = test_env["port"]
        token = test_env["token"]
        server = test_env["server"]

        received_events = []
        server.on_user_input(lambda payload: received_events.append(payload))

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))

        # Perform WebSocket upgrade
        handshake = (
            "GET /ws HTTP/1.1\r\n"
            "Host: 127.0.0.1\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n\r\n"
        )
        client.sendall(handshake.encode("utf-8"))
        upgrade_resp = client.recv(1024).decode("utf-8")
        assert "101 Switching Protocols" in upgrade_resp
        assert "Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=" in upgrade_resp

        # Send auth message
        auth_msg = json.dumps({"type": "auth", "token": token})
        client.sendall(_make_client_ws_frame(auth_msg))

        resp_bytes = client.recv(4096)
        text, _, _ = decode_ws_frame(resp_bytes)
        assert text is not None
        auth_resp = json.loads(text)
        assert auth_resp["type"] == "auth_ok"
        assert "session_id" in auth_resp

        # Send user input message
        input_msg = json.dumps({"type": "user_input", "text": "list running services", "origin": "hud"})
        client.sendall(_make_client_ws_frame(input_msg))

        time.sleep(0.05)
        assert len(received_events) == 1
        assert received_events[0]["text"] == "list running services"

        # Broadcast from server
        server.broadcast("transcript_update", {"speaker": "lazy", "message": "Services listed."})
        broadcast_bytes = client.recv(4096)
        b_text, _, _ = decode_ws_frame(broadcast_bytes)
        assert b_text is not None
        b_data = json.loads(b_text)
        assert b_data["type"] == "transcript_update"
        assert b_data["speaker"] == "lazy"

        client.close()

    def test_websocket_auth_failure(self, test_env):
        port = test_env["port"]
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))

        handshake = (
            "GET /ws HTTP/1.1\r\n"
            "Host: 127.0.0.1\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n\r\n"
        )
        client.sendall(handshake.encode("utf-8"))
        client.recv(1024)

        # Send invalid token
        auth_msg = json.dumps({"type": "auth", "token": "invalid_wrong_token"})
        client.sendall(_make_client_ws_frame(auth_msg))

        resp_bytes = client.recv(4096)
        text, _, _ = decode_ws_frame(resp_bytes)
        assert text is not None
        auth_resp = json.loads(text)
        assert auth_resp["type"] == "auth_failed"
        client.close()

    def test_websocket_query_param_auth(self, test_env):
        port = test_env["port"]
        token = test_env["token"]
        server = test_env["server"]

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))

        handshake = (
            f"GET /ws?token={token} HTTP/1.1\r\n"
            "Host: 127.0.0.1\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n\r\n"
        )
        client.sendall(handshake.encode("utf-8"))
        client.recv(1024)

        # Broadcast should directly reach this client without explicit auth message
        server.broadcast("system_metric", {"cpu": 15})
        b_bytes = client.recv(4096)
        text, _, _ = decode_ws_frame(b_bytes)
        assert text is not None
        b_data = json.loads(text)
        assert b_data["type"] == "system_metric"
        assert b_data["cpu"] == 15
        client.close()
