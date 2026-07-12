# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Graduation thesis workspace for a screen-privacy system based on temporal pixel masking (时间分片掩模): an image is split into `n` complementary subframes (each pixel lit in exactly one time slot, ChaCha20-CSPRNG-driven) so a human integrates the full image at high refresh rate while a camera exposure captures only fragments. Three main areas:

- `privacy-display/` — Python proof-of-concept, attack evaluation suite, experiments, and the user-study web app. This is where most code work happens.
- `paper/` — English IEEE Access manuscript (`main.tex`, XeLaTeX via latexmk). `paper-Chinese/` is the Chinese thesis version.
- `.trellis/` — Trellis task/spec system (see root `AGENTS.md`); task PRDs and per-layer coding specs live there.

## Commands

All Python work uses `privacy-display/.venv` (uv-managed). A second env `privacy-display/.venv-surya` exists only because `surya-ocr==0.14.7` has conflicting dependencies; use it for Surya OCR runs.

```bash
cd privacy-display

# Tests (Python)
.venv/bin/python -m pytest tests/ -q                      # full suite (~430 tests)
.venv/bin/python -m pytest tests/test_core.py -q          # one file
.venv/bin/python -m pytest tests/test_core.py::test_name  # one test

# Tests (JS, webstudy front-end scoring/timing logic — plain node:test, no npm)
node --test tests/js/

# Entry points
.venv/bin/python main.py demo         # comparison images/GIF + metrics
.venv/bin/python main.py benchmark    # parameter-sweep evaluation (needs tesseract)
.venv/bin/python main.py playback     # human-eye playback demo (240Hz screen)

# Reproduction orchestration
scripts/reproduce_all.sh              # safe path: tests + VLM dry-run + summary + manifest
scripts/reproduce_all.sh --full-offline

# User study server (Flask + SQLite)
.venv/bin/python webstudy/server.py   # http://127.0.0.1:5000
.venv/bin/python webstudy/analyze_study.py
```

Paper figures (matplotlib) regenerate from experiment JSONs into `paper/figures/*.pdf` — run from repo root:

```bash
privacy-display/.venv/bin/python privacy-display/experiments/paper_figures/make_all.py
```

Paper build: `latexmk -xelatex main.tex` in `paper/`.

VLM evaluation (`experiments/vlm_readability_analysis.py`, `experiments/real_capture_vlm_evaluation.py`) reads `SILICONFLOW_API_KEY` from the environment or `privacy-display/.env.local` (never committed). Always test with `--dry-run` first; live calls cost money.

## Architecture

`privacy-display/src/` is organized as defense vs. attack vs. measurement:

- `core/` — the defense. `mask_generator.py` (CSPRNG dot-matrix masks + Fisher-Yates playback permutation), `subframe_composer.py` (decomposition, brightness compensation, visual integration), `noise_injector.py` (FGSM adversarial noise split into temporally complementary parts, ΣN_k=0 with a pedestal ε so negative noise isn't clipped at black pixels), `timing_controller.py`, plus `hdr_compensation.py`, `config.py`, `fatigue_policy.py`, `multi_display.py`.
- `attack/` — the adversary. `camera_simulator.py` (global/rolling shutter, temporal averaging, long exposure), `ocr_evaluator.py` (Tesseract/EasyOCR/Surya CER-WER), `vlm_evaluator.py` (OpenAI-compatible online VLMs), `detection_evaluator.py`/`detectors.py` (YOLO etc.), `reconstruction_attack.py` (learned U-Net recovery).
- `evaluation/` — aggregation. `metrics.py` (FPI, CIEDE2000 ΔE, NMI — digital-model proxies only), `benchmark.py`, `real_capture*.py` (merging real-camera OCR results), `publication_summary.py` (aggregates existing result JSONs; does not rerun experiments), `reproducibility_manifest.py` (env/command/file hashes).
- `demo/` — pygame real-time window and playback demos; `gpu/` — moderngl renderer with software fallback.

`experiments/` holds one script per study (ablations, sweeps, attacks); each writes JSON into `experiments/results/`, which `publication_summary.py`, `reproducibility_manifest.py`, and `experiments/paper_figures/` consume downstream. The `real_captures_d{dist}_a{angle}_final/` directories are the real eMeet S600 capture archive (~10,575 images across conditions); heavy OCR/detection reruns happened on a Windows CUDA machine, hence the `.ps1`/`.bat` scripts in `scripts/`.

`webstudy/` is the controlled 240Hz laboratory user study (native JS/Canvas2D + Flask + SQLite). Formal sessions require ≥200Hz measured refresh and fixed `n=4`; `?demo=1` / `?debug=1` sessions are flagged and excluded from analysis so they cannot contaminate the paper dataset. `study_formal.db` is gitignored and contains personally identifying fields — never publish or commit it.

## Claims discipline (critical when editing paper or README)

Every reported security result is scoped to specific conditions: one eMeet S600 UVC camera, 3.91 ms common manual exposure, fixed geometry, three open-source OCR engines. Known failure boundaries are documented and must stay documented: 150-frame temporal averaging recovers most text, long exposure is not defeated, commercial VLMs read large-font short text, full-cycle digital averaging recovers ~94%. Do not generalize results into universal anti-photography/anti-VLM claims, and do not present digital-domain metrics (FPI/ΔE/SSIM, ΣI_k=I completeness) as physical-display or human-perception evidence. The playback demo is a research stimulus, not a validated production defense.
