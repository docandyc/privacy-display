import numpy as np
from PIL import Image

from src.demo.playback_demo import (
    PlaybackConfig,
    _frames_payload_for_dir,
    _load_png_frames,
    parse_args,
)


def _seed_pngs(directory, count, size=(48, 64)):
    directory.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        Image.fromarray(np.full((*size, 3), i * 10, dtype=np.uint8)).save(
            directory / f"{i:03d}.png"
        )


def test_load_png_frames_sorted(tmp_path):
    _seed_pngs(tmp_path, 4)
    frames = _load_png_frames(tmp_path)
    assert len(frames) == 4
    assert all(f.dtype == np.uint8 and f.shape == (48, 64, 3) for f in frames)
    # sorted by filename -> increasing fill value
    assert frames[0].mean() < frames[-1].mean()


def test_frames_payload_for_dir_meta_shape(tmp_path):
    _seed_pngs(tmp_path, 4)
    frames, meta = _frames_payload_for_dir(tmp_path, PlaybackConfig())
    assert len(frames) == 4
    assert all(kind == "subframe" for _f, kind in frames)
    assert meta["per_cycle_slots"] == 4
    assert meta["insert_inversion"] is False
    assert meta["anti_ocr"]["profile"] == "off"


def test_parse_args_accepts_frames_dir_and_control_file():
    cfg = parse_args(["--frames-dir", "/tmp/frames", "--control-file", "/tmp/ctrl.json"])
    assert cfg.frames_dir == "/tmp/frames"
    assert cfg.control_file == "/tmp/ctrl.json"


def test_parse_args_can_disable_hud_for_capture_frames():
    cfg = parse_args(["--frames-dir", "/tmp/frames", "--no-hud"])
    assert cfg.show_hud is False
