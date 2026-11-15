"""System management broker for Lazy OS (lazy-broker-sys)."""
from __future__ import annotations

import os
import signal
import subprocess
from typing import Any, Dict, List, Optional

from lazy.brokers.base import BaseBroker, BrokerExecutionError


class FakeSystemdClient:
    """In-memory systemd client for hermetic testing and CI without systemd daemon."""

    def __init__(self):
        self.services = {
            "bluetooth": {"active": True, "substate": "running", "pid": 1122},
            "systemd-networkd": {"active": True, "substate": "running", "pid": 1133},
            "sshd": {"active": True, "substate": "running", "pid": 1144},
            "cron": {"active": False, "substate": "dead", "pid": 0},
        }
        self.logs = {
            "bluetooth": ["Nov 15 12:00:00 lazy-os bluetoothd[1122]: Starting daemon", "Nov 15 12:00:01 lazy-os bluetoothd[1122]: Bluetooth daemon ready"],
            "sshd": ["Nov 15 12:00:00 lazy-os sshd[1144]: Server listening on 0.0.0.0 port 22."],
        }
        self.settings: Dict[str, str] = {
            "timezone": "UTC",
            "hostname": "lazyos",
        }
        self.processes = [
            {"pid": 1, "name": "systemd", "user": "root"},
            {"pid": 1122, "name": "bluetoothd", "user": "root"},
            {"pid": 1144, "name": "sshd", "user": "root"},
            {"pid": 2000, "name": "lazy-gateway", "user": "lazy-gw"},
        ]
        self.signaled_pids: List[Dict[str, Any]] = []

    def get_service_status(self, service: str) -> Dict[str, Any]:
        info = self.services.get(service, {"active": False, "substate": "inactive", "pid": 0})
        return {"service": service, "active": info["active"], "substate": info["substate"], "pid": info["pid"]}

    def get_service_logs(self, service: Optional[str], lines: int = 50) -> List[str]:
        if service and service in self.logs:
            return self.logs[service][-lines:]
        return ["Nov 15 12:00:00 lazy-os systemd[1]: System running"]

    def restart_service(self, service: str) -> bool:
        if service in self.services:
            self.services[service]["active"] = True
            self.services[service]["substate"] = "running"
            return True
        self.services[service] = {"active": True, "substate": "running", "pid": 9999}
        return True

    def set_setting(self, key: str, value: str) -> None:
        self.settings[key] = value

    def list_processes(self) -> List[Dict[str, Any]]:
        return list(self.processes)

    def signal_process(self, pid: int, sig_name: str) -> bool:
        self.signaled_pids.append({"pid": pid, "signal": sig_name})
        self.processes = [p for p in self.processes if p["pid"] != pid]
        return True


class SysBroker(BaseBroker):
    """Executes system administration capabilities via systemd client."""

    def __init__(self, client: Optional[Any] = None):
        super().__init__("lazy-broker-sys")
        self.client = client or FakeSystemdClient()
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register("sys.service_status", self.handle_service_status)
        self.register("sys.logs_read", self.handle_logs_read)
        self.register("sys.process_list", self.handle_process_list)
        self.register("sys.service_restart", self.handle_service_restart)
        self.register("sys.setting_set", self.handle_setting_set)
        self.register("sys.process_signal", self.handle_process_signal)

    def handle_service_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.get_service_status(params["service"])

    def handle_logs_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        lines = params.get("lines", 50)
        service = params.get("service")
        logs = self.client.get_service_logs(service, lines)
        return {"service": service, "lines": logs, "count": len(logs)}

    def handle_process_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        procs = self.client.list_processes()
        return {"processes": procs, "count": len(procs)}

    def handle_service_restart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        service = params["service"]
        ok = self.client.restart_service(service)
        return {"service": service, "restarted": ok}

    def handle_setting_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        key = params["key"]
        value = params["value"]
        self.client.set_setting(key, value)
        return {"key": key, "value": value, "applied": True}

    def handle_process_signal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pid = params["pid"]
        sig = params["signal"]
        ok = self.client.signal_process(pid, sig)
        return {"pid": pid, "signal": sig, "success": ok}
