(function attachStudyDesign(root, factory) {
  "use strict";
  const api = factory();
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
  if (root) {
    root.StudyDesign = api;
  }
})(typeof window !== "undefined" ? window : globalThis, function buildStudyDesign() {
  "use strict";

  function buildTypingSequence(counterbalanceIndex) {
    return Number(counterbalanceIndex) % 2 === 0
      ? ["control", "masked", "masked", "control"]
      : ["masked", "control", "control", "masked"];
  }

  function balancedLatinOrder(items, rowIndex) {
    const values = Array.from(items || []);
    const n = values.length;
    if (!n || n % 2 !== 0) {
      throw new Error("balancedLatinOrder requires a non-empty even number of items");
    }
    const firstRow = [0];
    for (let offset = 1; firstRow.length < n; offset += 1) {
      firstRow.push(offset);
      if (firstRow.length < n) {
        firstRow.push(n - offset);
      }
    }
    const shift = ((Number(rowIndex) || 0) % n + n) % n;
    return firstRow.map((index) => values[(index + shift) % n]);
  }

  function assignmentForRegistrationIndex(registrationIndex, ratingRowCount) {
    const index = Number(registrationIndex);
    const rows = Number(ratingRowCount);
    if (!Number.isInteger(index) || index < 0) {
      throw new Error("registrationIndex must be a non-negative integer");
    }
    if (!Number.isInteger(rows) || rows < 1) {
      throw new Error("ratingRowCount must be a positive integer");
    }
    return {
      registration_index: index,
      typing_order_index: index % 2,
      rating_order_index: Math.floor(index / 2) % rows
    };
  }

  return {
    buildTypingSequence,
    balancedLatinOrder,
    assignmentForRegistrationIndex
  };
});
