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
    return row && row.mask_meta ? fmt(row.mask_meta.cycle_hz, 1, " 赫兹") : "-";
  }

  async function loadData() {
    renderLoading();
    try {
      const response = await fetch(endpoint("/admin/data.json"), { headers: { "Accept": "application/json" } });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `请求失败 ${response.status}`);
      }
      renderDashboard(data);
    } catch (error) {
      renderError(error.message);
    }
  }

  function renderLoading() {
    root.innerHTML = `
      ${header("正在加载研究数据")}
      <section class="admin-panel">
        <p class="status-line">正在从研究服务器读取数据库数据……</p>
      </section>
    `;
    wireHeaderControls();
  }

  function renderError(message) {
    root.innerHTML = `
      ${header("研究后台")}
      <section class="admin-panel">
        <h2>数据不可用</h2>
        <p class="error">${escapeHtml(message)}</p>
        <p class="status-line">如果启用了导出保护，请输入与服务器环境一致的令牌。</p>
      </section>
    `;
    wireHeaderControls();
  }

  function header(title) {
    return `
      <header class="admin-header">
        <div>
          <h1>${escapeHtml(title)}</h1>
          <p>查看被试级结果、成对打字对比、评分以及导出数据。</p>
        </div>
        <div class="admin-actions">
          <input id="adminToken" type="password" placeholder="导出令牌" value="${escapeHtml(token)}">
          <button class="button secondary" id="saveToken">使用令牌</button>
          <button class="button secondary" id="refreshAdmin">刷新</button>
          <a class="button" href="${endpoint("/admin/export.csv")}">导出表格</a>
          <a class="button secondary" href="${endpoint("/admin/data.json")}">导出数据</a>
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
      ${header("研究后台")}
      <section class="admin-grid">
        ${statCard("被试人数", data.summary.participants, "已提交会话")}
        ${statCard("配对试次", paired.n_pairs || 0, "原文 + 遮罩")}
        ${statCard("原文词速", fmt(paired.control_wpm, 1), "配对均值")}
        ${statCard("遮罩词速", fmt(paired.masked_wpm, 1), "配对均值")}
        ${statCard("遮罩差值", `${fmt(paired.delta_wpm, 1)} / ${pct(paired.delta_pct)}`, "遮罩减原文")}
      </section>
      <section class="admin-panel">
        <div class="admin-panel-head">
          <h2>被试汇总</h2>
          <span>${escapeHtml(data.generated_at)}</span>
        </div>
        ${participantTable(data.participants)}
      </section>
      <section class="admin-panel">
        <div class="admin-panel-head">
          <h2>按条件统计的评分均值</h2>
        </div>
        ${ratingSummaryTable(data.summary.ratings || [])}
      </section>
      <details class="admin-panel" open>
        <summary>打字明细</summary>
        ${typingTable(data.typing)}
      </details>
      <details class="admin-panel">
        <summary>评分明细</summary>
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
      return `<p class="status-line">暂时没有提交记录。</p>`;
    }
    return `
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>编号</th><th>学号</th><th>姓名</th><th>刷新率</th><th>原文词速</th>
              <th>遮罩词速</th><th>差值</th><th>差值%</th><th>可读性</th>
              <th>闪烁感</th><th>疲劳感</th><th>隐私感</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map((row) => `
              <tr>
                <td>${row.participant_id}</td>
                <td>${escapeHtml(row.student_id)}</td>
                <td>${escapeHtml(row.name)}</td>
                <td>${fmt(row.refresh_hz, 1, " 赫兹")}${row.refresh_ok ? "" : " *"}</td>
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
      return `<p class="status-line">暂时没有评分记录。</p>`;
    }
    return `
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>条件</th><th>样本数</th><th>组件</th><th>行数</th>
              <th>可读性</th><th>闪烁感</th><th>疲劳感</th><th>隐私感</th>
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
      return `<p class="status-line">暂时没有打字记录。</p>`;
    }
    return `
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>被试</th><th>条件</th><th>样本数</th><th>模式</th><th>周期</th>
              <th>词/分</th><th>字/分</th><th>准确率</th><th>正确字符</th><th>时长</th>
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
      return `<p class="status-line">暂时没有评分记录。</p>`;
    }
    return `
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>被试</th><th>条件</th><th>样本数</th><th>模式</th><th>周期</th>
              <th>可读性</th><th>闪烁感</th><th>疲劳感</th><th>隐私感</th><th>顺序</th>
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
