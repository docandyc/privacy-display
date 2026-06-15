(function attachStudyApp(global) {
  "use strict";

  const app = document.getElementById("app");
  const params = new URLSearchParams(global.location.search);
  const DEBUG = params.get("debug") === "1";
  const SELFTEST = params.get("selftest") === "1";
  const TRIAL_DURATION_S = DEBUG ? 5 : 20;
  const TARGET_CHARS = DEBUG ? 100 : 220;
  const ASSUMED_MONITOR_HZ = 240;
  const MIN_REFRESH_HZ = 144;
  // Subframe cycle (refresh / n) below this falls back to a static subframe.
  const SAFE_FLICKER_HZ = 50;
  // Number of distinct mask/noise/stripe cycles looped for the masked stimulus.
  // More cycles stop a long-exposure phone camera from integrating one
  // repeating pattern back into readable text.
  const ANTI_CAPTURE_CYCLES = 6;
  // Best anti-capture artefacts measured on a 240 Hz panel, equivalent to the
  // CLI `playback --anti-ocr-profile strong --stripe-alpha 0.10 --glyph-alpha 0.12`.
  const ANTI_OCR_STRONG = {
    stripeWidth: 10,
    stripeAlpha: 0.1,
    glyphAlpha: 0.12
  };
  // Subframe count that gives the best anti-capture strength (240 Hz panel).
  const MASKED_TARGET_N = 4;
  // Refresh needed to run the target n in temporal mode: n must satisfy
  // refresh / n >= SAFE_FLICKER_HZ, so the full-strength config needs
  // MASKED_TARGET_N * SAFE_FLICKER_HZ = 200 Hz.
  const TEMPORAL_MIN_REFRESH_HZ = MASKED_TARGET_N * SAFE_FLICKER_HZ;

  // Largest subframe count that still keeps the cycle (refresh / n) at or above
  // the flicker-fusion threshold, capped at the target. Below 200 Hz this drops
  // n to 2-3 so the masked trial stays temporal (and safe) instead of falling
  // back to a static, unprotected frame -- at the cost of weaker privacy.
  function maskedSubframeCount(refreshHz) {
    const hz = Number(refreshHz) || ASSUMED_MONITOR_HZ;
    const maxTemporalN = Math.floor(hz / SAFE_FLICKER_HZ);
    return Math.max(2, Math.min(MASKED_TARGET_N, maxTemporalN));
  }

  const STEPS = [
    ["welcome", "知情同意"],
    ["identity", "被试信息"],
    ["refresh", "刷新率检查"],
    ["typing", "打字试次"],
    ["ratings", "消融评分"],
    ["submit", "提交"]
  ];

  const CONDITIONS = [
    {
      id: "n2_mask_noise",
      label: "层数 2，遮罩 + 噪声",
      n: 2,
      components: "mask+noise",
      useNoise: true
    },
    {
      id: "n4_mask_noise",
      label: "层数 4，遮罩 + 噪声",
      n: 4,
      components: "mask+noise",
      useNoise: true
    },
    {
      id: "n8_mask_noise",
      label: "层数 8，遮罩 + 噪声",
      n: 8,
      components: "mask+noise",
      useNoise: true
    },
    {
      id: "n4_mask_only",
      label: "层数 4，仅遮罩",
      n: 4,
      components: "mask-only",
      useNoise: false
    }
  ];

  const state = {
    step: "welcome",
    startedAt: new Date().toISOString(),
    participant: {},
    refresh: {
      hz: null,
      samples: 0,
      mean_frame_ms: null,
      ok: false
    },
    seed: "",
    trials: [],
    trialCursor: 0,
    typing: [],
    ratingOrder: [],
    ratingCursor: 0,
    ratings: [],
    submitStatus: null
  };

  let currentPlayer = null;
  let activeTimer = null;
  let activeFinish = null;

  function cleanupTransientWork() {
    if (currentPlayer) {
      currentPlayer.stop();
      currentPlayer = null;
    }
    if (activeTimer) {
      global.clearInterval(activeTimer);
      activeTimer = null;
    }
    activeFinish = null;
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatNumber(value, digits) {
    if (!Number.isFinite(Number(value))) {
      return "-";
    }
    return Number(value).toFixed(digits);
  }

  function setStep(step) {
    state.step = step;
    cleanupTransientWork();
    render();
  }

  function stepIndex(step) {
    return STEPS.findIndex(([id]) => id === step);
  }

  function renderSidebar() {
    const activeIndex = stepIndex(state.step);
    const steps = STEPS.map(([id, label], index) => {
      const cls = index === activeIndex ? "active" : index < activeIndex ? "done" : "";
      const dot = index < activeIndex ? "✓" : index + 1;
      return `
        <div class="step ${cls}">
          <div class="step-dot">${dot}</div>
          <div>${label}</div>
        </div>
      `;
    }).join("");

    return `
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-mark">隐</div>
          <div>
            <div class="brand-title">隐私显示<br>用户研究</div>
            <div class="brand-subtitle">${ASSUMED_MONITOR_HZ} 赫兹 实验演示</div>
          </div>
        </div>
        <div class="steps">${steps}</div>
        <div class="sidebar-note">
          会话数据保存在本地研究服务器中。刷新率会作为分析协变量记录。
        </div>
      </aside>
    `;
  }

  function renderSidePanel() {
    const latestControl = state.typing.find((row) => row.condition === "control");
    const latestMasked = state.typing.find((row) => row.condition === "masked");
    const refreshLabel = state.refresh.hz
      ? `${formatNumber(state.refresh.hz, 1)} 赫兹`
      : "未检查";
    const refreshClass = state.refresh.hz
      ? (state.refresh.ok ? "pill-ok" : "pill-warn")
      : "";

    return `
      <aside class="side-panel">
        <section class="side-section">
          <h2 class="side-title">会话</h2>
          <div class="metric"><span>学号</span><strong>${escapeHtml(state.participant.student_id || "-")}</strong></div>
          <div class="metric"><span>姓名</span><strong>${escapeHtml(state.participant.name || "-")}</strong></div>
          <div class="metric"><span>刷新率</span><strong class="${refreshClass}">${refreshLabel}</strong></div>
          <div class="metric"><span>假定屏幕</span><strong>${ASSUMED_MONITOR_HZ} 赫兹</strong></div>
        </section>
        <section class="side-section">
          <h2 class="side-title">打字</h2>
          <div class="metric"><span>原文词速</span><strong>${latestControl ? formatNumber(latestControl.wpm, 1) : "-"}</strong></div>
          <div class="metric"><span>遮罩词速</span><strong>${latestMasked ? formatNumber(latestMasked.wpm, 1) : "-"}</strong></div>
          <div class="metric"><span>试次</span><strong>${state.typing.length}/2</strong></div>
        </section>
        <section class="side-section">
          <h2 class="side-title">评分</h2>
          <div class="metric"><span>已完成</span><strong>${state.ratings.length}/4</strong></div>
          <div class="metric"><span>时长</span><strong>${TRIAL_DURATION_S} 秒/次</strong></div>
        </section>
      </aside>
    `;
  }

  function shell(stageHtml) {
    app.innerHTML = `
      ${renderSidebar()}
      <main class="main">
        <section class="stage">${stageHtml}</section>
      </main>
      ${renderSidePanel()}
    `;
  }

  function renderHeader(title, copy, tag) {
    return `
      <div class="stage-header">
        <div>
          <h1 class="stage-title">${title}</h1>
          <p class="stage-copy">${copy}</p>
        </div>
        <div class="tag">${tag}</div>
      </div>
    `;
  }

  function renderWelcome() {
    shell(`
      ${renderHeader(
        "隐私显示用户研究",
        "本次会话会记录原文与遮罩文本的打字表现，以及 1 到 5 分的主观评分。",
        "第 1 步"
      )}
      <div class="warning">
        光敏安全提示：遮罩显示会使用快速时间闪烁。若出现不适、眼睛疲劳、头晕、恶心或头痛，请立即停止。
      </div>
      <label class="check-row">
        <input type="checkbox" id="consentCheck">
        <span>我已阅读提示，并同意参加本地研究会话。</span>
      </label>
      <div class="actions">
        <button class="button" id="continueWelcome" disabled>继续</button>
      </div>
    `);
    const check = document.getElementById("consentCheck");
    const button = document.getElementById("continueWelcome");
    check.addEventListener("change", () => {
      button.disabled = !check.checked;
    });
    button.addEventListener("click", () => setStep("identity"));
  }

  function renderIdentity() {
    shell(`
      ${renderHeader(
        "被试信息",
        "填写用于将研究记录与实验名单对应起来的信息。",
        "第 2 步"
      )}
      <form id="identityForm" class="form-grid">
        <div class="field">
          <label for="studentId">学号</label>
          <input id="studentId" name="student_id" autocomplete="off" required value="${escapeHtml(state.participant.student_id || "")}">
        </div>
        <div class="field">
          <label for="studentName">姓名</label>
          <input id="studentName" name="name" autocomplete="name" required value="${escapeHtml(state.participant.name || "")}">
        </div>
        <div class="field">
          <label for="glasses">视力矫正</label>
          <select id="glasses" name="glasses">
            <option value="">未填写</option>
            <option value="none">不戴眼镜 / 隐形眼镜</option>
            <option value="glasses">戴眼镜</option>
            <option value="contacts">戴隐形眼镜</option>
          </select>
        </div>
        <div class="field">
          <label for="major">专业或班级</label>
          <input id="major" name="major" autocomplete="off" value="${escapeHtml(state.participant.major || "")}">
        </div>
      </form>
      <div class="actions">
        <button class="button secondary" id="backIdentity">返回</button>
        <button class="button" form="identityForm">继续</button>
      </div>
    `);
    if (state.participant.glasses) {
      document.getElementById("glasses").value = state.participant.glasses;
    }
    document.getElementById("backIdentity").addEventListener("click", () => setStep("welcome"));
    document.getElementById("identityForm").addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(event.currentTarget);
      state.participant = {
        student_id: String(data.get("student_id") || "").trim(),
        name: String(data.get("name") || "").trim(),
        glasses: String(data.get("glasses") || "").trim(),
        major: String(data.get("major") || "").trim()
      };
      if (!state.participant.student_id || !state.participant.name) {
        return;
      }
      setStep("refresh");
    });
  }

  function renderRefresh() {
    const degraded = state.refresh.ok && state.refresh.hz < TEMPORAL_MIN_REFRESH_HZ;
    const plannedN = maskedSubframeCount(state.refresh.hz);
    const status = state.refresh.hz
      ? `${formatNumber(state.refresh.hz, 1)} 赫兹，来自 ${state.refresh.samples} 个动画帧样本`
      : "尚未测量";
    const detail = state.refresh.hz
      ? (state.refresh.ok
        ? (degraded
          ? `刷新率检查通过，但低于 ${TEMPORAL_MIN_REFRESH_HZ}Hz：遮罩条件会自动把子帧数从 ${MASKED_TARGET_N} 降到 ${plannedN} 层以避免闪烁，防偷拍效果明显变差。`
          : "刷新率检查通过，可进入时间遮罩条件。")
        : `刷新率低于技术交底书最低要求 ${MIN_REFRESH_HZ} 赫兹，不能开始测试。请切换到 144Hz 或更高的显示模式后重新检测。`)
      : "请先运行浏览器刷新率测量，再开始试次。";

    shell(`
      ${renderHeader(
        "刷新率检查",
        "遮罩播放由动画帧回调驱动，并跟随显示器的垂直同步节奏。",
        "第 3 步"
      )}
      <div class="score-grid">
        <div class="score-cell">
          <div class="score-value">${state.refresh.hz ? formatNumber(state.refresh.hz, 1) : "-"}</div>
          <div class="score-label">实测赫兹</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${ASSUMED_MONITOR_HZ}</div>
          <div class="score-label">假定实验赫兹</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${MIN_REFRESH_HZ}</div>
          <div class="score-label">最低接受赫兹</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${state.refresh.mean_frame_ms ? formatNumber(state.refresh.mean_frame_ms, 2) : "-"}</div>
          <div class="score-label">帧间隔毫秒</div>
        </div>
      </div>
      <div class="status-line ${state.refresh.hz && !state.refresh.ok ? "error" : ""}" id="refreshStatus">${status}. ${detail}</div>
      ${degraded ? `
      <div class="warning">
        低于 ${TEMPORAL_MIN_REFRESH_HZ}Hz：为避免闪烁与光敏风险，遮罩条件会自动降到 ${plannedN} 层子帧（最优为 ${ASSUMED_MONITOR_HZ}Hz 下的 ${MASKED_TARGET_N} 层），防偷拍效果明显变差；若刷新率过低仍无法满足安全频率，会退回单张静态帧（等同相机视图，无防偷拍）。建议切换到 ≥${TEMPORAL_MIN_REFRESH_HZ}Hz 的显示模式。
      </div>` : ""}
      <div class="actions">
        <button class="button secondary" id="backRefresh">返回</button>
        <button class="button secondary" id="runRefresh">重新检测</button>
        <button class="button" id="continueRefresh" ${state.refresh.ok ? "" : "disabled"}>开始试次</button>
      </div>
    `);

    document.getElementById("backRefresh").addEventListener("click", () => setStep("identity"));
    document.getElementById("continueRefresh").addEventListener("click", () => {
      if (!state.refresh.ok) {
        renderRefresh();
        return;
      }
      prepareExperiment();
      setStep("typing");
    });
    document.getElementById("runRefresh").addEventListener("click", async () => {
      const button = document.getElementById("runRefresh");
      const statusLine = document.getElementById("refreshStatus");
      button.disabled = true;
      statusLine.textContent = "正在测量显示节奏……";
      const result = await global.PrivacyMask.estimateRefreshRate(DEBUG ? 500 : 900);
      state.refresh = {
        hz: result.hz,
        samples: result.samples,
        mean_frame_ms: result.mean_frame_ms,
        ok: result.hz >= MIN_REFRESH_HZ
      };
      renderRefresh();
    });
  }

  // The masked trial targets n=4 (best anti-capture), but below 200 Hz that
  // would drop below the flicker-fusion threshold and fall back to a static,
  // unprotected frame. There we shrink n (to 2-3) so it stays temporal and
  // flicker-safe, recording both the requested and the effective n.
  function prepareExperiment() {
    if (state.trials.length) {
      return;
    }
    state.seed = [
      state.participant.student_id,
      state.participant.name,
      Date.now(),
      Math.round(state.refresh.hz || ASSUMED_MONITOR_HZ)
    ].join(":");

    const maskedN = maskedSubframeCount(state.refresh.hz);
    const pair = global.Pseudoword.makePair(state.seed, TARGET_CHARS);
    state.trials = [
      {
        condition: "control",
        label: "原文文本",
        n: 0,
        components: "none",
        target_text: pair.control,
        useNoise: false
      },
      {
        condition: "masked",
        label: "遮罩条件",
        n: maskedN,
        requested_n: MASKED_TARGET_N,
        components: "mask+noise+anti-ocr",
        target_text: pair.masked,
        useNoise: true,
        antiOcr: ANTI_OCR_STRONG
      }
    ];

    const rng = global.Pseudoword.createRng(`${state.seed}:rating-order`);
    state.ratingOrder = global.PrivacyMask.shuffle(CONDITIONS, rng);
  }

  function renderTyping() {
    const trial = state.trials[state.trialCursor];
    if (!trial) {
      setStep("ratings");
      return;
    }
    const isMasked = trial.condition === "masked";
    const degraded = isMasked && trial.n < (trial.requested_n || MASKED_TARGET_N);
    const progressLabel = `试次 ${state.trialCursor + 1} / ${state.trials.length}`;
    const stimulus = isMasked
      ? `
        ${degraded ? `
        <div class="warning">
          检测到刷新率 ${formatNumber(state.refresh.hz, 1)}Hz，低于 ${TEMPORAL_MIN_REFRESH_HZ}Hz：遮罩条件已自动把子帧数从 ${trial.requested_n} 降到 ${trial.n} 层以避免闪烁与光敏风险，防偷拍效果明显低于 ${ASSUMED_MONITOR_HZ}Hz 的最优配置。
        </div>` : ""}
        <div class="masked-canvas-wrap">
          <canvas id="maskedCanvas" class="masked-canvas"></canvas>
        </div>
      `
      : `<div id="plainTarget" class="text-target"></div>`;

    shell(`
      ${renderHeader(
        trial.label,
        "将可见文本输入到输入框中。计时结束后输入框会自动锁定。",
        progressLabel
      )}
      <div class="trial-layout">
        <div class="stimulus">
          <div class="stimulus-head">
            <span>${isMasked ? "遮罩源文本" : "原文源文本"}</span>
            <span>${isMasked ? `层数 ${trial.n}${degraded ? `（请求 ${trial.requested_n}）` : ""}，${trial.components}` : "无遮罩基线"}</span>
          </div>
          ${stimulus}
        </div>
        <div class="timer-row">
          <div class="timer" id="timerValue">${TRIAL_DURATION_S.toFixed(0)}秒</div>
          <div class="meter"><div class="meter-fill" id="timerFill"></div></div>
          <button class="button" id="startTrial">开始</button>
        </div>
        <textarea id="typingInput" class="typing-input" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" disabled></textarea>
        <div id="trialResult"></div>
      </div>
      <div class="actions">
        <button class="button secondary" id="backToRefresh" ${state.trialCursor === 0 ? "" : "disabled"}>返回</button>
        <button class="button secondary" id="debugFinish" style="${DEBUG ? "" : "display:none"}">结束试次</button>
      </div>
    `);

    if (isMasked) {
      const canvas = document.getElementById("maskedCanvas");
      currentPlayer = new global.PrivacyMask.MaskedPlayer(canvas);
      const meta = currentPlayer.load(trial.target_text, {
        n: trial.n,
        seed: `${state.seed}:${trial.condition}`,
        useNoise: trial.useNoise,
        width: 900,
        height: 260,
        epsilonPixels: 8,
        gammaFactor: 1.1,
        refreshHz: state.refresh.hz,
        safeFlickerHz: SAFE_FLICKER_HZ,
        // Anti-capture profile tuned on a 240 Hz panel: strong anti-OCR
        // artefacts (stripe 0.10 / glyph 0.12) over multiple mask cycles defeat
        // a real phone camera while staying readable to the eye.
        cycles: ANTI_CAPTURE_CYCLES,
        antiOcr: trial.antiOcr || null
      });
      trial.mask_meta = meta;
      currentPlayer.start();
      logSelftest(trial.condition, meta);
    } else {
      document.getElementById("plainTarget").textContent = trial.target_text;
    }

    document.getElementById("backToRefresh").addEventListener("click", () => setStep("refresh"));
    document.getElementById("startTrial").addEventListener("click", () => startTrial(trial));
    document.getElementById("debugFinish").addEventListener("click", () => {
      if (activeFinish) {
        activeFinish();
      }
    });
  }

  function startTrial(trial) {
    const input = document.getElementById("typingInput");
    const startButton = document.getElementById("startTrial");
    const timerValue = document.getElementById("timerValue");
    const fill = document.getElementById("timerFill");
    startButton.disabled = true;
    input.disabled = false;
    input.value = "";
    input.focus();

    const started = performance.now();
    let finished = false;

    activeFinish = () => {
      if (finished) {
        return;
      }
      finished = true;
      if (activeTimer) {
        global.clearInterval(activeTimer);
        activeTimer = null;
      }
      const elapsed = Math.min(TRIAL_DURATION_S, Math.max(1, (performance.now() - started) / 1000));
      input.disabled = true;
      const score = global.Typing.scoreTyping(trial.target_text, input.value, elapsed);
      const result = {
        condition: trial.condition,
        n: trial.n,
        requested_n: trial.requested_n || trial.n,
        components: trial.components,
        target_text: trial.target_text,
        typed_text: input.value,
        mask_meta: trial.mask_meta || null,
        ...score
      };
      state.typing.push(result);
      renderTrialResult(result);
    };

    activeTimer = global.setInterval(() => {
      const elapsed = (performance.now() - started) / 1000;
      const remaining = Math.max(0, TRIAL_DURATION_S - elapsed);
      const percent = Math.min(100, (elapsed / TRIAL_DURATION_S) * 100);
      timerValue.textContent = `${Math.ceil(remaining)}s`;
      fill.style.width = `${percent}%`;
      if (remaining <= 0) {
        activeFinish();
      }
    }, 100);
  }

  function renderTrialResult(result) {
    const container = document.getElementById("trialResult");
    container.innerHTML = `
      <div class="score-grid">
        <div class="score-cell">
          <div class="score-value">${formatNumber(result.wpm, 1)}</div>
          <div class="score-label">词/分</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${formatNumber(result.cpm, 0)}</div>
          <div class="score-label">正确字符/分钟</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${formatNumber(result.accuracy * 100, 1)}%</div>
          <div class="score-label">输入准确率</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${result.correct_chars}/${result.total_chars}</div>
          <div class="score-label">正确 / 目标</div>
        </div>
      </div>
      <div class="actions">
        <button class="button" id="nextTrial">${state.trialCursor + 1 < state.trials.length ? "下一试次" : "进入评分"}</button>
      </div>
    `;
    document.getElementById("nextTrial").addEventListener("click", () => {
      state.trialCursor += 1;
      if (state.trialCursor < state.trials.length) {
        renderTyping();
      } else {
        setStep("ratings");
      }
    });
  }

  function renderRatings() {
    const condition = state.ratingOrder[state.ratingCursor];
    if (!condition) {
      setStep("submit");
      return;
    }
    const displayN = condition.n;
    const text = global.Pseudoword.generateText(`${state.seed}:rating:${condition.id}`, 170);
    const orderLabel = `条件 ${state.ratingCursor + 1} / ${state.ratingOrder.length}`;

    shell(`
      ${renderHeader(
        "消融评分",
        "查看遮罩样本，并在每个 1 到 5 分量表上进行评分。",
        orderLabel
      )}
      <div class="stimulus">
        <div class="stimulus-head">
          <span>${escapeHtml(condition.label)}</span>
          <span>显示为层数 ${displayN}，${escapeHtml(condition.components)}</span>
        </div>
        <div class="masked-canvas-wrap">
          <canvas id="ratingCanvas" class="masked-canvas"></canvas>
        </div>
      </div>
      <form id="ratingForm" class="ratings">
        ${ratingGroup("readability", "可读性", "1 = 难以阅读，5 = 非常清晰")}
        ${ratingGroup("flicker", "闪烁感", "1 = 很强，5 = 几乎察觉不到")}
        ${ratingGroup("fatigue", "疲劳感", "1 = 很强，5 = 很舒适")}
        ${ratingGroup("privacy", "隐私感", "1 = 很弱，5 = 很强")}
      </form>
      <div class="actions">
        <button class="button" id="saveRating" disabled>${state.ratingCursor + 1 < state.ratingOrder.length ? "下一条件" : "查看提交"}</button>
      </div>
    `);

    const canvas = document.getElementById("ratingCanvas");
    currentPlayer = new global.PrivacyMask.MaskedPlayer(canvas);
    const meta = currentPlayer.load(text, {
      n: displayN,
      seed: `${state.seed}:rating:${condition.id}`,
      useNoise: condition.useNoise,
      width: 900,
      height: 230,
      epsilonPixels: 8,
      gammaFactor: 1.1,
      fontSize: 22,
      refreshHz: state.refresh.hz,
      safeFlickerHz: SAFE_FLICKER_HZ
    });
    currentPlayer.start();
    logSelftest(condition.id, meta);

    const form = document.getElementById("ratingForm");
    const button = document.getElementById("saveRating");
    form.addEventListener("change", () => {
      button.disabled = !["readability", "flicker", "fatigue", "privacy"].every((name) => {
        return form.querySelector(`input[name="${name}"]:checked`);
      });
    });
    button.addEventListener("click", () => {
      const data = new FormData(form);
      state.ratings.push({
        condition_label: condition.id,
        display_label: condition.label,
        n: displayN,
        requested_n: condition.n,
        components: condition.components,
        stimulus_text: text,
        readability: Number(data.get("readability")),
        flicker: Number(data.get("flicker")),
        fatigue: Number(data.get("fatigue")),
        privacy: Number(data.get("privacy")),
        order_index: state.ratingCursor,
        mask_meta: meta
      });
      state.ratingCursor += 1;
      renderRatings();
    });
  }

  function ratingGroup(name, title, hint) {
    const options = [1, 2, 3, 4, 5].map((value) => `
      <label>
        <input type="radio" name="${name}" value="${value}">
        ${value}
      </label>
    `).join("");
    return `
      <fieldset class="rating-group">
        <legend class="group-label">${title}</legend>
      <div class="status-line">${hint}</div>
        <div class="rating-options">${options}</div>
      </fieldset>
    `;
  }

  function renderSubmit() {
    const control = state.typing.find((row) => row.condition === "control");
    const masked = state.typing.find((row) => row.condition === "masked");
    const delta = control && masked ? masked.wpm - control.wpm : null;
    const status = state.submitStatus;
    shell(`
      ${renderHeader(
        "提交",
        "确认已收集的记录后，将本次会话写入本地数据库。",
        "最后一步"
      )}
      <div class="score-grid">
        <div class="score-cell">
          <div class="score-value">${control ? formatNumber(control.wpm, 1) : "-"}</div>
          <div class="score-label">原文词速</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${masked ? formatNumber(masked.wpm, 1) : "-"}</div>
          <div class="score-label">遮罩词速</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${delta === null ? "-" : formatNumber(delta, 1)}</div>
          <div class="score-label">遮罩减原文</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${state.ratings.length}/4</div>
          <div class="score-label">评分行数</div>
        </div>
      </div>
      <div id="submitMessage" class="status-line ${status && status.error ? "error" : ""}">
        ${status ? escapeHtml(status.message) : "已准备提交。"}
      </div>
      <div class="actions">
        <button class="button secondary" id="backSubmit">返回评分</button>
        <button class="button" id="submitStudy">提交会话</button>
      </div>
    `);
    document.getElementById("backSubmit").addEventListener("click", () => {
      state.step = "ratings";
      state.ratingCursor = Math.max(0, state.ratingOrder.length - 1);
      state.ratings.pop();
      renderRatings();
    });
    document.getElementById("submitStudy").addEventListener("click", submitStudy);
  }

  function buildPayload() {
    return {
      participant: state.participant,
      session: {
        started_at: state.startedAt,
        submitted_at: new Date().toISOString(),
        assumed_monitor_hz: ASSUMED_MONITOR_HZ,
        refresh_hz: state.refresh.hz,
        refresh_ok: state.refresh.ok,
        refresh_samples: state.refresh.samples,
        mean_frame_ms: state.refresh.mean_frame_ms,
        user_agent: navigator.userAgent,
        screen: {
          width: global.screen.width,
          height: global.screen.height,
          avail_width: global.screen.availWidth,
          avail_height: global.screen.availHeight,
          color_depth: global.screen.colorDepth,
          device_pixel_ratio: global.devicePixelRatio || 1
        },
        debug: DEBUG
      },
      typing: state.typing,
      ratings: state.ratings
    };
  }

  async function submitStudy() {
    const button = document.getElementById("submitStudy");
    const message = document.getElementById("submitMessage");
    button.disabled = true;
    message.classList.remove("error");
    message.textContent = "正在提交……";
    try {
      const response = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload())
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `请求失败 ${response.status}`);
      }
      state.submitStatus = {
        error: false,
        message: `已保存被试 #${data.participant_id}：${data.typing_rows} 条打字记录，${data.rating_rows} 条评分记录。`
      };
      renderComplete();
    } catch (error) {
      state.submitStatus = { error: true, message: error.message };
      message.classList.add("error");
      message.textContent = error.message;
      button.disabled = false;
    }
  }

  function renderComplete() {
    shell(`
      ${renderHeader(
        "会话已保存",
        "本地研究数据库中已写入该被试记录。",
        "完成"
      )}
      <div class="complete-mark">✓</div>
      <div class="status-line">${escapeHtml(state.submitStatus.message)}</div>
      <div class="actions">
        <button class="button" id="newSession">开始下一位被试</button>
      </div>
    `);
    document.getElementById("newSession").addEventListener("click", () => {
      global.location.href = global.location.pathname;
    });
  }

  function logSelftest(label, meta) {
    if (!SELFTEST || !meta) {
      return;
    }
    // eslint-disable-next-line no-console
    console.log("[privacy-display selftest]", label, {
      n: meta.n,
      mode: meta.mode,
      cycle_hz: meta.cycle_hz,
      refresh_hz: meta.refresh_hz,
      safe_flicker_hz: meta.safe_flicker_hz,
      completeness_ok: meta.completeness_ok,
      mask_pixels: meta.counts.reduce((sum, count) => sum + count, 0),
      noise_residual: meta.noise_residual,
      permutation: meta.permutation
    });
  }

  function render() {
    if (state.step === "welcome") {
      renderWelcome();
    } else if (state.step === "identity") {
      renderIdentity();
    } else if (state.step === "refresh") {
      renderRefresh();
    } else if (state.step === "typing") {
      renderTyping();
    } else if (state.step === "ratings") {
      renderRatings();
    } else if (state.step === "submit") {
      renderSubmit();
    }
  }

  render();
})(window);
