"""Core policy evaluation engine for Lazy OS (lazy-policy)."""
from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import jsonschema

from lazy.policy.manifest import CapabilityManifest, ManifestLoader
from lazy.policy.rate_limiter import RateLimiter
from lazy.policy.state_machine import ApprovalRequest, ApprovalState
from lazy.policy.taint import TaintTracker

# Hard-coded L4 Forbidden Targets and Namespaces (Rule F6)
L4_FORBIDDEN_CAPABILITY_PREFIXES: Tuple[str, ...] = (
    "policy.",
    "broker.",
    "secrets.",
    "audit.",
    "sandbox.",
    "root.",
    "kernel.",
)

L4_FORBIDDEN_PATH_PATTERNS: List[re.Pattern] = [
    re.compile(r"/etc/lazy(/.*)?"),
    re.compile(r"/var/log/lazy(/.*)?"),
    re.compile(r"/var/lib/lazy/secrets(/.*)?"),
    re.compile(r"/etc/shadow.*"),
    re.compile(r"/etc/sudoers.*"),
    re.compile(r"\.ssh(/.*)?"),
    re.compile(r"\.(pem|key|id_rsa|id_ed25519)(\s|$)"),
    re.compile(r"/\.forward"),
    re.compile(r"/\.procmailrc"),
]


class PolicyEngine:
    """Evaluates proposed intents against manifests, tiers, taint, rate limits, and L4 rules."""

    def __init__(
        self,
        manifest_loader: Optional[ManifestLoader] = None,
        rate_limiter: Optional[RateLimiter] = None,
        allowlist_domains: Optional[Set[str]] = None,
        capabilities_dir: Optional[Path | str] = None,
    ):
        if manifest_loader is None and capabilities_dir is not None:
            manifest_loader = ManifestLoader([capabilities_dir])
        self.loader = manifest_loader or ManifestLoader()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.allowlist_domains = allowlist_domains or {
            "localhost",
            "127.0.0.1",
            "lazyos.local",
            "news.ycombinator.com",
            "en.wikipedia.org",
        }
        self.approval_requests: Dict[str, ApprovalRequest] = {}

    def is_l4_violation(self, capability: str, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Verify hard-coded Rule F6 L4 denylist prohibitions."""
        cap_lower = capability.lower()

        # 1. Prohibited capability namespaces
        for prefix in L4_FORBIDDEN_CAPABILITY_PREFIXES:
            if cap_lower.startswith(prefix):
                return True, f"Rule F6 violation: Capability namespace '{prefix}' is hardcoded L4 and never allowed."

        # 2. Prohibited path targets in parameters
        for key, val in params.items():
            if isinstance(val, str):
                normalized = val.strip()
                for pattern in L4_FORBIDDEN_PATH_PATTERNS:
                    if pattern.search(normalized):
                        return True, f"Rule F6 violation: Parameter '{key}' accesses protected L4 target '{normalized}'."

        return False, None

    def evaluate_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate an Intent object and output a compliant Decision object."""
        intent_id = intent.get("id", str(uuid.uuid4()))
        capability = intent.get("capability", "")
        params = intent.get("params", {})
        provenance = intent.get("provenance", [])
        requester = intent.get("requester", "text")

        # Step 1: L4 Hardcoded denylist check (Rule F6)
        is_l4, l4_reason = self.is_l4_violation(capability, params)
        if is_l4:
            return {
                "intent_id": intent_id,
                "verdict": "deny",
                "tier": "L4",
                "effect_class": "irreversible",
                "reason": l4_reason,
                "approval_mode": "denied",
            }

        # Step 2: Capability manifest resolution
        manifest = self.loader.get(capability)
        if manifest is None:
            return {
                "intent_id": intent_id,
                "verdict": "deny",
                "tier": "L4",
                "effect_class": "irreversible",
                "reason": f"Unknown capability '{capability}' is not registered in system manifests.",
                "approval_mode": "denied",
            }

        tier = manifest.tier
        effect_class = manifest.effect_class
        approval_mode = manifest.approval_mode

        # Step 3: Taint tracking and Credential Protection (Rules F3, F4, F8)
        # Evaluated before schema parsing to reject credentials and tainted parameters immediately
        taint_rules = manifest.taint_rules
        disallowed_keys = taint_rules.get("disallow_untrusted_keys", [])
        req_confirm = taint_rules.get("require_user_confirmation", False)

        is_safe, taint_err = TaintTracker.check_taint(
            capability_name=capability,
            params=params,
            provenance=provenance,
            disallowed_keys=disallowed_keys,
            require_user_confirmation=req_confirm,
        )
        if not is_safe:
            return {
                "intent_id": intent_id,
                "verdict": "deny",
                "tier": tier,
                "effect_class": effect_class,
                "reason": taint_err,
                "approval_mode": "denied",
            }

        # Step 4: Parameter schema validation
        try:
            validator = jsonschema.Draft202012Validator(manifest.params_schema)
            errors = list(validator.iter_errors(params))
            if errors:
                err_msg = "; ".join(e.message for e in errors)
                return {
                    "intent_id": intent_id,
                    "verdict": "deny",
                    "tier": tier,
                    "effect_class": effect_class,
                    "reason": f"Parameter schema validation failed for {capability}: {err_msg}",
                    "approval_mode": "denied",
                }
        except Exception as err:
            return {
                "intent_id": intent_id,
                "verdict": "deny",
                "tier": tier,
                "effect_class": effect_class,
                "reason": f"Parameter schema evaluation error: {str(err)}",
                "approval_mode": "denied",
            }

        # Step 5: Rate limit check
        is_limited, rate_reason = self.rate_limiter.is_rate_limited(capability)
        if is_limited:
            return {
                "intent_id": intent_id,
                "verdict": "deny",
                "tier": tier,
                "effect_class": effect_class,
                "reason": rate_reason,
                "approval_mode": "denied",
            }

        # Step 6: Dynamic Tier Adjustments (e.g. web.navigate allowlist)
        if capability == "web.navigate":
            url = params.get("url", "")
            domain = self._extract_domain(url)
            if domain not in self.allowlist_domains:
                tier = "L2"
                approval_mode = "user_confirm"

        # Step 7: Decision formation based on tier
        if tier in ("L0", "L1"):
            # Check user-only capabilities: task.undo and outbox.cancel require user confirmation
            if capability in ("task.undo", "outbox.cancel"):
                verdict = "ask"
                approval_mode = "user_confirm"
                reason = f"User supervisory capability {capability} requires explicit confirmation."
            else:
                verdict = "allow"
                approval_mode = manifest.approval_mode
                reason = f"Automatic execution permitted for {tier} capability {capability}."
        elif tier == "L2":
            verdict = "ask"
            if approval_mode == "automatic":
                approval_mode = "user_confirm"
            reason = f"Capability {capability} requires interactive user approval."
        elif tier == "L3":
            verdict = "ask"
            reason = f"Hazardous capability {capability} requires explicit preview approval and staging."
        else:
            verdict = "deny"
            approval_mode = "denied"
            reason = "Unsupported capability tier."

        return {
            "intent_id": intent_id,
            "verdict": verdict,
            "tier": tier,
            "effect_class": effect_class,
            "reason": reason,
            "approval_mode": approval_mode,
        }

    def create_approval_request(self, intent: Dict[str, Any], decision: Dict[str, Any]) -> ApprovalRequest:
        """Instantiate an interactive approval request for ask decisions."""
        request_id = f"req-{uuid.uuid4().hex[:8]}"
        preview = f"Execute {intent.get('capability')} with params {intent.get('params')}"
        req = ApprovalRequest(
            request_id=request_id,
            intent_id=intent.get("id", ""),
            capability=intent.get("capability", ""),
            tier=decision.get("tier", "L2"),
            params=intent.get("params", {}),
            preview=preview,
        )
        self.approval_requests[request_id] = req
        return req

    def approve_request(self, request_id: str, approver: str, mode: str) -> Tuple[bool, Optional[str]]:
        """Process user approval for a pending request."""
        req = self.approval_requests.get(request_id)
        if req is None:
            return False, f"Unknown approval request '{request_id}'."
        return req.approve(approver, mode)

    def deny_request(self, request_id: str, denier: str, reason: str) -> Tuple[bool, Optional[str]]:
        """Process user denial for a pending request."""
        req = self.approval_requests.get(request_id)
        if req is None:
            return False, f"Unknown approval request '{request_id}'."
        return req.deny(denier, reason)

    def expire_pending_requests(self, current_time: Optional[float] = None) -> List[str]:
        """Check all pending requests and expire those exceeding timeout."""
        expired = []
        for req_id, req in list(self.approval_requests.items()):
            if req.check_and_update_expiry(current_time):
                expired.append(req_id)
        return expired

    def _extract_domain(self, url: str) -> str:
        """Extract domain host from URL."""
        import urllib.parse
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc or parsed.path
            return host.split(":")[0].lower()
        except Exception:
            return ""
