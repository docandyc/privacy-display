(function attachStudyApp(global) {
  "use strict";

  const app = document.getElementById("app");
  const params = new URLSearchParams(global.location.search);
  const DEBUG = params.get("debug") === "1";
  const SELFTEST = params.get("selftest") === "1";
  const TRIAL_DURATION_S = DEBUG ? 5 : 20;
  const TARGET_CHARS = DEBUG ? 100 : 220;
  const ASSUMED_MONITOR_HZ = 240;
  const MIN_REFRESH_HZ = 100;

  const STEPS = [
    ["welcome", "Consent"],
    ["identity", "Participant"],
    ["refresh", "Refresh check"],
    ["typing", "Typing trial"],
    ["ratings", "Ablation ratings"],
    ["submit", "Submit"]
  ];

  const CONDITIONS = [
    {
      id: "n2_mask_noise",
      label: "n=2, mask + noise",
      n: 2,
      components: "mask+noise",
      useNoise: true
    },
    {
      id: "n4_mask_noise",
      label: "n=4, mask + noise",
      n: 4,
      components: "mask+noise",
      useNoise: true
    },
    {
      id: "n8_mask_noise",
      label: "n=8, mask + noise",
      n: 8,
      components: "mask+noise",
      useNoise: true
    },
    {
      id: "n4_mask_only",
      label: "n=4, mask only",
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
          <div class="brand-mark">PD</div>
          <div>
            <div class="brand-title">Privacy Display<br>User Study</div>
            <div class="brand-subtitle">${ASSUMED_MONITOR_HZ}Hz lab demo</div>
          </div>
        </div>
        <div class="steps">${steps}</div>
        <div class="sidebar-note">
          Session data is stored locally by the study server. Refresh rate is recorded as an analysis covariate.
        </div>
      </aside>
    `;
  }

  function renderSidePanel() {
    const latestControl = state.typing.find((row) => row.condition === "control");
    const latestMasked = state.typing.find((row) => row.condition === "masked");
    const refreshLabel = state.refresh.hz
      ? `${formatNumber(state.refresh.hz, 1)} Hz`
      : "not checked";
    const refreshClass = state.refresh.hz
      ? (state.refresh.ok ? "pill-ok" : "pill-warn")
      : "";

    return `
      <aside class="side-panel">
        <section class="side-section">
          <h2 class="side-title">Session</h2>
          <div class="metric"><span>Student ID</span><strong>${escapeHtml(state.participant.student_id || "-")}</strong></div>
          <div class="metric"><span>Name</span><strong>${escapeHtml(state.participant.name || "-")}</strong></div>
          <div class="metric"><span>Refresh</span><strong class="${refreshClass}">${refreshLabel}</strong></div>
          <div class="metric"><span>Assumed panel</span><strong>${ASSUMED_MONITOR_HZ} Hz</strong></div>
        </section>
        <section class="side-section">
          <h2 class="side-title">Typing</h2>
          <div class="metric"><span>Original WPM</span><strong>${latestControl ? formatNumber(latestControl.wpm, 1) : "-"}</strong></div>
          <div class="metric"><span>Masked WPM</span><strong>${latestMasked ? formatNumber(latestMasked.wpm, 1) : "-"}</strong></div>
          <div class="metric"><span>Trials</span><strong>${state.typing.length}/2</strong></div>
        </section>
        <section class="side-section">
          <h2 class="side-title">Ratings</h2>
          <div class="metric"><span>Completed</span><strong>${state.ratings.length}/4</strong></div>
          <div class="metric"><span>Duration</span><strong>${TRIAL_DURATION_S}s each</strong></div>
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
        "Privacy Display User Study",
        "This session records typing performance and 1-5 subjective ratings for original and masked text displays.",
        "Step 1"
      )}
      <div class="warning">
        Photosensitive safety notice: the masked display uses rapid temporal flicker. Stop immediately if you feel discomfort, eye strain, dizziness, nausea, or headache.
      </div>
      <label class="check-row">
        <input type="checkbox" id="consentCheck">
        <span>I have read the notice and agree to participate in this local study session.</span>
      </label>
      <div class="actions">
        <button class="button" id="continueWelcome" disabled>Continue</button>
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
        "Participant",
        "Enter the identifiers needed to match the study record with the experiment roster.",
        "Step 2"
      )}
      <form id="identityForm" class="form-grid">
        <div class="field">
          <label for="studentId">Student ID</label>
          <input id="studentId" name="student_id" autocomplete="off" required value="${escapeHtml(state.participant.student_id || "")}">
        </div>
        <div class="field">
          <label for="studentName">Name</label>
          <input id="studentName" name="name" autocomplete="name" required value="${escapeHtml(state.participant.name || "")}">
        </div>
        <div class="field">
          <label for="glasses">Vision correction</label>
          <select id="glasses" name="glasses">
            <option value="">Not specified</option>
            <option value="none">No glasses / contacts</option>
            <option value="glasses">Glasses</option>
            <option value="contacts">Contacts</option>
          </select>
        </div>
        <div class="field">
          <label for="major">Major or class</label>
          <input id="major" name="major" autocomplete="off" value="${escapeHtml(state.participant.major || "")}">
        </div>
      </form>
      <div class="actions">
        <button class="button secondary" id="backIdentity">Back</button>
        <button class="button" form="identityForm">Continue</button>
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
    const status = state.refresh.hz
      ? `${formatNumber(state.refresh.hz, 1)} Hz from ${state.refresh.samples} rAF samples`
      : "not measured";
    const detail = state.refresh.hz
      ? (state.refresh.ok
        ? "Refresh check passed for the temporal masking condition."
        : "Refresh is below the preferred threshold; this session will be flagged.")
      : "Run the browser refresh-rate measurement before starting the trials.";

    shell(`
      ${renderHeader(
        "Refresh check",
        "The masking playback is driven by requestAnimationFrame and follows the display vsync cadence.",
        "Step 3"
      )}
      <div class="score-grid">
        <div class="score-cell">
          <div class="score-value">${state.refresh.hz ? formatNumber(state.refresh.hz, 1) : "-"}</div>
          <div class="score-label">Measured Hz</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${ASSUMED_MONITOR_HZ}</div>
          <div class="score-label">Assumed lab Hz</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${MIN_REFRESH_HZ}</div>
          <div class="score-label">Minimum accepted Hz</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${state.refresh.mean_frame_ms ? formatNumber(state.refresh.mean_frame_ms, 2) : "-"}</div>
          <div class="score-label">Frame interval ms</div>
        </div>
      </div>
      <div class="status-line" id="refreshStatus">${status}. ${detail}</div>
      <div class="actions">
        <button class="button secondary" id="backRefresh">Back</button>
        <button class="button secondary" id="runRefresh">Run check</button>
        <button class="button" id="continueRefresh" ${state.refresh.hz ? "" : "disabled"}>Start trials</button>
      </div>
    `);

    document.getElementById("backRefresh").addEventListener("click", () => setStep("identity"));
    document.getElementById("continueRefresh").addEventListener("click", () => {
      prepareExperiment();
      setStep("typing");
    });
    document.getElementById("runRefresh").addEventListener("click", async () => {
      const button = document.getElementById("runRefresh");
      const statusLine = document.getElementById("refreshStatus");
      button.disabled = true;
      statusLine.textContent = "Measuring display cadence...";
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

  function effectiveN(n) {
    if (!state.refresh.hz || state.refresh.ok) {
      return n;
    }
    return Math.min(n, 2);
  }

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

    const pair = global.Pseudoword.makePair(state.seed, TARGET_CHARS);
    state.trials = [
      {
        condition: "control",
        label: "Original text",
        n: 0,
        components: "none",
        target_text: pair.control,
        useNoise: false
      },
      {
        condition: "masked",
        label: "Masked condition",
        n: effectiveN(4),
        requested_n: 4,
        components: "mask+noise",
        target_text: pair.masked,
        useNoise: true
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
    const progressLabel = `Trial ${state.trialCursor + 1} of ${state.trials.length}`;
    const stimulus = isMasked
      ? `
        <div class="masked-canvas-wrap">
          <canvas id="maskedCanvas" class="masked-canvas"></canvas>
        </div>
      `
      : `<div id="plainTarget" class="text-target"></div>`;

    shell(`
      ${renderHeader(
        trial.label,
        "Copy the visible source text into the input box. The input locks automatically when the timer ends.",
        progressLabel
      )}
      <div class="trial-layout">
        <div class="stimulus">
          <div class="stimulus-head">
            <span>${isMasked ? "Masked source text" : "Original source text"}</span>
            <span>${isMasked ? `n=${trial.n}, ${trial.components}` : "unmasked baseline"}</span>
          </div>
          ${stimulus}
        </div>
        <div class="timer-row">
          <div class="timer" id="timerValue">${TRIAL_DURATION_S.toFixed(0)}s</div>
          <div class="meter"><div class="meter-fill" id="timerFill"></div></div>
          <button class="button" id="startTrial">Start</button>
        </div>
        <textarea id="typingInput" class="typing-input" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" disabled></textarea>
        <div id="trialResult"></div>
      </div>
      <div class="actions">
        <button class="button secondary" id="backToRefresh" ${state.trialCursor === 0 ? "" : "disabled"}>Back</button>
        <button class="button secondary" id="debugFinish" style="${DEBUG ? "" : "display:none"}">End trial</button>
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
        gammaFactor: 1.1
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
          <div class="score-label">WPM</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${formatNumber(result.cpm, 0)}</div>
          <div class="score-label">Correct chars/min</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${formatNumber(result.accuracy * 100, 1)}%</div>
          <div class="score-label">Typed accuracy</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${result.correct_chars}/${result.total_chars}</div>
          <div class="score-label">Correct / target</div>
        </div>
      </div>
      <div class="actions">
        <button class="button" id="nextTrial">${state.trialCursor + 1 < state.trials.length ? "Next trial" : "Continue to ratings"}</button>
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
    const displayN = effectiveN(condition.n);
    const text = global.Pseudoword.generateText(`${state.seed}:rating:${condition.id}`, 170);
    const orderLabel = `Condition ${state.ratingCursor + 1} of ${state.ratingOrder.length}`;

    shell(`
      ${renderHeader(
        "Ablation ratings",
        "View the masked sample and rate the display on each 1-5 scale.",
        orderLabel
      )}
      <div class="stimulus">
        <div class="stimulus-head">
          <span>${escapeHtml(condition.label)}</span>
          <span>shown as n=${displayN}, ${escapeHtml(condition.components)}</span>
        </div>
        <div class="masked-canvas-wrap">
          <canvas id="ratingCanvas" class="masked-canvas"></canvas>
        </div>
      </div>
      <form id="ratingForm" class="ratings">
        ${ratingGroup("readability", "Readability", "1 = unreadable, 5 = very readable")}
        ${ratingGroup("flicker", "Flicker", "1 = severe, 5 = barely noticeable")}
        ${ratingGroup("fatigue", "Fatigue", "1 = severe, 5 = comfortable")}
        ${ratingGroup("privacy", "Privacy", "1 = weak, 5 = strong")}
      </form>
      <div class="actions">
        <button class="button" id="saveRating" disabled>${state.ratingCursor + 1 < state.ratingOrder.length ? "Next condition" : "Review submission"}</button>
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
      fontSize: 22
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
        "Submit",
        "Review the collected records, then write this session to the local SQLite database.",
        "Final step"
      )}
      <div class="score-grid">
        <div class="score-cell">
          <div class="score-value">${control ? formatNumber(control.wpm, 1) : "-"}</div>
          <div class="score-label">Original WPM</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${masked ? formatNumber(masked.wpm, 1) : "-"}</div>
          <div class="score-label">Masked WPM</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${delta === null ? "-" : formatNumber(delta, 1)}</div>
          <div class="score-label">Masked minus original</div>
        </div>
        <div class="score-cell">
          <div class="score-value">${state.ratings.length}/4</div>
          <div class="score-label">Rating rows</div>
        </div>
      </div>
      <div id="submitMessage" class="status-line ${status && status.error ? "error" : ""}">
        ${status ? escapeHtml(status.message) : "Ready to submit."}
      </div>
      <div class="actions">
        <button class="button secondary" id="backSubmit">Back to ratings</button>
        <button class="button" id="submitStudy">Submit session</button>
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
    message.textContent = "Submitting...";
    try {
      const response = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload())
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }
      state.submitStatus = {
        error: false,
        message: `Saved participant #${data.participant_id}: ${data.typing_rows} typing rows, ${data.rating_rows} rating rows.`
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
        "Session saved",
        "The local study database now contains this participant record.",
        "Complete"
      )}
      <div class="complete-mark">✓</div>
      <div class="status-line">${escapeHtml(state.submitStatus.message)}</div>
      <div class="actions">
        <button class="button" id="newSession">Start next participant</button>
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
