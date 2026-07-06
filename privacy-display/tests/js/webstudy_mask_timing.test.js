"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");

global.window = global;
let scheduled = null;
global.requestAnimationFrame = (callback) => {
  scheduled = callback;
  return 1;
};
global.cancelAnimationFrame = () => {};
require("../../webstudy/static/mask.js");

test("MaskedPlayer records rAF intervals over 1.5 expected frames as drops", () => {
  const canvas = {
    getContext() {
      return { drawImage() {}, imageSmoothingEnabled: true };
    },
  };
  const player = new global.PrivacyMask.MaskedPlayer(canvas);
  player.frames = [{}];
  player.meta = { mode: "temporal", refresh_hz: 240, n: 4 };
  player.start();
  scheduled(0);
  scheduled(4.2);
  scheduled(12.5);
  const stats = player.getTimingStats();
  assert.equal(stats.dropped_frames, 1);
  assert.equal(stats.timing_intervals, 2);
  assert.ok(stats.observed_refresh_hz > 100);
  assert.ok(stats.observed_effective_cycle_hz > 25);
});

test("refresh estimator returns median and interval distribution metadata", async () => {
  const promise = global.PrivacyMask.estimateRefreshRate({ durationMs: 450, repeats: 3 });
  let settled = false;
  promise.then(() => {
    settled = true;
  });
  let timestamp = 0;
  for (let sample = 0; sample < 500 && !settled; sample += 1) {
    const callback = scheduled;
    timestamp += sample === 70 ? 20 : 4.1667;
    callback(timestamp);
    await Promise.resolve();
  }

  const result = await promise;

  assert.equal(result.repeats, 3);
  assert.equal(result.runs.length, 3);
  assert.ok(result.median_frame_ms > 4 && result.median_frame_ms < 5);
  assert.ok(Array.isArray(result.frame_ms_p95));
});
