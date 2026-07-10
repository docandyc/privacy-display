# Real-Capture Design Audit

## Acquisition and estimand

- Component profiles were collected in the fixed source-plan order: original, mask_only, mask_noise, anti_ocr, deployed, capture_hardened. They were not randomized.
- The primary pool contains 8 geometries and excludes `d0.5_a15` because it used a different logged UVC setting.
- Readability-priority contributes 408 captured images but 288 duplicate-averaged matched cells.

## Evidence status

- The reported 3.9062 ms value is derived from the nominal UVC control convention; it is not a photometrically measured shutter time.
- Auto-exposure state is `unknown`. Unknown fields: ambient_illuminance, display_luminance, display_brightness_setting, sensor_gain, auto_white_balance_state, focus_state, photometric_exposure_time, capture_phase_within_display_cycle.

## Corpus

- The archive contains 12 content items. It is not all-English/ASCII; non-ASCII items are: cet6_p1, mixed_00, mixed_01.
