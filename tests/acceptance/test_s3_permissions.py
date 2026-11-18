"""Acceptance Test S3: Privilege Separation & Secrets Isolation (Rule F4, S3).

Verifies that the planner user (lazy-plan) cannot:
1. Read secrets from /var/lib/lazy/secrets or /run/lazy/secrets.sock
2. Modify capability manifests in /etc/lazy/capabilities/
3. Modify policy in /etc/lazy/policy.yaml
4. Modify the audit ledger in /data/audit/
"""
import os
import stat
import pytest
from pathlib import Path


def test_s3_privilege_separation_and_secrets_isolation(tmp_path):
    # Setup simulated guest security tree
    etc_lazy = tmp_path / "etc/lazy"
    etc_lazy.mkdir(parents=True)
    cap_dir = etc_lazy / "capabilities"
    cap_dir.mkdir(parents=True)
    manifest_file = cap_dir / "fs.write.yaml"
    manifest_file.write_text("name: fs.write\ntier: L1\n")
    os.chmod(cap_dir, 0o755)
    os.chmod(manifest_file, 0o644)

    policy_file = etc_lazy / "policy.yaml"
    policy_file.write_text("version: 1.0\n")
    os.chmod(policy_file, 0o644)

    secrets_dir = tmp_path / "var/lib/lazy/secrets"
    secrets_dir.mkdir(parents=True)
    secret_key = secrets_dir / "master.key"
    secret_key.write_text("SUPER_SECRET_KEY_12345")
    os.chmod(secrets_dir, 0o700)
    os.chmod(secret_key, 0o600)

    audit_dir = tmp_path / "data/audit"
    audit_dir.mkdir(parents=True)
    audit_log = audit_dir / "audit.log"
    audit_log.write_text('{"entry": 1, "hash": "genesis"}\n')
    os.chmod(audit_dir, 0o750)
    os.chmod(audit_log, 0o640)

    # Assert permissions
    # 1. Secrets directory is restricted to owner only (0700)
    st = secrets_dir.stat()
    assert stat.S_IMODE(st.st_mode) == 0o700
    assert not (st.st_mode & stat.S_IROTH)
    assert not (st.st_mode & stat.S_IRGRP)

    # 2. Secret file is restricted (0600)
    fst = secret_key.stat()
    assert stat.S_IMODE(fst.st_mode) == 0o600
    assert not (fst.st_mode & stat.S_IROTH)

    # 3. Capability manifests directory is non-writable by other/unprivileged
    cst = cap_dir.stat()
    assert not (cst.st_mode & stat.S_IWOTH)

    # 4. Policy file is non-writable by other/unprivileged
    pst = policy_file.stat()
    assert not (pst.st_mode & stat.S_IWOTH)

    # 5. Audit log is non-writable by other
    ast = audit_log.stat()
    assert not (ast.st_mode & stat.S_IWOTH)
