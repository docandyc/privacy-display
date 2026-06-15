# Detection Suite Server Runbook

This runbook is for the COCO/MOT detection suite. Run commands from the `privacy-display` directory on the server. MOT tracking uses BoxMOT ByteTrack when `boxmot` is installed; local tests fall back to a deterministic IoU tracker.

## Dataset Location

Default paths:

* COCO val2017: `data/coco/val2017`
* COCO annotations: `data/coco/annotations/instances_val2017.json`
* MOT17: `data/MOT17/train/MOT17-*/img1` and `data/MOT17/train/MOT17-*/gt/gt.txt`

Override paths when needed:

```bash
export COCO_ROOT=/data/datasets/coco
export MOT17_ROOT=/data/datasets/MOT17
```

## First-Time Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -U ultralytics
pip install -r requirements-detection.txt
```

## Download Datasets

```bash
bash scripts/download_coco_val2017.sh
bash scripts/download_mot17.sh
```

If MOTChallenge blocks automated download, download `MOT17.zip` manually from the MOTChallenge site, unzip it, and keep the final layout as `data/MOT17/train/...`.

## Smoke Run

```bash
SMOKE=1 MOT_SEQUENCES=MOT17-02 bash scripts/run_detection_suite.sh
```

This uses a small COCO image subset and at most 30 MOT frames per sequence.

## Full Run on 2 x RTX 4090

```bash
COCO_DEVICE=cuda:0 \
MOT_DEVICE=cuda:1 \
TRACK_DEVICE=cuda:0 \
bash scripts/run_detection_suite.sh
```

Outputs:

* `experiments/results/coco_detection_attack.json`
* `experiments/results/mot_video_detection.json`
* `experiments/results/mot_tracking_attack.json`
* refreshed `experiments/results/publication_summary.{json,md}`
* refreshed `experiments/results/reproducibility_manifest.json`

Useful overrides:

```bash
MODELS=yolo26x,rtdetr-x bash scripts/run_detection_suite.sh
COCO_MAX_IMAGES=500 MOT_MAX_FRAMES=300 bash scripts/run_detection_suite.sh
PARALLEL=0 bash scripts/run_detection_suite.sh
SEED=0 bash scripts/run_detection_suite.sh   # masks+noise are reproducible per seed
```

## Tracking Metrics

* MOTA / MOTP / IDF1 come from `py-motmetrics` (installed via `requirements-detection.txt`).
  If `motmetrics` is missing, the code falls back to an equivalent NumPy/SciPy path whose
  IDF1 still uses global identity matching (not detection F1); the active backend is recorded
  per row as `metric_backend`.
* **HOTA / DetA / AssA** come from [TrackEval](https://github.com/JonathonLuiten/TrackEval),
  the reference HOTA implementation (motmetrics cannot produce HOTA). The tracking experiment
  always exports its GT and predicted tracks in MOTChallenge format to
  `experiments/results/trackeval_workspace/`, and will automatically call TrackEval when it can
  find it.

  ```bash
  # one-time: clone TrackEval next to the project (or anywhere)
  git clone https://github.com/JonathonLuiten/TrackEval.git ~/TrackEval
  pip install -r ~/TrackEval/requirements.txt

  # tell the suite where it lives; the tracking run then fills the HOTA column
  export TRACKEVAL_ROOT=~/TrackEval
  bash scripts/run_detection_suite.sh
  ```

  Without `TRACKEVAL_ROOT` the run still succeeds — `hota` stays `null`, the MOTChallenge files
  are left in `trackeval_workspace/`, and `mot_tracking_attack.json` records why under
  `config.hota.reason`. You can then run TrackEval manually on those files. Set `NO_HOTA=1` to
  skip the export entirely. The HOTA path uses `--DO_PREPROC False` against the same
  pedestrian-filtered GT that MOTA/IDF1 use, so all tracking columns are mutually consistent.

## Reproducibility

Subframe masks use a ChaCha20 key derived from `--seed` plus a per-stimulus identifier
(COCO `file_name` / `sequence:frame`), and PGD noise uses the same seed, so reruns reproduce
identical attacked pixels. Bump `SEED` to draw an independent realization.
