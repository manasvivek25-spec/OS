"""Tests for lazy-gateway REST API endpoints (V2.B2, V2.B3, Phase C)."""
import json
import pytest
from pathlib import Path
from lazy.gateway.api import GatewayAPIHandler


@pytest.fixture
def api_handler(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    audit_file = tmp_path / "lazy-audit.log"
    return GatewayAPIHandler(
        data_dir=data_dir,
        audit_log_path=audit_file
    )


def test_api_identity_endpoint(api_handler):
    status, headers, body = api_handler.handle_request("GET", "/api/identity")
    assert status == 200
    assert headers["Content-Type"] == "application/json"
    data = json.loads(body.decode())
    assert "hostname" in data
    assert "kernel_release" in data
    assert "boot_id" in data
    assert "uptime" in data
    assert "mounts" in data
    assert data["git_commit"] in ["v2-command-center", "v3-product"]


def test_api_build_info_honest_badges(api_handler):
    status, headers, body = api_handler.handle_request("GET", "/api/build-info")
    assert status == 200
    data = json.loads(body.decode())
    assert data["kernel"]["status"] == "real"
    assert data["storage"]["status"] == "real"
    assert data["audit"]["status"] == "real"
    assert data["llm"]["status"] == "simulated"
    assert data["voice"]["status"] == "simulated"


def test_api_metrics_endpoint(api_handler):
    status, headers, body = api_handler.handle_request("GET", "/api/metrics")
    assert status == 200
    data = json.loads(body.decode())
    assert "cpu_percent" in data
    assert "memory" in data
    assert data["memory"]["used_mb"] > 0


def test_api_services_endpoint(api_handler):
    status, headers, body = api_handler.handle_request("GET", "/api/services")
    assert status == 200
    services = json.loads(body.decode())
    assert len(services) == 15
    assert any(s["unit"] == "lazy-gateway.service" for s in services)


def test_api_capabilities_endpoint(api_handler):
    status, headers, body = api_handler.handle_request("GET", "/api/capabilities")
    assert status == 200
    caps = json.loads(body.decode())
    assert len(caps) >= 30


def test_api_fs_crud_and_policy(api_handler):
    # 1. Write file via POST /api/fs
    write_payload = {"path": "test_note.txt", "content": "Hello API"}
    status, _, body = api_handler.handle_request("POST", "/api/fs", json.dumps(write_payload).encode())
    assert status == 200
    res = json.loads(body.decode())
    assert res["status"] == "created"

    # 2. Read back via GET /api/fs?path=test_note.txt
    status, _, body = api_handler.handle_request("GET", "/api/fs?path=test_note.txt")
    assert status == 200
    data = json.loads(body.decode())
    assert data["type"] == "file"
    assert data["content"] == "Hello API"

    # 3. List directory via GET /api/fs
    status, _, body = api_handler.handle_request("GET", "/api/fs")
    assert status == 200
    data = json.loads(body.decode())
    assert data["type"] == "directory"
    assert any(item["name"] == "test_note.txt" for item in data["items"])

    # 4. Request deletion via DELETE /api/fs (requires approval)
    status, _, body = api_handler.handle_request("DELETE", "/api/fs", json.dumps({"path": "test_note.txt"}).encode())
    assert status == 202
    del_res = json.loads(body.decode())
    app_id = del_res["approval_id"]

    # 5. Approve deletion
    status, _, _ = api_handler.handle_request("POST", "/api/approvals", json.dumps({"id": app_id, "action": "approve"}).encode())
    assert status == 200
    assert not (api_handler.data_dir / "test_note.txt").exists()


def test_api_denied_request_changes_nothing(api_handler):
    # Try forbidden path traversal write
    payload = {"path": "../../../etc/shadow", "content": "root:bad"}
    status, _, body = api_handler.handle_request("POST", "/api/fs", json.dumps(payload).encode())
    assert status == 403
    data = json.loads(body.decode())
    assert "error" in data
    # Ensure no file was created
    assert not (api_handler.data_dir / "shadow").exists()
