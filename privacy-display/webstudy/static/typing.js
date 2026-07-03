(function attachTyping(global) {
  "use strict";

  function alignToTargetPrefix(targetText, typedText) {
    const target = String(targetText || "");
    const typed = String(typedText || "");
    if (typed.length === 0) {
      return {
        edit_distance: target.length > 0 ? 1 : 0,
        aligned_target_chars: target.length > 0 ? 1 : 0,
        correct_chars: 0,
        correct_letters: 0,
        msd_error_rate: target.length > 0 ? 1 : 0,
        accuracy: 0
      };
    }
    const rows = target.length + 1;
    const cols = typed.length + 1;
    const distance = Array.from({ length: rows }, () => new Uint16Array(cols));

    for (let i = 0; i < rows; i += 1) {
      distance[i][0] = i;
    }
    for (let j = 0; j < cols; j += 1) {
      distance[0][j] = j;
    }
    for (let i = 1; i < rows; i += 1) {
      for (let j = 1; j < cols; j += 1) {
        const substitution = distance[i - 1][j - 1] + (target[i - 1] === typed[j - 1] ? 0 : 1);
        const deletion = distance[i - 1][j] + 1;
        const insertion = distance[i][j - 1] + 1;
        distance[i][j] = Math.min(substitution, deletion, insertion);
      }
    }

    let targetPrefixLength = 0;
    let editDistance = distance[0][typed.length];
    for (let i = 1; i < rows; i += 1) {
      const candidate = distance[i][typed.length];
      const candidateGap = Math.abs(i - typed.length);
      const currentGap = Math.abs(targetPrefixLength - typed.length);
      if (candidate < editDistance || (candidate === editDistance && candidateGap < currentGap)) {
        editDistance = candidate;
        targetPrefixLength = i;
      }
    }

    let i = targetPrefixLength;
    let j = typed.length;
    let matches = 0;
    let matchingLetters = 0;
    while (i > 0 || j > 0) {
      if (i > 0 && j > 0) {
        const substitutionCost = target[i - 1] === typed[j - 1] ? 0 : 1;
        if (distance[i][j] === distance[i - 1][j - 1] + substitutionCost) {
          if (substitutionCost === 0) {
            matches += 1;
            if (target[i - 1] !== " ") {
              matchingLetters += 1;
            }
          }
          i -= 1;
          j -= 1;
          continue;
        }
      }
      if (i > 0 && distance[i][j] === distance[i - 1][j] + 1) {
        i -= 1;
      } else {
        j -= 1;
      }
    }
    const denominator = Math.max(targetPrefixLength, typed.length, 1);
    return {
      edit_distance: editDistance,
      aligned_target_chars: targetPrefixLength,
      correct_chars: matches,
      correct_letters: matchingLetters,
      msd_error_rate: editDistance / denominator,
      accuracy: Math.max(0, 1 - editDistance / denominator)
    };
  }

  function scoreTyping(targetText, typedText, durationS) {
    const target = String(targetText || "");
    const typed = String(typedText || "");
    const duration = Math.max(1, Number(durationS) || 20);
    const alignment = alignToTargetPrefix(target, typed);
    let attemptedLetters = 0;

    for (let i = 0; i < typed.length; i += 1) {
      if (typed[i] !== " ") {
        attemptedLetters += 1;
      }
    }

    const attemptedChars = typed.length;
    const minutes = duration / 60;

    return {
      ...alignment,
      attempted_chars: attemptedChars,
      attempted_letters: attemptedLetters,
      total_chars: target.length,
      cpm: alignment.correct_chars / minutes,
      wpm: (alignment.correct_chars / 5) / minutes,
      duration_s: duration,
      scoring_method: "msd_target_prefix_v1"
    };
  }

  function formatNumber(value, digits) {
    if (!Number.isFinite(value)) {
      return "-";
    }
    return Number(value).toFixed(digits);
  }

  global.Typing = {
    alignToTargetPrefix,
    scoreTyping,
    formatNumber
  };
})(window);
