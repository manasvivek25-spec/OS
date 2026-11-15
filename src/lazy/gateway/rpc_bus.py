"""JSON-RPC 2.0 router and bus client for Lazy OS service IPC."""
from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple


class JSONRPCError(Exception):
    def __init__(self, code: int, message: str, data: Any = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


def make_request(method: str, params: Optional[Dict[str, Any]] = None, req_id: Any = 1) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
        "params": params or {},
    }


def make_response(req_id: Any, result: Any) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": result,
    }


def make_error(req_id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
    err: Dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": err,
    }


class RPCBus:
    """Manages routing of JSON-RPC requests across Unix domain sockets or registered handlers."""

    def __init__(self, socket_dir: Optional[Path | str] = None):
        self.socket_dir = Path(socket_dir) if socket_dir else Path("/run/lazy")
        self._local_handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    def register_local(self, method: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        """Register an in-process handler callback."""
        self._local_handlers[method] = handler

    def call_unix_socket(self, socket_path: Path | str, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Any:
        """Send a JSON-RPC request to a Unix domain socket and return the result."""
        path = Path(socket_path)
        if not path.exists():
            raise FileNotFoundError(f"Service socket '{path}' not found.")

        req = make_request(method, params)
        payload = json.dumps(req).encode("utf-8")

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(timeout)
        try:
            client.connect(str(path))
            client.sendall(payload)
            raw = client.recv(65536).decode("utf-8")
            if not raw:
                raise JSONRPCError(-32603, "Empty response from service")
            resp = json.loads(raw)
            if "error" in resp:
                err = resp["error"]
                raise JSONRPCError(err.get("code", -32603), err.get("message", "Error"), err.get("data"))
            return resp.get("result")
        finally:
            client.close()

    def dispatch(self, raw_message: str) -> str:
        """Process an incoming JSON-RPC raw string and return response string."""
        req_id = None
        try:
            req = json.loads(raw_message)
            if not isinstance(req, dict) or req.get("jsonrpc") != "2.0":
                return json.dumps(make_error(None, -32600, "Invalid Request: Must be JSON-RPC 2.0 object"))

            req_id = req.get("id")
            method = req.get("method")
            if not method or not isinstance(method, str):
                return json.dumps(make_error(req_id, -32600, "Invalid Request: Missing method"))

            params = req.get("params", {})
            if not isinstance(params, dict):
                return json.dumps(make_error(req_id, -32602, "Invalid params: Must be object"))

            if method in self._local_handlers:
                result = self._local_handlers[method](params)
                return json.dumps(make_response(req_id, result))

            # Delegate to service socket if method format is service.method
            service_name = method.split(".")[0]
            sock_candidate = self.socket_dir / f"{service_name}.sock"
            if sock_candidate.exists():
                res = self.call_unix_socket(sock_candidate, method, params)
                return json.dumps(make_response(req_id, res))

            return json.dumps(make_error(req_id, -32601, f"Method '{method}' not found"))

        except json.JSONDecodeError:
            return json.dumps(make_error(None, -32700, "Parse error"))
        except JSONRPCError as rpc_err:
            return json.dumps(make_error(req_id, rpc_err.code, rpc_err.message, rpc_err.data))
        except Exception as err:
            return json.dumps(make_error(req_id, -32603, f"Internal error: {str(err)}"))
