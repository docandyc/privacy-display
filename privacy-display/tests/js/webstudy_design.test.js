"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");

const design = require("../../webstudy/static/design.js");

test("typing counterbalance alternates ABBA and BAAB", () => {
  assert.deepEqual(design.buildTypingSequence(0), ["control", "masked", "masked", "control"]);
  assert.deepEqual(design.buildTypingSequence(1), ["masked", "control", "control", "masked"]);
});

test("six Latin rows contain every condition and balance immediate predecessors", () => {
  const items = ["a", "b", "c", "d", "e", "f"];
  const rows = items.map((_, index) => design.balancedLatinOrder(items, index));
  for (const row of rows) {
    assert.deepEqual([...row].sort(), items);
  }
  assert.equal(new Set(rows.map((row) => row.join(""))).size, 6);

  const directedAdjacencies = new Map();
  for (const row of rows) {
    for (let index = 1; index < row.length; index += 1) {
      const pair = `${row[index - 1]}->${row[index]}`;
      directedAdjacencies.set(pair, (directedAdjacencies.get(pair) || 0) + 1);
    }
  }
  assert.equal(directedAdjacencies.size, 30);
  assert.deepEqual([...directedAdjacencies.values()], Array(30).fill(1));
});

test("registration index independently crosses typing order and Latin row", () => {
  const assignments = Array.from({ length: 24 }, (_, registrationIndex) =>
    design.assignmentForRegistrationIndex(registrationIndex, 6)
  );
  const pairCounts = new Map();

  for (const assignment of assignments) {
    const pair = `${assignment.typing_order_index}:${assignment.rating_order_index}`;
    pairCounts.set(pair, (pairCounts.get(pair) || 0) + 1);
  }

  assert.equal(pairCounts.size, 12);
  assert.deepEqual([...pairCounts.values()].sort(), Array(12).fill(2));
  assert.deepEqual(assignments[0], {
    registration_index: 0,
    typing_order_index: 0,
    rating_order_index: 0
  });
  assert.deepEqual(assignments[11], {
    registration_index: 11,
    typing_order_index: 1,
    rating_order_index: 5
  });
  assert.throws(() => design.assignmentForRegistrationIndex(-1, 6));
});
