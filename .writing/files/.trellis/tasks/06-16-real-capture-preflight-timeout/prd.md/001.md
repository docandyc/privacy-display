# Fix Real Capture Playback Timeouts

## Goal

Prevent the real camera ablation smoke run from crashing with a Python traceback when playback preflight or per-group capture playback times out.

## Requirements

* Preserve the existing preflight fps check when playback reports benchmark JSON normally.
* Handle playback benchmark timeout as a recoverable preflight measurement failure for smoke/full orchestration, not as an uncaught `subprocess.TimeoutExpired`.
* Handle per-group playback readiness timeout/exits as a controlled orchestration failure with group/command/stdout context, not as an uncaught `TimeoutError`.
* Use slow-machine-friendly default timeouts so fullscreen playback has enough time to load before the orchestration gives up.
* Keep enough command/stdout context in the console output for diagnosis.
* Avoid opening camera hardware or pygame windows in regression tests.

## Acceptance Criteria

* [ ] A unit test reproduces a preflight subprocess timeout without launching real playback.
* [ ] A unit test reproduces a per-group playback readiness timeout without launching real playback or camera hardware.
* [ ] Parser defaults use larger timeout values for slow machines.
* [ ] The timeout test fails before the fix and passes after the fix.
* [ ] Existing real-capture ablation tests continue to pass.
* [ ] The default smoke command does not traceback for playback timeout paths; it either continues past preflight measurement or returns a controlled non-zero exit for a failed capture group.

## Definition of Done

* Tests added or updated for the timeout behavior.
* Relevant real-capture ablation tests pass.
* Existing user edits and experiment outputs are not reverted or committed accidentally.

## Technical Approach

Wrap both playback subprocess paths:

* `preflight_refresh_check` converts benchmark timeout into a `None` measurement with diagnostics, matching the existing "no benchmark output" soft-fail path.
* `_execute_plan` converts group playback readiness timeout/exits into a clear stderr diagnostic and controlled return code before any camera capture starts for that group.
* Timeout defaults are raised to allow slow fullscreen/pygame startup: playback ready 300s, preflight margin 300s, shutdown wait 300s.

## Out of Scope

* Changing camera calibration or capture timing.
* Reworking `main.py playback` fullscreen lifecycle.
* Modifying the user's Windows helper script unless root cause analysis shows it is required.

## Technical Notes

* User command failed in `experiments/real_capture_ablation.py::preflight_refresh_check` at `subprocess.run(..., timeout=54.0)`.
* Follow-up user command reached group playback and failed in `wait_for_playback_ready(proc, args.playback_timeout)` with `TimeoutError: playback did not print PLAYBACK_READY within 20.0s`.
* Backend spec applies: `.trellis/spec/backend/quality-guidelines.md`, especially "Real Camera Capture Ablation Orchestration" and "Playback Anti-OCR Profile".
* Shared guides read: `.trellis/spec/guides/index.md`, `code-reuse-thinking-guide.md`, `cross-layer-thinking-guide.md`.
