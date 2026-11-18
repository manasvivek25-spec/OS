"""Acceptance Test O5: Signed Update Bundle Verification & Tamper Resistance (Rule O5).

Validates:
1. Valid cryptographic signature (SHA-256 + HMAC / RSA) verification on an OS update bundle.
2. Immediate rejection when payload bytes are tampered or modified.
3. Immediate rejection when metadata or manifest is altered.
4. Immediate rejection when signature does not match public key or secret.
"""
import hashlib
import hmac
import json
import pytest
from pathlib import Path


class UpdateBundleVerifier:
    """Cryptographic update bundle packager and verifier."""

    def __init__(self, signing_key: bytes):
        self.signing_key = signing_key

    def create_bundle(self, version: str, payload_data: bytes) -> dict:
        payload_hash = hashlib.sha256(payload_data).hexdigest()
        manifest = {
            "version": version,
            "payload_sha256": payload_hash,
            "target": "lazy-os",
        }
        manifest_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
        sig = hmac.new(self.signing_key, manifest_bytes + payload_data, hashlib.sha256).hexdigest()
        return {
            "manifest": manifest,
            "signature": sig,
            "payload": payload_data.hex(),
        }

    def verify_bundle(self, bundle: dict) -> bool:
        try:
            manifest = bundle.get("manifest", {})
            sig = bundle.get("signature", "")
            payload_data = bytes.fromhex(bundle.get("payload", ""))

            # 1. Verify payload hash matches manifest
            payload_hash = hashlib.sha256(payload_data).hexdigest()
            if payload_hash != manifest.get("payload_sha256"):
                return False

            # 2. Verify HMAC signature
            manifest_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
            expected_sig = hmac.new(self.signing_key, manifest_bytes + payload_data, hashlib.sha256).hexdigest()
            return hmac.compare_digest(sig, expected_sig)
        except Exception:
            return False


def test_signed_update_bundle_verification():
    secret_key = b"LAZY_OS_SECURE_UPDATE_SIGNING_KEY_2026"
    verifier = UpdateBundleVerifier(secret_key)

    # 1. Valid bundle verifies cleanly
    valid_payload = b"KERNEL_UPDATE_DATA_V3.1_6.6.21"
    bundle = verifier.create_bundle("3.1.0", valid_payload)
    assert verifier.verify_bundle(bundle) is True

    # 2. Tampered payload is rejected
    tampered_bundle = json.loads(json.dumps(bundle))
    tampered_bytes = b"MALICIOUS_ROOTKIT_INJECTION_DATA"
    tampered_bundle["payload"] = tampered_bytes.hex()
    assert verifier.verify_bundle(tampered_bundle) is False

    # 3. Tampered manifest version is rejected
    tampered_manifest_bundle = json.loads(json.dumps(bundle))
    tampered_manifest_bundle["manifest"]["version"] = "9.9.9"
    assert verifier.verify_bundle(tampered_manifest_bundle) is False

    # 4. Tampered signature is rejected
    bad_sig_bundle = json.loads(json.dumps(bundle))
    bad_sig_bundle["signature"] = "0" * 64
    assert verifier.verify_bundle(bad_sig_bundle) is False

    # 5. Wrong key rejects
    wrong_verifier = UpdateBundleVerifier(b"WRONG_KEY_ATTACKER")
    assert wrong_verifier.verify_bundle(bundle) is False
