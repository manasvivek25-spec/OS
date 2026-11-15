/**
 * Lazy OS Futuristic HUD Controller (RFC 6455 WebSocket Client)
 * Pure vanilla JavaScript - 100% self-contained and offline.
 */
(function() {
  'use strict';

  // State
  let ws = null;
  let isConnected = false;
  let activeApprovalId = null;

  // DOM Elements
  const sessionInfo = document.getElementById('session-info');
  const transcriptFeed = document.getElementById('transcript-feed');
  const inputForm = document.getElementById('input-form');
  const userInput = document.getElementById('user-input');
  const planStatus = document.getElementById('plan-status');
  const planRationale = document.getElementById('plan-rationale');
  const stepsList = document.getElementById('steps-list');
  const metricCpu = document.getElementById('metric-cpu');
  const metricRam = document.getElementById('metric-ram');
  const metricModel = document.getElementById('metric-model');
  const metricMode = document.getElementById('metric-mode');
  const emptyApprovals = document.getElementById('empty-approvals');
  const activeApproval = document.getElementById('active-approval');
  const apprTier = document.getElementById('appr-tier');
  const apprCap = document.getElementById('appr-cap');
  const apprReason = document.getElementById('appr-reason');
  const apprDiffCode = document.getElementById('appr-diff-code');
  const btnApprove = document.getElementById('btn-approve');
  const btnDeny = document.getElementById('btn-deny');
  const wakeOverlay = document.getElementById('wake-animation');

  // Trigger boot wake animation
  function triggerWakeAnimation(durationMs = 1800) {
    if (!wakeOverlay) return;
    wakeOverlay.classList.add('active');
    setTimeout(() => {
      wakeOverlay.classList.remove('active');
    }, durationMs);
  }

  // Get token from URL param or default
  function getToken() {
    const params = new URLSearchParams(window.location.search);
    return params.get('token') || 'lazy_hud_default_token';
  }

  // Connect WebSocket
  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || '127.0.0.1';
    const port = window.location.port || '8765';
    const token = getToken();
    const wsUrl = `${protocol}//${host}:${port}/ws?token=${token}`;

    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = function() {
        isConnected = true;
        sessionInfo.textContent = 'ONLINE // SECURE';
        sessionInfo.style.color = '#00ff88';
        // Send explicit auth packet
        sendMsg('auth', { token: token });
      };

      ws.onmessage = function(evt) {
        try {
          const msg = JSON.parse(evt.data);
          handleMessage(msg);
        } catch (e) {
          console.error('Failed to parse WebSocket message', e);
        }
      };

      ws.onclose = function() {
        isConnected = false;
        sessionInfo.textContent = 'DISCONNECTED // RETRYING';
        sessionInfo.style.color = '#ff3366';
        setTimeout(connect, 3000);
      };

      ws.onerror = function() {
        if (ws) ws.close();
      };
    } catch (e) {
      setTimeout(connect, 3000);
    }
  }

  // Send message helper
  function sendMsg(type, payload = {}) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: type, ...payload }));
    }
  }

  // Dispatch message types
  function handleMessage(msg) {
    const type = msg.type;

    if (type === 'auth_ok') {
      sessionInfo.textContent = `AUTH OK [${msg.session_id || 'ID'}]`;
    } else if (type === 'auth_failed') {
      appendTranscript('SYSTEM', `Authentication failed: ${msg.reason}`, 'msg-system');
    } else if (type === 'transcript_update') {
      appendTranscript(msg.speaker || 'LAZY', msg.message, msg.speaker === 'USER' ? 'msg-user' : 'msg-lazy');
    } else if (type === 'plan_view') {
      renderPlan(msg.plan || {});
    } else if (type === 'step_update') {
      updateStepStatus(msg.step_index, msg.status);
    } else if (type === 'approval_request') {
      showApproval(msg);
    } else if (type === 'system_metric') {
      if (msg.cpu !== undefined) metricCpu.textContent = `${msg.cpu}%`;
      if (msg.ram !== undefined) metricRam.textContent = `${msg.ram} MB`;
      if (msg.model) metricModel.textContent = msg.model;
      if (msg.mode) metricMode.textContent = msg.mode;
    }
  }

  function appendTranscript(speaker, text, cssClass) {
    const now = new Date().toLocaleTimeString();
    const div = document.createElement('div');
    div.className = `message ${cssClass}`;
    div.innerHTML = `<span class="msg-ts">[${now}] ${speaker}:</span><span class="msg-body">${escapeHtml(text)}</span>`;
    transcriptFeed.appendChild(div);
    transcriptFeed.scrollTop = transcriptFeed.scrollHeight;
  }

  function renderPlan(plan) {
    planStatus.textContent = 'ACTIVE';
    planStatus.className = 'badge badge-safe';
    planRationale.textContent = plan.rationale || 'Executing directive...';
    stepsList.innerHTML = '';

    const steps = plan.steps || [];
    steps.forEach((step, idx) => {
      const card = document.createElement('div');
      card.className = 'step-card';
      card.id = `step-card-${idx}`;
      card.innerHTML = `
        <div class="step-header">
          <span>STEP ${idx + 1}</span>
          <span class="step-cap">${escapeHtml(step.capability || '')}</span>
        </div>
        <div class="step-params">${escapeHtml(JSON.stringify(step.params || {}))}</div>
      `;
      stepsList.appendChild(card);
    });
  }

  function updateStepStatus(idx, status) {
    const card = document.getElementById(`step-card-${idx}`);
    if (card) {
      card.className = `step-card ${status}`;
    }
  }

  function showApproval(appr) {
    activeApprovalId = appr.intent_id || appr.id;
    emptyApprovals.style.display = 'none';
    activeApproval.style.display = 'block';
    apprTier.textContent = `TIER ${appr.tier || 'L2'}`;
    apprCap.textContent = appr.capability || 'action';
    apprReason.textContent = appr.reason || 'Confirmation required.';
    apprDiffCode.textContent = JSON.stringify(appr.params || {}, null, 2);
  }

  function hideApproval() {
    activeApproval.style.display = 'none';
    emptyApprovals.style.display = 'block';
    activeApprovalId = null;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Event Listeners
  if (inputForm) {
    inputForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const val = userInput.value.trim();
      if (!val) return;
      appendTranscript('USER', val, 'msg-user');
      sendMsg('user_input', { text: val });
      userInput.value = '';
    });
  }

  if (btnApprove) {
    btnApprove.addEventListener('click', function() {
      sendMsg('approval_response', { intent_id: activeApprovalId, approved: true });
      hideApproval();
    });
  }

  if (btnDeny) {
    btnDeny.addEventListener('click', function() {
      sendMsg('approval_response', { intent_id: activeApprovalId, approved: false });
      hideApproval();
    });
  }

  // Initialize
  window.addEventListener('DOMContentLoaded', function() {
    triggerWakeAnimation(1500);
    connect();
  });
})();
