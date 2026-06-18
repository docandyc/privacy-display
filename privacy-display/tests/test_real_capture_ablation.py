import subprocess
import sys
import time
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.real_capture_ablation import (
    _attack_specs,
    _execute_plan,
    _load_subset,
    _parse_benchmark_fps,
    _parse_int_list,
    build_metadata_entry,
    build_study_plan,
    condition_to_playback_args,
    offline_video_attack_frames,
    pad_to_display_aspect,
    parse_args,
    parse_positions,
    preflight_refresh_check,
    wait_for_playback_ready,
)


def test_condition_to_playback_args_original_uses_static_baseline():
    args = condition_to_playback_args("original")

    assert "--show-original" in args
    assert "--anti-ocr-profile" not in args
    assert "--inversion" not in args


def test_condition_to_playback_args_deployed_matches_selected_profile():
    args = condition_to_playback_args("deployed")

    assert args == [
        "--anti-ocr-profile", "strong",
        "--stripe-alpha", "0.10",
        "--glyph-alpha", "0.12",
        "--inversion",
        "--inversion-alpha", "0.20",
    ]


def test_build_study1_plan_filters_conditions_and_attacks():
    plan = build_study_plan(
        study="1",
        names=["doc_a", "doc_b"],
        truths=["A", "B"],
        subset_size=2,
        attacks=("short",),
        conditions=("original", "deployed"),
    )

    assert len(plan) == 4
    assert {item["condition"] for item in plan} == {"original|short", "deployed|short"}
    assert {item["position"]["label"] for item in plan} == {"d0.5_a0"}


def test_build_study3_plan_uses_geometry_matrix_for_deployed_only():
    plan = build_study_plan(
        study="3",
        names=["doc_a"],
        truths=["A"],
        subset_size=1,
        attacks=("short",),
    )

    assert len(plan) == 12
    assert {item["ablation"] for item in plan} == {"deployed"}
    assert {item["attack"] for item in plan} == {"short"}
    assert "d1.5_a45" in {item["position"]["label"] for item in plan}


def test_build_all_plan_uses_study_specific_default_subset_sizes():
    names = [f"doc_{idx}" for idx in range(20)]
    truths = [f"T{idx}" for idx in range(20)]

    plan = build_study_plan(study="all", names=names, truths=truths)

    by_study = {}
    for item in plan:
        by_study[item["study"]] = by_study.get(item["study"], 0) + 1
    assert by_study == {
        "1": 12 * 6 * 3,
        "2": 5 * 24,
        "3": 5 * 12 * 2,
    }


def test_build_all_plan_applies_explicit_positions_to_every_study():
    names = [f"doc_{idx}" for idx in range(20)]
    truths = [f"T{idx}" for idx in range(20)]

    plan = build_study_plan(
        study="all",
        names=names,
        truths=truths,
        positions="d0.5_a15",
    )

    assert {item["study"] for item in plan} == {"1", "2", "3"}
    assert {item["position"]["label"] for item in plan} == {"d0.5_a15"}
    assert {item["position"]["angle_degrees"] for item in plan} == {15.0}


def test_load_subset_uses_full_corpus_when_requested_size_reaches_total():
    images, truths, names = _load_subset(120)

    assert len(images) == 120
    assert len(truths) == 120
    assert len(names) == 120


def test_parse_positions_accepts_compact_labels():
    positions = parse_positions("d0.5_a0,d1.5_a45")

    assert [p["label"] for p in positions] == ["d0.5_a0", "d1.5_a45"]
    assert positions[1]["distance_m"] == 1.5
    assert positions[1]["angle_degrees"] == 45.0


def test_pad_to_display_aspect_uses_black_letterbox_without_stretching():
    img = np.full((40, 20, 3), 200, dtype=np.uint8)

    out = pad_to_display_aspect(img, width=100, height=100)

    assert out.shape == (100, 100, 3)
    non_black = np.any(out != 0, axis=2)
    ys, xs = np.where(non_black)
    assert xs.max() - xs.min() + 1 == 50
    assert ys.max() - ys.min() + 1 == 100
    assert np.all(out[:, :20] == 0)


def test_offline_video_attack_frames_returns_attacker_candidates():
    frames = [
        np.full((4, 4, 3), 10, dtype=np.uint8),
        np.full((4, 4, 3), 50, dtype=np.uint8),
        np.full((4, 4, 3), 90, dtype=np.uint8),
    ]

    attacks = offline_video_attack_frames(frames, window=2)

    assert set(attacks) == {"single_best", "temporal_mean", "window_mean_best", "max_proj"}
    assert attacks["temporal_mean"].shape == frames[0].shape
    assert int(attacks["temporal_mean"][0, 0, 0]) == 50
    assert int(attacks["max_proj"][0, 0, 0]) == 90


def test_build_metadata_entry_adds_structured_ablation_fields():
    item = build_study_plan(
        study="1",
        names=["doc_a"],
        truths=["VISIBLE TEXT"],
        subset_size=1,
        attacks=("short",),
        conditions=("deployed",),
    )[0]
    entry = build_metadata_entry(
        item,
        image_name="capture.jpg",
        entry_id="capture-001",
        device_name="EMEET SmartCam S600",
        camera_type="usb_webcam",
        capture_mode="short_exposure",
        exposure_s=1 / 256,
        fps=30.0,
        refresh_hz=240.0,
        n=4,
        epsilon=8 / 255,
        playback_cmd=["python", "main.py", "playback"],
    )

    assert entry["condition"] == "deployed|short"
    assert entry["ablation"] == "deployed"
    assert entry["attack"] == "short"
    assert entry["profile"] == "strong"
    assert entry["stripe_alpha"] == 0.10
    assert entry["glyph_alpha"] == 0.12
    assert entry["inversion_alpha"] == 0.20
    assert entry["playback_cmd"] == "python main.py playback"


def test_wait_for_playback_ready_honors_timeout_without_stdout():
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(2)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    started = time.monotonic()
    try:
        with pytest.raises(TimeoutError):
            wait_for_playback_ready(proc, timeout=0.2)
    finally:
        proc.terminate()
        proc.wait(timeout=2)

    assert time.monotonic() - started < 1.0


def test_video_attack_uses_short_exposure_and_native_fps():
    video = _attack_specs()["video"]
    # Each video frame must be short-exposure so the burst samples many phases;
    # interval 0 keeps the native 60fps so successive frames differ in phase.
    assert video.exposure_key == "short"
    assert video.interval == 0.0
    assert video.fps == 60.0


def test_parse_benchmark_fps_extracts_measured_value():
    output = "PLAYBACK_READY\nnoise\n{\"measured_fps_avg\": 239.4, \"frame_count\": 1000}\n"
    assert _parse_benchmark_fps(output) == 239.4
    assert _parse_benchmark_fps("no json here") is None


def test_real_capture_timeouts_default_to_slow_machine_values():
    args = parse_args([])

    assert args.playback_timeout == 300.0
    assert args.preflight_timeout_margin == 300.0
    assert args.playback_shutdown_timeout == 300.0


def test_preflight_refresh_check_returns_none_when_benchmark_times_out(monkeypatch, capsys):
    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=cmd,
            timeout=kwargs["timeout"],
            output="PLAYBACK_READY\n",
        )

    monkeypatch.setattr("experiments.real_capture_ablation.subprocess.run", fake_run)
    args = SimpleNamespace(
        python_executable=sys.executable,
        display_width=32,
        display_height=24,
        n=4,
        cycles=16,
        refresh_check_seconds=4.0,
        playback_timeout=20.0,
        preflight_timeout_margin=300.0,
        fullscreen=True,
    )
    sample = np.zeros((8, 8, 3), dtype=np.uint8)

    assert preflight_refresh_check(args, sample) is None

    err = capsys.readouterr().err
    assert "preflight playback timed out" in err
    assert "main.py playback" in err


def test_execute_plan_reports_group_playback_timeout_without_traceback(monkeypatch, tmp_path, capsys):
    class FakePlaybackProcess:
        stdout = []

        def __init__(self):
            self.terminated = False
            self.killed = False
            self.wait_timeout = None

        def poll(self):
            return None

        def terminate(self):
            self.terminated = True

        def wait(self, timeout=None):
            self.wait_timeout = timeout
            return 0

        def kill(self):
            self.killed = True

    fake_proc = FakePlaybackProcess()
    monkeypatch.setattr(
        "experiments.real_capture_ablation.subprocess.Popen",
        lambda *args, **kwargs: fake_proc,
    )
    args = SimpleNamespace(
        skip_refresh_check=True,
        calibration_dir=str(tmp_path / "calibration"),
        prompt_positions=False,
        display_width=32,
        display_height=24,
        python_executable=sys.executable,
        n=4,
        cycles=16,
        fullscreen=True,
        playback_timeout=0.01,
        playback_shutdown_timeout=300.0,
        capture_dir=str(tmp_path / "captures"),
        metadata="metadata.json",
        analyze=False,
        engines="tesseract",
    )
    plan = build_study_plan(
        study="1",
        names=["doc_a"],
        truths=["VISIBLE TEXT"],
        subset_size=1,
        attacks=("short",),
        conditions=("deployed",),
    )
    image = np.zeros((8, 8, 3), dtype=np.uint8)

    assert _execute_plan(args, [image], plan) == 3

    err = capsys.readouterr().err
    assert "playback did not print PLAYBACK_READY" in err
    assert "main.py playback" in err
    assert "deployed doc_a d0.5_a0" in err
    assert fake_proc.terminated
    assert fake_proc.wait_timeout == 300.0


def test_parse_int_list():
    assert _parse_int_list("1, 2 ,3") == [1, 2, 3]
    assert _parse_int_list("") == []
    assert _parse_int_list(None) == []
