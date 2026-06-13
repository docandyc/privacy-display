# Privacy Display User Study Web Demo

This is the first 240 Hz-assumed lab web demo for the masking user study.
It keeps the implementation intentionally small:

- frontend: HTML, CSS, native JavaScript, Canvas2D
- masking playback: seeded random temporal pixel assignment plus optional complementary noise
- backend: Flask and SQLite
- output: local SQLite database plus CSV export

## Run

From `privacy-display/`:

```bash
.venv/bin/python -m pip install -r webstudy/requirements.txt
.venv/bin/python webstudy/server.py
```

Open:

```text
http://127.0.0.1:5000
```

For a quick operator test, use:

```text
http://127.0.0.1:5000/?debug=1&selftest=1
```

`debug=1` shortens each typing trial to 5 seconds. `selftest=1` prints mask
completeness, noise residual, and playback permutation metadata to the browser
console.

## Study Flow

1. Consent and photosensitive safety notice.
2. Student ID, name, and optional vision/class fields.
3. Browser refresh-rate check using `requestAnimationFrame`.
4. 20-second original-text typing trial.
5. 20-second masked-text typing trial with `n=4, mask+noise`.
6. Four randomized ablation rating conditions:
   - `n=2, mask+noise`
   - `n=4, mask+noise`
   - `n=8, mask+noise`
   - `n=4, mask-only`
7. Submit to SQLite.

The first version assumes the lab machines use 240 Hz monitors, but each
submission still records the measured refresh rate and flags low-refresh
sessions. If the browser measures below 100 Hz, the frontend displays a warning
and downgrades playback `n` to 2 so the session is marked rather than silently
mixed with normal 240 Hz data.

## Data

The default database is:

```text
webstudy/study.db
```

It is intentionally ignored by Git. The schema has three tables:

- `participants`
- `typing`
- `ratings`

Export all rows:

```text
http://127.0.0.1:5000/admin/export.csv
```

Preview aggregate means:

```text
http://127.0.0.1:5000/admin/stats
```

If the server is exposed beyond localhost, set an export token first:

```bash
export WEBSTUDY_EXPORT_TOKEN="change-me"
.venv/bin/python webstudy/server.py --host 0.0.0.0
```

Then export with:

```text
http://<host>:5000/admin/export.csv?token=change-me
```

## Notes

- The JavaScript implementation follows the same principle as the Python PoC:
  every pixel is assigned to exactly one temporal subframe, and complementary
  noise sums to zero before display clipping.
- The web demo uses a seeded JS PRNG for reproducible study stimuli, not
  ChaCha20. It is visually and statistically suitable for the user study demo,
  but it is not the cryptographic implementation used by the core Python PoC.
- Do not publish the SQLite database directly; it contains student IDs and names.
