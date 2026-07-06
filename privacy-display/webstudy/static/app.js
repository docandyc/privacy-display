(function attachStudyApp(global) {
  "use strict";

  const app = document.getElementById("app");
  const params = new URLSearchParams(global.location.search);
  const DEBUG = params.get("debug") === "1";
  const DEMO = params.get("demo") === "1";
  const SELFTEST = params.get("selftest") === "1";
  const TRIAL_DURATION_S = DEBUG ? 5 : 20;
  const TRIAL_COUNTDOWN_S = 5;
  const WARMUP_DURATION_S = DEBUG ? 3 : 12;
  const MASKED_PREVIEW_DURATION_S = DEBUG ? 3 : 10;
  const RATING_MIN_VIEW_MS = DEBUG ? 1500 : 10000;
  const TARGET_CHARS = DEBUG ? 100 : 220;
  const ASSUMED_MONITOR_HZ = 240;
  const MIN_REFRESH_HZ = DEMO ? 144 : 200;
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
  // Weak inversion frame alpha*(255-I) per cycle, mirroring the playback config
  // `--inversion --inversion-alpha 0.2`. On a 240 Hz panel this makes the masked
  // cycle n+1=5 slots -> 48 Hz. The study records its perceived discomfort;
  // readability and comfort are not assumed in advance.
  const INSERT_INVERSION = true;
  const INVERSION_ALPHA = 0.2;
  // Subframe count that gives the best anti-capture strength (240 Hz panel).
  const MASKED_TARGET_N = 4;
  // Refresh needed to run the target n in temporal mode: n must satisfy
  // refresh / n >= SAFE_FLICKER_HZ, so the full-strength config needs
  // MASKED_TARGET_N * SAFE_FLICKER_HZ = 200 Hz.
  const TEMPORAL_MIN_REFRESH_HZ = MASKED_TARGET_N * SAFE_FLICKER_HZ;

  // Formal research sessions always use n=4 and require >=200 Hz. Only the
  // explicitly marked demo mode adapts n on 144-199 Hz displays.
  function maskedSubframeCount(refreshHz) {
    if (!DEMO) {
      return MASKED_TARGET_N;
    }
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
    ["submit", "完成测试"]
  ];

  const CONDITIONS = [
    {
      id: "control_anchor",
      label: "未遮罩原文（量表锚点）",
      n: 1,
      components: "none",
      sourceOnly: true,
      useNoise: false
    },
    {
      id: "n2_mask_noise",
      label: "层数 2，遮罩 + 噪声",
      n: 2,
      components: "mask+noise",
      useNoise: true
    },
    {
      id: "n3_mask_noise",
      label: "层数 3，遮罩 + 噪声",
      n: 3,
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
      id: "n4_mask_only",
      label: "层数 4，仅遮罩",
      n: 4,
      components: "mask-only",
      useNoise: false
    },
    {
      id: "deployed_full",
      label: "实际部署完整配置",
      n: 4,
      components: "mask+noise+anti-ocr+inversion",
      useNoise: true,
      antiOcr: ANTI_OCR_STRONG,
      insertInversion: INSERT_INVERSION,
      inversionAlpha: INVERSION_ALPHA
    }
  ];

  function createSessionUuid() {
    if (global.crypto && typeof global.crypto.randomUUID === "function") {
      return global.crypto.randomUUID();
    }
    const bytes = new Uint8Array(16);
    global.crypto.getRandomValues(bytes);
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    const hex = Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("");
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  }

  const state = {
    step: "welcome",
    sessionUuid: createSessionUuid(),
    startedAt: new Date().toISOString(),
    participant: {},
    refresh: {
      hz: null,
      samples: 0,
      mean_frame_ms: null,
      ok: false
    },
    seed: "",
    warmupTrial: null,
    warmupDone: false,
    maskedPreviewTrial: null,
    maskedPreviewDone: false,
    trials: [],
    trialCursor: 0,
    typing: [],
    ratingOrder: [],
    ratingCursor: 0,
    ratings: [],
    counterbalanceIndex: 0,
    ratingOrderIndex: 0,
    typingOrder: "",
    environmentConfirmed: false,
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
            <div class="brand-subtitle">${DEMO ? `${ASSUMED_MONITOR_HZ} 赫兹 演示模式` : `${ASSUMED_MONITOR_HZ} 赫兹 受控实验`}</div>
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
    const conditionMeanWpm = (condition) => {
      const rows = state.typing.filter((row) => row.condition === condition);
      return rows.length ? rows.reduce((sum, row) => sum + row.wpm, 0) / rows.length : null;
    };
    const latestControl = conditionMeanWpm("control");
    const latestMasked = conditionMeanWpm("masked");
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
          <div class="metric"><span>会话编号</span><strong>${escapeHtml((state.sessionUuid || "-").slice(0, 8))}</strong></div>
          <div class="metric"><span>视力矫正</span><strong>${escapeHtml(state.participant.glasses || "-")}</strong></div>
          <div class="metric"><span>刷新率</span><strong class="${refreshClass}">${refreshLabel}</strong></div>
          <div class="metric"><span>假定屏幕</span><strong>${ASSUMED_MONITOR_HZ} 赫兹</strong></div>
        </section>
        <section class="side-section">
          <h2 class="side-title">打字</h2>
          <div class="metric"><span>原文平均词速</span><strong>${latestControl !== null ? formatNumber(latestControl, 1) : "-"}</strong></div>
          <div class="metric"><span>遮罩平均词速</span><strong>${latestMasked !== null ? formatNumber(latestMasked, 1) : "-"}</strong></div>
          <div class="metric"><span>计分试次</span><strong>${state.typing.length}/4</strong></div>
        </section>
        <section class="side-section">
          <h2 class="side-title">评分</h2>
          <div class="metric"><span>已完成</span><strong>${state.ratings.length}/6</strong></div>
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
        <input type="checkbox" id="consentCheck" checked>
        <span>我已阅读研究说明，自愿参加，并知道可在任意时刻无条件退出。研究会采集身份、人口学、显示时序、打字与评分数据；学号和姓名仅用于参与管理，分析与发布只使用去标识化数据。</span>
      </label>
      <label class="check-row">
        <input type="checkbox" id="photosensitivityCheck" checked>
        <span>我确认没有光敏性癫痫病史，也不属于对闪烁刺激敏感的人群。</span>
      </label>
      <div class="actions">
        <button class="button" id="continueWelcome">继续</button>
      </div>
    `);
    const check = document.getElementById("consentCheck");
    const photosensitivity = document.getElementById("photosensitivityCheck");
    const button = document.getElementById("continueWelcome");
    check.defaultChecked = true;
    check.checked = true;
    photosensitivity.defaultChecked = true;
    photosensitivity.checked = true;
    const updateConsent = () => {
      button.disabled = !(check.checked && photosensitivity.checked);
    };
    check.addEventListener("change", updateConsent);
    photosensitivity.addEventListener("change", updateConsent);
    updateConsent();
    button.addEventListener("click", () => {
      state.participant.consent_confirmed = true;
      state.participant.photosensitivity_screen_passed = true;
      state.participant.consented_at = new Date().toISOString();
      setStep("identity");
    });
  }

  function renderIdentity() {
    shell(`
      ${renderHeader(
        "被试信息",
        "只需要一项视力矫正信息，用于分析与视觉条件相关的差异。",
        "第 2 步"
      )}
      <form id="identityForm" class="form-grid">
        <div class="field">
          <label for="glasses">视力矫正</label>
          <select id="glasses" name="glasses">
            <option value="">未填写</option>
            <option value="none">不戴眼镜 / 隐形眼镜</option>
            <option value="glasses">戴眼镜</option>
            <option value="contacts">戴隐形眼镜</option>
          </select>
        </div>
      </form>
      <div id="identityStatus" class="status-line"></div>
      <div class="actions">
        <button class="button secondary" id="backIdentity">返回</button>
        <button class="button" id="continueIdentity" form="identityForm">继续</button>
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
        ...state.participant,
        glasses: String(data.get("glasses") || "").trim()
      };
      setStep("refresh");
    });
  }

  function renderRefresh() {
    const degraded = DEMO && state.refresh.ok && state.refresh.hz < TEMPORAL_MIN_REFRESH_HZ;
    const plannedN = maskedSubframeCount(state.refresh.hz);
    const status = state.refresh.hz
      ? `${formatNumber(state.refresh.hz, 1)} 赫兹，来自 ${state.refresh.samples} 个动画帧样本`
      : "尚未测量";
    const detail = state.refresh.hz
      ? (state.refresh.ok
        ? (degraded
          ? `演示模式已通过 ${MIN_REFRESH_HZ}Hz 门槛，但会把子帧数从 ${MASKED_TARGET_N} 降到 ${plannedN}；该会话不会进入正式统计。`
          : "刷新率检查通过，可进入固定 n=4 的正式时间遮罩条件。")
        : `刷新率低于本模式最低要求 ${MIN_REFRESH_HZ} 赫兹，不能开始测试。${DEMO ? "" : "正式研究要求实测刷新率至少 200Hz，不会自动降低 n。"}`)
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
      ${DEMO ? `<div class="warning">当前为演示模式（demo=1）；允许 144–199Hz 自适应播放，但提交会被标记为 demo，默认统计与导出会排除。</div>` : ""}
      <label class="check-row">
        <input type="checkbox" id="environmentCheck" ${state.environmentConfirmed ? "checked" : ""}>
        <span>实验员已确认：显示器亮度固定、自动亮度与省电模式关闭、浏览器全屏、观看距离约 60cm。</span>
      </label>
      <div class="actions">
        <button class="button secondary" id="backRefresh">返回</button>
        <button class="button secondary" id="runRefresh">重新检测</button>
        <button class="button" id="continueRefresh" ${state.refresh.ok && state.environmentConfirmed ? "" : "disabled"}>开始试次</button>
      </div>
    `);

    document.getElementById("backRefresh").addEventListener("click", () => setStep("identity"));
    document.getElementById("environmentCheck").addEventListener("change", (event) => {
      state.environmentConfirmed = event.currentTarget.checked;
      document.getElementById("continueRefresh").disabled = !(state.refresh.ok && state.environmentConfirmed);
    });
    document.getElementById("continueRefresh").addEventListener("click", () => {
      if (!state.refresh.ok || !state.environmentConfirmed) {
        renderRefresh();
        return;
      }
      resetExperimentPlan();
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
      resetExperimentPlan();
      renderRefresh();
    });
  }

  function resetExperimentPlan() {
    state.seed = "";
    state.warmupTrial = null;
    state.warmupDone = false;
    state.maskedPreviewTrial = null;
    state.maskedPreviewDone = false;
    state.trials = [];
    state.trialCursor = 0;
    state.typing = [];
    state.ratingOrder = [];
    state.ratingCursor = 0;
    state.ratings = [];
  }

  function prepareExperiment() {
    state.seed = [
      state.sessionUuid,
      Math.round(state.refresh.hz || ASSUMED_MONITOR_HZ)
    ].join(":");

    const maskedN = maskedSubframeCount(state.refresh.hz);
    const assignment = global.StudyDesign.assignmentForSessionUuid(state.sessionUuid, CONDITIONS.length);
    state.counterbalanceIndex = assignment.typing_order_index;
    state.ratingOrderIndex = assignment.rating_order_index;
    const sequence = global.StudyDesign.buildTypingSequence(state.counterbalanceIndex);
    state.typingOrder = sequence.map((condition) => condition === "control" ? "A" : "B").join("");
    const repetitions = { control: 0, masked: 0 };
    state.warmupTrial = {
      condition: "warmup",
      label: "热身试次（不计分）",
      n: 1,
      requested_n: 1,
      components: "none",
      target_text: global.Pseudoword.generateText(`${state.seed}:warmup`, TARGET_CHARS),
      useNoise: false,
      duration_s: WARMUP_DURATION_S
    };
    state.maskedPreviewTrial = {
      condition: "masked_preview",
      label: "遮罩预览（不计分）",
      n: maskedN,
      requested_n: MASKED_TARGET_N,
      components: "mask+noise+anti-ocr+inversion",
      target_text: global.Pseudoword.generateText(`${state.seed}:masked-preview`, TARGET_CHARS),
      useNoise: true,
      antiOcr: ANTI_OCR_STRONG,
      insertInversion: INSERT_INVERSION,
      inversionAlpha: INVERSION_ALPHA,
      duration_s: MASKED_PREVIEW_DURATION_S
    };
    state.trials = sequence.map((condition, trialIndex) => {
      repetitions[condition] += 1;
      const repetition = repetitions[condition];
      const pair = global.Pseudoword.makePair(`${state.seed}:pair:${repetition}`, TARGET_CHARS);
      const isMasked = condition === "masked";
      return {
        condition,
        label: isMasked ? "遮罩条件" : "原文条件",
        trial_index: trialIndex,
        condition_repetition: repetition,
        n: isMasked ? maskedN : 1,
        requested_n: isMasked ? MASKED_TARGET_N : 1,
        components: isMasked ? "mask+noise+anti-ocr+inversion" : "none",
        target_text: pair[condition],
        useNoise: isMasked,
        antiOcr: isMasked ? ANTI_OCR_STRONG : null,
        insertInversion: isMasked && INSERT_INVERSION,
        inversionAlpha: isMasked ? INVERSION_ALPHA : null,
        duration_s: TRIAL_DURATION_S
      };
    });
    state.ratingOrder = global.StudyDesign.balancedLatinOrder(CONDITIONS, state.ratingOrderIndex);
  }

  function renderTyping() {
    cleanupTransientWork();
    if (state.warmupDone && !state.maskedPreviewDone) {
      renderMaskedPreview();
      return;
    }
    const isWarmup = !state.warmupDone;
    const trial = isWarmup ? state.warmupTrial : state.trials[state.trialCursor];
    if (!trial) {
      setStep("ratings");
      return;
    }
    const isMasked = trial.condition === "masked";
    const degraded = isMasked && trial.n < (trial.requested_n || MASKED_TARGET_N);
    const slotsPerCycle = trial.n + (isMasked && trial.insertInversion ? 1 : 0);
    const inversionFlicker = isMasked && trial.insertInversion && state.refresh.hz > 0
      && state.refresh.hz / slotsPerCycle < SAFE_FLICKER_HZ;
    const progressLabel = isWarmup
      ? `热身 ${WARMUP_DURATION_S} 秒（不计分）`
      : `计分试次 ${state.trialCursor + 1} / ${state.trials.length} · ${state.typingOrder}`;
    const warnings = isMasked
      ? `
        ${degraded ? `
        <div class="warning">
          检测到刷新率 ${formatNumber(state.refresh.hz, 1)}Hz，低于 ${TEMPORAL_MIN_REFRESH_HZ}Hz：遮罩条件已自动把子帧数从 ${trial.requested_n} 降到 ${trial.n} 层以避免闪烁与光敏风险，防偷拍效果明显低于 ${ASSUMED_MONITOR_HZ}Hz 的最优配置。
        </div>` : ""}
        ${inversionFlicker ? `
        <div class="warning">
          已叠加弱反色帧（α=${INVERSION_ALPHA}）：每周期 ${slotsPerCycle} 帧使完整周期率降至 ${formatNumber(state.refresh.hz / slotsPerCycle, 1)}Hz，可能产生可感闪烁；若不适请立即停止。
        </div>` : ""}
      ` : "";

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
          ${warnings}
          <div class="masked-canvas-wrap">
            <canvas id="stimulusCanvas" class="masked-canvas"></canvas>
          </div>
        </div>
        <div class="timer-row">
          <div class="timer" id="timerValue">${trial.duration_s.toFixed(0)}秒</div>
          <div class="meter"><div class="meter-fill" id="timerFill"></div></div>
          <button class="button" id="startTrial">开始</button>
        </div>
        <div class="countdown" id="trialCountdown" hidden>
          <span>准备输入</span>
          <strong id="countdownValue">${TRIAL_COUNTDOWN_S}</strong>
        </div>
        <textarea id="typingInput" class="typing-input" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" disabled></textarea>
        <div id="trialResult"></div>
      </div>
      <div class="actions">
        <button class="button secondary" id="backToRefresh" ${state.trialCursor === 0 ? "" : "disabled"}>返回</button>
        <button class="button secondary" id="debugFinish" style="${DEBUG ? "" : "display:none"}">结束试次</button>
      </div>
    `);

    const canvas = document.getElementById("stimulusCanvas");
    currentPlayer = new global.PrivacyMask.MaskedPlayer(canvas);
    const playerOptions = {
      width: 900,
      height: 260,
      fontSize: 23,
      refreshHz: state.refresh.hz,
      safeFlickerHz: SAFE_FLICKER_HZ
    };
    if (isMasked) {
      trial.mask_meta = currentPlayer.load(trial.target_text, {
        ...playerOptions,
        n: trial.n,
        seed: `${state.seed}:${trial.condition}:${trial.condition_repetition}`,
        useNoise: trial.useNoise,
        epsilonPixels: 8,
        gammaFactor: 1.1,
        // Anti-capture profile tuned on a 240 Hz panel: strong anti-OCR
        // artefacts (stripe 0.10 / glyph 0.12) over multiple mask cycles defeat
        // a real phone camera while staying readable to the eye.
        cycles: ANTI_CAPTURE_CYCLES,
        antiOcr: trial.antiOcr || null,
        insertInversion: trial.insertInversion || false,
        inversionAlpha: trial.inversionAlpha || INVERSION_ALPHA
      });
    } else {
      trial.mask_meta = currentPlayer.loadSource(trial.target_text, playerOptions);
    }
    currentPlayer.start();
    logSelftest(trial.condition, trial.mask_meta);

    document.getElementById("backToRefresh").addEventListener("click", () => setStep("refresh"));
    document.getElementById("startTrial").addEventListener("click", () => startTrial(trial, isWarmup));
    document.getElementById("debugFinish").addEventListener("click", () => {
      if (activeFinish) {
        activeFinish();
      }
    });
  }

  function startTrial(trial, isWarmup) {
    const input = document.getElementById("typingInput");
    input.addEventListener("paste", (event) => {
      event.preventDefault();
    });
    const startButton = document.getElementById("startTrial");
    const timerValue = document.getElementById("timerValue");
    const fill = document.getElementById("timerFill");
    const countdown = document.getElementById("trialCountdown");
    const countdownValue = document.getElementById("countdownValue");
    startButton.disabled = true;
    input.disabled = true;
    input.value = "";
    let firstKeyAt = null;
    let finished = false;
    input.addEventListener("input", () => {
      if (firstKeyAt === null && input.value.length > 0) {
        firstKeyAt = performance.now();
      }
    });

    const beginTimedTyping = () => {
      if (finished) {
        return;
      }
      countdown.hidden = true;
      input.disabled = false;
      input.focus();
      if (currentPlayer) {
        currentPlayer.resetTimingStats();
      }

      const started = performance.now();
      activeFinish = () => {
        if (finished) {
          return;
        }
        finished = true;
        if (activeTimer) {
          global.clearInterval(activeTimer);
          activeTimer = null;
        }
        const elapsed = Math.min(trial.duration_s, Math.max(1, (performance.now() - started) / 1000));
        input.disabled = true;
        const timingMeta = currentPlayer ? { ...currentPlayer.getTimingStats() } : (trial.mask_meta || null);
        if (isWarmup) {
          state.warmupDone = true;
          renderWarmupResult();
          return;
        }
        const score = global.Typing.scoreTyping(trial.target_text, input.value, elapsed);
        const result = {
          condition: trial.condition,
          trial_index: trial.trial_index,
          condition_repetition: trial.condition_repetition,
          n: trial.n,
          requested_n: trial.requested_n || trial.n,
          components: trial.components,
          target_text: trial.target_text,
          typed_text: input.value,
          first_key_latency_ms: firstKeyAt === null ? null : firstKeyAt - started,
          mask_meta: timingMeta,
          ...score
        };
        state.typing.push(result);
        renderTrialResult(result);
      };

      activeTimer = global.setInterval(() => {
        const elapsed = (performance.now() - started) / 1000;
        const remaining = Math.max(0, trial.duration_s - elapsed);
        const percent = Math.min(100, (elapsed / trial.duration_s) * 100);
        timerValue.textContent = `${Math.ceil(remaining)}s`;
        fill.style.width = `${percent}%`;
        if (remaining <= 0) {
          activeFinish();
        }
      }, 100);
    };

    countdown.hidden = false;
    let remaining = TRIAL_COUNTDOWN_S;
    countdownValue.textContent = String(remaining);
    timerValue.textContent = "准备";
    fill.style.width = "0%";
    activeTimer = global.setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        global.clearInterval(activeTimer);
        activeTimer = null;
        beginTimedTyping();
        return;
      }
      countdownValue.textContent = String(remaining);
    }, 1000);
  }

  function renderWarmupResult() {
    const container = document.getElementById("trialResult");
    container.innerHTML = `
      <div class="status-line">无遮罩热身完成。本段输入不计分；下面先观看一次 ${MASKED_PREVIEW_DURATION_S} 秒遮罩预览，再开始正式试次。</div>
      <div class="actions"><button class="button" id="nextTrial">进入遮罩预览</button></div>
    `;
    document.getElementById("nextTrial").addEventListener("click", renderTyping);
  }

  function renderMaskedPreview() {
    const trial = state.maskedPreviewTrial;
    shell(`
      ${renderHeader(
        trial.label,
        "请先熟悉正式遮罩的外观与闪烁感。本段不要求输入，也不会计分。",
        `${MASKED_PREVIEW_DURATION_S} 秒预览`
      )}
      <div class="trial-layout">
        <div class="stimulus">
          <div class="stimulus-head">
            <span>完整部署遮罩</span>
            <span>层数 ${trial.n}，${trial.components}</span>
          </div>
          <div class="masked-canvas-wrap">
            <canvas id="stimulusCanvas" class="masked-canvas" hidden></canvas>
          </div>
        </div>
        <div class="timer-row">
          <div class="timer" id="timerValue">${trial.duration_s.toFixed(0)}秒</div>
          <div class="meter"><div class="meter-fill" id="timerFill"></div></div>
          <button class="button" id="startPreview">开始预览</button>
        </div>
        <div id="trialResult"></div>
      </div>
      <div class="actions">
        <button class="button secondary" id="debugFinishPreview" style="${DEBUG ? "" : "display:none"}">结束预览</button>
      </div>
    `);

    const canvas = document.getElementById("stimulusCanvas");
    currentPlayer = new global.PrivacyMask.MaskedPlayer(canvas);
    trial.mask_meta = currentPlayer.load(trial.target_text, {
      width: 900,
      height: 260,
      fontSize: 23,
      refreshHz: state.refresh.hz,
      safeFlickerHz: SAFE_FLICKER_HZ,
      n: trial.n,
      seed: `${state.seed}:masked-preview`,
      useNoise: trial.useNoise,
      epsilonPixels: 8,
      gammaFactor: 1.1,
      cycles: ANTI_CAPTURE_CYCLES,
      antiOcr: trial.antiOcr,
      insertInversion: trial.insertInversion,
      inversionAlpha: trial.inversionAlpha
    });
    logSelftest(trial.condition, trial.mask_meta);

    const startButton = document.getElementById("startPreview");
    const timerValue = document.getElementById("timerValue");
    const fill = document.getElementById("timerFill");
    startButton.addEventListener("click", () => {
      startButton.disabled = true;
      canvas.hidden = false;
      currentPlayer.start();
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
        if (currentPlayer) {
          currentPlayer.stop();
        }
        state.maskedPreviewDone = true;
        document.getElementById("trialResult").innerHTML = `
          <div class="status-line">遮罩预览完成。下面开始四个正式计分试次。</div>
          <div class="actions"><button class="button" id="nextTrial">开始正式试次</button></div>
        `;
        document.getElementById("nextTrial").addEventListener("click", renderTyping);
      };
      activeTimer = global.setInterval(() => {
        const elapsed = (performance.now() - started) / 1000;
        const remaining = Math.max(0, trial.duration_s - elapsed);
        timerValue.textContent = `${Math.ceil(remaining)}s`;
        fill.style.width = `${Math.min(100, (elapsed / trial.duration_s) * 100)}%`;
        if (remaining <= 0) {
          activeFinish();
        }
      }, 100);
    });
    document.getElementById("debugFinishPreview").addEventListener("click", () => {
      if (activeFinish) {
        activeFinish();
      }
    });
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
    cleanupTransientWork();
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
        `请至少观看 ${(RATING_MIN_VIEW_MS / 1000).toFixed(0)} 秒，再完成每个 1 到 5 分量表。`,
        orderLabel
      )}
      <div class="stimulus">
        <div class="stimulus-head">
          <span>${escapeHtml(condition.label)}</span>
          <span>${condition.sourceOnly ? "n=1 未遮罩 Canvas" : `显示为层数 ${displayN}，${escapeHtml(condition.components)}`}</span>
        </div>
        <div class="masked-canvas-wrap">
          <canvas id="ratingCanvas" class="masked-canvas"></canvas>
        </div>
      </div>
      <form id="ratingForm" class="ratings">
        ${ratingGroup("readability", "可读性", "1 = 难以阅读，5 = 非常清晰")}
        ${ratingGroup("flicker", "闪烁感", "1 = 很强，5 = 几乎察觉不到")}
        ${ratingGroup("fatigue", "即时视觉不适感", "1 = 很不适，5 = 很舒适")}
        ${ratingGroup("privacy", "防偷看效果", "1 = 旁人很容易看清，5 = 旁人几乎看不清")}
      </form>
      <div class="actions">
        <span class="status-line" id="viewGateStatus">请继续观看…</span>
        <button class="button" id="saveRating" disabled>${state.ratingCursor + 1 < state.ratingOrder.length ? "下一条件" : "查看提交"}</button>
      </div>
    `);

    const canvas = document.getElementById("ratingCanvas");
    currentPlayer = new global.PrivacyMask.MaskedPlayer(canvas);
    const playerOptions = {
      width: 900,
      height: 230,
      fontSize: 22,
      refreshHz: state.refresh.hz,
      safeFlickerHz: SAFE_FLICKER_HZ
    };
    const meta = condition.sourceOnly
      ? currentPlayer.loadSource(text, playerOptions)
      : currentPlayer.load(text, {
        ...playerOptions,
        n: displayN,
        seed: `${state.seed}:rating:${condition.id}`,
        useNoise: condition.useNoise,
        epsilonPixels: 8,
        gammaFactor: 1.1,
        cycles: condition.id === "deployed_full" ? ANTI_CAPTURE_CYCLES : 1,
        antiOcr: condition.antiOcr || null,
        insertInversion: condition.insertInversion || false,
        inversionAlpha: condition.inversionAlpha || INVERSION_ALPHA
      });
    currentPlayer.start();
    logSelftest(condition.id, meta);

    const form = document.getElementById("ratingForm");
    const button = document.getElementById("saveRating");
    const gateStatus = document.getElementById("viewGateStatus");
    const viewStartedAt = new Date().toISOString();
    const viewStartedPerformance = performance.now();
    const allRated = () => ["readability", "flicker", "fatigue", "privacy"].every((name) => {
        return form.querySelector(`input[name="${name}"]:checked`);
    });
    const updateRatingGate = () => {
      const elapsed = performance.now() - viewStartedPerformance;
      const remaining = Math.max(0, RATING_MIN_VIEW_MS - elapsed);
      gateStatus.textContent = remaining > 0
        ? `至少再观看 ${(remaining / 1000).toFixed(1)} 秒`
        : (allRated() ? "观看时长与评分均已完成" : "观看时长已满足，请完成四项评分");
      button.disabled = remaining > 0 || !allRated();
    };
    form.addEventListener("change", updateRatingGate);
    activeTimer = global.setInterval(updateRatingGate, 100);
    updateRatingGate();
    button.addEventListener("click", () => {
      const data = new FormData(form);
      const viewDurationMs = Math.round(performance.now() - viewStartedPerformance);
      const timingMeta = currentPlayer ? { ...currentPlayer.getTimingStats() } : meta;
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
        view_duration_ms: viewDurationMs,
        view_started_at: viewStartedAt,
        view_submitted_at: new Date().toISOString(),
        mask_meta: timingMeta
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
    const meanWpm = (condition) => {
      const rows = state.typing.filter((row) => row.condition === condition);
      return rows.length ? rows.reduce((sum, row) => sum + row.wpm, 0) / rows.length : null;
    };
    const control = meanWpm("control");
    const masked = meanWpm("masked");
    const delta = control !== null && masked !== null ? masked - control : null;
    const status = state.submitStatus;
    shell(`
      ${renderHeader(
        "完成测试",
        "确认已收集的记录后，将本次会话写入本地数据库。",
        "最后一步"
      )}
      <div class="score-grid">
        <div class="score-cell">
          <div class="score-value">${control !== null ? formatNumber(control, 1) : "-"}</div>
          <div class="score-label">原文词速</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${masked !== null ? formatNumber(masked, 1) : "-"}</div>
          <div class="score-label">遮罩词速</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${delta === null ? "-" : formatNumber(delta, 1)}</div>
          <div class="score-label">遮罩减原文</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${state.ratings.length}/6</div>
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
        session_uuid: state.sessionUuid,
        registration_index: -1,
        started_at: state.startedAt,
        submitted_at: new Date().toISOString(),
        assumed_monitor_hz: ASSUMED_MONITOR_HZ,
        refresh_hz: state.refresh.hz,
        refresh_ok: state.refresh.ok,
        refresh_samples: state.refresh.samples,
        mean_frame_ms: state.refresh.mean_frame_ms,
        typing_order: state.typingOrder,
        counterbalance_index: state.counterbalanceIndex,
        rating_order_index: state.ratingOrderIndex,
        environment_confirmed: state.environmentConfirmed,
        user_agent: navigator.userAgent,
        screen: {
          width: global.screen.width,
          height: global.screen.height,
          avail_width: global.screen.availWidth,
          avail_height: global.screen.availHeight,
          color_depth: global.screen.colorDepth,
          device_pixel_ratio: global.devicePixelRatio || 1
        },
        demo: DEMO,
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
      mask_pixels: (meta.counts || []).reduce((sum, count) => sum + count, 0),
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
