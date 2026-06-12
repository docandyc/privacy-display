# Quality Guidelines

> Code quality standards for backend development.

---

## Overview

<!--
Document your project's quality standards here.

Questions to answer:
- What patterns are forbidden?
- What linting rules do you enforce?
- What are your testing requirements?
- What code review standards apply?
-->

(To be filled by the team)

---

## Forbidden Patterns

<!-- Patterns that should never be used and why -->

(To be filled by the team)

---

## Required Patterns

<!-- Patterns that must always be used -->

- CSPRNG-derived bounded integers must use rejection sampling instead of direct modulo. This applies to mask index generation and Fisher-Yates permutation indices; direct `% upper` introduces modulo bias unless `upper` divides the random integer space exactly.
- Display-timing code that is exercised by an actual window should advance timing tokens from the display/vsync boundary when available. Software `sleep` loops are acceptable only as a simulation fallback and should share the same token-advance path.

## Scenario: Noise Injector Adversarial Loop

### 1. Scope / Trigger
- Trigger: `NoiseInjector` implements the disclosure's adversarial noise loop: differentiable shadow gradients, persisted noise templates, and online OCR monitoring.

### 2. Signatures
- `generate_fgsm_noise(image, model_name="tesseract", use_template=True) -> np.ndarray`
- `generate_pgd_noise(image, model_name="easyocr", ..., use_template=True) -> np.ndarray`
- `build_template(image, model_name="tesseract", method=None, name=None, save=True) -> tuple[np.ndarray, dict]`
- `monitor_online_recognition(image, ground_truth="", model_name="tesseract", engine=None, ocr_evaluator=None, threshold=None) -> dict`
- `save_template(name, noise, metadata=None) -> None`
- `get_template_metadata(name) -> dict`
- `WindowConfig.enable_ocr_monitoring: bool`
- `run_online_noise_monitor(injector, protected_frame, cycle, enabled, interval_cycles, ...) -> dict | None`

### 3. Contracts
- Template lookup is the first runtime path when `use_template=True`; template noise is clipped to the effective epsilon budget and sets `last_gradient_source == "template"`.
- Template building must bypass existing templates (`use_template=False`) so offline updates recompute gradients from the current shadow model.
- The normal gradient path must use a differentiable torch/autograd shadow model when torch is installed, and only fall back to the image-space surrogate when torch is unavailable.
- OCR online monitoring must call the configured/effective OCR evaluator, convert the recognition result to a score, and pass that score to `update_online_strategy`.
- The realtime privacy window must use `generate_rotating_noise`, not a hard-coded FGSM call, so online strategy updates can affect subsequent cycles.
- The realtime privacy window must periodically sample an already protected subframe and feed it through `monitor_online_recognition`; monitor failures should degrade to an `unavailable` state instead of crashing the display loop.
- Persisted templates must store both `noise` and JSON metadata; old metadata-free `.npz` files remain loadable.

### 4. Validation & Error Matrix
- No `template_dir` -> `save_template` is a no-op and does not fail template generation.
- Unknown model name -> resolve through `_get_spec` to the configured tesseract spec.
- No torch import -> mark gradient source as `surrogate` and continue with bounded noise.
- OCR text without `ground_truth` -> score is `1.0` for non-empty recognition and `0.0` otherwise.
- OCR dependency/runtime failure inside the window monitor -> return monitor status `unavailable` and keep rendering.

### 5. Good/Base/Bad Cases
- Good: build a template with metadata, reload a new injector, then reuse that template before calculating a new gradient.
- Base: generate FGSM/PGD with no template and verify `||noise||_inf <= epsilon`.
- Bad: claim online update exists while only accepting an external score and never invoking OCR monitoring.
- Bad: update `preferred_method` to PGD while the realtime window still always calls FGSM.

### 6. Tests Required
- Assert torch-backed FGSM records `last_gradient_source == "shadow"` and returns non-zero bounded noise.
- Assert `monitor_online_recognition` calls the evaluator and updates strategy state when the recognition score crosses the threshold.
- Assert generated templates persist metadata and are reused after reload.
- Assert the realtime monitor helper samples only on the configured interval and forwards protected frames to the injector.

### 7. Wrong vs Correct
#### Wrong
```python
grad = self._surrogate_gradient(image, spec)
```
#### Correct
```python
grad = self._target_gradient(image, spec)
```
where `_target_gradient` tries the differentiable shadow model first and records the fallback source.

## Scenario: OCR Evaluator Engine Integration

### 1. Scope / Trigger
- Trigger: `OCREvaluator` adds or changes a third-party OCR engine used by benchmarks, attack reports, or online monitoring.

### 2. Signatures
- `OCREvaluator(engines: list[str] | None = None)`
- `_detect_available_engines() -> list[str]`
- `recognize(image: np.ndarray, engine: str = "tesseract") -> str`
- `_parse_paddleocr_text(result) -> str`
- `run_corpus_multi_engine(engines: list[str] | None = None) -> dict`

### 3. Contracts
- Auto-detection must only list an engine when importing the package and any cheap local availability check succeeds.
- Unit tests must not instantiate OCR engines that download model weights; inject cached/fake readers for parser and dispatch tests.
- Images passed into OCR backends must be contiguous NumPy arrays.
- PaddleOCR 3.x should use `PaddleOCR(...).predict(image)` when present; older versions may fall back to `.ocr(image)`.
- PaddleOCR output parsing must accept 2.x list tuples like `[box, ("text", score)]` and 3.x dict/result-object payloads containing `rec_texts`, `text`, `texts`, `res`, or `.json`/`.res`.
- Corpus result JSON must include the exact engine keys that were run, and documentation values should match that file after reruns.

### 4. Validation & Error Matrix
- Engine package import fails -> omit the engine from `engines` and keep other engines available.
- Unsupported engine name in `recognize` -> raise `ValueError`.
- PaddleOCR output shape lacks recognized text fields -> return an empty string rather than crashing.
- Heavy model download or runtime setup failure -> keep it out of unit tests; verify with an explicit integration command when the environment has cached models or network access.

### 5. Good/Base/Bad Cases
- Good: add an engine with parser-only regression tests plus one fake-reader dispatch test.
- Base: existing Tesseract/EasyOCR behavior remains unchanged when PaddleOCR is unavailable.
- Bad: unit tests instantiate `PaddleOCR()` directly and trigger downloads.
- Bad: hand-edit `corpus_multi_engine.json` without rerunning `run_corpus_multi_engine`.

### 6. Tests Required
- Assert `OCREvaluator().engines` includes the engine in an environment where the dependency is installed.
- Assert parser coverage for every supported output shape.
- Assert `recognize(..., engine)` uses a cached/fake reader and returns joined text.
- Run `pytest tests/ -q` and, for corpus changes, rerun `run_corpus_multi_engine(...)`.

### 7. Wrong vs Correct
#### Wrong
```python
result = PaddleOCR(lang="ch").predict(image)
return result[0]["text"]
```

#### Correct
```python
if self._paddleocr_reader is None:
    self._paddleocr_reader = PaddleOCR(lang="ch", ...)
return self._parse_paddleocr_text(self._paddleocr_reader.predict(image))
```

## Scenario: Publication Corpus and Stratified OCR Reports

### 1. Scope / Trigger
- Trigger: changing the synthetic text corpus, OCR benchmark aggregation, or publication-facing OCR numbers used in the thesis or IEEE Access draft.

### 2. Signatures
- `iter_corpus_specs(samples_per_template=10) -> list[dict]`
- `build(samples_per_template=10) -> dict[str, str]`
- `load_corpus() -> tuple[list[np.ndarray], list[str], list[str]]`
- `load_corpus_metadata() -> dict[str, dict]`
- `summarize_corpus_strata(sample_rows, field) -> dict`
- `run_corpus_multi_engine(n=4, epsilon=8/255, engines=None, output_dir="experiments/results", merge_existing=False) -> dict`
- Command: `python experiments/build_corpus.py`
- Command: `python -c "from src.evaluation.benchmark import run_corpus_multi_engine; run_corpus_multi_engine(engines=['tesseract','easyocr','paddleocr'], merge_existing=True)"`

### 3. Contracts
- The default corpus is deterministic and publication-facing: 12 base templates times 10 variants, for 120 generated images.
- `build()` must write `data/test_images/*.png`, `ground_truth.json`, and `corpus_metadata.json`.
- `ground_truth.json` maps sample names to single-line ground-truth text.
- `corpus_metadata.json` uses the same sample keys and must include `truth`, `category`, `language`, `layout`, `font_size`, `variant`, `width`, and `height`.
- `load_corpus()` must preserve the existing return contract `(images, truths, names)` for older benchmark callers.
- `load_corpus_metadata()` must return `{}` rather than failing when older corpora do not have metadata.
- `run_corpus_multi_engine()` must persist `experiments/results/corpus_multi_engine.json` and include `n_samples`, `n_categories`, overall mean/std fields, per-field `strata`, and per-sample rows.
- `engines=None` means run every locally available engine; `engines=[]` means run no new engines and is valid when testing merge behavior.
- `merge_existing=True` must load any existing `corpus_multi_engine.json` and preserve engine entries not requested in the current run. This prevents a long EasyOCR/PaddleOCR run from deleting already verified Tesseract results.
- Publication OCR reports must include bootstrap 95% confidence intervals for original accuracy, subframe accuracy, and paired reduction. Keep the older `original_mean`, `original_std`, `subframe_mean`, and `subframe_std` fields for document compatibility.
- Paired reduction is computed per sample as `original_char_acc - subframe_char_acc` and summarized separately from independent original/subframe means.
- Publication OCR reports must include secondary recovery metrics under `recovery_metrics`: word-level accuracy, exact-match rate, and sensitive-token recall for both original and protected subframes.
- Sensitive tokens must cover structured privacy-bearing fields such as email-like strings, URLs, account numbers, long digit runs, codes, and uppercase identifiers; samples without sensitive tokens should not dilute the sensitive-token denominator.
- Publication text must cite values from the generated JSON, not from hand calculations or console-only output.

### 4. Validation & Error Matrix
- `samples_per_template <= 0` -> `ValueError`.
- Missing `ground_truth.json` in `load_corpus()` -> regenerate the default corpus.
- Missing image for a ground-truth key -> skip that sample instead of crashing, preserving legacy behavior.
- Missing metadata file -> return `{}` and group the sample under `unknown` in strata.
- OCR engine not available in `OCREvaluator().engines` -> omit that engine from the report.
- Existing JSON in an older format while `merge_existing=True` -> preserve it and print a legacy-result message instead of failing on missing CI fields.

### 5. Good/Base/Bad Cases
- Good: regenerate the corpus, rerun the OCR benchmark, then update thesis tables from `corpus_multi_engine.json`.
- Good: use category/language/layout/font-size strata to explain where OCR is weak on original frames or protected subframes.
- Base: Tesseract can be run on the full 120-sample corpus while heavier engines are retained as smaller review checks until cached models are available.
- Base: run EasyOCR/PaddleOCR with `merge_existing=True` so their results are added without deleting Tesseract.
- Bad: changing `BASE_CORPUS` without regenerating `ground_truth.json` and `corpus_metadata.json`.
- Bad: editing `corpus_multi_engine.json` by hand or updating the thesis from stale 12-sample numbers.

### 6. Tests Required
- Assert a temporary corpus build emits images, ground truth, metadata, and loader-compatible return values.
- Assert `iter_corpus_specs()` rejects non-positive sample counts.
- Assert summary helpers include count, mean, standard deviation, and deterministic 95% confidence intervals.
- Assert strata summaries include original, subframe, and paired-reduction statistics.
- Assert recovery-metric summaries report word-level, exact-match, and sensitive-token values without counting samples that contain no sensitive tokens.
- Assert `engines=[]` with `merge_existing=True` preserves an existing JSON report and does not implicitly run every detected engine.
- Run `pytest tests/test_corpus.py tests/test_ocr_evaluator.py -q` after changing corpus or aggregation code.
- Run `pytest tests/ -q` before using the resulting numbers in publication-facing documents.

### 7. Wrong vs Correct
#### Wrong
```python
report["tesseract"] = {"subframe_mean": 0.0}
```

#### Correct
```bash
python experiments/build_corpus.py
python -c "from src.evaluation.benchmark import run_corpus_multi_engine; run_corpus_multi_engine(engines=['tesseract','easyocr','paddleocr'], merge_existing=True)"
```

## Scenario: Screen-Camera Strong Attack Baselines

### 1. Scope / Trigger
- Trigger: `CameraSimulator` adds attacks inspired by screen-camera communication or optical covert-channel work, especially attacks that search timing phase, accumulate frame differences, or recover from a single color channel.

### 2. Signatures
- `phase_search_recovery_attack(frame_sequence, window_size=None, method="mean", restore_brightness=True) -> tuple[np.ndarray, dict]`
- `weighted_differential_accumulator_attack(frame_sequence, channel="luma", normalize=True) -> tuple[np.ndarray, dict]`
- `channel_selective_recovery_attack(frame_sequence, channel="blue", method="max") -> tuple[np.ndarray, dict]`
- `screen_camera_attack_suite(frame_sequence, cycle_length) -> dict`
- `compose_protected_subframes(image, n=4, epsilon=8/255, cycles=1, cycle_start=0, with_noise=True) -> list[np.ndarray]`
- `run_corpus_strong_camera_attacks(n=4, epsilon=8/255, cycles=2, engine="tesseract", output_dir="experiments/results", max_samples=None, evaluator=None, corpus=None, metadata=None, with_noise=True, ocr_timeout=4.0, progress_interval=10, save=True) -> dict`
- `summarize_strong_attack_rows(sample_rows, leak_threshold=0.20) -> dict`
- `experiments/attack_analysis.py` writes `experiments/results/attack_analysis_strong_camera.json`
- Corpus attack result file: `experiments/results/corpus_strong_camera_attack.json`

### 3. Contracts
- Each attack must return both a reconstructed `uint8` frame and metadata suitable for paper tables.
- Metadata must include `attack`, `score`, and any attack-specific selection fields such as `best_offset`, `window_size`, `method`, `channel`, or `frames`.
- `screen_camera_attack_suite` must include `phase_search_mean`, `phase_search_max`, `differential_luma`, `differential_blue`, and `blue_channel_max`.
- Phase search scoring must not prefer sparse high-frequency mask residue over a complete-period reconstruction; include coverage and saturation/edge penalties in the heuristic.
- Publication-facing strong-attack claims must include corpus-level statistics, not only a single demo image. `run_corpus_strong_camera_attacks` must include at least `global_shutter_slot0`, `temporal_average_cycle`, the screen-camera suite attacks, per-attack summaries, and `best_attack_per_sample`.
- Corpus attack rows must include `char_accuracy`, `word_accuracy`, `exact_match`, `sensitive_token_recall`, `sensitive_token_count`, `psnr_db`, attack metadata, recognized-text preview, and any OCR error.
- Long OCR experiment paths must expose bounded timeout and progress reporting; an OCR timeout/failure should be recorded as zero recovery for that attack row, not hang or delete the experiment.
- `attack_analysis.py` must persist OCR outcomes and metadata in JSON, not only print console output.

### 4. Validation & Error Matrix
- Empty frame sequence -> `ValueError`.
- `window_size <= 0` or `window_size > len(frame_sequence)` -> `ValueError`.
- Unknown combine method -> `ValueError`.
- Differential accumulator with fewer than two frames -> `ValueError`.
- Unknown channel outside `{luma, red, green, blue}` -> `ValueError`.
- `cycle_length <= 0` in the suite -> `ValueError`.
- `cycles <= 0` in corpus strong attacks -> `ValueError`.
- `max_samples <= 0` when provided -> `ValueError`.
- `progress_interval < 0` -> `ValueError`.
- Requested OCR engine unavailable -> `ValueError`.
- Single OCR call timeout/failure inside corpus attack -> row-level `ocr_error` plus zero recovery, continue the corpus run.

### 5. Good/Base/Bad Cases
- Good: phase search finds the complete-cycle window in a sequence with prefix/suffix distractor frames.
- Good: blue-channel recovery is reported separately from luma recovery to catch color side channels.
- Good: corpus strong-attack JSON reports both defended single-frame attacks and leaking complete-cycle attacks, with `best_attack_per_sample` making the worst case explicit.
- Base: differential accumulation returns a normalized RGB visualization plus metadata even when OCR remains 0%.
- Bad: adding only temporal averaging and claiming coverage of screen-camera communication attacks.
- Bad: printing attack results without a machine-readable JSON artifact.
- Bad: reporting only the single demo attack matrix while using it as evidence for corpus-level publication claims.
- Bad: running hundreds of OCR calls without timeout/progress, making the experiment non-reproducible in automation.

### 6. Tests Required
- Assert phase search recovers a known complete-cycle synthetic image and reports the expected offset.
- Assert differential accumulation reports channel metadata and highlights the changing region.
- Assert the attack suite returns all publication baselines with frames and metadata.
- Assert protected-subframe composition can produce multiple deterministic cycles for corpus attack experiments.
- Assert strong-attack row summaries include per-attack means, leak-rate statistics, sensitive-token denominators, and best-attacker wins.
- Assert corpus strong attacks can run with an injected fake OCR evaluator and write `corpus_strong_camera_attack.json`.
- Assert invalid inputs raise `ValueError`.
- Run `pytest tests/ -q` and `python experiments/attack_analysis.py` after modifying these attacks.

### 7. Wrong vs Correct
#### Wrong
```python
frame = cam.temporal_averaging_attack(subframes, k=n)
print(ocr(frame))
```

#### Correct
```python
suite = cam.screen_camera_attack_suite(captured_frames, cycle_length=n)
for name, entry in suite.items():
    result = evaluator.evaluate_single(entry["frame"], ground_truth, "tesseract")
    report[name] = {**entry["metadata"], "char_accuracy": result.char_accuracy}
```

#### Wrong
```python
print("phase search OCR=100%")
```

#### Correct
```python
report = run_corpus_strong_camera_attacks(ocr_timeout=4.0, progress_interval=10)
json.dump(report, out_file, ensure_ascii=False, indent=2)
```

## Scenario: Privacy Window Runtime Configuration

### 1. Scope / Trigger
- Trigger: runtime config crosses persisted JSON, `PrivacyDisplayConfig`, `WindowConfig`, realtime display scheduling, and disclosure-derived safety claims.

### 2. Signatures
- `PrivacyDisplayConfig(width=1280, height=720, n=2, epsilon=8/255, gamma_factor=1.1, brightness_model="backlight", inversion_alpha=0.3, insert_inversion=False, key_hex="", refresh_rate=120, show_hud=True)`
- `PrivacyDisplayConfig.from_dict(payload: dict) -> PrivacyDisplayConfig`
- `PrivacyDisplayConfig.to_window_kwargs() -> dict`
- `WindowConfig(..., gamma_factor: float = 1.1, brightness_model: str = "backlight", inversion_alpha: float = 0.3, insert_inversion: bool = False, ...)`
- `runtime_renderer_gamma(n: int, gamma_factor: float, brightness_model: str) -> float`
- `sub_noises_to_pixel_space(sub_noises_f: list[np.ndarray], epsilon: float) -> tuple[list[np.ndarray], float]`
- `output_slot_duration(frame_interval: float, output_kind: str, inversion_alpha: float) -> float`

### 3. Contracts
- `gamma_factor` is the SDR brightness-comfort multiplier; it is not the disclosure's inversion-frame alpha.
- `brightness_model == "backlight"` is the default and must keep realtime renderer gamma at `1.0`, matching demo/benchmark. It models brightness restoration as display/backlight gain rather than pixel amplification.
- `brightness_model == "pixel"` is the explicit SDR pixel-compensation mode and must use `gamma = n * gamma_factor`; document that it clips bright document backgrounds.
- `inversion_alpha` is the disclosure coefficient for `t_inv = alpha * Δt` and must be forwarded from persisted config into `WindowConfig`.
- Persisted legacy `alpha` values in `[0.2, 0.5]` map to `inversion_alpha`; legacy `alpha` values above that range map to the older `gamma_factor` meaning for backward compatibility.
- Realtime window noise must be converted with `nf * 255 + epsilon * 255` before rendering, matching demo/benchmark/reconstruction experiments. Omitting pedestal makes inactive pixels exactly zero and reopens the documented single-frame inpaint weakness.
- Non-vsync realtime scheduling should use `output_slot_duration`; inversion slots use `inversion_alpha * frame_interval`, while normal subframes and black frames use the full frame interval.

### 4. Validation & Error Matrix
- `n < 2` or `n > 16` -> `ValueError`.
- `epsilon` outside `[0, 1]` -> `ValueError`.
- `gamma_factor <= 0` -> `ValueError`.
- `brightness_model` outside `{"backlight", "pixel"}` -> `ValueError`.
- `inversion_alpha` outside `[0.2, 0.5]` -> `ValueError`.
- `key_hex` not encoding exactly 32 bytes -> `ValueError`.
- Negative epsilon passed to pedestal conversion -> `ValueError`.

### 5. Good/Base/Bad Cases
- Good: JSON with `gamma_factor=1.2`, `inversion_alpha=0.3`, and `insert_inversion=true` round-trips and produces matching window kwargs.
- Good: default realtime window uses `brightness_model="backlight"` and renderer gamma `1.0`.
- Good: explicit `brightness_model="pixel"` uses renderer gamma `n * gamma_factor`.
- Base: old JSON with `alpha=1.2` still maps to `gamma_factor=1.2`.
- Base: old JSON with `alpha=0.3` maps to `inversion_alpha=0.3`.
- Bad: using a single `alpha` field for both brightness compensation and inversion timing.
- Bad: realtime window uses `nf * 255` without pedestal while docs claim pedestal-backed inpaint resistance.

### 6. Tests Required
- Assert config save/load preserves `gamma_factor`, `inversion_alpha`, `insert_inversion`, and key material.
- Assert config save/load preserves `brightness_model` and forwards it through `to_window_kwargs`.
- Assert realtime renderer gamma is `1.0` for default backlight mode and `n * gamma_factor` for pixel mode.
- Assert both legacy `alpha` migrations.
- Assert invalid `inversion_alpha` is rejected in config and window paths.
- Assert `sub_noises_to_pixel_space` adds `epsilon * 255` pedestal.
- Assert inversion output slots use `alpha * frame_interval`.

### 7. Wrong vs Correct
#### Wrong
```python
cfg = PrivacyDisplayConfig(alpha=1.1)
WindowConfig(gamma_factor=cfg.alpha)
sub_noises = [(nf * 255).astype(np.float32) for nf in sub_noises_f]
```

#### Correct
```python
cfg = PrivacyDisplayConfig(gamma_factor=1.1, inversion_alpha=0.3)
WindowConfig(**cfg.to_window_kwargs())
sub_noises, pedestal = sub_noises_to_pixel_space(sub_noises_f, cfg.epsilon)
```

## Scenario: Playback Anti-OCR Profile

### 1. Scope / Trigger
- Trigger: `main.py playback` adds opt-in OCR suppression that changes precomputed playback frames and CLI flags.

### 2. Signatures
- `PlaybackConfig(..., image_path=None, demo_name="document", pdf_page=1, anti_ocr_profile="off", mask_cell_size=1, stripe_width=10, stripe_alpha=0.18, glyph_alpha=0.22)`
- `build_playback_frames(..., anti_ocr_profile="off", mask_cell_size=None, stripe_width=None, stripe_alpha=None, glyph_alpha=None) -> tuple[list[tuple[np.ndarray, str]], dict]`
- `resolve_anti_ocr_options(profile, mask_cell_size=None, stripe_width=None, stripe_alpha=None, glyph_alpha=None) -> AntiOcrOptions`
- `fit_image_to_canvas(image, width, height, background=(245,245,245)) -> np.ndarray`
- `render_pdf_page_to_canvas(pdf_path, page_number, width, height) -> np.ndarray`
- `make_cet6_demo_document(width, height, page_number=1) -> np.ndarray`
- `generate_cell_masks(width, height, n, cycle, cell_size, key=None) -> list[np.ndarray]`
- `extract_text_saliency_mask(image) -> np.ndarray`
- `apply_anti_ocr_artifacts(frame, original, saliency_mask, cycle, slot, stripe_width, stripe_alpha, glyph_alpha, profile="strong") -> np.ndarray`
- CLI flags: `--demo document|cet6`, `--pdf-page`, `--anti-ocr-profile off|strong|vlm`, `--mask-cell-size`, `--stripe-width`, `--stripe-alpha`, `--glyph-alpha`.

### 3. Contracts
- `--image` takes precedence over built-in `--demo`; otherwise `--demo document` generates the synthetic document and `--demo cet6` renders the local CET6 PDF.
- PDF pages must be rendered to RGB and fitted to the playback canvas without aspect-ratio distortion.
- PDF rendering should prefer `pypdfium2`; `pdftoppm`/Poppler is only a fallback.
- `anti_ocr_profile == "off"` is the default and must preserve existing playback output for the same key, image, `n`, cycles, noise, and inversion settings.
- `anti_ocr_profile == "strong"` is a demonstration/OCR-suppression mode, not a strict completeness proof; it may intentionally perturb full-cycle averages.
- Strong mode defaults are readability-first: default `mask_cell_size` must stay at `1`, and default artifacts must preserve measurable text-vs-background contrast. Users can manually raise cell size/alphas for more aggressive OCR suppression.
- `anti_ocr_profile == "vlm"` is a camera/VLM stress profile. Its defaults should be more aggressive than strong (`mask_cell_size=2`, `stripe_width=6`, `stripe_alpha=0.42`, `glyph_alpha=0.55`) and may reduce human readability; it exists for phone-photo VLM/OCR suppression experiments, not for clean reading demos.
- Strong and VLM modes must suppress requested equal-duration playback inversion and expose `requested_inversion=True`, `insert_inversion=False`, and `inversion_suppressed=True` in metadata. A full inversion slot turns `n=4` playback into 5 equal slots at 240Hz and washes out small text.
- Strong and VLM modes must do all extra NumPy work during precomputation only. The playback loop remains blit/HUD/flip and does not run per-frame image processing.
- Strong and VLM modes must keep masks mutually exclusive and complete before artifacts are applied; large cells are generated through `MaskGenerator`, not ad hoc modulo randomness.
- Strong and VLM mode metadata must record the selected profile and effective tunable parameters under `meta["anti_ocr"]`, so HUD/tests can expose what was displayed.

### 4. Validation & Error Matrix
- Unknown `anti_ocr_profile` -> `ValueError` or argparse choices rejection.
- `mask_cell_size <= 0` -> `ValueError`.
- `stripe_width <= 0` -> `ValueError`.
- `stripe_alpha` or `glyph_alpha` outside `[0, 1]` -> `ValueError`.
- Non-`uint8 HxWx3` image/frame inputs -> `ValueError`.
- Missing CET6 PDF -> `FileNotFoundError` with the expected path.
- `pdf_page <= 0` or page beyond PDF length -> `ValueError`.
- No `pypdfium2` and no `pdftoppm` -> `RuntimeError` explaining the PDF rendering dependency.

### 5. Good/Base/Bad Cases
- Good: `python main.py playback --n 4 --anti-ocr-profile strong` shows OCR suppression parameters in HUD, keeps small text readable by default, and keeps the hot loop lightweight.
- Good: `python main.py playback --demo cet6 --pdf-page 1 --width 900 --height 1280 --n 4` renders the first CET6 PDF page as a portrait playback demo without stretching.
- Good: `python main.py playback --demo cet6 --pdf-page 1 --width 900 --height 1280 --n 4 --anti-ocr-profile vlm` uses the VLM stress defaults and records them in HUD/metadata.
- Base: if a user passes `--anti-ocr-profile strong --inversion` or `--anti-ocr-profile vlm --inversion`, playback suppresses the inversion slot for readability and records that suppression in metadata/HUD.
- Base: existing `python main.py playback --n 4` stays visually/mathematically equivalent to the previous playback path.
- Bad: stretching an A4 PDF page into the 1280x720 canvas and making text unreadable.
- Bad: enabling strong artifacts by default and breaking existing visual-completeness tests.
- Bad: adding random `% n` cell assignment instead of reusing `MaskGenerator` rejection-sampled output.

### 6. Tests Required
- Assert `--demo cet6` and `--pdf-page` parse into `PlaybackConfig`.
- Assert PDF/demo images are fitted to canvas with preserved aspect ratio.
- Assert explicit `anti_ocr_profile="off"` matches the default output.
- Assert cell masks are deterministic, mutually exclusive, complete, and spatially enlarged.
- Assert strong mode changes generated subframes and records metadata.
- Assert VLM mode uses stronger defaults than strong, changes generated subframes, and records metadata.
- Assert strong mode disrupts integrated glyph/saliency regions enough to affect OCR-oriented averages.
- Assert VLM mode disrupts integrated glyph/saliency regions more than default strong mode.
- Assert default strong mode preserves text contrast so the human-readable demo does not regress.
- Assert strong and VLM modes suppress requested equal-duration inversion and keep `per_cycle_slots == n`.
- Assert CLI parsing covers the profile and all tunable parameters.

### 7. Wrong vs Correct
#### Wrong
```python
masks = [(np.random.randint(n, size=(h, w)) == k) for k in range(n)]
frames = [apply_artifacts(surface) for surface in surfaces]  # inside playback loop
```

#### Correct
```python
masks = generate_cell_masks(w, h, n, cycle, cell_size, key=gen.key)
frame = apply_anti_ocr_artifacts(precomputed_frame, image, saliency, cycle, slot, ...)
```

## Scenario: HDR Compensation Integration

### 1. Scope / Trigger
- Trigger: `SubframeComposer(hdr_mode=True)` composes HDR-compensated subframes and evaluates visual integration against the original content.

### 2. Signatures
- `SubframeComposer(n, ..., hdr_mode=False, peak_nits=1000.0, content_peak_nits=100.0)`
- `SubframeComposer.compose(image, masks, sub_noises=None) -> list[np.ndarray]`
- `SubframeComposer.integrate_subframes(subframes, boost=None, pedestal=0.0) -> np.ndarray`
- `hdr_compensate(subframe_linear, n, peak_nits=1000.0, content_peak_nits=100.0) -> np.ndarray`

### 3. Contracts
- HDR composition stores subframes as SDR preview pixels that encode display luminance normalized to `peak_nits`.
- HDR visual integration must decode preview pixels back to linear peak-normalized luminance, average subframes, then multiply by `peak_nits / content_peak_nits` before converting to SDR for comparison.
- Do not use the SDR default `boost = n / gamma` for HDR integration; it treats HDR preview pixels as ordinary SDR values and under-restores bright content.
- `peak_nits` and `content_peak_nits` must be positive.

### 4. Validation & Error Matrix
- `peak_nits <= 0` -> `ValueError`.
- `content_peak_nits <= 0` -> `ValueError`.
- `peak_nits / content_peak_nits < n` -> bright HDR content may clip; tests should either use adequate headroom or assert clipping explicitly.

### 5. Good/Base/Bad Cases
- Good: `n=4`, `peak_nits=1000`, `content_peak_nits=100` restores mid-gray and white after HDR integration within small quantization error.
- Base: SDR mode still uses the existing `boost = n / gamma` integration model.
- Bad: HDR tests only assert that `compose()` returns `uint8` subframes without checking integrated luminance.

### 6. Tests Required
- Assert PQ/HLG round-trips remain in tolerance.
- Assert HDR `compose()` returns valid subframes.
- Assert HDR `integrate_subframes()` restores content luminance when headroom allows.
- Assert white content remains near white after HDR integration with sufficient headroom.

### 7. Wrong vs Correct
#### Wrong
```python
subframes = SubframeComposer(n=4, hdr_mode=True).compose(img, masks)
integrated = SubframeComposer(n=4, hdr_mode=True).integrate_subframes(subframes, boost=4)
```

#### Correct
```python
composer = SubframeComposer(n=4, hdr_mode=True, peak_nits=1000, content_peak_nits=100)
subframes = composer.compose(img, masks)
integrated = composer.integrate_subframes(subframes)
```

## Scenario: Disclosure Gap Experiments

### 1. Scope / Trigger
- Trigger: adding PoC coverage for a technical-disclosure gap such as off-axis capture, learned reconstruction, HLG/ALS, bandwidth checks, pregeneration, or config persistence.

### 2. Signatures
- `CameraSimulator.off_axis_temporal_average_attack(subframes, angle_degrees=..., regions=..., cycles=...) -> np.ndarray`
- `NoiseInjector.split_complementary_spatial(noise_base, tile=1) -> list[np.ndarray]`
- `train_tiny_unet_reconstructor(pairs, epochs=..., size=...) -> tuple[object, dict]`
- `compute_bandwidth_gbps(width, height, refresh_rate, bpp=4, overhead=1.2) -> float`
- `PrivacyDisplayConfig.load/save(path)` and `main.py window <config.json>`

### 3. Contracts
- Experiments must persist bounded JSON summaries under `experiments/results/`.
- Single-frame and full-cycle attack results must be reported separately; do not use full-cycle recovery to claim single-frame failure or vice versa.
- Learned attacks are PoC lower bounds unless trained and evaluated on a broad dataset; document weak results honestly.
- Heavy model paths must fail soft or be optional in unit tests.
- Runtime config persistence must validate n, epsilon, gamma_factor, inversion_alpha, refresh rate, and 32-byte key material.

### 4. Validation & Error Matrix
- Empty subframe list -> raise `ValueError`.
- Invalid config values -> raise `ValueError`.
- Torch/CV unavailable for learned reconstruction -> return a fallback reconstructor and metadata with `available=False`.
- Unknown target model with tesseract omitted from configured targets -> fall back to the first configured spec, not a missing tesseract key.

### 5. Good/Base/Bad Cases
- Good: each new disclosure interface has a pure unit test plus a reproducible experiment result if it is an experimental claim.
- Base: optional heavy dependencies are exercised by smoke tests with small inputs.
- Bad: documenting a disclosure claim as complete when there is only a helper function and no test or result artifact.
- Bad: regenerating a result JSON by hand instead of running the experiment script.

### 6. Tests Required
- Off-axis capture changes the reconstructed frame and preserves shape.
- Spatial complementary noise has per-pixel zero-sum and local checkerboard cancellation.
- HLG round-trips within floating point tolerance.
- Bandwidth/interface decisions match known DP/HDMI capacities.
- Config save/load round-trips key material and window kwargs, including gamma_factor/inversion_alpha separation.

### 7. Wrong vs Correct
#### Wrong
```python
report["g5"] = "implemented"
```

#### Correct
```python
report["g5"] = {
    "script": "experiments/unet_reconstruction.py",
    "ssim": measured_ssim,
    "scope": "tiny U-Net lower bound",
}
```

---

## Testing Requirements

<!-- What level of testing is expected -->

- Add regression tests for bounded-random rejection paths, including a value in the rejected tail.
- Add pure-function tests for display safety decisions, such as hardware refresh-rate constraint handling and black/inversion frame selection, so the behavior is covered without opening a GUI window.
- Add regression tests for adversarial noise source selection, template metadata persistence, and online OCR monitoring callbacks.

---

## Code Review Checklist

<!-- What reviewers should check -->

(To be filled by the team)
