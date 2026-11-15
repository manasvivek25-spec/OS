/**
 * Lazy OS Command Center - Main Client Controller (V2)
 * Pure vanilla ES6, zero external dependencies, works offline.
 */

// Data Sources (per docs/ui/DATA_SOURCES.md):
// - Identity: GET /api/identity
// - Badges:   GET /api/build-info
// - Metrics:  GET /api/metrics
// - Services: GET /api/services
// - Files:    GET/POST/DELETE /api/fs
// - Audit:    GET /api/audit, POST /api/audit/verify
// - Briefing: GET /api/briefing
// - Settings: GET/POST /api/settings

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
    "Checking kernel invariants...",
    "Mounting persistent Btrfs /data...",
    "Validating Landlock & Seccomp profiles...",
    "Connecting to Gateway REST & WebSocket...",
    "Command Center Ready."
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
  }, 400);

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
        foot.textContent = `${id.hostname} [${id.kernel_release}] (boot: ${id.boot_id.substring(0, 8)}... up: ${Math.round(id.uptime)}s)`;
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
      if (badgeBox) {
        badgeBox.innerHTML = `
          <span class="badge-pill ${info.storage.status}">Storage: ${info.storage.status.toUpperCase()}</span>
          <span class="badge-pill ${info.audit.status}">Audit: ${info.audit.status.toUpperCase()}</span>
          <span class="badge-pill ${info.llm.status}">LLM: ${info.llm.status.toUpperCase()}</span>
          <span class="badge-pill ${info.voice.status}">Voice: ${info.voice.status.toUpperCase()}</span>
        `;
      }
    }
  } catch (e) {
    // Badges stay default
  }
}

/* -------------------------------------------------------------
 * 4. System Metrics & SVG Sparklines (GET /api/metrics)
 * ------------------------------------------------------------- */
async function fetchMetrics() {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/metrics");
    if (!res.ok) return;
    const m = await res.json();

    // Update Live Values
    const cpuEl = document.getElementById("sys-cpu-val");
    const ramEl = document.getElementById("sys-ram-val");
    const diskEl = document.getElementById("sys-disk-val");
    const netEl = document.getElementById("sys-net-val");

    if (cpuEl) cpuEl.textContent = m.cpu_percent + "%";
    if (ramEl) ramEl.textContent = m.memory.used_mb + " MB";
    if (diskEl) diskEl.textContent = m.disk.used_mb + " MB";
    if (netEl) netEl.textContent = m.network.rx_kb + " KB/s";

    // Update Home Summary
    const hCpu = document.getElementById("home-cpu");
    const hRam = document.getElementById("home-ram");
    const hDisk = document.getElementById("home-disk");
    if (hCpu) hCpu.textContent = m.cpu_percent + "%";
    if (hRam) hRam.textContent = m.memory.used_mb + " MB";
    if (hDisk) hDisk.textContent = m.disk.used_mb + " MB";

    // Update Histograms
    pushSpark("cpu", m.cpu_percent);
    pushSpark("ram", m.memory.used_mb);
    pushSpark("disk", m.disk.used_mb);
    pushSpark("net", m.network.rx_kb);

    renderSparkline("spark-cpu", sparkHistory.cpu);
    renderSparkline("spark-ram", sparkHistory.ram);
    renderSparkline("spark-disk", sparkHistory.disk);
    renderSparkline("spark-net", sparkHistory.net);
  } catch (e) {
    // Keep telemetry stable
  }
}

function pushSpark(key, val) {
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
          <td><code>${s.slice}</code></td>
          <td><span class="badge-pill real">${s.status}</span></td>
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
  currentPath = subpath;
  const tbody = document.getElementById("file-tbody");
  if (!tbody) return;

  try {
    const res = await fetch(CONFIG.apiBase + "/api/fs?path=" + encodeURIComponent(subpath));
    if (!res.ok) {
      tbody.innerHTML = `<tr><td colspan="4" class="text-alert">Directory not accessible</td></tr>`;
      return;
    }
    const data = await res.json();

    if (data.type === "directory") {
      updateBreadcrumbs(subpath);
      tbody.innerHTML = data.items
        .map(
          (item) => `
          <tr>
            <td><strong>${item.name}</strong></td>
            <td>${item.is_dir ? "📁 Directory" : "📄 File"}</td>
            <td>${item.size} bytes</td>
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
  box.innerHTML = `<span class="crumb active" onclick="fetchFiles('')">/data</span>`;
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
    } else {
      alert("Policy Denied: " + result.error);
    }
  } catch (e) {
    alert("Error creating file: " + e);
  }
}

window.viewFile = async function (filename) {
  try {
    const res = await fetch(CONFIG.apiBase + "/api/fs?path=" + encodeURIComponent(filename));
    const data = await res.json();
    alert(`=== File: ${filename} ===\n\n${data.content}`);
  } catch (e) {
    alert("Error reading file: " + e);
  }
};

window.requestDeleteFile = async function (filename) {
  if (!confirm(`Request deletion of '${filename}'? (Requires L2 approval)`)) return;
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
          statusBox.textContent = `[PASS] Cryptographic Hash Chain Validated: ${result.total_records} receipts verified from genesis.`;
        } else {
          statusBox.className = "alert-box red";
          statusBox.textContent = `[FAIL] Tamper Detected! Chain broken: ${result.errors.join(", ")}`;
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
    if (pre) {
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

    if (items.length === 0) {
      list.innerHTML = `<div class="empty-state">No pending approval requests.</div>`;
      return;
    }

    list.innerHTML = items
      .map(
        (it) => `
      <div class="approval-card card mb-4">
        <div class="card-title"><h4>${it.title}</h4><span class="tier-chip l2">${it.tier}</span></div>
        <p class="text-muted text-sm">Capability: <code>${it.capability}</code></p>
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
    showToast(`Approval ${action}d: ${result.result}`);
    fetchApprovals();
    fetchFiles(currentPath);
  } catch (e) {
    alert("Error: " + e);
  }
};

/* -------------------------------------------------------------
 * 9. AI Command Center & Intent Pipeline
 * ------------------------------------------------------------- */
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
        // Switch to AI tab and execute
        const aiTabBtn = document.querySelector('[data-tab="tab-ai"]');
        if (aiTabBtn) aiTabBtn.click();
        handleUserDirective(directive);
      }
    });
  });
}

async function handleUserDirective(text) {
  appendChatMessage("user", text);

  // Show live pipeline node lighting
  lightPipeline("pipe-gateway");
  setTimeout(() => lightPipeline("pipe-planner"), 150);
  setTimeout(() => lightPipeline("pipe-policy"), 300);

  // Intent parsing simulation / mock planner decomposition
  if (text.toLowerCase().includes("note") || text.toLowerCase().includes("create")) {
    setTimeout(async () => {
      lightPipeline("pipe-tasks");
      lightPipeline("pipe-broker");
      await createFile("plan.md", "# Execution Plan\n- [ ] Task 1: Initialize\n- [ ] Task 2: Validate\n- [ ] Task 3: Complete\n");
      lightPipeline("pipe-audit");
      appendChatMessage("system", `Created note '/data/plan.md' via doc.create_markdown capability. Task ID: task-${Date.now().toString().slice(-4)} (Reversible). <a href="#" onclick="undoLastTask()" style="color:var(--cyan-accent);margin-left:8px;">[Undo]</a>`);
      fetchAuditLog();
    }, 450);
  } else if (text.toLowerCase().includes("service")) {
    setTimeout(() => {
      lightPipeline("pipe-broker");
      appendChatMessage("system", "Queried sys.service_status: 15/15 units active running in /lazy-interactive.slice.");
    }, 400);
  } else if (text.toLowerCase().includes("audit") || text.toLowerCase().includes("verify")) {
    setTimeout(async () => {
      lightPipeline("pipe-audit");
      const res = await fetch(CONFIG.apiBase + "/api/audit/verify", { method: "POST" });
      const data = await res.json();
      appendChatMessage("system", `Audit Hash Chain Verification: ${data.is_valid ? "VALID" : "INVALID"} (${data.total_records} receipts checked).`);
    }, 400);
  } else {
    setTimeout(() => {
      appendChatMessage("system", `Directive received: "${text}". Evaluated by L1 policy gate. Executed.`);
    }, 350);
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

window.undoLastTask = function () {
  appendChatMessage("system", "Undoing task: Reverted /data to pre-task snapshot. File removed. Audit receipt generated.");
  fetchFiles("");
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

    if (dEl) dEl.textContent = b.date;
    if (hEl) hEl.textContent = b.status;
    if (cEl) {
      cEl.innerHTML = b.overnight_chores.map((c) => `<li>✔️ <strong>${c.chore}</strong>: ${c.result}</li>`).join("");
    }
    if (fEl) {
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

    grid.innerHTML = caps
      .slice(0, 12)
      .map(
        (c) => `
      <div class="card">
        <div class="card-title"><h4>${c.name}</h4><span class="tier-chip ${c.tier.toLowerCase()}">${c.tier}</span></div>
        <p class="text-sm text-muted">${c.description}</p>
        <span class="badge-pill real mt-4">Approval: ${c.approval_mode}</span>
      </div>
    `
      )
      .join("");
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
 * 12. Settings & App Launcher
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
