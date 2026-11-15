# Deck Input - Task 5: Multi-Tier Policy, Taint Tracking & Outbox Safety

## Slide Metadata
- **Slide Title**: Multi-Tier Security: Policy Engine, Taint Tracking & Outbox
- **Topic**: Guardrail Architecture, Dynamic Taint Tracking & Rate Limiting
- **Time Allocation**: 2 Minutes

---

## Slide Content & Bullets

### 1. The 4-Tier Capability Model (37 Capability Manifests)
- **L0 (Read-only)**: Automatic (`fs.read`, `sys.service_status`, `web.read`, `hw.usb_list`).
- **L1 (Low-risk Automatic)**: Modifies user space (`fs.write`, `doc.create_markdown`, `hw.volume_set`).
- **L2 (Approval Required)**: Mutating or privileged (`fs.delete`, `code.run`, `sys.service_restart`, `hw.rfkill_set`).
- **L3 (Hazardous / Outbox)**: External communication (`mail.send`, `chat.send`, `web.submit`, `sys.process_signal`).
- **L4 (Strictly Disallowed)**: Hardcoded prohibitions (`/etc/shadow`, audit ledger, policy files).

### 2. Dynamic Taint Tracking (Rule F8)
- External send actions require clear provenance:
  - If a recipient or destination originated from untrusted data (e.g. prompt injection in an incoming email or web page), the taint tracker flags the parameter as **UNVERIFIED**.
  - Tainted sends are immediately blocked unless explicitly confirmed by the user via the HUD.

### 3. The Outbox Safety Barrier (`lazy-outbox`)
- Irreversible actions (`mail.send`, `chat.send`) enter a staged queue with a configurable delay window (e.g. 10s).
- During the window, the user can inspect the preview diff and cancel the action with a single click.

---

## Speaker Talking Points
1. "In an autonomous agent, security cannot be an afterthought prompt instruction. It must be an architectural gate."
2. "Notice Rule F8: even if an attacker tricks the LLM into proposing an email exfiltration intent, the policy engine traces the taint back to untrusted web content and denies execution."
3. "Our adversarial attack evaluation demonstrated 100% defense against 70 distinct attack vectors across indirect web injections, shell escapes, and L4 privilege escalation."

---

## Evidence & Verification References
- [config/capabilities/](file:///c:/Users/len/OS/config/capabilities/): 37 YAML capability manifests.
- [src/lazy/outbox/queue.py](file:///c:/Users/len/OS/src/lazy/outbox/queue.py): Outbox delay and approval queue.
- [bench/results/safety_metrics.csv](file:///c:/Users/len/OS/bench/results/safety_metrics.csv): 0.00% guarded unsafe action rate vs 57.14% unguarded baseline.
- [tests/results/M4.4.log](file:///c:/Users/len/OS/tests/results/M4.4.log): 70-attack adversarial evaluation log.
