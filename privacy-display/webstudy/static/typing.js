(function attachTyping(global) {
  "use strict";

  function scoreTyping(targetText, typedText, durationS) {
    const target = String(targetText || "");
    const typed = String(typedText || "");
    const duration = Math.max(1, Number(durationS) || 20);
    const comparable = Math.min(target.length, typed.length);
    let correctChars = 0;
    let correctLetters = 0;
    let attemptedLetters = 0;

    for (let i = 0; i < typed.length; i += 1) {
      if (typed[i] !== " ") {
        attemptedLetters += 1;
      }
    }

    for (let i = 0; i < comparable; i += 1) {
      if (typed[i] === target[i]) {
        correctChars += 1;
        if (target[i] !== " ") {
          correctLetters += 1;
        }
      }
    }

    const attemptedChars = typed.length;
    const accuracy = attemptedChars > 0 ? correctChars / attemptedChars : 0;
    const minutes = duration / 60;

    return {
      correct_chars: correctChars,
      correct_letters: correctLetters,
      attempted_chars: attemptedChars,
      attempted_letters: attemptedLetters,
      total_chars: target.length,
      accuracy,
      cpm: correctChars / minutes,
      wpm: (correctChars / 5) / minutes,
      duration_s: duration
    };
  }

  function formatNumber(value, digits) {
    if (!Number.isFinite(value)) {
      return "-";
    }
    return Number(value).toFixed(digits);
  }

  global.Typing = {
    scoreTyping,
    formatNumber
  };
})(window);
