"""HTTP static HUD server and RFC 6455 WebSocket gateway on 127.0.0.1:8765."""
from __future__ import annotations

import json
import os
import socket
import threading
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from lazy.gateway.protocol import (
    GatewayProtocolMessage,
    compute_ws_accept,
    decode_ws_frame,
    encode_ws_frame,
)
from lazy.gateway.rpc_bus import RPCBus
from lazy.gateway.token import HUDTokenManager
from lazy.gateway.api import GatewayAPIHandler


class GatewayServer:
    """Integrated HTTP and WebSocket gateway server."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8765,
        token_manager: Optional[HUDTokenManager] = None,
        rpc_bus: Optional[RPCBus] = None,
        hud_dir: Optional[Path | str] = None,
    ):
        self.host = host
        self.port = port
        self.token_manager = token_manager or HUDTokenManager()
        self.rpc_bus = rpc_bus or RPCBus()

        if hud_dir:
            self.hud_dir = Path(hud_dir)
        else:
            candidates = [
                Path("/usr/share/lazy/hud"),
                Path(__file__).resolve().parent.parent.parent.parent / "hud",
            ]
            self.hud_dir = next((c for c in candidates if c.is_dir()), candidates[0])

        self.api_handler = GatewayAPIHandler(repo_root=Path(__file__).resolve().parent.parent.parent.parent)

        self._server_sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._active_sessions: Dict[str, socket.socket] = {}
        self._lock = threading.Lock()
        self._input_handlers: List[Callable[[Dict[str, Any]], None]] = []

    def on_user_input(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register callback for received user input events."""
        self._input_handlers.append(handler)

    def start(self) -> None:
        """Start listening on the specified loopback port."""
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(25)
        self._running = True

        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Shut down the server and terminate active client connections."""
        self._running = False
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass

        with self._lock:
            for s in list(self._active_sessions.values()):
                try:
                    s.close()
                except Exception:
                    pass
            self._active_sessions.clear()

    def broadcast(self, msg_type: str, payload: Dict[str, Any]) -> None:
        """Broadcast a message frame to all authenticated connected HUD sessions."""
        msg = GatewayProtocolMessage(msg_type, payload).to_json()
        frame = encode_ws_frame(msg)

        with self._lock:
            dead = []
            for sess_id, sock in self._active_sessions.items():
                try:
                    sock.sendall(frame)
                except Exception:
                    dead.append(sess_id)
            for d in dead:
                self._active_sessions.pop(d, None)

    def _accept_loop(self) -> None:
        while self._running:
            try:
                client_sock, _ = self._server_sock.accept()
                threading.Thread(target=self._handle_connection, args=(client_sock,), daemon=True).start()
            except Exception:
                break

    def _handle_connection(self, client_sock: socket.socket) -> None:
        try:
            req_data = client_sock.recv(4096).decode("utf-8", errors="replace")
            if not req_data:
                client_sock.close()
                return

            lines = req_data.split("\r\n")
            if not lines:
                client_sock.close()
                return

            parts = lines[0].split()
            if len(parts) < 2:
                client_sock.close()
                return

            method, path = parts[0], parts[1]
            headers: Dict[str, str] = {}
            for line in lines[1:]:
                if ": " in line:
                    k, v = line.split(": ", 1)
                    headers[k.lower()] = v.strip()

            # Check for WebSocket Upgrade
            if headers.get("upgrade", "").lower() == "websocket":
                self._upgrade_and_handle_ws(client_sock, path, headers)
            else:
                self._serve_http(client_sock, method, path, req_data)
        except Exception:
            try:
                client_sock.close()
            except Exception:
                pass

    def _serve_http(self, client_sock: socket.socket, method: str, path: str, req_data: str = "") -> None:
        """Serve REST API endpoints and static HUD assets."""
        if path.startswith("/api/"):
            body_bytes = b""
            if "\r\n\r\n" in req_data:
                body_bytes = req_data.split("\r\n\r\n", 1)[1].encode("utf-8")
            status, resp_headers, body = self.api_handler.handle_request(method, path, body_bytes)
            status_text = {200: "OK", 202: "Accepted", 403: "Forbidden", 404: "Not Found", 500: "Internal Server Error"}.get(status, "OK")
            header_lines = [f"HTTP/1.1 {status} {status_text}"]
            for k, v in resp_headers.items():
                header_lines.append(f"{k}: {v}")
            header_lines.append("Connection: close\r\n\r\n")
            client_sock.sendall("\r\n".join(header_lines).encode("utf-8") + body)
            client_sock.close()
            return

        clean_path = path.split("?")[0].lstrip("/")
        if clean_path == "" or clean_path == "index.html":
            file_name = "index.html"
            content_type = "text/html; charset=utf-8"
        elif clean_path == "hud.css":
            file_name = "hud.css"
            content_type = "text/css; charset=utf-8"
        elif clean_path == "hud.js":
            file_name = "hud.js"
            content_type = "application/javascript; charset=utf-8"
        else:
            file_name = clean_path
            ext = os.path.splitext(file_name)[1].lower()
            content_type = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".js": "application/javascript; charset=utf-8",
                ".json": "application/json",
                ".png": "image/png",
                ".svg": "image/svg+xml",
                ".txt": "text/plain; charset=utf-8"
            }.get(ext, "application/octet-stream")

        target_file = self.hud_dir / file_name
        if not target_file.is_file():
            resp = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
            client_sock.sendall(resp.encode("utf-8"))
            client_sock.close()
            return

        body = target_file.read_bytes()
        headers = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: close\r\n\r\n"
        ).encode("utf-8")
        client_sock.sendall(headers + body)
        client_sock.close()

    def _upgrade_and_handle_ws(self, client_sock: socket.socket, path: str, headers: Dict[str, str]) -> None:
        """Perform RFC 6455 handshake and run WebSocket session."""
        ws_key = headers.get("sec-websocket-key")
        if not ws_key:
            client_sock.close()
            return

        ws_accept = compute_ws_accept(ws_key)
        handshake_resp = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {ws_accept}\r\n\r\n"
        ).encode("utf-8")
        client_sock.sendall(handshake_resp)

        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        is_authenticated = False

        # Check token in query param: ?token=...
        if "?token=" in path:
            q_token = path.split("?token=")[-1].split("&")[0]
            if self.token_manager.validate(q_token):
                is_authenticated = True
                with self._lock:
                    self._active_sessions[session_id] = client_sock

        buffer = bytearray()
        try:
            while self._running:
                chunk = client_sock.recv(4096)
                if not chunk:
                    break
                buffer.extend(chunk)

                while True:
                    text_msg, remaining, opcode = decode_ws_frame(bytes(buffer))
                    if text_msg is None:
                        break
                    buffer = bytearray(remaining)

                    if opcode == 0x8:  # Close frame
                        return

                    # Process protocol message
                    try:
                        proto_msg = GatewayProtocolMessage.from_json(text_msg)
                        msg_type = proto_msg.type
                        payload = proto_msg.payload

                        if msg_type == "auth":
                            candidate = payload.get("token", "")
                            if self.token_manager.validate(candidate):
                                is_authenticated = True
                                with self._lock:
                                    self._active_sessions[session_id] = client_sock
                                ok_msg = GatewayProtocolMessage("auth_ok", {"session_id": session_id}).to_json()
                                client_sock.sendall(encode_ws_frame(ok_msg))
                            else:
                                fail_msg = GatewayProtocolMessage("auth_failed", {"reason": "Invalid HUD token"}).to_json()
                                client_sock.sendall(encode_ws_frame(fail_msg))
                                return

                        elif not is_authenticated:
                            fail_msg = GatewayProtocolMessage("auth_failed", {"reason": "Authentication required"}).to_json()
                            client_sock.sendall(encode_ws_frame(fail_msg))
                            return

                        elif msg_type == "user_input":
                            for handler in self._input_handlers:
                                handler(payload)

                        elif msg_type == "approval_response":
                            # Route approval response into RPC bus / policy
                            pass

                    except Exception:
                        pass
        finally:
            with self._lock:
                self._active_sessions.pop(session_id, None)
            try:
                client_sock.close()
            except Exception:
                pass


def main():
    import argparse
    import time
    parser = argparse.ArgumentParser(description="Lazy OS Gateway Service")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8765, help="Bind port")
    parser.add_argument("--hud-dir", default=None, help="Path to HUD directory")
    args = parser.parse_args()

    server = GatewayServer(host=args.host, port=args.port, hud_dir=args.hud_dir)
    server.start()
    print(f"Lazy OS Gateway Service online on {args.host}:{args.port}")
    try:
        while True:
            time.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        server.stop()


if __name__ == "__main__":
    main()

