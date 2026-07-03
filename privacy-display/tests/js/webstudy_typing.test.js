"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");

global.window = global;
require("../../webstudy/static/typing.js");

test("MSD prefix alignment tolerates one omitted character", () => {
  const score = global.Typing.scoreTyping("hello world", "helo world", 60);
  assert.equal(score.edit_distance, 1);
  assert.equal(score.aligned_target_chars, 11);
  assert.equal(score.correct_chars, 10);
  assert.ok(score.accuracy > 0.9);
  assert.equal(score.scoring_method, "msd_target_prefix_v1");
});

test("MSD prefix alignment tolerates one inserted character", () => {
  const score = global.Typing.scoreTyping("hello world", "hellxo world", 60);
  assert.equal(score.edit_distance, 1);
  assert.equal(score.correct_chars, 11);
  assert.ok(score.accuracy > 0.9);
});

test("empty input is zero accuracy rather than perfect accuracy", () => {
  const score = global.Typing.scoreTyping("hello world", "", 20);
  assert.equal(score.attempted_chars, 0);
  assert.equal(score.correct_chars, 0);
  assert.equal(score.accuracy, 0);
  assert.equal(score.msd_error_rate, 1);
});
