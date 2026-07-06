# Privacy Display User Study

This is the controlled 240Hz laboratory WebStudy for the privacy-display user experiment. It uses native JavaScript/Canvas2D, a Flask API, and SQLite. Formal-study and demo sessions are deliberately separated so an adaptive low-refresh demonstration cannot contaminate the paper dataset.

## Run

From `privacy-display/`:

```bash
.venv/bin/python -m pip install -r webstudy/requirements.txt
.venv/bin/python webstudy/server.py
```

Open `http://127.0.0.1:5000`. Formal mode requires a measured refresh rate of at least 200Hz and always uses deployed `n=4`; it never silently reduces `n`.

Operator-only modes:

```text
http://127.0.0.1:5000/?debug=1&selftest=1
http://127.0.0.1:5000/?demo=1
```

- `debug=1` shortens timing for software checks.
- `demo=1` allows 144–199Hz and adaptively lowers `n`.
- Both flags are persisted. Admin statistics, JSON, and CSV exclude these sessions by default. Add `include_debug=1` only for troubleshooting.

## Formal study flow

1. Separate informed-consent and photosensitivity-screening confirmations.
2. Required vision-correction field. The server assigns the next formal participant to the currently least-filled joint counterbalance bucket before the experiment leaves this page; the participant never enters `k`.
3. Browser rAF refresh measurement using repeated samples, 200Hz hard gate, and operator environment confirmation.
4. One 12-second unscored source-Canvas warm-up, one 10-second unscored deployed-mask preview, and one 8-second unscored deployed-mask typing practice.
5. Four scored 20-second typing trials: two control and two deployed masked trials in ABBA or BAAB order. The typing order is assigned by the server from the registration index.
6. Six rating conditions in a six-row balanced Latin order selected by the same server assignment:
   - unmasked `n=1` source-Canvas anchor;
   - `n=2`, `n=3`, and `n=4` mask+noise;
   - `n=4` mask-only;
   - deployed `n=4` mask+noise+anti-OCR+weak inversion.
7. Each rating requires at least 10 seconds of viewing before submission. The analysis flags minimum-view straight-line ratings as satisficing.
8. Submit four typing rows and six rating rows under one idempotent session UUID, then show a debriefing screen with the study purpose and withdrawal reference.

Control and masked typing stimuli both come from the same `renderSourceCanvas` path (dark background, light 23px bold text). The only treatment difference is the temporal protection pipeline. Typing uses target-prefix Levenshtein/MSD alignment; an insertion or omission therefore does not invalidate all following characters. The database also stores first-key latency, the original/typed text, edit distance, scoring method, viewing duration, and rAF dropped-frame metadata.

## Laboratory protocol

Before every participant, the operator must verify and tick the on-page checklist:

- use the same 240Hz monitor and display mode;
- fix brightness at the lab-defined value and record that value in the lab log;
- disable automatic brightness, power saving, variable refresh, and browser/background throttling;
- use the designated browser in full-screen mode;
- keep viewing distance at approximately 60cm;
- close unrelated GPU/CPU-heavy applications;
- re-run refresh measurement after any display-mode change.

Stop immediately if the participant reports eye discomfort, dizziness, nausea, headache, or other adverse effects. Do not enroll participants who self-report photosensitive epilepsy or sensitivity to flicker.

## Data and idempotency

The default formal database is `webstudy/study_formal.db` and is ignored by Git. It contains personally identifying participation-management fields and must not be published directly. The older `webstudy/study.db` is a legacy trial database and is deliberately not opened or migrated by the no-argument server, analysis, or backup commands.

Tables:

- `participants`: unique formal registration index, identity, optional demographics, consent/screening trace, session UUID, counterbalancing, refresh and environment fields;
- `typing`: four scored rows per completed participant, MSD metrics, first-key latency, and display timing metadata;
- `ratings`: six rows per completed participant, 10-second view duration/timestamps, and display timing metadata.

`participants.session_uuid` is unique. Formal `registration_index` values are also unique; the server assigns the least-filled joint bucket, recomputes the expected ABBA/BAAB and Latin-row indexes from that index, and rejects mismatches at final submission. The mapping crosses 2 typing orders with 6 rating rows over every 12 consecutive registrations. If the server commits a submission but the response is lost, retrying the same browser submission returns the existing participant instead of inserting duplicate rows. Existing pre-migration databases are upgraded in place, assigned `legacy-<id>` UUIDs, and keep `registration_index=-1`.

Operator endpoints:

```text
http://127.0.0.1:5000/admin
http://127.0.0.1:5000/admin/export.csv
http://127.0.0.1:5000/admin/data.json
http://127.0.0.1:5000/admin/stats
```

Set `WEBSTUDY_EXPORT_TOKEN` before exposing the service beyond localhost. The same `?token=...` query protects all export/stat endpoints.

## Daily backup

At the end of each collection day, stop new submissions and run:

```bash
.venv/bin/python webstudy/backup_db.py \
  --db webstudy/study_formal.db \
  --output webstudy/backups
```

The script uses SQLite's Online Backup API and runs `PRAGMA integrity_check` on the timestamped snapshot. Store a second copy on the approved encrypted research drive; never use a raw file copy while a write transaction may be active.

## Predeclared analysis

Target at least `N=24`, which fills exactly two complete 12-participant joint counterbalance cycles. For the primary paired typing endpoint, a two-tailed paired test at `alpha=0.05` has approximately 0.80 power for a medium paired effect of `d_z=0.6` at `N=24`. If the expected effect is smaller (`d_z=0.3-0.4`), the planned sample should be expanded to roughly 52-90 participants. Run:

```bash
.venv/bin/python webstudy/analyze_study.py \
  --db webstudy/study_formal.db \
  --output webstudy/analysis_output
```

Outputs:

- `analysis_report.json`: inclusion/exclusion audit, paired inference, effect sizes, confidence intervals, Friedman and Holm-adjusted Wilcoxon results;
- `typing_participant_means.csv`: de-identified participant-level condition means;
- `typing_table.tex` and `ratings_table.tex`: paper-ready table bodies.

The participant is the unit of analysis: the two typing repetitions are averaged before paired inference. The typing task tests only the deployed full configuration against the unmasked source-Canvas control; the `n=2/3/4` layer ablation is limited to readability, stability, discomfort, and subjective anti-camera ratings. The 220-character target is intentionally longer than normal participants can complete in a 20-second trial, so WPM/CPM are not capped by target exhaustion for ordinary typing speeds. Default exclusions are debug/demo sessions, incomplete submissions, refresh below 200Hz, any typing trial with fewer than 5 attempted characters, control accuracy below 50%, non-temporal masked trials, observed effective base cycle below 50Hz, and minimum-view straight-line rating sessions. WPM/CPM and accuracy are interpreted jointly rather than treating speed without correctness as improvement; attempted characters and first-key latency provide additional engagement/readability checks. These metrics use a paired t test when the predeclared Shapiro check does not reject normality, otherwise Wilcoxon signed-rank. Ratings use Friedman tests and Holm-adjusted pairwise Wilcoxon tests. All reported comparisons include an effect size and deterministic participant-bootstrap confidence interval where defined.

## Reproducibility notes

- Stimuli and mask patterns are seeded and stored with source text. Typing/rating orders are deterministically assigned by the server from the auditable registration index `k`; participants never type this value.
- Refresh metadata stores repeated-run timing distributions in addition to the mean frame interval. Fullscreen state and screen/device-pixel-ratio sanity fields are stored with the session for later audit.

## Tests

From `privacy-display/`:

```bash
node --test
.venv/bin/pytest -q
```
- The browser PRNG is deterministic for study reproducibility; it is not the ChaCha20 implementation used by the core security PoC.
- rAF dropped-frame monitoring measures browser presentation timing, not panel scan-out or photometric output. A physical 240Hz preflight remains mandatory.
- “防偷拍效果” is a subjective camera-capture rating, not objective anti-camera evidence. “稳定感” is coded so higher means less perceived flicker. “即时视觉不适” is a single item after short exposure, not a clinical fatigue measure.
