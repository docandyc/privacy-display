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
