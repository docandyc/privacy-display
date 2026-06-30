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

## Scenario: Web Study Submission Backend

### 1. Scope / Trigger
- Trigger: `privacy-display/webstudy` adds or changes the Flask + SQLite user-study demo used to collect participant identity, refresh-rate covariates, typing performance, and ablation ratings.

### 2. Signatures
- Command: `python webstudy/server.py --host 127.0.0.1 --port 5000 --db webstudy/study.db`
- API: `POST /api/submit` with JSON `{participant, session, typing, ratings}`
- Page: `GET /admin`
- API: `GET /admin/data.json?token=...`
- API: `GET /admin/export.csv?token=...`
- API: `GET /admin/stats`
- DB tables: `participants`, `typing`, `ratings`
- Env: `WEBSTUDY_DB`, `WEBSTUDY_HOST`, `WEBSTUDY_PORT`, optional `WEBSTUDY_EXPORT_TOKEN`

### 3. Contracts
- `participant.student_id` and `participant.name` are required non-empty strings; optional fields include `glasses` and `major`.
- `session` must preserve measured display timing: `assumed_monitor_hz`, `refresh_hz`, `refresh_ok`, `refresh_samples`, and `mean_frame_ms`.
- `typing` must contain exactly two rows: one `control` and one `masked`; each row stores `target_text`, `typed_text`, accuracy metrics, `duration_s`, `n`, `requested_n`, and `components`.
- `ratings` must contain exactly four rows for the ablation conditions; each row stores 1-5 integer ratings for `readability`, `flicker`, `fatigue`, and `privacy`, plus `order_index`.
- CSV export is a long table with `row_type` set to `typing` or `rating`, repeating participant/session columns on each row.
- `/admin/data.json` returns `summary`, `participants`, `typing`, and `ratings`; event rows must expose parsed `mask_meta` so operators can stratify `temporal` vs `static_fallback` sessions without reparsing CSV.
- `/admin` is an operator dashboard over `/admin/data.json`; it must expose participant summaries, paired typing deltas, rating means, typing rows, rating rows, and CSV/JSON export links.

### 4. Validation & Error Matrix
- Missing participant object -> HTTP 400.
- Empty `student_id` or `name` -> HTTP 400.
- `typing` length not equal to 2 -> HTTP 400.
- Duplicate or unknown typing condition -> HTTP 400.
- `ratings` length not equal to 4 -> HTTP 400.
- Rating outside `[1, 5]` -> HTTP 400.
- `accuracy` outside `[0, 1]` -> HTTP 400.
- `WEBSTUDY_EXPORT_TOKEN` set and query token missing/mismatched -> HTTP 403 for admin JSON exports, CSV exports, and stats.

### 5. Good/Base/Bad Cases
- Good: run a debug browser session, submit once, then confirm `/admin/stats` reports one participant, two typing groups, and four rating groups.
- Good: open `/admin`, confirm the participant appears in the summary table, paired WPM delta is visible, and export links point to CSV/JSON endpoints.
- Base: low-refresh browser sessions are accepted but must preserve `refresh_ok=false` and the effective `n`/`requested_n` distinction.
- Bad: storing only aggregate WPM and dropping `target_text`/`typed_text`, because later analysis cannot audit scoring.
- Bad: exporting separate participant-only rows without event rows, because CSV consumers cannot join typing/rating outcomes without extra queries.
- Bad: requiring the operator to query raw SQLite manually during collection; the web backend must expose read-only summary/export endpoints.

### 6. Tests Required
- Assert valid payload submission returns 200 and inserts one participant, two typing rows, and four rating rows.
- Assert malformed payloads return 400 for missing identity, wrong typing count, wrong rating count, invalid rating, and invalid accuracy.
- Assert `/admin/export.csv` includes participant columns plus typing/rating event columns.
- Assert `/admin/data.json` includes participant summaries, paired typing deltas, parsed `mask_meta`, and the same row counts as the database.
- Assert `/admin` renders the dashboard tables and CSV/JSON export links in a browser.
- Assert token-protected admin endpoints reject missing or incorrect tokens when `WEBSTUDY_EXPORT_TOKEN` is set.

### 7. Wrong vs Correct
#### Wrong
```python
conn.execute("INSERT INTO typing (condition, wpm) VALUES (?, ?)", (condition, wpm))
```

#### Correct
```python
conn.execute(
    "INSERT INTO typing (participant_id, condition, target_text, typed_text, wpm, duration_s) "
    "VALUES (?, ?, ?, ?, ?, ?)",
    (participant_id, condition, target_text, typed_text, wpm, duration_s),
)
```

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
- `_parse_surya_text(result) -> str`
- `run_corpus_multi_engine(engines: list[str] | None = None) -> dict`

### 3. Contracts
- Auto-detection must only list an engine when importing the package and any cheap local availability check succeeds.
- Tesseract detection must configure `pytesseract.pytesseract.tesseract_cmd` from `TESSERACT_CMD`/`TESSERACT_EXE`, PATH, or the Windows default install dirs (`C:\Program Files\Tesseract-OCR\tesseract.exe`, `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`) before calling `get_tesseract_version()`.
- Unit tests must not instantiate OCR engines that download model weights; inject cached/fake readers for parser and dispatch tests.
- Images passed into OCR backends must be contiguous NumPy arrays.
- Surya must be pinned to `surya-ocr==0.14.7` for direct in-process inference; Surya 0.20+ uses a server-based API and is not compatible with this adapter.
- Surya should lazily construct one `RecognitionPredictor` and one `DetectionPredictor`, reuse them across images, and select the device through `SURYA_DEVICE=auto|cpu|cuda|mps`.
- Surya model files should use the project-local `.cache/surya` directory. On Windows, default model download concurrency to one worker because the upstream parallel downloader can trigger TLS EOF failures on constrained networks.
- The Windows model bootstrap should use `scripts/download_surya_models.ps1`, downloading to `.part` files with curl retries and resume support before renaming completed files into the cache expected by Surya.
- Windows PowerShell scripts must resolve external executables to one scalar path. For `curl.exe`, prefer `%SystemRoot%\\System32\\curl.exe`; fallback discovery must use `Get-Command -All | Select-Object -First 1` before reading `.Source`, because activated Conda environments can expose multiple `curl.exe` applications and PowerShell otherwise coerces their paths into one invalid command string.
- Surya output parsing must accept `OCRResult.text_lines[*].text` objects and equivalent dictionaries.
- Corpus result JSON must include the exact engine keys that were run, and documentation values should match that file after reruns.

### 4. Validation & Error Matrix
- Engine package import fails -> omit the engine from `engines` and keep other engines available.
- Tesseract Python package is installed but `tesseract.exe` is not on PATH -> try configured env/default executable paths before omitting the engine.
- Unsupported engine name in `recognize` -> raise `ValueError`.
- Surya output has no recognized text lines -> return an empty string rather than crashing.
- Heavy model download or runtime setup failure -> keep it out of unit tests; verify with an explicit integration command when the environment has cached models or network access.
- Multiple `curl.exe` entries on PATH -> select one executable explicitly and verify a real manifest download; do not invoke an array-valued `.Source` result.

### 5. Good/Base/Bad Cases
- Good: add an engine with parser-only regression tests plus one fake-reader dispatch test.
- Good: Windows machines with Tesseract installed under `C:\Program Files\Tesseract-OCR` are detected without requiring users to edit PATH.
- Base: existing Tesseract/EasyOCR behavior remains unchanged when Surya is unavailable.
- Bad: unit tests instantiate Surya predictors directly and trigger model downloads.
- Bad: hand-edit `corpus_multi_engine.json` without rerunning `run_corpus_multi_engine`.

### 6. Tests Required
- Assert `OCREvaluator().engines` includes the engine in an environment where the dependency is installed.
- Assert Windows default Tesseract install path is used when `tesseract` is not on PATH.
- Assert parser coverage for every supported output shape.
- Assert `recognize(..., engine)` uses a cached/fake reader and returns joined text.
- Run `pytest tests/ -q` and, for corpus changes, rerun `run_corpus_multi_engine(...)`.

### 7. Wrong vs Correct
#### Wrong
```python
result = RecognitionPredictor()([image], det_predictor=DetectionPredictor())
return result[0].text_lines[0].text
```

#### Correct
```python
if self._surya_readers is None:
    self._surya_readers = (
        RecognitionPredictor(device=device),
        DetectionPredictor(device=device),
    )
return self._parse_surya_text(
    self._surya_readers[0]([image], det_predictor=self._surya_readers[1])
)
```

## Scenario: Detection Suite Server Experiments

### 1. Scope / Trigger
- Trigger: adding or changing COCO/MOT object-detection, video-detection, or tracking experiment scripts and their server runner.

### 2. Signatures
- Command: `python experiments/coco_detection_attack.py --coco-root data/coco --models yolo26x,rtdetr-x,faster_rcnn,retinanet --device cuda:0`
- Command: `python experiments/mot_video_detection.py --mot-root data/MOT17 --device cuda:1`
- Command: `python experiments/mot_tracking_attack.py --mot-root data/MOT17 --device cuda:0`
- Command: `bash scripts/run_detection_suite.sh`
- Dataset paths: `data/coco/val2017`, `data/coco/annotations/instances_val2017.json`, `data/MOT17/train/MOT17-*/img1`, `data/MOT17/train/MOT17-*/gt/gt.txt`

### 3. Contracts
- Experiment JSON files must be written under `experiments/results/` unless `--output-dir` or `RESULTS_DIR` overrides it.
- `COCO_ROOT`, `MOT17_ROOT`, `RESULTS_DIR`, `MODELS`, `ATTACKS`, `COCO_DEVICE`, `MOT_DEVICE`, `TRACK_DEVICE`, `SMOKE`, `COCO_MAX_IMAGES`, `MOT_MAX_FRAMES`, `MOT_SEQUENCES`, `NO_EXTERNAL_TRACKER`, `NO_HOTA`, and `TRACKEVAL_ROOT` are supported server-runner environment keys.
- Each experiment result is shaped as `{config, detectors, results}`, with `results[model][attack]` holding scalar metrics.
- MOT tracking should prefer BoxMOT ByteTrack when available and fall back to a deterministic tracker for local tests.
- TrackEval HOTA runs against a local checkout pointed to by `TRACKEVAL_ROOT`; keep the project NumPy stack compatible with the rest of the thesis environment, and use a local venv compatibility shim for TrackEval's removed NumPy aliases (`np.float`, `np.int`, etc.) instead of downgrading NumPy.

### 4. Validation & Error Matrix
- Missing COCO annotations -> `FileNotFoundError` naming `instances_<split>.json`.
- Missing MOT split/image directory -> `FileNotFoundError` naming the missing MOT path.
- Unknown detector spec -> `ValueError`.
- Missing optional heavy evaluator dependency in local tests -> fall back to deterministic simple metrics or tracker instead of failing the unit path.
- `TRACKEVAL_ROOT` unset or missing `scripts/run_mot_challenge.py` -> HOTA remains unavailable with a recorded reason while MOTChallenge files are still exported.
- NumPy 2.x with unpatched TrackEval aliases -> configure a venv-local `sitecustomize.py` alias shim or equivalent before running the HOTA subprocess.

### 5. Good/Base/Bad Cases
- Good: run `SMOKE=1 MOT_SEQUENCES=MOT17-02 bash scripts/run_detection_suite.sh` after datasets are placed to verify server setup cheaply.
- Good: run full suite with `COCO_DEVICE=cuda:0 MOT_DEVICE=cuda:1 TRACK_DEVICE=cuda:0 bash scripts/run_detection_suite.sh`.
- Good: verify TrackEval with a tiny exported MOTChallenge workspace before launching the full suite; the subprocess should return `available=True` and parse `hota`, `deta`, and `assa`.
- Base: local tests inject fake detectors and tiny COCO/MOT fixtures without downloading weights or datasets.
- Bad: writing separate result schemas per script, because publication summary and manifest cannot consume them uniformly.
- Bad: requiring BoxMOT in unit tests, because local machines may not have compiled tracker dependencies.
- Bad: installing TrackEval's old pinned requirements by downgrading NumPy/SciPy/OpenCV in the project venv, because it can break the rest of the detection/OCR stack.

### 6. Tests Required
- Assert detector adapters normalize YOLO/RT-DETR and torchvision outputs to `DetectionBox`.
- Assert COCO, MOT detection, and MOT tracking scripts emit the expected `model -> attack -> metrics` schema on tiny fixtures.
- Assert publication summary renders COCO, MOT video detection, and MOT tracking rows when result JSON files exist.
- Assert reproducibility manifest records the detection result files, scripts, and server commands.
- Assert `tests/test_trackeval_export.py` passes after TrackEval environment changes, and run a tiny real TrackEval subprocess when changing the server environment.

### 7. Wrong vs Correct
#### Wrong
```bash
python experiments/mot_tracking_attack.py --mot-root /tmp/MOT17
# assumes boxmot is always installed and crashes local tests if it is not
```

#### Correct
```bash
SMOKE=1 MOT_SEQUENCES=MOT17-02 bash scripts/run_detection_suite.sh
# uses BoxMOT ByteTrack on the server when available, with a local fallback for tests
```

## Scenario: Real Camera Capture Ablation Orchestration

### 1. Scope / Trigger
- Trigger: adding or changing Windows/macOS/Linux real-camera capture, calibration, playback orchestration, or OCR summary code for `privacy-display` physical-device ablation experiments.

### 2. Signatures
- Command: `python experiments/real_capture_shoot.py --list [--backend msmf|dshow|avfoundation|v4l2|any]`
- Command: `python experiments/real_capture_shoot.py --probe --device 1 --backend dshow`
- Command: `python experiments/real_capture_calibrate.py --select-roi --pos d0.5_a0 --backend dshow`
- Command: `python experiments/real_capture_calibrate.py --calibrate-exposure --backend dshow`
- Command: `python experiments/real_capture_ablation.py --study {1,2,3,all} --dry-run`
- Command: `python experiments/real_capture_ablation.py --study 1 --subset-size 1 --attacks short --conditions original,deployed --backend dshow --analyze`
- Command: `python experiments/real_capture_ablation.py --study all --subset-size 120 --backend dshow --analyze`
- Timeout CLI: `--playback-timeout 300 --preflight-timeout-margin 300 --playback-shutdown-timeout 300` by default; callers may increase them further on slow machines.
- Windows helper: `scripts\run_real_capture_ablation_windows.bat [dry-run|calibrate-roi|calibrate-exposure|full]` where `dry-run` and `full` use `--subset-size 120`.
- Playback command contract: `python main.py playback --image <png> --width 2560 --height 1600 --n 4 --fullscreen [condition flags]` prints `PLAYBACK_READY` before captures start.

### 3. Contracts
- `real_capture_shoot.get_camera_backends(system="Windows")` must prefer `msmf` then `dshow`; macOS uses `avfoundation`; Linux uses `v4l2`.
- DirectShow exposure values are log2 seconds (`-8 ~= 1/256s`, `-6 ~= 1/64s`); metadata should include both the requested OpenCV value and `exposure_s` when known.
- `condition` remains a backward-compatible string such as `deployed|short`; structured optional fields must include `ablation`, `attack`, `profile`, `stripe_alpha`, `glyph_alpha`, `inversion_alpha`, `playback_cmd`, and `roi_pos`.
- Dry-run paths must not open a camera or pygame window; they only load corpus metadata, build plans, and print counts.
- Default all-study planning must stay bounded: study 1 uses about 12 stratified samples; studies 2 and 3 use about 5 unless `--subset-size` overrides.
- Video attacks should save attacker-friendly derived frames (`single_best`, `temporal_mean`, `window_mean_best`, `max_proj`) rather than raw bursts only.
- Real-capture playback startup defaults must be slow-machine friendly: wait about five minutes for `PLAYBACK_READY`, add about five minutes of margin around preflight benchmark subprocesses, and wait five minutes before killing a terminated playback process.

### 4. Validation & Error Matrix
- Unknown camera backend -> `ValueError` before opening hardware.
- Unknown attack or condition for a study -> `ValueError` during plan construction.
- Missing ROI calibration -> capture raw frames and preserve `roi_pos`; do not fail the run.
- ROI rectification -> scale the saved homography from calibration `image_shape` to the current frame resolution before warping, because calibration preview and capture frames may differ between 1080p and 4K.
- Missing exposure calibration -> skip manual exposure for that attack and leave `exposure_s` null unless provided.
- Metadata merge writes -> use same-directory temp JSON plus atomic replace with bounded retry, so transient Windows file-open errors do not abort long capture runs or leave partial metadata files.
- Preflight playback benchmark timeout -> record the command/stdout tail, set measured fps to null, and continue with a manual verification warning.
- Capture playback exits or times out before `PLAYBACK_READY` -> terminate the playback process, report group/command/stdout context, and return a controlled non-zero code instead of raising a traceback.
- Playback hot-swap control file is updated but the requested `epoch` is not acknowledged -> fail the current run before opening/grabbing the camera for that sample.
- Empty video frame list -> `ValueError` from offline video attack helper.

### 5. Good/Base/Bad Cases
- Good: run `--study all --dry-run` first and verify the plan size before opening camera hardware.
- Good: run the one-sample smoke command before full study collection to prove `original|short` can be read and `deployed|short` suppresses recovery.
- Base: run without ROI calibration; metadata remains usable, but notes should make the missing rectification auditable.
- Bad: starting capture after a fixed sleep only; playback must expose `PLAYBACK_READY` so camera timing is deterministic.
- Bad: after a persistent playback process is running, switching `frames_dir` and then starting capture after only `sleep(settle)`; hot-swaps must acknowledge the requested epoch (for example through an ack file in the control payload) before the camera grabs frames.
- Bad: leaving playback HUD enabled for camera-captured benchmark frames; HUD overlays contaminate object-detection and tracking metrics.
- Bad: changing `condition` to a nested object only, because existing real-capture analysis groups by string condition.
- Bad: letting default all-study planning expand to the full 120-image corpus without an explicit `--subset-size`.

### 6. Tests Required
- Assert Windows backend preference and backend-specific auto-exposure values.
- Assert DirectShow log2 exposure conversion.
- Assert playback CLI parses `--fullscreen`, `--show-original`, and `--inversion-alpha 1.0`.
- Assert study plan sizes, condition filtering, geometry matrix positions, and default bounded all-study behavior.
- Assert persistent playback hot-swaps wait for the requested epoch acknowledgement and time out if it never arrives.
- Assert real-capture playback commands disable HUD overlays.
- Assert letterbox padding preserves aspect ratio with black borders.
- Assert ROI rectification still selects the same screen region when capture resolution differs from the calibration frame shape.
- Assert metadata merge retries a transient `OSError` during JSON write and preserves existing plus new capture entries.
- Assert preflight playback benchmark timeout returns a null fps measurement with diagnostic output instead of raising `TimeoutExpired`.
- Assert capture playback readiness timeout returns a controlled non-zero result with group and command diagnostics instead of raising `TimeoutError`.
- Assert timeout parser defaults remain slow-machine friendly.
- Assert offline video attack helpers return all expected derived frame keys.
- Assert structured metadata fields survive into `summarize_real_capture_rows(...)[by_ablation_attack]`.

### 7. Wrong vs Correct
#### Wrong
```python
time.sleep(5)
capture_once(cap, args, condition="deployed", ...)
```

#### Correct
```python
proc = subprocess.Popen(playback_cmd, stdout=subprocess.PIPE, text=True)
wait_for_playback_ready(proc, timeout=300)
frames = grab_frames(cap, count=attack.burst, interval=attack.interval)
entry = build_metadata_entry(item, playback_cmd=playback_cmd, ...)
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
- Command: `.venv-surya/bin/python -c "from src.evaluation.benchmark import run_corpus_multi_engine; run_corpus_multi_engine(engines=['tesseract','easyocr','surya'], merge_existing=True)"`

### 3. Contracts
- The default corpus is deterministic and publication-facing: 12 base templates times 10 variants, for 120 generated images.
- `build()` must write `data/test_images/*.png`, `ground_truth.json`, and `corpus_metadata.json`.
- `ground_truth.json` maps sample names to single-line ground-truth text.
- `corpus_metadata.json` uses the same sample keys and must include `truth`, `category`, `language`, `layout`, `font_size`, `variant`, `width`, and `height`.
- `load_corpus()` must preserve the existing return contract `(images, truths, names)` for older benchmark callers.
- `load_corpus_metadata()` must return `{}` rather than failing when older corpora do not have metadata.
- `run_corpus_multi_engine()` must persist `experiments/results/corpus_multi_engine.json` and include `n_samples`, `n_categories`, overall mean/std fields, per-field `strata`, and per-sample rows.
- `engines=None` means run every locally available engine; `engines=[]` means run no new engines and is valid when testing merge behavior.
- `merge_existing=True` must load any existing `corpus_multi_engine.json` and preserve engine entries not requested in the current run. This prevents a long EasyOCR/Surya run from deleting already verified Tesseract results.
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
- Base: run EasyOCR/Surya with `merge_existing=True` so their results are added without deleting Tesseract.
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
.venv-surya/bin/python -c "from src.evaluation.benchmark import run_corpus_multi_engine; run_corpus_multi_engine(engines=['tesseract','easyocr','surya'], merge_existing=True)"
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

## Scenario: Online VLM Readability Evaluation

### 1. Scope / Trigger
- Trigger: adding an online vision-language model as an attack evaluator for camera-captured protected frames.

### 2. Signatures
- `image_to_data_url(image: np.ndarray) -> str`
- `extract_json_object(text: str) -> dict`
- `VLMClient(api_key=None, base_url="https://api.siliconflow.cn/v1", model="Qwen/Qwen3-VL-32B-Instruct", timeout=60.0, transport=None)`
- `VLMClient.analyze_image(image, ground_truth="", prompt=None, max_tokens=256) -> dict`
- `build_vlm_attack_frames(image, n=4, epsilon=8/255, cycles=2, cycle_start=0, attacks=None, with_noise=True) -> dict`
- `select_stratified_samples(names, metadata, samples_per_category=1, max_samples=None) -> list[int]`
- `run_vlm_benchmark(client=None, output_dir="experiments/results", n=4, epsilon=8/255, cycles=2, samples_per_category=1, max_samples=None, attacks=None, save=True, corpus=None, metadata=None) -> dict`
- Command: `python experiments/vlm_readability_analysis.py --samples-per-category 1`

### 3. Contracts
- API keys must come only from the `SILICONFLOW_API_KEY` environment variable or an in-memory constructor argument for tests; never store keys in source, docs, command examples, logs, or JSON result files.
- The SiliconFlow request must use the OpenAI-compatible `POST {base_url}/chat/completions` payload with `model`, `messages`, `temperature=0`, `max_tokens`, and `response_format={"type":"json_object"}`.
- VLM image inputs must be sent as PNG `data:image/png;base64,...` URLs inside a user message content list.
- Ground truth must not be sent to the VLM prompt. It is used only locally to calculate `text_recovery_metrics(visible_text, ground_truth)`.
- The model must be instructed to return JSON only with `visible_text`, `can_read_sensitive`, `confidence`, and `notes`.
- Corpus VLM reports must include model/base_url, sample-selection config, attack name, metadata, `visible_text` preview, recovery metrics, confidence, row-level errors, per-attack summaries, and best-attacker summaries.
- Corpus VLM summaries must include `call_status` with total, successful, and failed call counts. If every row failed, the live CLI must return nonzero after writing the diagnostic JSON.
- Result JSON must not include authorization headers, API keys, full request payloads, or any secret-bearing environment values.
- Unit tests must use a fake transport/client; online calls are explicit integration runs only.

### 4. Validation & Error Matrix
- Missing API key in normal client use -> `ValueError` mentioning `SILICONFLOW_API_KEY` but not any key value.
- Non-2xx API response -> `RuntimeError` with sanitized status/body and no authorization header.
- Malformed VLM JSON -> `ValueError` from JSON extraction, recorded as row-level `vlm_error` in corpus runs.
- `samples_per_category <= 0` -> `ValueError`.
- `max_samples <= 0` when provided -> `ValueError`.
- Unknown requested attack name -> `ValueError`.
- Per-row VLM failure during corpus benchmark -> record empty visible text, zero/derived recovery metrics, and continue.
- All live VLM rows fail due API/DNS/parse errors -> write diagnostic JSON, set `call_status.all_calls_failed=True`, and return nonzero so scripts do not treat zero recovery metrics as valid evidence.

### 5. Good/Base/Bad Cases
- Good: dry-run command reports the selected samples and attack calls without requiring an API key.
- Good: fake transport test asserts the request contains an image URL data URL and no ground-truth text.
- Base: live command reads `SILICONFLOW_API_KEY` from the shell environment and writes `experiments/results/vlm_qwen3_siliconflow.json`.
- Base: some VLM rows fail, but successful rows remain summarized and the failure count is visible.
- Bad: adding `--api-key` CLI flags, hard-coding a key, or putting a secret in README examples.
- Bad: sending the ground-truth text to the VLM prompt and then using its answer as a readability metric.
- Bad: citing a 0.0% VLM recovery rate from a result file where all rows have `vlm_error`.

### 6. Tests Required
- Assert `image_to_data_url` emits a PNG data URL for uint8 arrays.
- Assert `extract_json_object` parses direct and fenced JSON responses.
- Assert `VLMClient` builds the expected OpenAI-compatible payload through a fake transport, excludes ground truth from the prompt, and computes local recovery metrics.
- Assert missing API key raises a sanitized `ValueError`.
- Assert stratified sample selection is deterministic by metadata category.
- Assert `run_vlm_benchmark` works with an injected fake client, writes JSON, and contains no secret fields.
- Assert VLM row summaries report call-status counts and all-failed state.
- Run `pytest tests/test_vlm_evaluator.py tests/test_vlm_benchmark.py -q` after changing VLM paths.
- Run `pytest tests/ -q` before citing VLM scaffolding in publication-facing docs.

### 7. Wrong vs Correct
#### Wrong
```python
payload["messages"][1]["content"] = f"Ground truth is {ground_truth}; can you read it?"
api_key = "<hard-coded-secret>"
```

#### Correct
```python
payload["messages"][1]["content"] = [
    {"type": "text", "text": "Transcribe only visible text and return JSON."},
    {"type": "image_url", "image_url": {"url": image_to_data_url(frame)}},
]
api_key = os.environ["SILICONFLOW_API_KEY"]
```

## Scenario: Publication Result Summary

### 1. Scope / Trigger
- Trigger: consolidating experiment artifacts into thesis or IEEE Access tables.

### 2. Signatures
- `build_publication_summary(results_dir="experiments/results") -> dict`
- `render_markdown(summary: dict) -> str`
- `write_publication_summary(results_dir="experiments/results", summary=None) -> dict`
- Command: `python experiments/publication_summary.py --results-dir experiments/results`
- Output files: `experiments/results/publication_summary.json`, `experiments/results/publication_summary.md`

### 3. Contracts
- The summary builder must only read existing machine-readable result artifacts; it must not rerun experiments, call online services, or require API keys.
- Required source files are `corpus_multi_engine.json` and `corpus_strong_camera_attack.json`; optional files are `detection_attack_yolo.json`, `view_attack.json`, and `vlm_qwen3_siliconflow.json`.
- The generated JSON must include `source_files`, `ocr`, `strong_camera`, `detection`, `view_attack`, and `vlm` sections.
- Missing optional result files must be represented explicitly as `available=False` with a reason, not silently omitted.
- Missing VLM output must say the online benchmark is implemented but no live result has been generated; thesis text must not cite VLM numbers until the file exists.
- A VLM result file where every sample row has `vlm_error` must be represented as `available=False`, `reason=all_calls_failed`; thesis/paper text must not cite its zero recovery metrics.
- Markdown percentages must be derived from the loaded JSON values, including confidence intervals where present.
- Paper/thesis tables should be updated from `publication_summary.{json,md}` rather than hand-copying from multiple raw result files.

### 4. Validation & Error Matrix
- Missing required OCR or strong-camera result -> normal file error; do not synthesize placeholder values.
- Missing optional detection/view/VLM result -> keep summary generation successful and mark that section unavailable.
- Real-capture COCO/MOT result exists but lacks `real_clean`, has zero shared samples, mismatched attack sample counts, or `capture.coverage.complete=false` -> keep summary generation successful and mark that real-capture section unavailable with an explicit reason.
- Optional VLM result exists but all rows failed -> keep summary generation successful and mark VLM unavailable with an explicit all-failed interpretation.
- Older result JSON missing CI fields -> render mean-only percentages instead of failing.
- Unknown extra OCR engines or attack names -> include them after the known ordered entries.

### 5. Good/Base/Bad Cases
- Good: rerun experiments, then run `python experiments/publication_summary.py`, then update thesis tables from the generated Markdown.
- Good: VLM result is absent and the summary explicitly records that no live VLM number should be cited.
- Good: real-capture COCO/MOT sections are rendered only when every model/attack row has the same positive captured sample count and includes a `real_clean` baseline.
- Good: VLM result file exists only as an API-error diagnostic and the summary says it is not available for citation.
- Base: detection or view-attack result is absent in a lightweight environment, but OCR and strong attack summaries still render.
- Bad: editing `publication_summary.md` by hand while raw JSON disagrees.
- Bad: copying OCR values into the thesis from console logs instead of the generated summary.
- Bad: treating an all-error VLM JSON file as proof that the VLM could not read the protected frame.

### 6. Tests Required
- Assert summary building reads minimal OCR and strong-camera fixtures and reports expected means.
- Assert missing optional VLM/view result files are marked unavailable.
- Assert all-error VLM result files are marked unavailable and rendered as not citable.
- Assert real-capture COCO/MOT result files with incomplete coverage, missing `real_clean`, zero samples, or mismatched attack counts are marked unavailable and not rendered as citable tables.
- Assert Markdown includes OCR, strong-camera, detection, view, and VLM sections.
- Assert `write_publication_summary` writes both JSON and Markdown outputs.
- Run `pytest tests/test_publication_summary.py -q` after changing the summary builder.
- Run `python experiments/publication_summary.py` before updating publication-facing tables.

### 7. Wrong vs Correct
#### Wrong
```python
README_TABLE = "Tesseract | 94.0% | 0.0%"
```

#### Correct
```bash
python experiments/publication_summary.py
sed -n '1,120p' experiments/results/publication_summary.md
```

## Scenario: Reproducibility Manifest

### 1. Scope / Trigger
- Trigger: adding or changing publication-facing experiment scripts, result files, dependency assumptions, or online-service evaluation paths that must be reproducible from an archived project state.

### 2. Signatures
- `sha256_file(path: Path) -> str`
- `file_record(project_root: Path, relative_path: str) -> dict`
- `package_versions(package_names: list[str] | None = None) -> dict`
- `git_metadata(project_root: Path) -> dict`
- `build_reproducibility_manifest(project_root=".", result_files=None, source_files=None, timestamp=None) -> dict`
- `write_reproducibility_manifest(project_root=".", output_path="experiments/results/reproducibility_manifest.json", manifest=None) -> dict`
- Command: `scripts/reproduce_all.sh`
- Command: `scripts/reproduce_all.sh --full-offline`
- Command: `scripts/reproduce_all.sh --with-vlm-live`
- Command: `python experiments/reproducibility_manifest.py`
- Output file: `experiments/results/reproducibility_manifest.json`

### 3. Contracts
- The manifest must record environment metadata, canonical reproduction commands, Git commit/branch/dirty state, and SHA-256/byte-size records for publication-facing result and source files.
- Secret values must never be read into or written by the manifest. Online VLM evaluation may list required environment variable names such as `SILICONFLOW_API_KEY`, but not their values.
- The live VLM command entry must declare `requires_env=["SILICONFLOW_API_KEY"]` and a secret policy note; README examples must use placeholders only.
- `result_files=[]` and `source_files=[]` are valid explicit empty lists for unit tests and should not be replaced with defaults; defaults apply only when the argument is `None`.
- Missing result/source files must be represented as `exists=False`, empty `sha256`, and zero bytes rather than failing manifest generation.
- Absolute output paths must be respected; relative output paths are resolved against `project_root`.
- Regenerate the manifest after rerunning experiments or changing code that it hashes, otherwise the file hashes no longer describe the current archive.
- Real-capture COCO/MOT detection/tracking manifests are publication provenance artifacts; include the planned capture manifests in the reproducibility manifest alongside the metric JSON files.
- When large real-capture image trees already live in position-specific directories, do not duplicate gigabytes of image data just to satisfy a canonical path. Instead, write a canonical manifest such as `experiments/results/real_capture_mot_capture_manifest.json`, rewrite each capture `path` to the actual existing image location, and point metric JSON `capture.manifest_path` plus embedded `capture.manifest` to that canonical manifest.
- `scripts/reproduce_all.sh` is the publication artifact orchestrator. Its default path must stay offline and bounded: tests, VLM dry-run, publication summary, and reproducibility manifest only.
- Heavy offline experiments must require `--full-offline`; live online VLM calls must require `--with-vlm-live` plus `SILICONFLOW_API_KEY` in the environment.
- The orchestrator must never accept an API key as a positional argument or CLI flag.
- The orchestrator may source a local `.env.local` file, but that file must be gitignored. Only `.env.example` with placeholders may be committed.

### 4. Validation & Error Matrix
- Missing optional result file -> record `exists=False` and continue.
- Running outside a Git repository -> return empty commit/branch and `dirty=False`; do not fail.
- Package not installed -> record that package version as `None`.
- Unreadable file path in a required test fixture -> normal file error for `sha256_file`, because that helper is direct hash IO.
- Environment contains an API key -> generated manifest must not contain the key value.

### 5. Good/Base/Bad Cases
- Good: run `scripts/reproduce_all.sh`, then archive generated summary, manifest, and raw result JSON.
- Good: run `python experiments/publication_summary.py`, then `python experiments/reproducibility_manifest.py`, then archive both generated files with raw result JSON.
- Good: manifest shows VLM live benchmark requires `SILICONFLOW_API_KEY` but contains no authorization headers, key values, or request payloads.
- Good: finalize real-capture artifacts by merging per-position OCR reports and writing a canonical MOT capture manifest whose paths resolve to the existing capture image directory.
- Base: lightweight environments without a live VLM output still generate a manifest with `vlm_qwen3_siliconflow.json` marked missing.
- Bad: putting API keys into README examples, CLI flags, JSON outputs, or manifest command strings.
- Bad: committing `.env.local` or any file containing a real `sk-...` secret.
- Bad: editing a result JSON after generating the manifest and then using stale hashes as archival evidence.
- Bad: copying a multi-gigabyte MOT capture directory only to make a stale manifest path exist, or leaving metric JSON pointing at a missing capture manifest.

### 6. Tests Required
- Assert file records include SHA-256, byte size, and missing-file placeholders.
- Assert explicit empty `result_files=[]` and `source_files=[]` stay empty.
- Assert command metadata includes the live VLM environment requirement.
- Assert a fake `SILICONFLOW_API_KEY` in the process environment does not appear in `json.dumps(manifest)`.
- Assert nested relative output paths are created by `write_reproducibility_manifest`.
- Assert real-capture finalization records the canonical MOT capture manifest and position-matrix OCR result paths.
- Run `bash -n scripts/reproduce_all.sh` after changing the orchestration script.
- Run `scripts/reproduce_all.sh --skip-tests` to verify the default non-network artifact refresh path when script behavior changes.
- Run `pytest tests/test_reproducibility_manifest.py -q` after changing manifest code.
- Run `python experiments/reproducibility_manifest.py` after updating publication-facing result files.

### 7. Wrong vs Correct
#### Wrong
```python
manifest["api_key"] = os.environ["SILICONFLOW_API_KEY"]
result_files = result_files or RESULT_FILES
```

#### Correct
```python
manifest["secret_policy"] = {
    "record_secret_values": False,
    "secret_env_vars": ["SILICONFLOW_API_KEY"],
}
if result_files is None:
    result_files = RESULT_FILES
```

## Scenario: Real Camera Capture Analysis

### 1. Scope / Trigger
- Trigger: adding or changing analysis for manually collected phone, smart-glasses, or camera photos/video frames used as publication evidence.

### 2. Signatures
- `write_capture_template(capture_dir="experiments/real_captures", filename="metadata_template.json") -> Path`
- `load_capture_metadata(capture_dir="experiments/real_captures", metadata_file="metadata.json") -> list[dict]`
- `run_real_capture_ocr(capture_dir="experiments/real_captures", metadata_file="metadata.json", output_dir="experiments/results", engines=None, evaluator=None, ocr_timeout=10.0, save=True) -> dict`
- `summarize_real_capture_rows(rows: list[dict]) -> dict`
- `render_real_capture_markdown(report: dict) -> str`
- Command: `python experiments/real_capture_analysis.py --init-template`
- Command: `python experiments/real_capture_analysis.py --engines tesseract`
- Output files: `experiments/results/real_capture_ocr.json`, `experiments/results/real_capture_ocr.md`

### 3. Contracts
- The module analyzes manually collected image files only; it must not claim that real hardware was tested unless `metadata.json` and referenced capture files exist.
- Metadata entries must include `id`, `image`, and exact `truth`; publication-grade entries should also include device, camera type, capture mode, distance, angle, exposure, frame rate, display refresh rate, n, epsilon, lighting, and notes.
- Missing real-capture result files must be marked unavailable in publication summaries, not silently omitted or replaced with simulated results.
- OCR rows must include engine, condition, device, capture mode, geometry/exposure metadata, recognized-text preview, OCR errors, character accuracy, word accuracy, exact-match, sensitive-token recall, and sensitive-token denominator.
- Summaries must keep real captures grouped by condition, device, and engine so reviewers can distinguish original/protected/short-exposure/video-frame cases.
- Unit tests must use tiny local images and fake OCR evaluators; they must not require camera hardware or heavyweight OCR downloads.

### 4. Validation & Error Matrix
- Missing `metadata.json` in analysis mode -> `FileNotFoundError`.
- Metadata without a list-valued `captures` field -> `ValueError`.
- Capture entry missing `id`, `image`, or `truth` -> `ValueError`.
- Referenced image missing -> `FileNotFoundError`.
- OCR failure for a row -> record `ocr_error` and zero/derived recovery metrics, continue other rows.
- No available/requested OCR engines -> `ValueError`.

### 5. Good/Base/Bad Cases
- Good: generate template, collect phone photos, fill metadata, run analysis, then update publication summary from generated JSON.
- Good: real capture summary is absent and paper text says no real-device numbers are available yet.
- Base: analyze only Tesseract on a small reviewed real-capture subset before running heavier OCR engines.
- Bad: copying simulated `view_attack` or `corpus_strong_camera_attack` values into the real-capture section.
- Bad: reporting photos without exact ground-truth text, exposure/distance/angle metadata, or the capture image files.

### 6. Tests Required
- Assert template generation writes required metadata fields.
- Assert malformed metadata is rejected.
- Assert fake-OCR real-capture analysis writes JSON and Markdown, groups by condition/device, and preserves metadata.
- Assert missing referenced image fails before producing a misleading result.
- Run `pytest tests/test_real_capture.py -q` after changing real-capture code.

### 7. Wrong vs Correct
#### Wrong
```python
summary["real_capture"] = summary["view_attack"]
```

#### Correct
```bash
python experiments/real_capture_analysis.py --init-template
python experiments/real_capture_analysis.py --engines tesseract
python experiments/publication_summary.py
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
- `PlaybackConfig(..., image_path=None, demo_name="document", pdf_page=1, insert_inversion=False, inversion_alpha=0.2, anti_ocr_profile="off", mask_cell_size=1, stripe_width=10, stripe_alpha=0.18, glyph_alpha=0.22)`
- `build_playback_frames(..., insert_inversion=False, inversion_alpha=0.2, anti_ocr_profile="off", mask_cell_size=None, stripe_width=None, stripe_alpha=None, glyph_alpha=None) -> tuple[list[tuple[np.ndarray, str]], dict]`
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
- Strong and VLM modes may coexist with requested playback inversion. The inversion frame must be a weak amplitude-scaled frame `alpha * (255 - I)` generated by `compose_partial_inversion_frame`, not a full `255 - I` slot. This preserves the long-exposure defence while keeping playback readable.
- When inversion is enabled, metadata must expose `insert_inversion=True`, `inversion_alpha`, and `per_cycle_slots == n + 1`; when disabled, `inversion_alpha` is `None` and `per_cycle_slots == n`.
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
- Base: if a user passes `--anti-ocr-profile strong --inversion` or `--anti-ocr-profile vlm --inversion`, playback appends the weak inversion frame after each cycle and records the extra slot plus alpha in metadata/HUD.
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
- Assert strong and VLM modes coexist with weak inversion, append one inversion frame per cycle, keep inversion frames free of anti-OCR artifacts, and set `per_cycle_slots == n + 1`.
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
