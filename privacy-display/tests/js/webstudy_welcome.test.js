"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { join } = require("node:path");
const test = require("node:test");

const appJs = readFileSync(join(__dirname, "../../webstudy/static/app.js"), "utf8");
const styleCss = readFileSync(join(__dirname, "../../webstudy/static/style.css"), "utf8");

function elementMarkup(tag, id) {
  const pattern = new RegExp(`<${tag}[^>]*id="${id}"[^>]*>`);
  const match = appJs.match(pattern);
  assert.ok(match, `${id} ${tag} is rendered`);
  return match[0];
}

test("welcome page starts with both safety confirmations checked", () => {
  assert.match(elementMarkup("input", "consentCheck"), /\bchecked\b/);
  assert.match(elementMarkup("input", "photosensitivityCheck"), /\bchecked\b/);
  assert.match(appJs, /check\.defaultChecked = true;\s*check\.checked = true;/);
  assert.match(appJs, /photosensitivity\.defaultChecked = true;\s*photosensitivity\.checked = true;/);
});

test("welcome safety confirmations use visible custom checkmarks", () => {
  assert.match(appJs, /<span class="check-box" aria-hidden="true"><\/span>/);
  assert.match(styleCss, /\.check-row input:checked \+ \.check-box::after\s*\{[^}]*content: "✓";/s);
  assert.match(styleCss, /\.check-box\s*\{[^}]*width: 24px;[^}]*height: 24px;/s);
});

test("welcome continue button is synchronized from checkbox state", () => {
  assert.doesNotMatch(elementMarkup("button", "continueWelcome"), /\bdisabled\b/);
  assert.match(appJs, /const updateConsent = \(\) => \{\s*button\.disabled = !\(check\.checked && photosensitivity\.checked\);\s*\};/);
  assert.match(appJs, /photosensitivity\.addEventListener\("change", updateConsent\);\s*updateConsent\(\);/);
});

test("typing trials count down before accepting input", () => {
  assert.match(appJs, /const TRIAL_COUNTDOWN_S = 5;/);
  assert.match(appJs, /id="countdownValue"/);
  assert.match(appJs, /countdownValue\.textContent = String\(remaining\);/);
  assert.match(appJs, /input\.disabled = true;/);
  assert.match(appJs, /beginTimedTyping\(\);/);
});

test("refresh check can continue immediately after a passing measurement", () => {
  assert.match(appJs, /environmentConfirmed: true,/);
  assert.match(appJs, /id="environmentCheck"[^>]*checked/);
  assert.match(appJs, /<input type="checkbox" id="environmentCheck"[^>]*>\s*<span class="check-box" aria-hidden="true"><\/span>/);
  assert.match(appJs, /id="continueRefresh" \$\{state\.refresh\.ok && state\.environmentConfirmed \? "" : "disabled"\}/);
});

test("formal identity requires vision correction and fetches server assignment", () => {
  assert.match(elementMarkup("select", "glasses"), /\brequired\b/);
  assert.match(appJs, /if \(!state\.participant\.glasses\)/);
  assert.match(appJs, /fetch\("\/api\/next-assignment"/);
  assert.match(appJs, /state\.assignment = data\.assignment;/);
  assert.doesNotMatch(appJs, /assignmentForSessionUuid\(state\.sessionUuid/);
});

test("masked preview is followed by an unscored masked typing practice", () => {
  assert.match(appJs, /const MASKED_PRACTICE_DURATION_S = DEBUG \? 3 : 8;/);
  assert.match(appJs, /maskedPracticeTrial: null,/);
  assert.match(appJs, /state\.maskedPracticeDone = true;/);
  assert.match(appJs, /遮罩练习/);
});

test("rating labels and submit backtracking avoid silent data loss", () => {
  assert.match(appJs, /ratingGroup\("flicker", "稳定感", "1 = 闪烁很强，5 = 几乎察觉不到"\)/);
  assert.match(appJs, /confirm\("返回评分会删除最后一条评分并重新填写，是否继续？"\)/);
});

test("completion screen includes debriefing and session state is recoverable", () => {
  assert.match(appJs, /sessionStorage/);
  assert.match(appJs, /研究目的/);
  assert.match(appJs, /撤回/);
});
