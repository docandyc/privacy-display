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

  const DEFAULT_SAFE_FLICKER_HZ = 50;

  // Anti-OCR "strong" profile, ported from src/demo/playback_demo.py. Defaults
  // mirror the CLI `--anti-ocr-profile strong` profile; the webstudy overrides
  // stripe/glyph alpha to the values that performed best on a 240 Hz panel.
  const ANTI_OCR_STRONG = Object.freeze({
    profile: "strong",
    stripeWidth: 10,
    stripeAlpha: 0.18,
    glyphAlpha: 0.22
  });

  function clamp01(value) {
    if (!Number.isFinite(value)) {
      return 0;
    }
    return Math.max(0, Math.min(1, value));
  }

  function resolveAntiOcr(option) {
    if (!option) {
      return null;
    }
    const o = option === true ? {} : option;
    return {
      profile: "strong",
      stripeWidth: Math.max(1, Math.round(Number(o.stripeWidth) || ANTI_OCR_STRONG.stripeWidth)),
      stripeAlpha: clamp01(o.stripeAlpha != null ? Number(o.stripeAlpha) : ANTI_OCR_STRONG.stripeAlpha),
      glyphAlpha: clamp01(o.glyphAlpha != null ? Number(o.glyphAlpha) : ANTI_OCR_STRONG.glyphAlpha)
    };
  }

  // Square dilation via two separable 1-D max passes (cheap, early-exit).
  function dilateBool(mask, width, height, radius) {
    if (radius <= 0) {
      return mask.slice();
    }
    const tmp = new Uint8Array(width * height);
    for (let y = 0; y < height; y += 1) {
      const row = y * width;
      for (let x = 0; x < width; x += 1) {
        const x0 = Math.max(0, x - radius);
        const x1 = Math.min(width - 1, x + radius);
        let hit = 0;
        for (let xx = x0; xx <= x1; xx += 1) {
          if (mask[row + xx]) { hit = 1; break; }
        }
        tmp[row + x] = hit;
      }
    }
    const out = new Uint8Array(width * height);
    for (let x = 0; x < width; x += 1) {
      for (let y = 0; y < height; y += 1) {
        const y0 = Math.max(0, y - radius);
        const y1 = Math.min(height - 1, y + radius);
        let hit = 0;
        for (let yy = y0; yy <= y1; yy += 1) {
          if (tmp[yy * width + x]) { hit = 1; break; }
        }
        out[y * width + x] = hit;
      }
    }
    return out;
  }

  // Per-subframe stripe field: odd/even slots flip horizontal/vertical to
  // create rolling-shutter aliasing on a phone camera. Mirrors _stripe_mask.
  function stripeMask(width, height, cycle, slot, stripeWidth) {
    const sw = Math.max(1, stripeWidth);
    const period = Math.max(2, sw * 2);
    const phase = (((cycle * sw + slot * Math.max(1, Math.floor(sw / 2))) % period) + period) % period;
    const useX = (cycle + slot) % 2 === 0;
    const out = new Uint8Array(width * height);
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const coord = (useX ? x : y) + phase;
        out[y * width + x] = (Math.floor(coord / sw) % 2 === 0) ? 1 : 0;
      }
    }
    return out;
  }

  // Locate text strokes plus glyph and background colours. Polarity-agnostic:
  // the webstudy renders light text on a dark panel, the opposite of the
  // light-paper documents in playback_demo, so saliency keys off luminance
  // deviation from the (median) background rather than absolute darkness.
  function computeAntiOcrContext(imageData) {
    const { width, height, data } = imageData;
    const count = width * height;
    const gray = new Float32Array(count);
    const lumaHist = new Uint32Array(256);
    for (let p = 0; p < count; p += 1) {
      const i = p * 4;
      const l = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      gray[p] = l;
      lumaHist[Math.max(0, Math.min(255, Math.round(l)))] += 1;
    }
    let acc = 0;
    let bgLuma = 0;
    const half = count >> 1;
    for (let v = 0; v < 256; v += 1) {
      acc += lumaHist[v];
      if (acc >= half) { bgLuma = v; break; }
    }

    const base = new Uint8Array(count);
    let inkR = 0; let inkG = 0; let inkB = 0; let inkCount = 0;
    let bgR = 0; let bgG = 0; let bgB = 0; let bgCount = 0;
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const p = y * width + x;
        const i = p * 4;
        const dev = Math.abs(gray[p] - bgLuma);
        const left = gray[y * width + (x > 0 ? x - 1 : 0)];
        const up = gray[(y > 0 ? y - 1 : 0) * width + x];
        const grad = Math.max(Math.abs(gray[p] - left), Math.abs(gray[p] - up));
        const isCore = dev >= 35;
        base[p] = (isCore || grad >= 22) ? 1 : 0;
        if (isCore) {
          inkR += data[i]; inkG += data[i + 1]; inkB += data[i + 2]; inkCount += 1;
        } else if (dev < 8) {
          bgR += data[i]; bgG += data[i + 1]; bgB += data[i + 2]; bgCount += 1;
        }
      }
    }
    const inkRgb = inkCount
      ? [inkR / inkCount, inkG / inkCount, inkB / inkCount]
      : [255, 255, 255];
    const bgRgb = bgCount
      ? [bgR / bgCount, bgG / bgCount, bgB / bgCount]
      : [0, 0, 0];

    const stroke = dilateBool(base, width, height, 1);
    const halo = dilateBool(stroke, width, height, 2);
    const stripeRegion = dilateBool(stroke, width, height, 1);
    let salientPixels = 0;
    for (let p = 0; p < count; p += 1) {
      salientPixels += stroke[p];
    }
    return { stroke, halo, stripeRegion, inkRgb, bgRgb, salientPixels };
  }

  function blendPixel(data, i, rgb, alpha) {
    if (alpha <= 0) {
      return;
    }
    const inv = 1 - alpha;
    data[i] = Math.max(0, Math.min(255, data[i] * inv + rgb[0] * alpha));
    data[i + 1] = Math.max(0, Math.min(255, data[i + 1] * inv + rgb[1] * alpha));
    data[i + 2] = Math.max(0, Math.min(255, data[i + 2] * inv + rgb[2] * alpha));
  }

  // Overlay the strong anti-OCR artefacts onto one composed subframe in place:
  // faint stripe aliases around glyph edges, hole-punching on real strokes, and
  // false strokes in the glyph halo. Mirrors apply_anti_ocr_artifacts (strong).
  function applyAntiOcrStrong(frame, antiCtx, width, height, cycle, slot, opt) {
    const { stroke, halo, stripeRegion, inkRgb, bgRgb } = antiCtx;
    const stripe = stripeMask(width, height, cycle, slot, opt.stripeWidth);
    const data = frame.data;
    const stripeInkAlpha = opt.stripeAlpha;
    const strokeBgAlpha = opt.stripeAlpha * 0.3;
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const p = y * width + x;
        const i = p * 4;
        const isStroke = stroke[p];
        const nearStroke = halo[p] && !isStroke;
        const st = stripe[p];
        if (stripeRegion[p] && !isStroke && st) {
          blendPixel(data, i, inkRgb, stripeInkAlpha);
        }
        if (isStroke && !st) {
          blendPixel(data, i, bgRgb, strokeBgAlpha);
        }
        if (isStroke && ((x + 2 * y + cycle + slot) % 5 === 0)) {
          blendPixel(data, i, bgRgb, opt.glyphAlpha);
        }
        if (nearStroke && ((3 * x + 5 * y + 2 * cycle + slot) % 7 <= 1)) {
          blendPixel(data, i, inkRgb, opt.glyphAlpha);
        }
      }
    }
  }

  function makeSubframes(text, options) {
    const n = Math.max(2, Math.min(16, Number(options.n) || 4));
    const seed = options.seed || "privacy-display-study";
    const width = options.width || 900;
    const height = options.height || 260;
    const gamma = n * (Number(options.gammaFactor) || 1.1);
    const epsilonPixels = Math.max(0, Number(options.epsilonPixels) || 8);
    // Distinct mask + noise + stripe realisations to cycle through. >1 keeps a
    // long-exposure phone capture from integrating a single repeating pattern.
    const cycles = Math.max(1, Math.min(64, Math.round(Number(options.cycles) || 1)));
    // Safety gate: a full subframe cycle below the flicker-fusion threshold
    // (~50 Hz) would flicker and sits in the 3-30 Hz photosensitive-seizure
    // band. Such conditions fall back to a single static subframe (camera view).
    const safeFlickerHz = Number(options.safeFlickerHz) > 0 ? Number(options.safeFlickerHz) : DEFAULT_SAFE_FLICKER_HZ;
    const refreshHz = Number(options.refreshHz) > 0 ? Number(options.refreshHz) : 0;
    const cycleHz = refreshHz > 0 ? refreshHz / n : null;
    const mode = refreshHz > 0 && cycleHz < safeFlickerHz ? "static_fallback" : "temporal";
    const sourceCanvas = renderSourceCanvas(text, { width, height, fontSize: options.fontSize });
    const sourceCtx = sourceCanvas.getContext("2d", { willReadFrequently: true });
    const source = sourceCtx.getImageData(0, 0, width, height);
    const pixelCount = width * height;

    const antiOcr = resolveAntiOcr(options.antiOcr);
    const antiCtx = antiOcr ? computeAntiOcrContext(source) : null;

    // Scratch context only used to mint ImageData buffers before artefacts.
    const scratch = document.createElement("canvas");
    scratch.width = width;
    scratch.height = height;
    const scratchCtx = scratch.getContext("2d");

    const frames = [];
    let firstCounts = null;
    let firstPermutation = null;
    let noiseResidual = 0;

    for (let cycle = 0; cycle < cycles; cycle += 1) {
      const suffix = cycles > 1 ? `:${cycle}` : "";
      const cycleSeed = `${seed}${suffix}`;
      const { indices, counts } = buildIndexMatrix(pixelCount, n, cycleSeed);
      const subNoises = options.useNoise
        ? splitComplementary(computeNoiseBase(source, epsilonPixels, cycleSeed), n)
        : null;
      if (subNoises) {
        noiseResidual = Math.max(noiseResidual, verifyNoiseResidual(subNoises));
      }

      const framesByIndex = [];
      for (let k = 0; k < n; k += 1) {
        const frame = scratchCtx.createImageData(width, height);
        for (let p = 0; p < pixelCount; p += 1) {
          const px = p * 4;
          const noise = p * 3;
          const active = indices[p] === k;
          for (let c = 0; c < 3; c += 1) {
            const base = active ? source.data[px + c] * gamma : 0;
            const perturb = subNoises ? subNoises[k][noise + c] : 0;
            frame.data[px + c] = Math.max(0, Math.min(255, Math.round(base + perturb)));
          }
          frame.data[px + 3] = 255;
        }
        framesByIndex.push(frame);
      }

      const permutation = shuffle(
        Array.from({ length: n }, (_, i) => i),
        createRng(`${cycleSeed}:perm`)
      );
      permutation.forEach((idx, slot) => {
        const frame = framesByIndex[idx];
        if (antiCtx) {
          applyAntiOcrStrong(frame, antiCtx, width, height, cycle, slot, antiOcr);
        }
        const frameCanvas = document.createElement("canvas");
        frameCanvas.width = width;
        frameCanvas.height = height;
        frameCanvas.getContext("2d").putImageData(frame, 0, 0);
        frames.push(frameCanvas);
      });

      if (cycle === 0) {
        firstCounts = counts;
        firstPermutation = permutation;
      }
    }

    return {
      frames,
      sourceCanvas,
      meta: {
        n,
        width,
        height,
        gamma,
        epsilonPixels,
        counts: firstCounts,
        permutation: firstPermutation,
        completeness_ok: firstCounts.reduce((sum, count) => sum + count, 0) === pixelCount,
        noise_residual: noiseResidual,
        mode,
        cycle_hz: cycleHz,
        refresh_hz: refreshHz || null,
        safe_flicker_hz: safeFlickerHz,
        cycles,
        frame_count: frames.length,
        anti_ocr: antiOcr
          ? {
            profile: antiOcr.profile,
            stripe_width: antiOcr.stripeWidth,
            stripe_alpha: antiOcr.stripeAlpha,
            glyph_alpha: antiOcr.glyphAlpha,
            salient_pixels: antiCtx ? antiCtx.salientPixels : 0
          }
          : { profile: "off" }
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
      // Never smooth: the canvas buffer is drawn 1:1, and CSS uses
      // image-rendering:pixelated so display scaling stays nearest-neighbour.
      this.ctx.imageSmoothingEnabled = false;
      const frame = this.frames[this.frameIndex % this.frames.length];
      this.ctx.drawImage(frame, 0, 0);
    }

    start() {
      this.stop();
      // Safety gate: below the flicker-fusion threshold we do NOT animate.
      // Show one static subframe (the camera-view) instead of flickering.
      if (this.meta && this.meta.mode === "static_fallback") {
        this.frameIndex = 0;
        this.draw();
        return;
      }
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
    estimateRefreshRate,
    computeAntiOcrContext,
    applyAntiOcrStrong,
    ANTI_OCR_STRONG
  };
})(window);
