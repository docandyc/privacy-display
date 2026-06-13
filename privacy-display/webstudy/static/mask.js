(function attachPrivacyMask(global) {
  "use strict";

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
    let state = hashString(seed) || 0x9e3779b9;
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

  function shuffle(values, rng) {
    const out = values.slice();
    for (let i = out.length - 1; i > 0; i -= 1) {
      const j = uniformInt(rng, i + 1);
      const tmp = out[i];
      out[i] = out[j];
      out[j] = tmp;
    }
    return out;
  }

  function wrapWords(ctx, text, maxWidth) {
    const words = String(text).split(/\s+/).filter(Boolean);
    const lines = [];
    let line = "";
    for (const word of words) {
      const candidate = line ? `${line} ${word}` : word;
      if (ctx.measureText(candidate).width <= maxWidth || !line) {
        line = candidate;
      } else {
        lines.push(line);
        line = word;
      }
    }
    if (line) {
      lines.push(line);
    }
    return lines;
  }

  function renderSourceCanvas(text, options) {
    const width = options.width || 900;
    const height = options.height || 260;
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.fillStyle = "#0c1117";
    ctx.fillRect(0, 0, width, height);

    const fontSize = options.fontSize || 23;
    const lineHeight = Math.round(fontSize * 1.48);
    ctx.font = `700 ${fontSize}px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`;
    ctx.fillStyle = "#edf7f8";
    ctx.textBaseline = "top";

    const margin = 22;
    const lines = wrapWords(ctx, text, width - margin * 2);
    let y = margin;
    for (const line of lines) {
      if (y + lineHeight > height - margin) {
        break;
      }
      ctx.fillText(line, margin, y);
      y += lineHeight;
    }
    return canvas;
  }

  function buildIndexMatrix(pixelCount, n, seed) {
    const rng = createRng(`${seed}:mask`);
    const indices = new Uint8Array(pixelCount);
    const counts = Array.from({ length: n }, () => 0);
    for (let i = 0; i < pixelCount; i += 1) {
      const k = uniformInt(rng, n);
      indices[i] = k;
      counts[k] += 1;
    }
    return { indices, counts };
  }

  function computeNoiseBase(imageData, epsilonPixels, seed) {
    const { width, height, data } = imageData;
    const gray = new Float32Array(width * height);
    for (let p = 0; p < gray.length; p += 1) {
      const i = p * 4;
      gray[p] = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
    }

    const noise = new Float32Array(width * height * 3);
    const rng = createRng(`${seed}:noise`);
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const p = y * width + x;
        const left = gray[y * width + Math.max(0, x - 1)];
        const right = gray[y * width + Math.min(width - 1, x + 1)];
        const up = gray[Math.max(0, y - 1) * width + x];
        const down = gray[Math.min(height - 1, y + 1) * width + x];
        const gx = right - left;
        const gy = down - up;
        const texture = ((x * 37 + y * 17 + uniformInt(rng, 31)) % 31) - 15;
        const strokeEnergy = Math.abs(gx) + Math.abs(gy);
        const direction = gx + gy + texture >= 0 ? 1 : -1;
        const scale = strokeEnergy > 4 ? 1 : 0.35;
        const value = direction * epsilonPixels * scale;
        const j = p * 3;
        noise[j] = value;
        noise[j + 1] = value * 0.92;
        noise[j + 2] = value * 1.08;
      }
    }
    return noise;
  }

  function splitComplementary(noiseBase, n) {
    const subNoises = Array.from({ length: n }, () => new Float32Array(noiseBase.length));
    if (n % 2 === 0) {
      const denom = n / 2;
      for (let k = 0; k < n; k += 1) {
        const sign = k % 2 === 0 ? 1 : -1;
        for (let i = 0; i < noiseBase.length; i += 1) {
          subNoises[k][i] = sign * noiseBase[i] / denom;
        }
      }
    } else {
      const denom = (n - 1) / 2;
      for (let k = 0; k < n - 1; k += 1) {
        const sign = k % 2 === 0 ? 1 : -1;
        for (let i = 0; i < noiseBase.length; i += 1) {
          subNoises[k][i] = sign * noiseBase[i] / denom;
        }
      }
      for (let i = 0; i < noiseBase.length; i += 1) {
        let sum = 0;
        for (let k = 0; k < n - 1; k += 1) {
          sum += subNoises[k][i];
        }
        subNoises[n - 1][i] = -sum;
      }
    }
    return subNoises;
  }

  function verifyNoiseResidual(subNoises) {
    if (!subNoises || subNoises.length === 0) {
      return 0;
    }
    let residual = 0;
    for (let i = 0; i < subNoises[0].length; i += 1) {
      let sum = 0;
      for (const noise of subNoises) {
        sum += noise[i];
      }
      residual = Math.max(residual, Math.abs(sum));
    }
    return residual;
  }

  function makeSubframes(text, options) {
    const n = Math.max(2, Math.min(16, Number(options.n) || 4));
    const seed = options.seed || "privacy-display-study";
    const width = options.width || 900;
    const height = options.height || 260;
    const gamma = n * (Number(options.gammaFactor) || 1.1);
    const epsilonPixels = Math.max(0, Number(options.epsilonPixels) || 8);
    const sourceCanvas = renderSourceCanvas(text, { width, height, fontSize: options.fontSize });
    const sourceCtx = sourceCanvas.getContext("2d", { willReadFrequently: true });
    const source = sourceCtx.getImageData(0, 0, width, height);
    const pixelCount = width * height;
    const { indices, counts } = buildIndexMatrix(pixelCount, n, seed);
    const subNoises = options.useNoise
      ? splitComplementary(computeNoiseBase(source, epsilonPixels, seed), n)
      : null;

    const framesByIndex = [];
    for (let k = 0; k < n; k += 1) {
      const frameCanvas = document.createElement("canvas");
      frameCanvas.width = width;
      frameCanvas.height = height;
      const frameCtx = frameCanvas.getContext("2d");
      const frame = frameCtx.createImageData(width, height);
      for (let p = 0; p < pixelCount; p += 1) {
        const src = p * 4;
        const dst = p * 4;
        const noise = p * 3;
        const active = indices[p] === k;
        for (let c = 0; c < 3; c += 1) {
          const base = active ? source.data[src + c] * gamma : 0;
          const perturb = subNoises ? subNoises[k][noise + c] : 0;
          frame.data[dst + c] = Math.max(0, Math.min(255, Math.round(base + perturb)));
        }
        frame.data[dst + 3] = 255;
      }
      frameCtx.putImageData(frame, 0, 0);
      framesByIndex.push(frameCanvas);
    }

    const permutation = shuffle(
      Array.from({ length: n }, (_, i) => i),
      createRng(`${seed}:perm`)
    );
    const frames = permutation.map((idx) => framesByIndex[idx]);
    const noiseResidual = subNoises ? verifyNoiseResidual(subNoises) : 0;

    return {
      frames,
      sourceCanvas,
      meta: {
        n,
        width,
        height,
        gamma,
        epsilonPixels,
        counts,
        permutation,
        completeness_ok: counts.reduce((sum, count) => sum + count, 0) === pixelCount,
        noise_residual: noiseResidual
      }
    };
  }

  class MaskedPlayer {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.frames = [];
      this.meta = null;
      this.rafId = 0;
      this.frameIndex = 0;
    }

    load(text, options) {
      this.stop();
      const rendered = makeSubframes(text, options);
      this.frames = rendered.frames;
      this.meta = rendered.meta;
      this.canvas.width = rendered.meta.width;
      this.canvas.height = rendered.meta.height;
      this.frameIndex = 0;
      this.draw();
      return this.meta;
    }

    draw() {
      if (!this.frames.length) {
        return;
      }
      const frame = this.frames[this.frameIndex % this.frames.length];
      this.ctx.drawImage(frame, 0, 0);
    }

    start() {
      this.stop();
      const tick = () => {
        this.draw();
        this.frameIndex = (this.frameIndex + 1) % this.frames.length;
        this.rafId = global.requestAnimationFrame(tick);
      };
      this.rafId = global.requestAnimationFrame(tick);
    }

    stop() {
      if (this.rafId) {
        global.cancelAnimationFrame(this.rafId);
        this.rafId = 0;
      }
    }
  }

  function estimateRefreshRate(durationMs) {
    const duration = Math.max(450, Number(durationMs) || 850);
    return new Promise((resolve) => {
      const deltas = [];
      let start = 0;
      let last = 0;
      function step(ts) {
        if (!start) {
          start = ts;
          last = ts;
          global.requestAnimationFrame(step);
          return;
        }
        deltas.push(ts - last);
        last = ts;
        if (ts - start >= duration && deltas.length >= 20) {
          const sorted = deltas.slice().sort((a, b) => a - b);
          const trim = Math.floor(sorted.length * 0.1);
          const kept = sorted.slice(trim, sorted.length - trim);
          const mean = kept.reduce((sum, value) => sum + value, 0) / kept.length;
          resolve({
            hz: 1000 / mean,
            samples: deltas.length,
            mean_frame_ms: mean
          });
        } else {
          global.requestAnimationFrame(step);
        }
      }
      global.requestAnimationFrame(step);
    });
  }

  global.PrivacyMask = {
    createRng,
    uniformInt,
    shuffle,
    makeSubframes,
    MaskedPlayer,
    estimateRefreshRate
  };
})(window);
