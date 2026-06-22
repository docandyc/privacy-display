import argparse
import json
import pytest
from pathlib import Path

import numpy as np
from PIL import Image

import experiments.real_capture_detection as rcd
from experiments.real_capture_detection import (
    COCO_CAPTURE_SPECS,
    capture_coco,
    crop_content_to_original,
    evaluate_capture,
    letterbox_rect,
)
from src.attack.detection_evaluator import DetectionBox
from src.evaluation.detection_suite import build_attack_variants, build_display_subframes


# --------------------------------------------------------------------------- #
# A) build_display_subframes shares the exact construction with the sim attack
# --------------------------------------------------------------------------- #
def test_display_subframes_match_attack_variants_single_subframe():
    rng = np.random.default_rng(0)
    img = (rng.random((48, 64, 3)) * 255).astype(np.uint8)
    subs = build_display_subframes(img, n=4, epsilon=0.0, identifier="x")
    variants = build_attack_variants(
        img, attacks=["single_subframe", "temporal_average"], n=4, epsilon=0.0, identifier="x"
    )
    assert len(subs) == 4
    np.testing.assert_array_equal(subs[0], variants["single_subframe"])


# --------------------------------------------------------------------------- #
# B) geometry: letterbox placement + crop-back round trip
# --------------------------------------------------------------------------- #
def test_letterbox_rect_centers_and_scales():
    x, y, tw, th, scale = letterbox_rect(64, 48, 256, 256)
    assert (tw, th) == (256, 192)
    assert (x, y) == (0, 32)
    assert scale == 4.0


def test_crop_content_recovers_original_resolution():
    canvas = np.zeros((256, 256, 3), dtype=np.uint8)
    x, y, tw, th, _ = letterbox_rect(64, 48, 256, 256)
    canvas[y : y + th, x : x + tw] = 200
    crop = crop_content_to_original(canvas, 64, 48, 256, 256)
    assert crop.shape == (48, 64, 3)
    assert int(crop.mean()) == 200


def test_assert_roi_matches_canvas_rejects_size_mismatch():
    # mismatched ROI output -> rectified crop would corrupt GT alignment -> must fail
    with pytest.raises(ValueError, match="output size"):
        rcd.assert_roi_matches_canvas(
            {"output_width": 1920, "output_height": 1080}, 2560, 1600
        )
    # matching ROI passes
    rcd.assert_roi_matches_canvas({"output_width": 2560, "output_height": 1600}, 2560, 1600)


def test_exposure_calibration_status_flags_missing_keys():
    missing = rcd.exposure_calibration_status({}, rcd.COCO_CAPTURE_SPECS)
    assert missing["calibrated"] is False
    assert set(missing["missing_keys"]) == {"short", "long"}

    calib = {"short": {"value": -8.0}, "long": {"value": -5.0}}
    ok = rcd.exposure_calibration_status(calib, rcd.COCO_CAPTURE_SPECS)
    assert ok["calibrated"] is True
    assert ok["missing_keys"] == []


# --------------------------------------------------------------------------- #
# C) evaluate_capture scores seeded frames against COCO GT (hardware-free)
# --------------------------------------------------------------------------- #
class FakeDetector:
    name = "fake"

    def detect(self, image):
        # box matches the GT bbox [10,10,30,40] -> xyxy (10,10,40,50)
        return [DetectionBox((10, 10, 40, 50), 0.9, "person")]

    def status(self):
        return {"available": True, "fake": True}


def _write_coco_fixture(root: Path) -> None:
    (root / "val2017").mkdir(parents=True)
    (root / "annotations").mkdir(parents=True)
    for image_id in (1, 2):
        Image.fromarray(np.full((64, 80, 3), image_id, dtype=np.uint8)).save(
            root / "val2017" / f"{image_id:012d}.jpg"
        )
    payload = {
        "images": [
            {"id": 1, "file_name": "000000000001.jpg", "width": 80, "height": 64},
            {"id": 2, "file_name": "000000000002.jpg", "width": 80, "height": 64},
        ],
        "annotations": [
            {"id": 1, "image_id": 1, "category_id": 1, "bbox": [10, 10, 30, 40], "area": 1200, "iscrowd": 0},
            {"id": 2, "image_id": 2, "category_id": 1, "bbox": [10, 10, 30, 40], "area": 1200, "iscrowd": 0},
        ],
        "categories": [{"id": 1, "name": "person"}],
    }
    (root / "annotations" / "instances_val2017.json").write_text(json.dumps(payload), encoding="utf-8")


def _seed_captures(capture_dir: Path, attacks, image_ids, size=(64, 80)) -> None:
    for attack in attacks:
        d = capture_dir / "coco_detection" / attack
        d.mkdir(parents=True, exist_ok=True)
        for image_id in image_ids:
            Image.fromarray(np.full((*size, 3), 120, dtype=np.uint8)).save(d / f"{image_id}.png")


def test_evaluate_capture_writes_real_attack_schema(tmp_path):
    coco_root = tmp_path / "coco"
    _write_coco_fixture(coco_root)
    capture_dir = tmp_path / "caps"
    attacks = ["real_clean", "real_short", "real_video"]
    _seed_captures(capture_dir, attacks, [1, 2])

    report = evaluate_capture(
        coco_root=coco_root,
        output_dir=tmp_path / "results",
        capture_dir=capture_dir,
        models=["fake"],
        attacks=attacks,
        max_images=2,
        detector_factory=lambda _m, _d: FakeDetector(),
    )
    clean = report["results"]["fake"]["real_clean"]
    assert clean["n_images"] == 2
    assert {"map", "map50", "ap_small", "ap_medium", "ap_large", "ar"} <= set(clean)
    assert clean["map50"] > 0.9  # detector box matches GT -> high mAP
    assert set(report["results"]["fake"]) == set(attacks)
    assert report["config"]["capture"] == "real_device_webcam"
    assert report["baseline_clean_map"]["fake"] == clean["map"]
    assert report["capture"]["coverage"]["complete"] is True
    assert report["capture"]["coverage"]["n_shared"] == 2
    assert (tmp_path / "results" / "real_capture_coco_detection.json").exists()


def test_evaluate_capture_rejects_missing_attack_frames(tmp_path):
    coco_root = tmp_path / "coco"
    _write_coco_fixture(coco_root)
    capture_dir = tmp_path / "caps"
    # only image 1 captured for real_short
    _seed_captures(capture_dir, ["real_short"], [1])

    with pytest.raises(ValueError, match="Incomplete COCO capture coverage"):
        evaluate_capture(
            coco_root=coco_root,
            output_dir=tmp_path / "results",
            capture_dir=capture_dir,
            models=["fake"],
            attacks=["real_short"],
            max_images=2,
            detector_factory=lambda _m, _d: FakeDetector(),
        )


def test_persistent_display_command_disables_hud(tmp_path):
    args = argparse.Namespace(display_width=128, display_height=96, n=4)
    display = rcd.PersistentDisplay(args, tmp_path)

    cmd = display._command(tmp_path / "frames")

    assert "--no-hud" in cmd


def test_persistent_display_show_times_out_without_ack(tmp_path):
    args = argparse.Namespace(
        display_width=128,
        display_height=96,
        n=4,
        settle=0.0,
        advance_timeout=0.01,
    )
    display = rcd.PersistentDisplay(args, tmp_path)

    with pytest.raises(TimeoutError, match="playback did not acknowledge"):
        display.show([np.zeros((4, 4, 3), dtype=np.uint8)])


def test_real_capture_detection_dry_run_without_dataset(tmp_path, capsys):
    args = rcd.build_arg_parser().parse_args(
        ["--dry-run", "--coco-root", str(tmp_path / "missing"), "--max-images", "2"]
    )

    assert rcd.run(args) == 0
    assert "dataset unavailable" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# D) capture orchestration smoke (stubbed camera + display, no pygame/camera)
# --------------------------------------------------------------------------- #
def test_capture_coco_writes_cropped_frames(tmp_path, monkeypatch):
    coco_root = tmp_path / "coco"
    _write_coco_fixture(coco_root)
    canvas = (128, 96)

    # stub the persistent display so no pygame/subprocess is launched
    monkeypatch.setattr(rcd.PersistentDisplay, "start", lambda self, frames: None)
    monkeypatch.setattr(rcd.PersistentDisplay, "show", lambda self, frames: None)
    monkeypatch.setattr(rcd.PersistentDisplay, "stop", lambda self: None)
    # stub calibration + camera I/O (ROI output must match the display canvas)
    monkeypatch.setattr(
        rcd, "load_roi_calibration",
        lambda _p: {"output_width": canvas[0], "output_height": canvas[1]},
    )
    monkeypatch.setattr(rcd, "roi_path", lambda _d, _p: Path("unused"))
    monkeypatch.setattr(rcd, "rectify_frame", lambda frame, _calib: frame)

    class FakeCap:
        def release(self):
            pass

    monkeypatch.setattr(rcd, "open_camera_with_backend", lambda *a, **k: (FakeCap(), "dshow"))
    monkeypatch.setattr(rcd, "try_set_exposure", lambda *a, **k: {"honored": True})
    monkeypatch.setattr(rcd, "warmup", lambda *a, **k: None)
    # camera returns canvas-sized frames; reduce + crop should recover original res
    monkeypatch.setattr(
        rcd, "grab_frames",
        lambda cap, count, interval: [
            np.full((canvas[1], canvas[0], 3), 90, dtype=np.uint8) for _ in range(max(1, count))
        ],
    )

    args = argparse.Namespace(
        camera_index=1, backend="dshow", fourcc="MJPG", warmup=0.0, settle=0.0,
        display_width=canvas[0], display_height=canvas[1], n=2, epsilon=0.0, seed=0,
        device="cpu", calibration_dir=str(tmp_path / "calib"), pos="d0.5_a0",
        capture_dir=str(tmp_path / "caps"), video_window=0, playback_timeout=5.0,
    )
    images, _, _ = rcd.load_coco_records(coco_root, split="val2017", max_images=2)
    manifest = capture_coco(args, images, coco_root, "val2017")

    assert len(manifest["captures"]) == 2 * len(COCO_CAPTURE_SPECS)
    assert manifest["config"]["capture_mode"] == "real_device_still_physical_validation"
    for spec in COCO_CAPTURE_SPECS:
        for image_id in (1, 2):
            out = Path(args.capture_dir) / "coco_detection" / spec.label / f"{image_id}.png"
            assert out.exists()
            assert np.array(Image.open(out)).shape == (64, 80, 3)
    first = manifest["captures"][0]
    assert "exposure" in first
    assert "camera" in first
    assert "crop" in first
