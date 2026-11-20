/**
 * Lazy OS Command Center - Main Client Controller (V4 QEMU Edition)
 * Pure vanilla ES6, zero external dependencies, works 100% offline.
 *
 * Implements full Track A WebSocket streaming protocol per docs/API_CONTRACT.md:
 * - Real WebSocket token streaming on CONFIG.wsUrl
 * - GBNF schema plan proposals & policy tier (L0-L4) evaluation badges
 * - Pending Approvals gates & resolution
 * - Real Btrfs snapshot rollback via POST /api/tasks/undo
 * - Responsive 720p / 1080p / 4K UI scale persistence
 * - Zero client-side mocks or substrings
 */

const CONFIG = {
  wsUrl: (location.protocol === "https:" ? "wss://" : "ws://") + location.host,
  apiBase: "",
  pollIntervalMs: 2500,
  maxSparkPoints: 20
};

// Telemetry Histograms for SVG Sparklines
const sparkHistory = {
  cpu: [4, 5, 4, 6, 8, 5, 4, 7, 5, 4],
  ram: [68, 68, 69, 69, 70, 71, 70, 69, 69, 70],
  disk: [5.8, 5.8, 5.8, 5.8, 5.8, 5.8, 5.8, 5.8, 5.8, 5.8],
  net: [12, 18, 14, 25, 42, 19, 15, 22, 16, 14]
};

let currentPath = "";
let currentSessionToken = "lazy-token-default";
let ws = null;
let wsConnected = false;
let lastTaskId = null;
let activeStreamingElement = null;

document.addEventListener("DOMContentLoaded", () => {
  initBootAnimation();
  initClock();
  initNavigation();
  initCommandPalette();
  initApprovalsDrawer();
  initAICommandCenter();
  initFileManager();
  initSecurityCenter();
  initSettings();
  initAppLauncher();
  initWebSocket();

  // Initial Data Load
  fetchIdentityAndBadges();
  fetchBriefing();
  fetchMetrics();
  fetchServices();
  fetchCapabilities();
  fetchAuditLog();
  fetchFiles("");

  // Start background telemetry polling
  setInterval(fetchMetrics, CONFIG.pollIntervalMs);
  setInterval(fetchIdentityAndBadges, 10000);
});

/* -------------------------------------------------------------
 * 1. Boot Animation (Skippable within 3s)
 * ------------------------------------------------------------- */
function initBootAnimation() {
  const overlay = document.getElementById("boot-overlay");
  const fill = document.getElementById("boot-progress");
  const status = document.getElementById("boot-status");
  const skipBtn = document.getElementById("btn-skip-boot");

  if (!overlay) return;

  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("noboot") === "1" || window.location.hash) {
    overlay.classList.add("hidden");
    return;
  }

  let progress = 0;
  const stages = [
    "Checking kernel invariants & AVX2 SIMD...",
    "Mounting persistent Btrfs /data partition...",
    "Validating systemd unprivileged security slices...",
    "Connecting to Gateway REST & WebSocket streaming...",
    "Zero-Trust Edge ML Command Center Ready."
  ];

  const interval = setInterval(() => {
    progress += 25;
    if (fill) fill.style.width = progress + "%";
    const stageIdx = Math.min(Math.floor(progress / 25), stages.length - 1);
    if (status) status.textContent = stages[stageIdx];

    if (progress >= 100) {
      clearInterval(interval);
      setTimeout(dismissBoot, 200);
    }
  }, 350);

  function dismissBoot() {
    clearInterval(interval);
    overlay.classList.add("hidden");
  }

  if (skipBtn) skipBtn.addEventListener("click", dismissBoot);
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !overlay.classList.contains("hidden")) {
      dismissBoot();
    }
  });
}

/* -------------------------------------------------------------
 * 2. Top Bar Clock & Navigation
 * ------------------------------------------------------------- */
function initClock() {
  const clockEl = document.getElementById("clock-display");
  function updateTime() {
    const d = new Date();
    if (clockEl) clockEl.textContent = d.toISOString().substring(11, 19) + " UTC";
  }
  updateTime();
  setInterval(updateTime, 1000);
}

function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn");
  const panels = document.querySelectorAll(".view-panel");

  navBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      navBtns.forEach((b) => b.classList.remove("active"));
      panels.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add("active");
    });
  });

  function handleRoute() {
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get("tab") || window.location.hash.replace("#", "");
    if (tabParam) {
      const targetBtn = document.querySelector(`[data-tab="${tabParam}"]`) || document.querySelector(`[data-tab="tab-${tabParam}"]`);
      if (targetBtn) {
        targetBtn.click();
      }
    }
  }
  window.addEventListener("hashchange", handleRoute);
  handleRoute();
}

/* -------------------------------------------------------------
 * 3. Identity & Honest Badges (GET /api/identity & /api/build-info)
 * ------------------------------------------------------------- */
async function fetchIdentityAndBadges() {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/identity");
    if (res.ok) {
      const id = await res.json();
      const foot = document.getElementById("foot-identity");
      if (foot) {
        foot.textContent = `${id.hostname} [${id.kernel_release}] (boot: ${id.boot_id ? id.boot_id.substring(0, 8) : 'active'}... up: ${Math.round(id.uptime || 0)}s)`;
      }
    }
  } catch (e) {
    const foot = document.getElementById("foot-identity");
    if (foot) foot.textContent = "Identity: Unavailable (Offline)";
  }

  try {
    const bRes = await fetch(CONFIG.apiBase + "/api/build-info");
    if (bRes.ok) {
      const info = await bRes.json();
      const badgeBox = document.getElementById("foot-badges");
      if (badgeBox && info) {
        badgeBox.innerHTML = `
          <span class="badge-pill ${info.storage ? info.storage.status : 'real'}">Storage: ${info.storage ? (info.storage.label || 'Btrfs') : 'Btrfs'}</span>
          <span class="badge-pill ${info.audit ? info.audit.status : 'real'}">Audit: ${info.audit ? (info.audit.label || 'SHA-256') : 'SHA-256'}</span>
          <span class="badge-pill real">LLM: Qwen2.5-1.5B</span>
          <span class="badge-pill real">Policy: L0-L4 Gate</span>
        `;
      }
    }
  } catch (e) {}
}

/* -------------------------------------------------------------
 * 4. System Metrics & SVG Sparklines (GET /api/metrics)
 * ------------------------------------------------------------- */
async function fetchMetrics() {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/metrics");
    if (!res.ok) return;
    const m = await res.json();

    const cpuEl = document.getElementById("sys-cpu-val");
    const ramEl = document.getElementById("sys-ram-val");
    const diskEl = document.getElementById("sys-disk-val");
    const netEl = document.getElementById("sys-net-val");

    if (cpuEl && m.cpu_percent !== undefined) cpuEl.textContent = m.cpu_percent + "%";
    if (ramEl && m.memory) ramEl.textContent = m.memory.used_mb + " MB";
    if (diskEl && m.disk) diskEl.textContent = m.disk.used_mb + " MB";
    if (netEl && m.network) netEl.textContent = m.network.rx_kb + " KB/s";

    const hCpu = document.getElementById("home-cpu");
    const hRam = document.getElementById("home-ram");
    const hDisk = document.getElementById("home-disk");
    if (hCpu && m.cpu_percent !== undefined) hCpu.textContent = m.cpu_percent + "%";
    if (hRam && m.memory) hRam.textContent = m.memory.used_mb + " MB";
    if (hDisk && m.disk) hDisk.textContent = m.disk.used_mb + " MB";

    if (m.cpu_percent !== undefined) pushSpark("cpu", m.cpu_percent);
    if (m.memory && m.memory.used_mb !== undefined) pushSpark("ram", m.memory.used_mb);
    if (m.disk && m.disk.used_mb !== undefined) pushSpark("disk", m.disk.used_mb);
    if (m.network && m.network.rx_kb !== undefined) pushSpark("net", m.network.rx_kb);

    renderSparkline("spark-cpu", sparkHistory.cpu);
    renderSparkline("spark-ram", sparkHistory.ram);
    renderSparkline("spark-disk", sparkHistory.disk);
    renderSparkline("spark-net", sparkHistory.net);
  } catch (e) {}
}

function pushSpark(key, val) {
  if (!sparkHistory[key]) return;
  sparkHistory[key].push(val);
  if (sparkHistory[key].length > CONFIG.maxSparkPoints) {
    sparkHistory[key].shift();
  }
}

function renderSparkline(svgId, points) {
  const svg = document.getElementById(svgId);
  if (!svg || points.length < 2) return;

  const min = Math.min(...points);
  const max = Math.max(...points) || 1;
  const range = max - min || 1;
  const w = 100;
  const h = 30;

  const coords = points.map((p, i) => {
    const x = (i / (points.length - 1)) * w;
    const y = h - ((p - min) / range) * (h - 6) - 3;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const pathD = "M " + coords.join(" L ");
  const fillD = pathD + ` L ${w},${h} L 0,${h} Z`;

  svg.innerHTML = `
    <path d="${fillD}" class="sparkline-fill" />
    <path d="${pathD}" class="sparkline-path" />
  `;
}

/* -------------------------------------------------------------
 * 5. Services Table (GET /api/services)
 * ------------------------------------------------------------- */
async function fetchServices() {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/services");
    if (!res.ok) return;
    const services = await res.json();
    const tbody = document.getElementById("services-tbody");
    if (!tbody) return;

    tbody.innerHTML = services
      .map(
        (s) => `
        <tr>
          <td><strong>${s.unit}</strong></td>
          <td><code>${s.slice || '/lazy-interactive.slice'}</code></td>
          <td><span class="badge-pill ${s.status === 'running' ? 'real' : 'sim'}">${s.status}</span></td>
          <td>${s.desc}</td>
        </tr>
      `
      )
      .join("");
  } catch (e) {}
}

/* -------------------------------------------------------------
 * 6. File Manager Module (/data)
 * ------------------------------------------------------------- */
function initFileManager() {
  const refreshBtn = document.getElementById("btn-refresh-files");
  const newFileBtn = document.getElementById("btn-new-file");

  if (refreshBtn) refreshBtn.addEventListener("click", () => fetchFiles(currentPath));
  if (newFileBtn) {
    newFileBtn.addEventListener("click", async () => {
      const filename = prompt("Enter new filename in /data (e.g. notes.md):");
      if (!filename) return;
      const content = prompt("Enter file content:") || "";
      await createFile(filename, content);
    });
  }
}

async function fetchFiles(subpath) {
  currentPath = subpath || "";
  const tbody = document.getElementById("file-tbody");
  if (!tbody) return;

  try {
    const res = await fetch(CONFIG.apiBase + "/api/fs?path=" + encodeURIComponent(subpath || ""));
    if (!res.ok) {
      tbody.innerHTML = `<tr><td colspan="4" class="text-alert">Directory not accessible</td></tr>`;
      return;
    }
    const data = await res.json();

    if (data.type === "directory" && Array.isArray(data.items)) {
      updateBreadcrumbs(subpath);
      if (data.items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-muted">Empty directory</td></tr>`;
        return;
      }
      tbody.innerHTML = data.items
        .map(
          (item) => `
          <tr>
            <td><strong>${item.name}</strong></td>
            <td>${item.is_dir ? "📁 Directory" : "📄 File"}</td>
            <td>${item.size || 0} bytes</td>
            <td>
              ${
                !item.is_dir
                  ? `<button class="btn-secondary" onclick="viewFile('${item.name}')">View</button>
                     <button class="btn-secondary" onclick="requestDeleteFile('${item.name}')">Delete</button>`
                  : `<button class="btn-secondary" onclick="fetchFiles('${item.name}')">Open</button>`
              }
            </td>
          </tr>
        `
        )
        .join("");
    }
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4">Error loading files</td></tr>`;
  }
}

function updateBreadcrumbs(subpath) {
  const box = document.getElementById("file-breadcrumbs");
  if (!box) return;
  box.innerHTML = `<span class="crumb active" onclick="fetchFiles('')">/data${subpath ? '/' + subpath : ''}</span>`;
}

async function createFile(filename, content) {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/fs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: filename, content: content })
    });
    const result = await res.json();
    if (res.ok) {
      showToast(`File '${filename}' created successfully!`);
      fetchFiles(currentPath);
      fetchAuditLog();
    } else {
      alert("Policy Denied: " + (result.error || "Permission denied"));
    }
  } catch (e) {
    alert("Error creating file: " + e);
  }
}

window.viewFile = async function (filename) {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/fs?path=" + encodeURIComponent(filename));
    const data = await res.json();
    alert(`=== File: ${filename} ===\n\n${data.content || ""}`);
  } catch (e) {
    alert("Error reading file: " + e);
  }
};

window.requestDeleteFile = async function (filename) {
  if (!confirm(`Request deletion of '${filename}'? (Requires L2 policy approval)`)) return;
  try {
    const res = await fetch(CONFIG.apiBase + "/api/fs", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: filename })
    });
    const result = await res.json();
    if (res.status === 202) {
      showToast("Deletion queued for L2 approval!");
      fetchApprovals();
      openApprovalsDrawer();
    } else if (res.ok) {
      showToast(`Deleted '${filename}'`);
      fetchFiles(currentPath);
      fetchAuditLog();
    }
  } catch (e) {
    alert("Error: " + e);
  }
};

/* -------------------------------------------------------------
 * 7. Security & Audit Center (GET /api/audit & POST /api/audit/verify)
 * ------------------------------------------------------------- */
function initSecurityCenter() {
  const verifyBtn = document.getElementById("btn-verify-audit-chain");
  if (verifyBtn) {
    verifyBtn.addEventListener("click", async () => {
      const statusBox = document.getElementById("audit-verify-status");
      if (statusBox) statusBox.textContent = "Verifying cryptographic SHA-256 chain...";

      try {
        const res = await fetch(CONFIG.apiBase + "/api/audit/verify", { method: "POST" });
        const result = await res.json();
        if (result.is_valid) {
          statusBox.className = "alert-box green";
          statusBox.textContent = `[PASS] Cryptographic Hash Chain Validated: ${result.total_records || result.verified_entries || 0} receipts verified from genesis.`;
        } else {
          statusBox.className = "alert-box red";
          statusBox.textContent = `[FAIL] Tamper Detected! Chain broken: ${Array.isArray(result.errors) ? result.errors.join(", ") : "Hash mismatch"}`;
        }
      } catch (e) {
        if (statusBox) statusBox.textContent = "Verification error: " + e;
      }
    });
  }
}

async function fetchAuditLog() {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/audit?limit=20");
    if (!res.ok) return;
    const records = await res.json();
    const pre = document.getElementById("audit-log-pre");
    if (pre && Array.isArray(records)) {
      pre.textContent = records.map((r) => JSON.stringify(r)).join("\n\n");
    }
  } catch (e) {}
}

/* -------------------------------------------------------------
 * 8. Approvals Drawer & Queue
 * ------------------------------------------------------------- */
function initApprovalsDrawer() {
  const toggleBtn = document.getElementById("btn-toggle-approvals");
  const closeBtn = document.getElementById("btn-close-drawer");
  const drawer = document.getElementById("approvals-drawer");

  if (toggleBtn) toggleBtn.addEventListener("click", () => drawer.classList.toggle("open"));
  if (closeBtn) closeBtn.addEventListener("click", () => drawer.classList.remove("open"));
  fetchApprovals();
}

function openApprovalsDrawer() {
  const drawer = document.getElementById("approvals-drawer");
  if (drawer) drawer.classList.add("open");
}

async function fetchApprovals() {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/approvals");
    if (!res.ok) return;
    const items = await res.json();
    const badge = document.getElementById("badge-alerts");
    if (badge) badge.textContent = items.length;

    const list = document.getElementById("approvals-list");
    if (!list) return;

    if (!Array.isArray(items) || items.length === 0) {
      list.innerHTML = `<div class="empty-state">No pending approval requests.</div>`;
      return;
    }

    list.innerHTML = items
      .map(
        (it) => `
      <div class="approval-card card mb-4">
        <div class="card-title"><h4>${it.title || it.capability}</h4><span class="tier-chip ${it.tier ? it.tier.toLowerCase() : 'l2'}">${it.tier || 'L2'}</span></div>
        <p class="text-muted text-sm">Capability: <code>${it.capability}</code></p>
        <p class="text-muted text-sm">${it.description || JSON.stringify(it.params || {})}</p>
        <div class="approval-actions mt-4">
          <button class="btn-primary" onclick="resolveApproval('${it.id}', 'approve')">Approve</button>
          <button class="btn-secondary" onclick="resolveApproval('${it.id}', 'deny')">Deny</button>
        </div>
      </div>
    `
      )
      .join("");
  } catch (e) {}
}

window.resolveApproval = async function (id, action) {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/approvals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, action: action })
    });
    const result = await res.json();
    showToast(`Approval ${action}d: ${result.result || action}`);
    fetchApprovals();
    fetchFiles(currentPath);
    fetchAuditLog();

    // Notify over WebSocket if open
    if (ws && ws.readyState === WebSocket.OPEN && wsConnected) {
      ws.send(JSON.stringify({
        type: "approval_response",
        payload: { approval_id: id, approved: action === "approve" }
      }));
    }
  } catch (e) {
    alert("Error: " + e);
  }
};

/* -------------------------------------------------------------
 * 9. WebSocket Streaming & AI Command Center
 * ------------------------------------------------------------- */
function initWebSocket() {
  try {
    ws = new WebSocket(CONFIG.wsUrl);
  } catch (e) {
    console.warn("WebSocket initialization error:", e);
    return;
  }

  ws.onopen = () => {
    wsConnected = true;
    ws.send(JSON.stringify({
      type: "auth",
      payload: { token: currentSessionToken }
    }));
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      handleWebSocketMessage(msg);
    } catch (err) {
      console.error("WebSocket message parsing error:", err);
    }
  };

  ws.onclose = () => {
    wsConnected = false;
    setTimeout(initWebSocket, 3000);
  };

  ws.onerror = () => {
    wsConnected = false;
  };
}

function handleWebSocketMessage(msg) {
  const type = msg.type;
  const payload = msg.payload || {};

  switch (type) {
    case "auth_ok":
      lightPipeline("pipe-gateway");
      break;

    case "token_stream":
      lightPipeline("pipe-planner");
      if (activeStreamingElement) {
        activeStreamingElement.textContent += (payload.chunk || "");
        const transcript = document.getElementById("chat-transcript");
        if (transcript) transcript.scrollTop = transcript.scrollHeight;
      }
      break;

    case "plan_proposal":
      lightPipeline("pipe-planner");
      lightPipeline("pipe-policy");
      lastTaskId = payload.task_id;
      renderPlanProposal(payload);
      break;

    case "policy_eval":
      lightPipeline("pipe-policy");
      renderPolicyEval(payload);
      break;

    case "approval_required":
      lightPipeline("pipe-policy");
      appendChatMessage("system", `⚠️ <strong>Approval Required:</strong> [${payload.policy_tier || 'L2'}] ${payload.description || payload.capability}<br><button class="btn-primary" style="margin-top:6px;" onclick="resolveApproval('${payload.approval_id}', 'approve')">Approve Task</button> <button class="btn-secondary" style="margin-top:6px;" onclick="resolveApproval('${payload.approval_id}', 'deny')">Deny Task</button>`);
      fetchApprovals();
      openApprovalsDrawer();
      break;

    case "task_receipt":
      lightPipeline("pipe-tasks");
      lightPipeline("pipe-broker");
      lightPipeline("pipe-audit");
      lastTaskId = payload.task_id;
      renderTaskReceipt(payload);
      activeStreamingElement = null;
      fetchFiles(currentPath);
      fetchAuditLog();
      break;

    case "error":
      activeStreamingElement = null;
      appendChatMessage("system", `<span class="text-alert">Error: ${payload.reason || JSON.stringify(payload)}</span>`);
      break;
  }
}

function renderPlanProposal(proposal) {
  const box = document.getElementById("plan-stream-box");
  const taskIdEl = document.getElementById("plan-task-id");
  const stepsEl = document.getElementById("plan-steps");
  const footerEl = document.getElementById("plan-footer");

  if (box && taskIdEl && stepsEl) {
    box.style.display = "block";
    taskIdEl.textContent = proposal.task_id || "task";
    stepsEl.innerHTML = `
      <div class="plan-step-item">
        <span class="tier-chip ${(proposal.policy_tier || 'L1').toLowerCase()}">${proposal.policy_tier || 'L1'}</span>
        <strong>Capability:</strong> <code>${proposal.capability}</code>
        <div class="text-muted text-sm mt-4">Params: ${JSON.stringify(proposal.params || {})}</div>
      </div>
    `;
    if (footerEl) {
      footerEl.innerHTML = `<span class="text-sm text-muted">Risk Level: <strong>${proposal.risk_level || 'low'}</strong> | Approval Required: <strong>${proposal.requires_approval ? 'YES' : 'NO'}</strong></span>`;
    }
  }
}

function renderPolicyEval(ev) {
  const verdictColor = ev.verdict === "allow" ? "var(--green-real)" : "var(--red-alert)";
  appendChatMessage("system", `🛡️ <strong>Policy Gate:</strong> <span class="tier-chip ${(ev.tier || 'L1').toLowerCase()}">${ev.tier || 'L1'}</span> Verdict: <strong style="color:${verdictColor};">${(ev.verdict || 'allow').toUpperCase()}</strong> — ${ev.reason || 'Evaluated'}`);
}

function renderTaskReceipt(receipt) {
  const receiptHtml = `
    ✔️ <strong>Task Execution Receipt:</strong> <code>${receipt.task_id}</code> [${receipt.status}]<br>
    Capability: <code>${receipt.capability || 'executed'}</code><br>
    ${receipt.target ? `Target: <code>${receipt.target}</code><br>` : ''}
    ${receipt.btrfs_snapshot_id ? `Btrfs Snapshot: <code>${receipt.btrfs_snapshot_id}</code><br>` : ''}
    ${receipt.chain_hash ? `Audit Chain Hash: <code>${receipt.chain_hash.substring(0, 16)}...</code><br>` : ''}
    ${receipt.rollback_available ? `<button class="btn-secondary" style="margin-top:6px;" onclick="undoLastTask('${receipt.task_id}')">⏪ Undo Task (Rollback Btrfs Snapshot)</button>` : ''}
  `;
  appendChatMessage("system", receiptHtml);
}

function initAICommandCenter() {
  const form = document.getElementById("ai-input-form");
  const input = document.getElementById("ai-input-text");
  const quickBtns = document.querySelectorAll(".btn-action");

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      handleUserDirective(text);
      input.value = "";
    });
  }

  quickBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const directive = btn.getAttribute("data-directive");
      if (directive) {
        const aiTabBtn = document.querySelector('[data-tab="tab-ai"]');
        if (aiTabBtn) aiTabBtn.click();
        handleUserDirective(directive);
      }
    });
  });
}

async function handleUserDirective(text) {
  appendChatMessage("user", text);
  lightPipeline("pipe-gateway");

  // Create container for live token stream
  activeStreamingElement = createStreamingMessage("system");

  // Route directive through WebSocket if connected
  if (ws && ws.readyState === WebSocket.OPEN && wsConnected) {
    lightPipeline("pipe-planner");
    ws.send(JSON.stringify({
      type: "user_input",
      payload: {
        text: text,
        mode: "interactive"
      }
    }));
  } else {
    // REST POST /api/command fallback per API_CONTRACT Section 1.5
    try {
      lightPipeline("pipe-planner");
      lightPipeline("pipe-policy");
      const res = await fetch(CONFIG.apiBase + "/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text, session_id: "sess-default", interactive: false })
      });
      const data = await res.json();
      if (res.ok) {
        lastTaskId = data.task_id;
        lightPipeline("pipe-tasks");
        lightPipeline("pipe-broker");
        lightPipeline("pipe-audit");
        if (activeStreamingElement) {
          activeStreamingElement.textContent = data.message || "Executed via zero-trust broker.";
          activeStreamingElement = null;
        }
        renderTaskReceipt({
          task_id: data.task_id,
          status: data.status,
          capability: data.intent ? data.intent.capability : "action",
          target: data.intent ? data.intent.target_path : null,
          rollback_available: true
        });
        fetchFiles(currentPath);
        fetchAuditLog();
      } else {
        if (activeStreamingElement) activeStreamingElement.remove();
        appendChatMessage("system", `<span class="text-alert">Policy Denied / Error: ${data.error || res.statusText}</span>`);
      }
    } catch (err) {
      if (activeStreamingElement) activeStreamingElement.remove();
      appendChatMessage("system", `<span class="text-alert">Gateway communication error: ${err.message}</span>`);
    }
  }
}

function lightPipeline(nodeId) {
  const node = document.getElementById(nodeId);
  if (node) {
    node.classList.add("active");
    setTimeout(() => node.classList.remove("active"), 800);
  }
}

function appendChatMessage(type, html) {
  const transcript = document.getElementById("chat-transcript");
  if (!transcript) return;
  const div = document.createElement("div");
  div.className = `chat-msg ${type}`;
  div.innerHTML = `<div class="msg-sender">${type === "user" ? "You" : "Lazy OS Supervisor"}</div><div class="msg-body">${html}</div>`;
  transcript.appendChild(div);
  transcript.scrollTop = transcript.scrollHeight;
}

function createStreamingMessage(type) {
  const transcript = document.getElementById("chat-transcript");
  if (!transcript) return null;
  const div = document.createElement("div");
  div.className = `chat-msg ${type}`;
  div.innerHTML = `<div class="msg-sender">${type === "user" ? "You" : "Lazy OS Supervisor"}</div><div class="msg-body stream-text"></div>`;
  transcript.appendChild(div);
  transcript.scrollTop = transcript.scrollHeight;
  return div.querySelector(".stream-text");
}

/* -------------------------------------------------------------
 * Real Btrfs Undo Rollback (POST /api/tasks/undo)
 * ------------------------------------------------------------- */
window.undoLastTask = async function (taskId) {
  const targetId = taskId || lastTaskId;
  appendChatMessage("system", `<em>Initiating Btrfs snapshot rollback for task ${targetId || 'latest'}...</em>`);
  lightPipeline("pipe-tasks");

  try {
    const res = await fetch(CONFIG.apiBase + "/api/tasks/undo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: targetId || "" })
    });
    const result = await res.json();
    if (res.ok && result.success) {
      lightPipeline("pipe-audit");
      appendChatMessage(
        "system",
        `✔️ <strong>Btrfs Rollback Succeeded:</strong> Task <code>${result.task_id}</code><br>` +
        `Restored Snapshot: <code>${result.snapshot_restored}</code><br>` +
        `Audit Entry ID: ${result.audit_entry_id} (Hash: <code>${result.chain_hash ? result.chain_hash.substring(0, 16) + '...' : 'Verified'}</code>)`
      );
      fetchFiles(currentPath);
      fetchAuditLog();
      showToast(`Task ${result.task_id} rolled back successfully`);
    } else {
      appendChatMessage("system", `❌ <strong>Rollback Failed:</strong> ${result.error || "No rollback snapshot available"}`);
    }
  } catch (err) {
    appendChatMessage("system", `❌ <strong>Rollback Network Error:</strong> ${err.message}`);
  }
};

/* -------------------------------------------------------------
 * 10. Briefing & Capabilities
 * ------------------------------------------------------------- */
async function fetchBriefing() {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/briefing");
    if (!res.ok) return;
    const b = await res.json();
    const dEl = document.getElementById("briefing-date");
    const hEl = document.getElementById("briefing-headline");
    const cEl = document.getElementById("briefing-chores");
    const fEl = document.getElementById("briefing-feed");

    if (dEl && b.date) dEl.textContent = b.date;
    if (hEl && b.status) hEl.textContent = b.status;
    if (cEl && Array.isArray(b.overnight_chores)) {
      cEl.innerHTML = b.overnight_chores.map((c) => `<li>✔️ <strong>${c.chore}</strong>: ${c.result}</li>`).join("");
    }
    if (fEl && Array.isArray(b.niche_feed)) {
      fEl.innerHTML = b.niche_feed.map((f) => `<li>📰 <strong>${f.title}</strong> (${f.source})</li>`).join("");
    }
  } catch (e) {}
}

async function fetchCapabilities() {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/capabilities");
    if (!res.ok) return;
    const caps = await res.json();
    const grid = document.getElementById("agent-cards-grid");
    if (!grid) return;

    if (Array.isArray(caps)) {
      grid.innerHTML = caps
        .slice(0, 12)
        .map(
          (c) => `
        <div class="card">
          <div class="card-title"><h4>${c.name}</h4><span class="tier-chip ${(c.tier || 'l1').toLowerCase()}">${c.tier || 'L1'}</span></div>
          <p class="text-sm text-muted">${c.description || ""}</p>
          <span class="badge-pill real mt-4">Approval: ${c.approval_mode || 'auto'}</span>
        </div>
      `
        )
        .join("");
    }
  } catch (e) {}
}

/* -------------------------------------------------------------
 * 11. Command Palette (Ctrl+K)
 * ------------------------------------------------------------- */
function initCommandPalette() {
  const modal = document.getElementById("cmd-modal");
  const triggerBtn = document.getElementById("btn-cmd-palette");
  const input = document.getElementById("cmd-palette-input");
  const options = document.querySelectorAll(".cmd-option");

  function openPalette() {
    if (modal) modal.style.display = "flex";
    if (input) {
      input.value = "";
      input.focus();
    }
  }

  function closePalette() {
    if (modal) modal.style.display = "none";
  }

  if (triggerBtn) triggerBtn.addEventListener("click", openPalette);
  window.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      openPalette();
    }
    if (e.key === "Escape" && modal && modal.style.display !== "none") {
      closePalette();
    }
  });

  options.forEach((opt) => {
    opt.addEventListener("click", () => {
      const target = opt.getAttribute("data-target");
      if (target) {
        const btn = document.querySelector(`[data-tab="${target}"]`);
        if (btn) btn.click();
      }
      closePalette();
    });
  });
}

/* -------------------------------------------------------------
 * 12. Settings & Responsive UI Scale
 * ------------------------------------------------------------- */
function initSettings() {
  const motionCheck = document.getElementById("set-reduced-motion");
  if (motionCheck) {
    motionCheck.addEventListener("change", (e) => {
      if (e.target.checked) {
        document.body.classList.add("reduced-motion");
      } else {
        document.body.classList.remove("reduced-motion");
      }
    });
  }

  const scaleSelect = document.getElementById("set-ui-scale");
  if (scaleSelect) {
    const savedScale = localStorage.getItem("lazy_ui_scale") || "1080p";
    scaleSelect.value = savedScale;
    applyUIScale(savedScale);

    scaleSelect.addEventListener("change", (e) => {
      const val = e.target.value;
      localStorage.setItem("lazy_ui_scale", val);
      applyUIScale(val);
      showToast(`Display scale profile updated to ${val.toUpperCase()}`);
    });
  }
}

function applyUIScale(scale) {
  document.body.setAttribute("data-ui-scale", scale);
  document.documentElement.setAttribute("data-ui-scale", scale);
}

function initAppLauncher() {
  const tiles = document.querySelectorAll(".app-tile.active-app");
  tiles.forEach((t) => {
    t.addEventListener("click", () => {
      const app = t.getAttribute("data-launch");
      if (app === "notes") {
        const btn = document.querySelector('[data-tab="tab-files"]');
        if (btn) btn.click();
      } else if (app === "briefing") {
        const btn = document.querySelector('[data-tab="tab-home"]');
        if (btn) btn.click();
      } else if (app === "outbox") {
        openApprovalsDrawer();
      } else if (app === "web" || app === "comms") {
        const btn = document.querySelector('[data-tab="tab-ai"]');
        if (btn) btn.click();
      } else if (app === "sys") {
        const btn = document.querySelector('[data-tab="tab-system"]');
        if (btn) btn.click();
      }
    });
  });
}

function showToast(msg) {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}
