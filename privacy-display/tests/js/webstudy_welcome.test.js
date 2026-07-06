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
