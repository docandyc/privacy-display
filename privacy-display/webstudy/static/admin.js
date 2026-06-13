(function attachAdmin(global) {
  "use strict";

  const root = document.getElementById("adminApp");
  const params = new URLSearchParams(global.location.search);
  let token = params.get("token") || global.localStorage.getItem("webstudyAdminToken") || "";

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function endpoint(path) {
    if (!token) {
      return path;
    }
    return `${path}?token=${encodeURIComponent(token)}`;
  }

  function fmt(value, digits = 1, suffix = "") {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "-";
    }
    return `${Number(value).toFixed(digits)}${suffix}`;
  }

  function pct(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "-";
    }
    return `${(Number(value) * 100).toFixed(1)}%`;
  }

  function maskMode(row) {
    return row && row.mask_meta ? (row.mask_meta.mode || "-") : "-";
  }

  function cycleHz(row) {
    return row && row.mask_meta ? fmt(row.mask_meta.cycle_hz, 1, " Hz") : "-";
  }

  async function loadData() {
    renderLoading();
    try {
      const response = await fetch(endpoint("/admin/data.json"), { headers: { "Accept": "application/json" } });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }
      renderDashboard(data);
    } catch (error) {
      renderError(error.message);
    }
  }

  function renderLoading() {
    root.innerHTML = `
      ${header("Loading study data")}
      <section class="admin-panel">
        <p class="status-line">Reading SQLite rows from the study server...</p>
      </section>
    `;
    wireHeaderControls();
  }

  function renderError(message) {
    root.innerHTML = `
      ${header("Study Admin")}
      <section class="admin-panel">
        <h2>Data unavailable</h2>
        <p class="error">${escapeHtml(message)}</p>
        <p class="status-line">If export protection is enabled, enter the same token used in the server environment.</p>
      </section>
    `;
    wireHeaderControls();
  }

  function header(title) {
    return `
      <header class="admin-header">
        <div>
          <h1>${escapeHtml(title)}</h1>
          <p>Participant-level results, paired typing comparison, ratings, and exports.</p>
        </div>
        <div class="admin-actions">
          <input id="adminToken" type="password" placeholder="Export token" value="${escapeHtml(token)}">
          <button class="button secondary" id="saveToken">Use token</button>
          <button class="button secondary" id="refreshAdmin">Refresh</button>
          <a class="button" href="${endpoint("/admin/export.csv")}">Export CSV</a>
          <a class="button secondary" href="${endpoint("/admin/data.json")}">Export JSON</a>
        </div>
      </header>
    `;
  }

  function wireHeaderControls() {
    const tokenInput = document.getElementById("adminToken");
    document.getElementById("saveToken").addEventListener("click", () => {
      token = tokenInput.value.trim();
      if (token) {
        global.localStorage.setItem("webstudyAdminToken", token);
      } else {
        global.localStorage.removeItem("webstudyAdminToken");
      }
      loadData();
    });
    document.getElementById("refreshAdmin").addEventListener("click", loadData);
  }

  function renderDashboard(data) {
    const paired = data.summary.paired_typing || {};
    root.innerHTML = `
      ${header("Study Admin")}
      <section class="admin-grid">
        ${statCard("Participants", data.summary.participants, "submitted sessions")}
        ${statCard("Paired trials", paired.n_pairs || 0, "control + masked")}
        ${statCard("Original WPM", fmt(paired.control_wpm, 1), "paired mean")}
        ${statCard("Masked WPM", fmt(paired.masked_wpm, 1), "paired mean")}
        ${statCard("Masked delta", `${fmt(paired.delta_wpm, 1)} / ${pct(paired.delta_pct)}`, "masked minus original")}
      </section>
      <section class="admin-panel">
        <div class="admin-panel-head">
          <h2>Participant Summary</h2>
          <span>${escapeHtml(data.generated_at)}</span>
        </div>
        ${participantTable(data.participants)}
      </section>
      <section class="admin-panel">
        <div class="admin-panel-head">
          <h2>Rating Means By Condition</h2>
        </div>
        ${ratingSummaryTable(data.summary.ratings || [])}
      </section>
      <details class="admin-panel" open>
        <summary>Typing Rows</summary>
        ${typingTable(data.typing)}
      </details>
      <details class="admin-panel">
        <summary>Rating Rows</summary>
        ${ratingRowsTable(data.ratings)}
      </details>
    `;
    wireHeaderControls();
  }

  function statCard(valueLabel, value, label) {
    return `
      <div class="admin-stat">
        <div class="score-value">${escapeHtml(value)}</div>
        <div class="score-label">${escapeHtml(valueLabel)} · ${escapeHtml(label)}</div>
      </div>
    `;
  }

  function participantTable(rows) {
    if (!rows.length) {
      return `<p class="status-line">No submissions yet.</p>`;
    }
    return `
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th><th>Student</th><th>Name</th><th>Refresh</th><th>Original WPM</th>
              <th>Masked WPM</th><th>Delta</th><th>Delta %</th><th>Readability</th>
              <th>Flicker</th><th>Fatigue</th><th>Privacy</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map((row) => `
              <tr>
                <td>${row.participant_id}</td>
                <td>${escapeHtml(row.student_id)}</td>
                <td>${escapeHtml(row.name)}</td>
                <td>${fmt(row.refresh_hz, 1, " Hz")}${row.refresh_ok ? "" : " *"}</td>
                <td>${fmt(row.control_wpm, 1)}</td>
                <td>${fmt(row.masked_wpm, 1)}</td>
                <td>${fmt(row.delta_wpm, 1)}</td>
                <td>${pct(row.delta_pct)}</td>
                <td>${fmt(row.mean_readability, 2)}</td>
                <td>${fmt(row.mean_flicker, 2)}</td>
                <td>${fmt(row.mean_fatigue, 2)}</td>
                <td>${fmt(row.mean_privacy, 2)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  function ratingSummaryTable(rows) {
    if (!rows.length) {
      return `<p class="status-line">No rating rows yet.</p>`;
    }
    return `
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Condition</th><th>n</th><th>Components</th><th>Rows</th>
              <th>Readability</th><th>Flicker</th><th>Fatigue</th><th>Privacy</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map((row) => `
              <tr>
                <td>${escapeHtml(row.condition_label)}</td>
                <td>${row.n}</td>
                <td>${escapeHtml(row.components)}</td>
                <td>${row.n_rows}</td>
                <td>${fmt(row.readability, 2)}</td>
                <td>${fmt(row.flicker, 2)}</td>
                <td>${fmt(row.fatigue, 2)}</td>
                <td>${fmt(row.privacy, 2)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  function typingTable(rows) {
    if (!rows.length) {
      return `<p class="status-line">No typing rows yet.</p>`;
    }
    return `
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Participant</th><th>Condition</th><th>n</th><th>Mode</th><th>Cycle</th>
              <th>WPM</th><th>CPM</th><th>Accuracy</th><th>Correct</th><th>Duration</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map((row) => `
              <tr>
                <td>${escapeHtml(row.student_id)} · ${escapeHtml(row.name)}</td>
                <td>${escapeHtml(row.condition)}</td>
                <td>${row.n}</td>
                <td>${escapeHtml(maskMode(row))}</td>
                <td>${cycleHz(row)}</td>
                <td>${fmt(row.wpm, 1)}</td>
                <td>${fmt(row.cpm, 0)}</td>
                <td>${pct(row.accuracy)}</td>
                <td>${row.correct_chars}/${row.total_chars}</td>
                <td>${fmt(row.duration_s, 1, "s")}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  function ratingRowsTable(rows) {
    if (!rows.length) {
      return `<p class="status-line">No rating rows yet.</p>`;
    }
    return `
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Participant</th><th>Condition</th><th>n</th><th>Mode</th><th>Cycle</th>
              <th>Readability</th><th>Flicker</th><th>Fatigue</th><th>Privacy</th><th>Order</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map((row) => `
              <tr>
                <td>${escapeHtml(row.student_id)} · ${escapeHtml(row.name)}</td>
                <td>${escapeHtml(row.condition_label)}</td>
                <td>${row.n}</td>
                <td>${escapeHtml(maskMode(row))}</td>
                <td>${cycleHz(row)}</td>
                <td>${row.readability}</td>
                <td>${row.flicker}</td>
                <td>${row.fatigue}</td>
                <td>${row.privacy}</td>
                <td>${row.order_index + 1}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  loadData();
})(window);
