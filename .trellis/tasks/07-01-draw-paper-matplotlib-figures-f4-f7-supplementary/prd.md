# Draw Paper Matplotlib Figures (F4–F7 + Supplementary)

## Goal

Fill the paper's empty figure placeholders with publication-quality matplotlib data figures. `paper/main.tex` (IEEE Access template) declares 7 figures (F1–F7), all currently `\fbox` placeholders with commented-out `\includegraphics`, and `paper/figures/` does not exist. This task produces the 4 figures that are genuinely matplotlib data plots (F4/F5/F6/F7) plus 4 curated supplementary figures (S1–S4) drawn from the existing ablation JSON, all as vector PDFs with **English** labels, and wires them into `main.tex`. F1/F2 (schematic diagrams) and F3 (photo montage) are out of matplotlib scope (F3 handled via the existing PIL grid helper).

Source plan: `/Users/andyhuang/.claude/plans/python-matplotlib-python-wild-hare.md` (approved).

## Requirements

* Create `privacy-display/experiments/paper_figures/` with a shared `figstyle.py` (headless Agg + `MPLCONFIGDIR`, English sans-serif font, `pdf.fonttype=42`/`ps.fonttype=42`, IEEE Access sizes `COL_W=3.5in`/`FULL_W=7.16in`, colorblind-friendly palette with consistent grade colors original=grey/deployed=blue/vlm=orange-red, and helpers `load(name)`, `ci_err(field)`, `save(fig, stem)` writing `paper/figures/<stem>.pdf`).
* F4 `real_capture_bar.pdf` — grouped bar, X=attack mode {short, long, video-avg}, series=grade {original, deployed, vlm}, Y=OCR char-recovery % with exact-match and 95% CI error bars. Data: `results/real_capture_ocr.json` (`summary.by_condition` / `summary.protection_delta`).
* F5 `readability_robustness_tradeoff.pdf` — dual-axis line, X=inversion α (0→0.5)/grade, left Y=long-exposure char-recovery, right Y=readability proxy. Data: `results/anti_ocr_profile_ablation.json` block3 + `real_capture_ocr.json` (deployed|long, vlm|long).
* F6 `real_detection_drop.pdf` — grouped bar, X=4 detectors, series={real_clean, real_short, real_video}, Y=mAP50 %. Data: `results/real_capture_coco_detection.json`.
* F7 `pareto_sweep.pdf` — reuse the plot logic already in `experiments/pareto_sweep.py::_plot` (English labels already), re-drawn via `figstyle` and exported as PDF. Data: `results/pareto_sweep.json`.
* S1 `antiocr_heatmap.pdf` — twin heatmaps (stripe×glyph) colored by `temporal_avg_char` and `readability_drift`. Data: `results/anti_ocr_profile_ablation.json` block2.
* S2 `multiengine_ocr.pdf` — paired bar per engine (original vs single-subframe) with CI. Data: `results/corpus_multi_engine.json`.
* S3 `baselines_scatter.pdf` — privacy(char-recovery) vs usability(ΔE) scatter, 6 baselines + our operating point. Data: `results/screen_privacy_baselines.json` + `results/pareto_sweep.json` recommended.
* S4 `all_attackers.pdf` — grouped bar across attacker families {OCR, VLM, Detection, Tracking}, clean vs protected, normalized to % of clean baseline. Data: `corpus_multi_engine`, `vlm_model_ablation`, `coco_detection_attack`, `mot_tracking_attack`.
* F3 `real_capture_montage.pdf` — reuse `src/demo/visual_integration.py::make_comparison_grid` (PIL) to tile real-capture JPGs; export PDF. Lightweight, not a new matplotlib chart.
* `make_all.py` regenerates every figure PDF in one command; append its invocation to `privacy-display/scripts/reproduce_all.sh`.
* Wire figures into `paper/main.tex`: uncomment `\includegraphics` + remove `\fbox` for F3–F7; add new `\begin{figure}` blocks + one referencing sentence each for S1–S4.

## Acceptance Criteria

* [ ] `privacy-display/experiments/paper_figures/figstyle.py` provides the shared setup + `load`/`ci_err`/`save` helpers and is imported by every figure script (no duplicated rcParams).
* [ ] `fig_f4_attack_bar.py`, `fig_f5_tradeoff.py`, `fig_f6_detection_drop.py`, `fig_f7_pareto.py` each emit their PDF to `paper/figures/`.
* [ ] `fig_s1_antiocr_heatmap.py`, `fig_s2_multiengine_ocr.py`, `fig_s3_baselines_scatter.py`, `fig_s4_all_attackers.py` each emit their PDF to `paper/figures/`.
* [ ] `fig_f3_montage.py` (or a reuse of `visual_integration.py`) emits `real_capture_montage.pdf`.
* [ ] `make_all.py` runs all scripts end-to-end with the venv and produces all PDFs with no errors; `reproduce_all.sh` calls it.
* [ ] Bar/line figures carry 95% CI error bars taken from the source JSON `ci95` fields; grade colors are consistent across figures.
* [ ] `paper/main.tex` references resolve (no `??`) and compile cleanly with the new figures embedded; F3–F7 placeholders replaced; S1–S4 added with captions/labels + in-text `\ref`.
* [ ] Key on-figure values match abstract/§V text (e.g. F4 deployed-short ≈14.1%, F6 real_short ≈1.6–5.8%).

## Definition of Done

* All figure scripts run headless from `privacy-display/.venv` and regenerate deterministically via `make_all.py`.
* PDFs are vector with embedded (non-Type-3) fonts, legible at single-column 3.5in width.
* `paper/main.tex` compiles (pdflatex/xelatex/latexmk) with all figures placed and referenced.
* F5 readability axis annotates its source; if the user-study data (§V, still `\TODO`) is unavailable, it uses the SSIM/readability_drift objective proxy and says so in the caption.

## Technical Approach

Build a thin `paper_figures` package that reads the already-computed `experiments/results/*.json` (each aggregate carries `{mean, std, ci95}`) and renders one script per figure via a shared `figstyle` module. Reuse the two existing plotting idioms: the grouped-bar + threshold pattern in `src/evaluation/benchmark.py::generate_plots` (`:671-724`) for F4/F6/S2/S4, and the Pareto plot in `experiments/pareto_sweep.py::_plot` (`:171-204`) for F7. Prefer each figure's dedicated per-file JSON for provenance; only S4 aggregates across multiple source files. Do not run heavy experiments — all inputs already exist on disk.

## Decision (ADR-lite)

**Context**: The paper needs real data figures but currently ships empty placeholders; figure styling is duplicated inline across two scripts and there is no shared theme.

**Decision**: Add a dedicated `paper_figures/` package with a single shared `figstyle.py` and one script per figure, emitting vector PDFs directly into `paper/figures/`. Reuse existing plot code rather than re-deriving data. Keep in-figure text English for IEEE Access.

**Consequences**: Figures regenerate deterministically from committed JSON with one command, styling stays consistent and DRY, and the LaTeX build gets real vector artifacts. F1/F2 remain a separate diagramming task (TikZ/drawio); F3 stays a PIL montage.

## Out of Scope

* F1 (concept/threat) and F2 (system pipeline) schematic diagrams — belong in a diagramming tool, not matplotlib.
* Re-running or re-computing any experiment; only reading existing `results/*.json`.
* The optional extra figures (noise-ε sweep line, component-ablation horizontal bar) — not drawn by default.
* Translating the paper body to English (separate task); only figure labels are English now.

## Technical Notes

* Approved source plan: `/Users/andyhuang/.claude/plans/python-matplotlib-python-wild-hare.md`.
* Reuse targets: `privacy-display/experiments/pareto_sweep.py` (`_plot`, headless setup `:173-178`), `privacy-display/src/evaluation/benchmark.py::generate_plots` (`:671-724`, but replace Chinese-font rcParams with English), `privacy-display/src/demo/visual_integration.py::make_comparison_grid` (`:35-107`).
* LaTeX placeholder anchors in `paper/main.tex`: F3 `:316-322`, F4 `:324-330`, F5 `:332-338`, F6 `:430-436`, F7 `:548-554` (each has a commented `\includegraphics{figures/*.pdf}`).
* Env: `privacy-display/.venv` (Python 3.10, `matplotlib>=3.7`, Pillow, numpy, scipy present).
* Data provenance map lives in the source plan; aggregated fallback is `results/publication_summary.json`.
* Relevant spec: `.trellis/spec/backend/quality-guidelines.md`, `.trellis/spec/backend/directory-structure.md`.
