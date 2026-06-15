"""MOT17 dataset helpers for frame detection and tracking evaluation."""

from __future__ import annotations

import configparser
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.attack.detection_evaluator import DetectionBox, average_precision_at_iou, box_iou


@dataclass(frozen=True)
class MOTFrame:
    sequence: str
    frame_id: int
    path: Path


@dataclass(frozen=True)
class MOTObject:
    sequence: str
    frame_id: int
    track_id: int
    box: tuple[float, float, float, float]
    score: float = 1.0


def list_mot_sequences(mot_root: str | Path, split: str = "train") -> list[str]:
    root = Path(mot_root) / split
    if not root.exists():
        raise FileNotFoundError(f"MOT17 split not found: {root}")
    return sorted(path.name for path in root.iterdir() if path.is_dir() and (path / "img1").exists())


def load_mot_sequence(
    mot_root: str | Path,
    sequence: str,
    split: str = "train",
    max_frames: int | None = None,
) -> tuple[list[MOTFrame], dict[int, list[MOTObject]]]:
    seq_root = Path(mot_root) / split / sequence
    img_dir = seq_root / "img1"
    gt_path = seq_root / "gt" / "gt.txt"
    if not img_dir.exists():
        raise FileNotFoundError(f"MOT image directory not found: {img_dir}")
    frames = [
        MOTFrame(sequence, int(path.stem), path)
        for path in sorted(img_dir.glob("*.jpg"))
    ]
    if max_frames is not None:
        frames = frames[: int(max_frames)]
    keep = {frame.frame_id for frame in frames}
    gt = _load_gt(gt_path, sequence, keep)
    return frames, gt


def compute_detection_metrics(
    gt_by_frame: dict[str, dict[int, list[MOTObject]]],
    pred_by_frame: dict[str, dict[int, list[DetectionBox]]],
) -> dict:
    refs: list[DetectionBox] = []
    preds: list[DetectionBox] = []
    tp = fp = fn = 0
    frame_count = 0
    for sequence, frames in gt_by_frame.items():
        for frame_id, gt_rows in frames.items():
            frame_count += 1
            frame_refs = [
                DetectionBox(obj.box, 1.0, f"person:{sequence}:{frame_id}")
                for obj in gt_rows
            ]
            frame_preds = [
                DetectionBox(pred.box, pred.score, f"person:{sequence}:{frame_id}")
                for pred in pred_by_frame.get(sequence, {}).get(frame_id, [])
                if pred.label == "person"
            ]
            refs.extend(frame_refs)
            preds.extend(frame_preds)
            matched = _match_boxes(frame_refs, frame_preds, threshold=0.5)
            tp += len(matched)
            fp += max(0, len(frame_preds) - len(matched))
            fn += max(0, len(frame_refs) - len(matched))
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {
        "map": _mean_ap(refs, preds),
        "map50": average_precision_at_iou(refs, preds, 0.5),
        "recall": float(recall),
        "precision": float(precision),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "n_frames": int(frame_count),
    }


def compute_tracking_metrics(
    gt_by_frame: dict[str, dict[int, list[MOTObject]]],
    tracks_by_frame: dict[str, dict[int, list[MOTObject]]],
) -> dict:
    """Compute MOT metrics, preferring the citable py-motmetrics backend.

    py-motmetrics gives standard CLEAR-MOT (MOTA/MOTP) and identity (IDF1)
    metrics. When it is unavailable (e.g. local CI without the optional
    detection deps) we fall back to an equivalent NumPy/SciPy implementation
    whose IDF1 uses true global identity matching, not detection F1. HOTA is
    only filled when TrackEval is available; otherwise it stays ``None`` and
    should be produced via the exported MOTChallenge files.
    """
    backend, metrics = _tracking_with_motmetrics(gt_by_frame, tracks_by_frame)
    if metrics is None:
        metrics = _tracking_fallback(gt_by_frame, tracks_by_frame)
        backend = "approximate_scipy"
    metrics.setdefault("hota", None)
    metrics["metric_backend"] = backend
    return metrics


def _box_xywh(box: tuple[float, float, float, float]) -> list[float]:
    x1, y1, x2, y2 = box
    return [float(x1), float(y1), float(x2 - x1), float(y2 - y1)]


def _as_float(value, default: float = 0.0) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return default
    return default if np.isnan(value) else value


def _tracking_with_motmetrics(
    gt_by_frame: dict[str, dict[int, list[MOTObject]]],
    tracks_by_frame: dict[str, dict[int, list[MOTObject]]],
) -> tuple[str, dict | None]:
    try:
        import motmetrics as mm
    except Exception:
        return "motmetrics_unavailable", None

    # motmetrics 1.4.0 still calls removed NumPy aliases (e.g. np.asfarray under
    # NumPy >= 2.0), and other version skews can fail at runtime. Any failure here
    # must fall back to the scipy implementation rather than crash the experiment.
    try:
        accumulators = []
        names = []
        for sequence, frames in gt_by_frame.items():
            acc = mm.MOTAccumulator(auto_id=False)
            for frame_id in sorted(frames):
                gt_rows = frames[frame_id]
                pred_rows = tracks_by_frame.get(sequence, {}).get(frame_id, [])
                gt_ids = [obj.track_id for obj in gt_rows]
                pred_ids = [obj.track_id for obj in pred_rows]
                gt_boxes = np.array([_box_xywh(obj.box) for obj in gt_rows], dtype=float).reshape(-1, 4)
                pred_boxes = np.array([_box_xywh(obj.box) for obj in pred_rows], dtype=float).reshape(-1, 4)
                distances = mm.distances.iou_matrix(gt_boxes, pred_boxes, max_iou=0.5)
                acc.update(gt_ids, pred_ids, distances, frameid=int(frame_id))
            accumulators.append(acc)
            names.append(sequence)

        if not accumulators:
            return "motmetrics", _empty_tracking_metrics()

        mh = mm.metrics.create()
        summary = mh.compute_many(
            accumulators,
            names=names,
            metrics=[
                "mota",
                "motp",
                "idf1",
                "num_switches",
                "num_false_positives",
                "num_misses",
                "num_frames",
            ],
            generate_overall=True,
        )
        row = summary.loc["OVERALL"]
        motp_distance = _as_float(row.get("motp"), default=1.0)
        return "motmetrics", {
            "mota": _as_float(row.get("mota")),
            # py-motmetrics MOTP is the mean (1 - IoU) distance of matches; report as
            # mean IoU overlap so the column stays "higher is better".
            "motp": max(0.0, 1.0 - motp_distance),
            "idf1": _as_float(row.get("idf1")),
            "fp": int(_as_float(row.get("num_false_positives"))),
            "fn": int(_as_float(row.get("num_misses"))),
            "id_switches": int(_as_float(row.get("num_switches"))),
            "n_frames": int(_as_float(row.get("num_frames"))),
        }
    except Exception as exc:  # pragma: no cover - depends on motmetrics/numpy skew
        return f"motmetrics_failed:{type(exc).__name__}", None


def _empty_tracking_metrics() -> dict:
    return {
        "mota": 0.0,
        "motp": 0.0,
        "idf1": 0.0,
        "fp": 0,
        "fn": 0,
        "id_switches": 0,
        "n_frames": 0,
    }


def _tracking_fallback(
    gt_by_frame: dict[str, dict[int, list[MOTObject]]],
    tracks_by_frame: dict[str, dict[int, list[MOTObject]]],
) -> dict:
    total_gt = total_pred = tp = fp = fn = id_switches = 0
    ious: list[float] = []
    gt_to_pred: dict[tuple[str, int], int] = {}
    cooccurrence: dict[tuple[tuple[str, int], tuple[str, int]], int] = {}
    frame_count = 0
    for sequence, frames in gt_by_frame.items():
        for frame_id, gt_rows in frames.items():
            frame_count += 1
            pred_rows = tracks_by_frame.get(sequence, {}).get(frame_id, [])
            total_gt += len(gt_rows)
            total_pred += len(pred_rows)
            matches = _match_objects(gt_rows, pred_rows, threshold=0.5)
            tp += len(matches)
            fp += max(0, len(pred_rows) - len(matches))
            fn += max(0, len(gt_rows) - len(matches))
            for gt_idx, pred_idx, iou in matches:
                gt_obj = gt_rows[gt_idx]
                pred_obj = pred_rows[pred_idx]
                key = (sequence, gt_obj.track_id)
                previous = gt_to_pred.get(key)
                if previous is not None and previous != pred_obj.track_id:
                    id_switches += 1
                gt_to_pred[key] = pred_obj.track_id
                ious.append(iou)
                pair = (key, (sequence, pred_obj.track_id))
                cooccurrence[pair] = cooccurrence.get(pair, 0) + 1
    mota = 1.0 - ((fn + fp + id_switches) / max(total_gt, 1))
    idf1 = _global_idf1(cooccurrence, total_gt, total_pred)
    return {
        "mota": float(mota),
        "motp": float(np.mean(ious)) if ious else 0.0,
        "idf1": float(idf1),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "id_switches": int(id_switches),
        "n_frames": int(frame_count),
    }


def _global_idf1(
    cooccurrence: dict[tuple[tuple[str, int], tuple[str, int]], int],
    total_gt: int,
    total_pred: int,
) -> float:
    """True IDF1 via global identity assignment (Hungarian on co-occurrence)."""
    if not cooccurrence:
        return 0.0
    from scipy.optimize import linear_sum_assignment

    gt_ids = sorted({pair[0] for pair in cooccurrence})
    pred_ids = sorted({pair[1] for pair in cooccurrence})
    gt_index = {gid: i for i, gid in enumerate(gt_ids)}
    pred_index = {pid: j for j, pid in enumerate(pred_ids)}
    weights = np.zeros((len(gt_ids), len(pred_ids)), dtype=float)
    for (gid, pid), count in cooccurrence.items():
        weights[gt_index[gid], pred_index[pid]] = count
    rows, cols = linear_sum_assignment(-weights)
    id_tp = int(weights[rows, cols].sum())
    id_fp = max(0, total_pred - id_tp)
    id_fn = max(0, total_gt - id_tp)
    denom = 2 * id_tp + id_fp + id_fn
    return (2 * id_tp) / denom if denom > 0 else 0.0


# ---------------------------------------------------------------------------
# HOTA via TrackEval
#
# py-motmetrics gives MOTA/MOTP/IDF1 but not HOTA. HOTA's reference
# implementation is TrackEval (https://github.com/JonathonLuiten/TrackEval),
# which consumes MOTChallenge-format text files. We export the in-memory GT and
# predicted tracks to that layout, then optionally shell out to TrackEval and
# parse the per-tracker ``pedestrian_summary.txt`` it writes. Everything degrades
# gracefully: if TrackEval is not installed the files are still written (so HOTA
# can be produced manually later) and ``hota`` stays ``None``.
# ---------------------------------------------------------------------------


def _frames_to_mot_lines(
    frames_map: dict[int, list[MOTObject]],
    *,
    is_gt: bool,
) -> list[str]:
    lines: list[str] = []
    for frame_id in sorted(frames_map):
        for obj in frames_map[frame_id]:
            x, y, w, h = _box_xywh(obj.box)
            if is_gt:
                # frame,id,x,y,w,h,conf=1,class=1(pedestrian),visibility=1
                lines.append(
                    f"{int(frame_id)},{int(obj.track_id)},{x:.2f},{y:.2f},{w:.2f},{h:.2f},1,1,1"
                )
            else:
                # frame,id,x,y,w,h,conf,-1,-1,-1
                lines.append(
                    f"{int(frame_id)},{int(obj.track_id)},{x:.2f},{y:.2f},{w:.2f},{h:.2f},"
                    f"{float(obj.score):.4f},-1,-1,-1"
                )
    return lines


def _max_frame(frames_map: dict[int, list[MOTObject]]) -> int:
    return max(frames_map) if frames_map else 0


def _write_seqinfo(
    path: Path,
    *,
    name: str,
    seq_length: int,
    frame_rate: int = 30,
    im_width: int = 1920,
    im_height: int = 1080,
) -> None:
    config = configparser.ConfigParser()
    config.optionxform = str  # preserve key case (TrackEval reads "seqLength")
    config["Sequence"] = {
        "name": name,
        "imDir": "img1",
        "frameRate": str(int(frame_rate)),
        "seqLength": str(max(1, int(seq_length))),
        "imWidth": str(int(im_width)),
        "imHeight": str(int(im_height)),
        "imExt": ".jpg",
    }
    with open(path, "w", encoding="utf-8") as handle:
        config.write(handle)


def prepare_trackeval_workspace(
    workspace: str | Path,
    gt_by_sequence: dict[str, dict[int, list[MOTObject]]],
    trackers: dict[str, dict[str, dict[int, list[MOTObject]]]],
    *,
    benchmark: str = "PRIVACY",
    split: str = "all",
    frame_rate: int = 30,
    im_width: int = 1920,
    im_height: int = 1080,
) -> dict:
    """Write GT + predicted tracks in MOTChallenge layout for TrackEval.

    ``trackers`` maps a tracker label (we use ``"<model>__<attack>"``) to its
    ``tracks_by_sequence``. GT is written once and shared across trackers, so a
    single TrackEval invocation can score every model/attack combination. The
    returned dict describes the folders/flags ``run_trackeval_hota`` needs.
    """
    ws = Path(workspace)
    sub = f"{benchmark}-{split}"
    gt_root = ws / "gt" / sub
    seqmap_dir = ws / "gt" / "seqmaps"
    trackers_root = ws / "trackers" / sub

    for stale in (gt_root, trackers_root):
        if stale.exists():
            shutil.rmtree(stale)
    gt_root.mkdir(parents=True, exist_ok=True)
    seqmap_dir.mkdir(parents=True, exist_ok=True)
    trackers_root.mkdir(parents=True, exist_ok=True)

    sequences = sorted(gt_by_sequence)
    seq_lengths: dict[str, int] = {seq: _max_frame(gt_by_sequence.get(seq, {})) for seq in sequences}
    for tracks_by_sequence in trackers.values():
        for seq, frames_map in tracks_by_sequence.items():
            seq_lengths[seq] = max(seq_lengths.get(seq, 0), _max_frame(frames_map))

    for seq in sequences:
        seq_gt_dir = gt_root / seq / "gt"
        seq_gt_dir.mkdir(parents=True, exist_ok=True)
        gt_lines = _frames_to_mot_lines(gt_by_sequence.get(seq, {}), is_gt=True)
        (seq_gt_dir / "gt.txt").write_text(
            ("\n".join(gt_lines) + "\n") if gt_lines else "", encoding="utf-8"
        )
        _write_seqinfo(
            gt_root / seq / "seqinfo.ini",
            name=seq,
            seq_length=seq_lengths.get(seq, 1),
            frame_rate=frame_rate,
            im_width=im_width,
            im_height=im_height,
        )

    seqmap_path = seqmap_dir / f"{sub}.txt"
    seqmap_path.write_text("name\n" + "\n".join(sequences) + "\n", encoding="utf-8")

    for tracker_name, tracks_by_sequence in trackers.items():
        data_dir = trackers_root / tracker_name / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        for seq in sequences:
            lines = _frames_to_mot_lines(tracks_by_sequence.get(seq, {}), is_gt=False)
            (data_dir / f"{seq}.txt").write_text(
                ("\n".join(lines) + "\n") if lines else "", encoding="utf-8"
            )

    return {
        "workspace": str(ws),
        "gt_folder": str(ws / "gt"),
        "trackers_folder": str(ws / "trackers"),
        "seqmap_file": str(seqmap_path),
        "benchmark": benchmark,
        "split": split,
        "sequences": sequences,
        "trackers": sorted(trackers),
    }


def _parse_trackeval_summary(text: str) -> dict[str, float]:
    """Parse a TrackEval ``pedestrian_summary.txt`` (header row + values row).

    TrackEval reports metrics as percentages (0-100); we return 0-1 fractions to
    match the rest of the pipeline. Unknown/missing columns are simply omitted.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) < 2:
        return {}
    header = lines[0].split()
    values = lines[-1].split()
    # Some TrackEval versions prefix the values row with a label (e.g. the
    # tracker/"COMBINED_SEQ" name); drop the leading token so columns align.
    if len(values) == len(header) + 1:
        values = values[1:]
    if len(values) != len(header):
        return {}
    pairs = dict(zip(header, values))

    def grab(key: str) -> float | None:
        raw = pairs.get(key)
        if raw is None:
            return None
        try:
            return float(raw) / 100.0
        except ValueError:
            return None

    wanted = {
        "hota": "HOTA",
        "deta": "DetA",
        "assa": "AssA",
        "loca": "LocA",
        "mota": "MOTA",
        "motp": "MOTP",
        "idf1": "IDF1",
    }
    parsed = {out: grab(col) for out, col in wanted.items()}
    return {key: value for key, value in parsed.items() if value is not None}


def run_trackeval_hota(
    workspace_info: dict,
    *,
    trackeval_root: str | Path | None = None,
    metrics: tuple[str, ...] = ("HOTA", "CLEAR", "Identity"),
    python_bin: str | None = None,
    timeout: float | None = None,
) -> dict:
    """Run TrackEval on a prepared workspace and parse per-tracker HOTA.

    ``trackeval_root`` should point at a TrackEval checkout (containing
    ``scripts/run_mot_challenge.py``); it falls back to the ``TRACKEVAL_ROOT``
    environment variable. Returns ``{"available": bool, "reason": str,
    "trackers": {tracker_name: {hota, deta, assa, ...}}}`` and never raises, so
    HOTA stays ``None`` when TrackEval is absent or fails.
    """
    root = trackeval_root or os.environ.get("TRACKEVAL_ROOT")
    if not root:
        return {"available": False, "reason": "trackeval_root_not_set", "trackers": {}}
    root_path = Path(root)
    script = root_path / "scripts" / "run_mot_challenge.py"
    if not script.exists():
        return {"available": False, "reason": f"script_not_found:{script}", "trackers": {}}

    # TrackEval's run_mot_challenge.py parses any None-default arg (e.g.
    # --SEQMAP_FILE) with nargs='+', leaving it a *list* that later breaks
    # os.path.isfile(). We therefore do NOT pass --SEQMAP_FILE and instead rely on
    # TrackEval's default discovery at GT_FOLDER/seqmaps/BENCHMARK-SPLIT.txt, which
    # is exactly where prepare_trackeval_workspace writes the seqmap.
    interpreter = python_bin or os.environ.get("TRACKEVAL_PYTHON") or sys.executable
    cmd = [
        interpreter,
        str(script),
        "--GT_FOLDER", workspace_info["gt_folder"],
        "--TRACKERS_FOLDER", workspace_info["trackers_folder"],
        "--BENCHMARK", workspace_info["benchmark"],
        "--SPLIT_TO_EVAL", workspace_info["split"],
        "--DO_PREPROC", "False",
        "--METRICS", *metrics,
        "--USE_PARALLEL", "False",
        "--NUM_PARALLEL_CORES", "1",
        "--PRINT_RESULTS", "False",
        "--PRINT_CONFIG", "False",
        "--TIME_PROGRESS", "False",
        "--OUTPUT_SUMMARY", "True",
        "--OUTPUT_DETAILED", "False",
        "--PLOT_CURVES", "False",
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(root_path),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"available": False, "reason": f"subprocess_error:{exc}", "trackers": {}}
    if proc.returncode != 0:
        return {
            "available": False,
            "reason": "nonzero_exit",
            "returncode": proc.returncode,
            "stderr": (proc.stderr or "")[-2000:],
            "trackers": {},
        }

    out_root = Path(workspace_info["trackers_folder"]) / (
        f"{workspace_info['benchmark']}-{workspace_info['split']}"
    )
    parsed: dict[str, dict[str, float]] = {}
    for tracker_name in workspace_info["trackers"]:
        summary = out_root / tracker_name / "pedestrian_summary.txt"
        if summary.exists():
            metrics_for_tracker = _parse_trackeval_summary(summary.read_text(encoding="utf-8"))
            if metrics_for_tracker:
                parsed[tracker_name] = metrics_for_tracker
    if not parsed:
        return {"available": False, "reason": "no_summary_parsed", "trackers": {}}
    return {"available": True, "reason": "ok", "trackers": parsed}


class GreedyByteTracker:
    """Small ByteTrack-style fallback used when external tracking is unavailable."""

    name = "greedy_bytetrack_fallback"

    def __init__(self, iou_threshold: float = 0.3):
        self.iou_threshold = float(iou_threshold)
        self.next_id = 1
        self.active: dict[int, DetectionBox] = {}

    def update(
        self,
        detections: list[DetectionBox],
        sequence: str,
        frame_id: int,
        image: np.ndarray | None = None,
    ) -> list[MOTObject]:
        assigned_tracks: set[int] = set()
        outputs: list[MOTObject] = []
        for det in sorted(detections, key=lambda box: box.score, reverse=True):
            best_track = None
            best_iou = 0.0
            for track_id, previous in self.active.items():
                if track_id in assigned_tracks:
                    continue
                iou = box_iou(previous, det)
                if iou > best_iou:
                    best_iou = iou
                    best_track = track_id
            if best_track is None or best_iou < self.iou_threshold:
                best_track = self.next_id
                self.next_id += 1
            assigned_tracks.add(best_track)
            self.active[best_track] = det
            outputs.append(MOTObject(sequence, frame_id, best_track, det.box, det.score))
        stale = set(self.active) - assigned_tracks
        for track_id in stale:
            self.active.pop(track_id, None)
        return outputs


class BoxMOTByteTracker:
    """Adapter around BoxMOT ByteTrack with a deterministic fallback."""

    name = "boxmot_bytetrack"

    def __init__(self):
        from boxmot import ByteTrack

        self._tracker = ByteTrack()
        self._fallback = GreedyByteTracker()

    def update(
        self,
        detections: list[DetectionBox],
        sequence: str,
        frame_id: int,
        image: np.ndarray | None = None,
    ) -> list[MOTObject]:
        dets = np.array(
            [
                [*det.box, float(det.score), 0.0]
                for det in detections
            ],
            dtype=np.float32,
        )
        if dets.size == 0:
            dets = np.empty((0, 6), dtype=np.float32)
        try:
            try:
                tracks = self._tracker.update(dets, image)
            except TypeError:
                tracks = self._tracker.update(dets)
            return [_track_row_to_object(row, sequence, frame_id) for row in np.asarray(tracks)]
        except Exception:
            return self._fallback.update(detections, sequence, frame_id, image=image)


def build_bytetrack_tracker(prefer_external: bool = True):
    if prefer_external:
        try:
            return BoxMOTByteTracker()
        except Exception:
            pass
    return GreedyByteTracker()


def _track_row_to_object(row, sequence: str, frame_id: int) -> MOTObject:
    values = [float(value) for value in row]
    x1, y1, x2, y2 = values[:4]
    track_id = int(values[4]) if len(values) > 4 else 0
    score = float(values[5]) if len(values) > 5 else 1.0
    return MOTObject(sequence, frame_id, track_id, (x1, y1, x2, y2), score)


def _load_gt(path: Path, sequence: str, keep: set[int]) -> dict[int, list[MOTObject]]:
    rows: dict[int, list[MOTObject]] = {frame_id: [] for frame_id in sorted(keep)}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 6:
            continue
        frame_id = int(float(parts[0]))
        if frame_id not in keep:
            continue
        track_id = int(float(parts[1]))
        x, y, w, h = (float(parts[i]) for i in range(2, 6))
        mark = float(parts[6]) if len(parts) > 6 else 1.0
        class_id = int(float(parts[7])) if len(parts) > 7 else 1
        visibility = float(parts[8]) if len(parts) > 8 else 1.0
        if mark <= 0 or class_id != 1 or visibility <= 0:
            continue
        rows.setdefault(frame_id, []).append(
            MOTObject(sequence, frame_id, track_id, (x, y, x + w, y + h), 1.0)
        )
    return rows


def _mean_ap(refs: list[DetectionBox], preds: list[DetectionBox]) -> float:
    thresholds = np.arange(0.5, 1.0, 0.05)
    return float(np.mean([average_precision_at_iou(refs, preds, float(thr)) for thr in thresholds]))


def _match_boxes(
    refs: list[DetectionBox],
    preds: list[DetectionBox],
    threshold: float,
) -> list[tuple[int, int, float]]:
    candidates: list[tuple[float, int, int]] = []
    for ref_idx, ref in enumerate(refs):
        for pred_idx, pred in enumerate(preds):
            candidates.append((box_iou(ref, pred), ref_idx, pred_idx))
    return _select_matches(candidates, threshold)


def _match_objects(
    refs: list[MOTObject],
    preds: list[MOTObject],
    threshold: float,
) -> list[tuple[int, int, float]]:
    candidates: list[tuple[float, int, int]] = []
    for ref_idx, ref in enumerate(refs):
        ref_box = DetectionBox(ref.box, 1.0, "person")
        for pred_idx, pred in enumerate(preds):
            pred_box = DetectionBox(pred.box, pred.score, "person")
            candidates.append((box_iou(ref_box, pred_box), ref_idx, pred_idx))
    return _select_matches(candidates, threshold)


def _select_matches(
    candidates: list[tuple[float, int, int]],
    threshold: float,
) -> list[tuple[int, int, float]]:
    matches: list[tuple[int, int, float]] = []
    used_refs: set[int] = set()
    used_preds: set[int] = set()
    for iou, ref_idx, pred_idx in sorted(candidates, reverse=True):
        if iou < threshold or ref_idx in used_refs or pred_idx in used_preds:
            continue
        used_refs.add(ref_idx)
        used_preds.add(pred_idx)
        matches.append((ref_idx, pred_idx, float(iou)))
    return matches
