(function attachPseudoword(global) {
  "use strict";

  const CONSONANTS = "bdfgklmnprstvwz".split("");
  const VOWELS = "aeiou".split("");
  const BLOCKED = new Set([
    "data", "demo", "file", "line", "mine", "more", "name", "note",
    "time", "tone", "word", "zero", "solo", "mama", "papa"
  ]);
  const UINT32_SPACE = 0x100000000;

  function hashString(value) {
    let h = 2166136261 >>> 0;
    const text = String(value);
    for (let i = 0; i < text.length; i += 1) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h >>> 0;
  }

  function createRng(seed) {
    let state = hashString(seed) || 0x6d2b79f5;
    return function nextUint32() {
      state = (state + 0x6d2b79f5) >>> 0;
      let t = state;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return (t ^ (t >>> 14)) >>> 0;
    };
  }

  function uniformInt(rng, upperExclusive) {
    if (!Number.isInteger(upperExclusive) || upperExclusive <= 0) {
      throw new Error("upperExclusive must be a positive integer");
    }
    const limit = UINT32_SPACE - (UINT32_SPACE % upperExclusive);
    let value = rng();
    while (value >= limit) {
      value = rng();
    }
    return value % upperExclusive;
  }

  function makeWord(rng) {
    const length = 4 + uniformInt(rng, 4);
    let word = "";
    let consonantTurn = uniformInt(rng, 2) === 0;
    while (word.length < length) {
      const source = consonantTurn ? CONSONANTS : VOWELS;
      word += source[uniformInt(rng, source.length)];
      consonantTurn = !consonantTurn;
    }
    if (BLOCKED.has(word)) {
      return makeWord(rng);
    }
    return word;
  }

  function generateText(seed, targetChars) {
    const rng = createRng(seed);
    const words = [];
    const target = Math.max(80, Number(targetChars) || 220);
    while (words.join(" ").length < target) {
      words.push(makeWord(rng));
    }
    return words.join(" ").slice(0, target).trim();
  }

  function makePair(seed, targetChars) {
    return {
      control: generateText(`${seed}:control`, targetChars),
      masked: generateText(`${seed}:masked`, targetChars)
    };
  }

  global.Pseudoword = {
    createRng,
    uniformInt,
    generateText,
    makePair
  };
})(window);
