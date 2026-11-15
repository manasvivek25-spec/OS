"""Unit tests for lazy-secrets vault and peer-credential checks (Rule F4).

Exit criteria M1.5:
- the planner user cannot read secrets.
- peer-credential checks enforced on Unix domain socket and vault.
"""

import json
import os
import socket
import time
from pathlib import Path
import pytest

from lazy.secrets import (
    SecretAccessDenied,
    SecretsService,
    SecretVault,
)

PLANNER_UID = 2001
BROKER_UID = 2002
UNAUTHORIZED_UID = 9999


@pytest.fixture
def vault_env(tmp_path: Path):
    vault_dir = tmp_path / "secrets_vault"
    vault = SecretVault(
        vault_dir=vault_dir,
        allowed_uids={0, os.getuid(), BROKER_UID},
        denied_uids={PLANNER_UID},
        allowed_users={"root", "lazy-comms", "lazy-web"},
        denied_users={"lazy-planner", "planner"},
    )
    return vault, tmp_path


# ==============================================================================
# 1. PEER CREDENTIALS & PLANNER ISOLATION (RULE F4)
# ==============================================================================

def test_authorized_user_can_set_and_get_secrets(vault_env):
    """Verify that authorized services can access credential vault."""
    vault, _ = vault_env
    # Current UID is authorized
    current_uid = os.getuid()
    vault.set_secret("smtp_password", "supersecret123", peer_uid=current_uid, peer_user="lazy-comms")

    retrieved = vault.get_secret("smtp_password", peer_uid=current_uid, peer_user="lazy-comms")
    assert retrieved == "supersecret123"

    keys = vault.list_keys(peer_uid=current_uid, peer_user="lazy-comms")
    assert "smtp_password" in keys


def test_planner_user_cannot_read_secrets_rule_f4(vault_env):
    """[M1.5 Exit Criterion / Rule F4] Prove negative: The planner user CANNOT read secrets."""
    vault, _ = vault_env
    current_uid = os.getuid()
    vault.set_secret("api_token", "token-xyz-987", peer_uid=current_uid, peer_user="lazy-comms")

    # 1. Attempt read by denied user 'lazy-planner'
    with pytest.raises(SecretAccessDenied) as exc1:
        vault.get_secret("api_token", peer_uid=current_uid, peer_user="lazy-planner")
    assert "Rule F4 violation" in str(exc1.value)
    assert "planner" in str(exc1.value)

    # 2. Attempt read by denied UID
    with pytest.raises(SecretAccessDenied) as exc2:
        vault.get_secret("api_token", peer_uid=PLANNER_UID, peer_user="unknown")
    assert "Rule F4 violation" in str(exc2.value)

    # 3. Attempt list keys by planner
    with pytest.raises(SecretAccessDenied):
        vault.list_keys(peer_uid=PLANNER_UID, peer_user="planner")

    # 4. Attempt set secret by planner
    with pytest.raises(SecretAccessDenied):
        vault.set_secret("backdoor", "val", peer_uid=PLANNER_UID, peer_user="planner")


def test_unauthorized_uid_denied_access(vault_env):
    """Verify arbitrary unauthorized UIDs are rejected."""
    vault, _ = vault_env
    with pytest.raises(SecretAccessDenied):
        vault.get_secret("any_key", peer_uid=UNAUTHORIZED_UID, peer_user="nobody")


# ==============================================================================
# 2. UNIX DOMAIN SOCKET SERVICE WITH JSON-RPC
# ==============================================================================

def test_secrets_service_over_unix_domain_socket(vault_env):
    """Verify JSON-RPC IPC over Unix domain socket with peer credential check."""
    vault, tmp_path = vault_env
    sock_path = tmp_path / "secrets.sock"

    service = SecretsService(sock_path, vault)
    service.start()
    time.sleep(0.1)

    try:
        # Client 1: Authorized (current process UID is in allowed_uids)
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(sock_path))

        # Set secret via RPC
        set_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "secrets.set",
            "params": {"key": "bot_token", "value": "tg-token-456"}
        }
        client.sendall(json.dumps(set_payload).encode("utf-8"))
        res = json.loads(client.recv(4096).decode("utf-8"))
        assert res["result"]["status"] == "ok"
        client.close()

        # Get secret via RPC
        client2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client2.connect(str(sock_path))
        get_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "secrets.get",
            "params": {"key": "bot_token"}
        }
        client2.sendall(json.dumps(get_payload).encode("utf-8"))
        res2 = json.loads(client2.recv(4096).decode("utf-8"))
        assert res2["result"]["value"] == "tg-token-456"
        client2.close()

    finally:
        service.stop()


def test_secrets_service_denies_blocked_uid(tmp_path: Path):
    """Verify service denies requests from blocked planner UID."""
    sock_path = tmp_path / "secrets_denied.sock"
    current_uid = os.getuid()

    # Create vault where CURRENT UID is explicitly denied (simulating planner process)
    vault = SecretVault(
        vault_dir=tmp_path / "vault_denied",
        allowed_uids=set(),
        denied_uids={current_uid},
    )

    service = SecretsService(sock_path, vault)
    service.start()
    time.sleep(0.1)

    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(sock_path))
        payload = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "secrets.get",
            "params": {"key": "secret"}
        }
        client.sendall(json.dumps(payload).encode("utf-8"))
        res = json.loads(client.recv(4096).decode("utf-8"))
        assert "error" in res
        assert res["error"]["code"] == -32001
        assert "Rule F4 violation" in res["error"]["message"]
        client.close()
    finally:
        service.stop()
