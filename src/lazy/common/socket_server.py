"""Generic Unix domain socket JSON-RPC 2.0 service runner for Lazy OS microservices."""
from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import socket
import struct
import sys
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger("lazy.socket_server")

SO_PEERCRED = 17


def get_peer_creds(sock: socket.socket) -> Tuple[int, int, int]:
    """Retrieve (pid, uid, gid) from Linux Unix domain socket."""
    try:
        creds = sock.getsockopt(socket.SOL_SOCKET, SO_PEERCRED, struct.calcsize("3i"))
        pid, uid, gid = struct.unpack("3i", creds)
        return pid, uid, gid
    except Exception:
        return os.getpid(), os.getuid(), os.getgid()


class UnixSocketServer:
    """Multi-threaded Unix domain socket server dispatching JSON-RPC 2.0 requests."""

    def __init__(self, socket_path: Path | str, service_name: str = "service"):
        self.socket_path = Path(socket_path)
        self.service_name = service_name
        self.handlers: Dict[str, Callable[[Dict[str, Any], Tuple[int, int, int]], Any]] = {}
        self._server_sock: Optional[socket.socket] = None
        self._running = False

    def register(self, method: str, handler: Callable[[Dict[str, Any], Tuple[int, int, int]], Any]) -> None:
        """Register a handler for a specific JSON-RPC method."""
        self.handlers[method] = handler

    def register_simple(self, method: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        """Register a simple handler that ignores peer creds."""
        self.handlers[method] = lambda params, creds: handler(params)

    def register_broker(self, broker: Any) -> None:
        """Register all handlers from a BaseBroker instance."""
        for cap, handler in getattr(broker, "_handlers", {}).items():
            self.register_simple(cap, handler)

    def serve_forever(self) -> None:
        """Bind socket, set permissions, and loop accepting connections."""
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to remove stale socket {self.socket_path}: {e}")

        self._server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_sock.bind(str(self.socket_path))
        try:
            self.socket_path.chmod(0o666)
        except Exception:
            pass

        self._server_sock.listen(64)
        self._running = True
        logger.info(f"[{self.service_name}] listening on {self.socket_path}")

        def handle_signal(sig, frame):
            logger.info(f"[{self.service_name}] caught signal {sig}, stopping...")
            self._running = False
            if self._server_sock:
                try:
                    self._server_sock.close()
                except Exception:
                    pass
            if self.socket_path.exists():
                try:
                    self.socket_path.unlink()
                except Exception:
                    pass
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        while self._running:
            try:
                client_sock, _ = self._server_sock.accept()
                t = threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True)
                t.start()
            except Exception:
                if not self._running:
                    break

    def _handle_client(self, client_sock: socket.socket) -> None:
        req_id = None
        try:
            creds = get_peer_creds(client_sock)
            raw = client_sock.recv(65536).decode("utf-8")
            if not raw:
                return

            req = json.loads(raw)
            req_id = req.get("id")
            method = req.get("method", "")
            params = req.get("params", {})

            if method in self.handlers:
                result = self.handlers[method](params, creds)
                resp = {"jsonrpc": "2.0", "id": req_id, "result": result}
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"},
                }
            client_sock.sendall(json.dumps(resp).encode("utf-8"))
        except json.JSONDecodeError:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
            try:
                client_sock.sendall(json.dumps(resp).encode("utf-8"))
            except Exception:
                pass
        except Exception as e:
            resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}
            try:
                client_sock.sendall(json.dumps(resp).encode("utf-8"))
            except Exception:
                pass
        finally:
            try:
                client_sock.close()
            except Exception:
                pass


def parse_socket_arg(default_name: str) -> Path:
    """Standard CLI argument parser for --socket."""
    parser = argparse.ArgumentParser(description=f"Lazy OS {default_name} service")
    parser.add_argument("--socket", type=str, default=f"/run/lazy/{default_name}.sock", help="Path to Unix domain socket")
    args = parser.parse_args()
    return Path(args.socket)
