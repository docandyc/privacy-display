"""
Capture real photos from a USB webcam (Logitech C920) for Experiment A.

This is the *shooter* that complements ``real_capture_analysis.py`` (the
analyzer). The camera is fixed in front of the screen; you display protected
content with ``python main.py playback ...`` and then trigger a capture here.
Captured stills are written into ``experiments/real_captures/`` and merged into
``metadata.json`` using the exact schema expected by
``src.evaluation.real_capture`` so the OCR analysis runs without manual edits.

Typical flow
------------
1. Grant the terminal app (Tabby) Camera permission once, then restart it.
2. ``python experiments/real_capture_shoot.py --probe``           # check device caps
3. On the high-refresh screen: ``python main.py playback --demo cet6 --n 4 ...``
4. ``python experiments/real_capture_shoot.py --interactive``     # reposition + shoot
5. ``python experiments/real_capture_analysis.py --engines tesseract``

macOS note: manual exposure of a UVC webcam is usually *not* honored through
OpenCV/AVFoundation. The script attempts it and reports the effective value; for
a true short-exposure condition, brighten the scene so auto-exposure shortens
the shutter, or set exposure in Logitech's own utility.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.real_capture import (  # noqa: E402
    METADATA_TEMPLATE_JSON,
    REAL_CAPTURE_JSON,
    REAL_CAPTURE_MD,
    run_real_capture_ocr,
)

DEFAULT_CAPTURE_DIR = "experiments/real_captures"
DEFAULT_DEVICE = 0  # AVFoundation index of "HD Pro Webcam C920"
DEFAULT_DEVICE_NAME = "HD Pro Webcam C920"
DEFAULT_EPSILON = 8.0 / 255.0  # matches metadata template (ε=8/255)
CONDITIONS = ("protected", "original", "short_exposure", "video_frame")

PERMISSION_HINT = (
    "Camera could not be opened. On macOS this is almost always a permission "
    "issue: System Settings -> Privacy & Security -> Camera -> enable for "
    "'Tabby', then fully quit and reopen Tabby (resume with `claude --continue`)."
)


# --------------------------------------------------------------------------- #
# Camera helpers
# --------------------------------------------------------------------------- #
def open_camera(
    device: int,
    width: int,
    height: int,
    fourcc: str = "MJPG",
    fps: float | None = None,
) -> cv2.VideoCapture:
    """Open the webcam via the AVFoundation backend with the requested format."""
    cap = cv2.VideoCapture(device, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        raise RuntimeError(PERMISSION_HINT)
    # FOURCC must be set before resolution so the C920 exposes MJPG high-res modes.
    if fourcc:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if fps:
        cap.set(cv2.CAP_PROP_FPS, fps)
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except cv2.error:
        pass
    return cap


def camera_settings(cap: cv2.VideoCapture) -> dict:
    """Read back the effective camera settings."""
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    cc = "".join(chr((fourcc >> 8 * i) & 0xFF) for i in range(4)).strip("\x00")
    return {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": round(float(cap.get(cv2.CAP_PROP_FPS)), 2),
        "fourcc": cc,
        "auto_exposure": cap.get(cv2.CAP_PROP_AUTO_EXPOSURE),
        "exposure": cap.get(cv2.CAP_PROP_EXPOSURE),
    }


def try_set_exposure(cap: cv2.VideoCapture, manual: bool, value: float | None) -> dict:
    """Best-effort manual exposure; returns requested vs effective values."""
    before = camera_settings(cap)
    if manual:
        # 0.25 == manual on the V4L/AVFoundation convention; 0.75 == auto.
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        if value is not None:
            cap.set(cv2.CAP_PROP_EXPOSURE, value)
    else:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
    cap.read()
    after = camera_settings(cap)
    value_honored = (
        manual
        and value is not None
        and abs(after["exposure"] - value) < 1e-6
    )
    auto_mode_changed = manual and after["auto_exposure"] != before["auto_exposure"]
    return {
        "requested_manual": manual,
        "requested_value": value,
        "before": before,
        "after": after,
        "honored": bool(value_honored),
        "manual_mode_changed": bool(auto_mode_changed),
    }


def warmup(cap: cv2.VideoCapture, seconds: float) -> None:
    """Discard frames so auto-exposure / autofocus settle before capturing."""
    end = time.time() + max(0.0, seconds)
    while time.time() < end:
        cap.read()


def grab_frames(cap: cv2.VideoCapture, count: int, interval: float):
    """Grab ``count`` frames (BGR), spaced by ``interval`` seconds."""
    frames = []
    for i in range(max(1, count)):
        ok, frame = cap.read()
        if not ok or frame is None:
            print(f"  [warn] frame {i} grab failed", file=sys.stderr)
            continue
        frames.append(frame)
        if interval > 0 and i < count - 1:
            time.sleep(interval)
    return frames


# --------------------------------------------------------------------------- #
# Device enumeration / probe
# --------------------------------------------------------------------------- #
def list_devices(max_index: int = 4) -> None:
    print("Probing AVFoundation video device indices (0..%d)..." % (max_index - 1))
    for idx in range(max_index):
        cap = cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION)
        opened = cap.isOpened()
        ok = False
        if opened:
            ok, _ = cap.read()
        s = camera_settings(cap) if opened else {}
        cap.release()
        status = "OPEN+frame" if ok else ("opened-no-frame" if opened else "closed")
        extra = f" {s.get('width')}x{s.get('height')}@{s.get('fps')} {s.get('fourcc')}" if opened else ""
        print(f"  [{idx}] {status}{extra}")
    print("Index 0 is normally the C920. If all are 'closed', grant Camera permission to Tabby.")


def probe(device: int, width: int, height: int, fourcc: str) -> int:
    try:
        cap = open_camera(device, width, height, fourcc)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1
    warmup(cap, 0.8)
    ok, frame = cap.read()
    print(f"device {device}: first_frame_ok={ok} shape={None if not ok else frame.shape}")
    print(f"default request {width}x{height} {fourcc} -> {camera_settings(cap)}")
    for (w, h) in [(1920, 1080), (1280, 720), (640, 480)]:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        cap.read()
        s = camera_settings(cap)
        print(f"  request {w}x{h} -> effective {s['width']}x{s['height']}@{s['fps']} {s['fourcc']}")
    exp = try_set_exposure(cap, manual=True, value=-7)
    print(f"  manual-exposure attempt honored={exp['honored']} effective_exposure={exp['after']['exposure']}")
    cap.release()
    return 0


# --------------------------------------------------------------------------- #
# Metadata
# --------------------------------------------------------------------------- #
def slug(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_") or "x"


def build_base(device_name: str, condition: str, angle: float, distance: float, content: str, n: int) -> str:
    return (
        f"{slug(device_name)}_{slug(condition)}_{int(round(angle))}deg_"
        f"{distance:g}m_{slug(content)}_n{n}"
    )


def make_entry(*, image: str, truth: str, condition: str, device_name: str, camera_type: str,
               capture_mode: str, distance: float, angle: float, exposure_s, fps, refresh: float,
               n: int, epsilon: float, lux, environment: str, notes: str, entry_id: str) -> dict:
    return {
        "id": entry_id,
        "image": image,
        "truth": truth,
        "condition": condition,
        "device": device_name,
        "camera_type": camera_type,
        "capture_mode": capture_mode,
        "distance_m": distance,
        "angle_degrees": angle,
        "exposure_s": exposure_s,
        "frame_rate_fps": fps,
        "display_refresh_hz": refresh,
        "n": n,
        "epsilon": epsilon,
        "lighting_lux": lux,
        "environment": environment,
        "notes": notes,
    }


def merge_metadata(capture_dir: Path, metadata_file: str, new_entries: list[dict]) -> Path:
    """Append entries into metadata.json (create if missing), dedup by id."""
    path = capture_dir / metadata_file
    if path.exists():
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload.get("captures"), list):
            raise ValueError(f"{path} must contain a list-valued 'captures' field")
    else:
        payload = {
            "schema_version": 1,
            "notes": "Generated by real_capture_shoot.py (Logitech C920).",
            "captures": [],
        }
    by_id = {e.get("id"): e for e in payload["captures"] if isinstance(e, dict)}
    for entry in new_entries:
        by_id[entry["id"]] = entry
    payload["captures"] = list(by_id.values())
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


# --------------------------------------------------------------------------- #
# Capture
# --------------------------------------------------------------------------- #
def capture_once(cap, args, *, condition, distance, angle, content, truth, capture_mode) -> list[dict]:
    settings = camera_settings(cap)
    warmup(cap, args.warmup)
    frames = grab_frames(cap, args.burst, args.burst_interval)
    if not frames:
        print("  [error] no frames captured", file=sys.stderr)
        return []
    capture_dir = Path(args.capture_dir)
    capture_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    base = build_base(args.device_name, condition, angle, distance, content, args.n)
    notes = (
        f"{args.environment}; cam={settings['width']}x{settings['height']}@{settings['fps']} "
        f"{settings['fourcc']}; auto_exp={settings['auto_exposure']}; "
        f"profile={args.profile}; {args.notes}".strip("; ")
    )
    entries: list[dict] = []
    for i, frame in enumerate(frames):
        fname = f"{base}_{ts}_s{i:02d}.jpg"
        cv2.imwrite(str(capture_dir / fname), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        entries.append(make_entry(
            image=fname, truth=truth, condition=condition, device_name=args.device_name,
            camera_type=args.camera_type, capture_mode=capture_mode, distance=distance,
            angle=angle, exposure_s=args.exposure_s, fps=settings["fps"], refresh=args.refresh_hz,
            n=args.n, epsilon=args.epsilon, lux=args.lighting_lux, environment=args.environment,
            notes=notes, entry_id=f"{base}_{ts}_s{i:02d}",
        ))
    path = merge_metadata(capture_dir, args.metadata, entries)
    print(f"  saved {len(entries)} frame(s) -> {base}_{ts}_s*.jpg  (metadata: {path})")
    return entries


def read_truth(args) -> str:
    if args.truth_file:
        return Path(args.truth_file).read_text(encoding="utf-8").strip()
    return args.truth or ""


def interactive_loop(cap, args) -> list[dict]:
    print("\nInteractive capture. Fix the C920, display protected content, then capture.")
    print("Conditions: protected / original / short_exposure / video_frame. Empty = keep previous.\n")
    state = {
        "condition": args.condition, "distance": args.distance_m, "angle": args.angle_deg,
        "content": args.content, "truth": read_truth(args),
    }
    all_entries: list[dict] = []

    def ask(label, key, cast=str):
        cur = state[key]
        raw = input(f"  {label} [{cur}]: ").strip()
        if raw:
            try:
                state[key] = cast(raw)
            except ValueError:
                print(f"    (invalid, keeping {cur})")

    while True:
        cmd = input("ENTER=capture, e=edit fields, q=quit: ").strip().lower()
        if cmd == "q":
            break
        if cmd == "e":
            ask("condition", "condition")
            ask("distance_m", "distance", float)
            ask("angle_deg", "angle", float)
            ask("content label", "content")
            t = input(f"  truth (exact text) [{state['truth'][:30]}...]: ").strip()
            if t:
                state["truth"] = t
            continue
        if not state["truth"]:
            print("  [error] truth is required (run with --truth/--truth-file or use 'e' to set it)")
            continue
        mode = "video_frame" if args.burst > 1 else "auto_photo"
        if state["condition"] == "short_exposure":
            mode = "short_exposure"
        all_entries += capture_once(
            cap, args, condition=state["condition"], distance=state["distance"],
            angle=state["angle"], content=state["content"], truth=state["truth"], capture_mode=mode,
        )
    return all_entries


# --------------------------------------------------------------------------- #
# Matrix sweep
# --------------------------------------------------------------------------- #
def _num_list(text, cast):
    return [cast(x.strip()) for x in str(text).split(",") if x.strip()]


def planned_matrix(args) -> list[tuple]:
    """Cartesian product of condition × n × distance × angle."""
    conditions = _num_list(args.conditions, str) or [args.condition]
    unknown = sorted(set(conditions) - set(CONDITIONS))
    if unknown:
        raise ValueError(f"unknown capture condition(s): {', '.join(unknown)}")
    ns = _num_list(args.ns, int) if args.ns else [args.n]
    if any(n <= 0 for n in ns):
        raise ValueError("all n values must be positive")
    distances = _num_list(args.distances, float)
    if any(d <= 0 for d in distances):
        raise ValueError("all distances must be positive")
    angles = _num_list(args.angles, float)
    return [
        (cond, n, dist, ang)
        for cond in conditions
        for n in ns
        for dist in distances
        for ang in angles
    ]


def run_matrix(cap, args) -> list[dict]:
    """Walk the matrix, prompting to arrange display + camera before each shot."""
    truth = read_truth(args)
    if not truth:
        print("[error] truth is required for --matrix (use --truth/--truth-file)", file=sys.stderr)
        return []
    combos = planned_matrix(args)
    print(f"\nMatrix sweep: {len(combos)} combinations (condition×n×distance×angle). "
          f"content='{args.content}'.")
    print("Before each shot set the DISPLAY (condition+n) and the CAMERA (distance+angle).\n")
    all_entries: list[dict] = []
    for i, (cond, n, dist, ang) in enumerate(combos, 1):
        args.n = n  # capture_once uses args.n for naming + metadata
        base = build_base(args.device_name, cond, ang, dist, args.content, n)
        print(f"[{i}/{len(combos)}] DISPLAY: condition={cond}, n={n}  |  "
              f"CAMERA: distance={dist:g}m, angle={int(round(ang))}deg  ->  {base}_*")
        cmd = input("    ENTER=capture, s=skip, q=quit: ").strip().lower()
        if cmd == "q":
            break
        if cmd == "s":
            continue
        if cond == "short_exposure":
            try_set_exposure(cap, manual=True, value=args.exposure_value)
        mode = "video_frame" if args.burst > 1 else (
            "short_exposure" if cond == "short_exposure" else "auto_photo"
        )
        all_entries += capture_once(
            cap, args, condition=cond, distance=dist, angle=ang,
            content=args.content, truth=truth, capture_mode=mode,
        )
    return all_entries


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Capture real C920 photos for Experiment A")
    p.add_argument("--list", action="store_true", help="List AVFoundation device indices and exit")
    p.add_argument("--probe", action="store_true", help="Probe device capabilities and exit")
    p.add_argument("--interactive", action="store_true", help="Interactive reposition-and-shoot loop")
    p.add_argument("--matrix", action="store_true",
                   help="Batch driver: prompt for each condition×n×distance×angle combo")
    p.add_argument("--list-conditions", action="store_true",
                   help="Print condition labels and the planned matrix, then exit (no camera)")
    p.add_argument("--analyze", action="store_true", help="Run OCR analysis on metadata.json after capture")

    p.add_argument("--device", type=int, default=DEFAULT_DEVICE)
    p.add_argument("--device-name", default=DEFAULT_DEVICE_NAME)
    p.add_argument("--camera-type", default="usb_webcam")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--fourcc", default="MJPG")
    p.add_argument("--fps", type=float, default=None)
    p.add_argument("--warmup", type=float, default=2.0, help="Seconds to settle AE/AF before capture")
    p.add_argument("--burst", type=int, default=1, help="Frames per capture (use >1 for video_frame)")
    p.add_argument("--burst-interval", type=float, default=0.0)
    p.add_argument("--manual-exposure", action="store_true", help="Best-effort manual exposure (often ignored on macOS)")
    p.add_argument("--exposure-value", type=float, default=None)

    # Metadata tagging for the capture condition.
    p.add_argument("--condition", default="protected", choices=CONDITIONS)
    p.add_argument("--truth", default="", help="Exact displayed text (required unless --truth-file)")
    p.add_argument("--truth-file", default="", help="Path to a txt file with the exact displayed text")
    p.add_argument("--distance-m", type=float, default=1.0, dest="distance_m")
    p.add_argument("--angle-deg", type=float, default=0.0, dest="angle_deg")
    p.add_argument("--content", default="doc", help="Content label, e.g. cet6/code/credentials/table")
    p.add_argument("--n", type=int, default=4, help="Subframe count used on the display")
    p.add_argument("--epsilon", type=float, default=DEFAULT_EPSILON)
    p.add_argument("--refresh-hz", type=float, default=240.0, dest="refresh_hz")
    p.add_argument("--lighting-lux", type=float, default=None, dest="lighting_lux")
    p.add_argument("--environment", default="office")
    p.add_argument("--notes", default="", help="Extra free-text notes recorded in metadata")

    # Matrix sweep dimensions (used with --matrix / --list-conditions).
    p.add_argument("--distances", default="0.5,1,2", help="Comma distances (m) for --matrix")
    p.add_argument("--angles", default="0,15,30,45", help="Comma angles (deg) for --matrix")
    p.add_argument("--conditions", default="protected",
                   help="Comma conditions for --matrix (subset of %s)" % ",".join(CONDITIONS))
    p.add_argument("--ns", default="", help="Comma subframe counts for --matrix (default: just --n)")
    p.add_argument("--exposure-s", type=float, default=None, dest="exposure_s",
                   help="Measured/known shutter time in seconds for this condition (metadata only)")
    p.add_argument("--profile", default="", help="anti-ocr-profile used on display (off/strong/vlm), metadata only")

    p.add_argument("--capture-dir", default=DEFAULT_CAPTURE_DIR)
    p.add_argument("--metadata", default="metadata.json")
    p.add_argument("--engines", default="tesseract", help="Comma OCR engines for --analyze")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.list:
        list_devices()
        return 0
    if args.list_conditions:
        combos = planned_matrix(args)
        print("Condition labels:", ", ".join(CONDITIONS))
        print(f"Planned matrix: {len(combos)} combos (content='{args.content}')")
        for cond, n, dist, ang in combos:
            print(f"  - condition={cond} n={n} distance={dist:g}m angle={int(round(ang))}deg")
        return 0
    if args.probe:
        return probe(args.device, args.width, args.height, args.fourcc)

    try:
        cap = open_camera(args.device, args.width, args.height, args.fourcc, args.fps)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.manual_exposure or args.condition == "short_exposure":
        exp = try_set_exposure(cap, manual=True, value=args.exposure_value)
        if not exp["honored"]:
            print("[note] manual exposure not honored by AVFoundation/OpenCV; "
                  "brighten the scene for a short auto shutter, or set it in Logitech's utility.")

    try:
        if args.matrix:
            entries = run_matrix(cap, args)
        elif args.interactive:
            entries = interactive_loop(cap, args)
        else:
            truth = read_truth(args)
            if not truth:
                print("[error] --truth or --truth-file is required for a single capture.", file=sys.stderr)
                return 2
            mode = "video_frame" if args.burst > 1 else "auto_photo"
            if args.condition == "short_exposure":
                mode = "short_exposure"
            entries = capture_once(
                cap, args, condition=args.condition, distance=args.distance_m,
                angle=args.angle_deg, content=args.content, truth=truth, capture_mode=mode,
            )
    finally:
        cap.release()

    print(f"\nTotal captures this run: {len(entries)}")
    if args.analyze and entries:
        engines = [e.strip() for e in args.engines.split(",") if e.strip()]
        run_real_capture_ocr(capture_dir=args.capture_dir, metadata_file=args.metadata, engines=engines)
        out = Path("experiments/results")
        print(f"Analysis written: {out / REAL_CAPTURE_JSON} , {out / REAL_CAPTURE_MD}")
    elif entries:
        print("Next: python experiments/real_capture_analysis.py --engines tesseract")
    _ = METADATA_TEMPLATE_JSON  # template provided by real_capture_analysis.py --init-template
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
