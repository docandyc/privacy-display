# 修复 WebStudy 实验设计与数据质量问题

## Goal

Strengthen the WebStudy formal experiment against reviewer-visible design and data-quality weaknesses: balanced assignment should not depend on UUID randomness, rating and typing flows should reduce satisficing and learning artifacts, collected metadata should support exclusion/audit decisions, and documentation should clearly limit the claims made by the current task structure.

## Requirements

- Add a server-side assignment endpoint that returns the least-filled formal counterbalance bucket across the 12 `(typing_order_index, rating_order_index)` pairs.
- Remove participant/operator-facing `k` entry from the formal flow. The browser should receive a server assignment and use `assignmentForRegistrationIndex` rather than deriving assignment from `session_uuid`.
- Keep backend validation authoritative: submitted assignment/order fields must match the submitted registration index, and formal registration indexes remain unique.
- Make vision-correction (`glasses`) required for formal submissions.
- Add a masked typing practice trial after the masked preview and before scored masked/control trials.
- Add data-quality signals for rating satisficing, including attention-check and straight-line / low-view-duration exclusions in analysis.
- Improve refresh-rate measurement from a short single window to a more stable measurement with distribution metadata.
- Attempt fullscreen at scored-trial start and persist display/screen sanity metadata for later audit.
- Prevent silent data loss when returning from submit to ratings.
- Add debriefing content to the completion screen.
- Update README and analysis outputs to clarify:
  - typing evidence covers deployed full configuration vs control only;
  - `n`-level ablation is subjective readability/privacy evidence only;
  - `TARGET_N=24` power justification for paired `d_z=0.6`;
  - smaller effects require larger N;
  - 220 target characters and 20-second trials avoid a hard ceiling for normal typists.

## Acceptance Criteria

- [ ] `POST /api/next-assignment` returns a valid least-filled assignment and ignores debug/demo rows.
- [ ] Existing occupied formal registration indexes remain unavailable and duplicate submissions are rejected except idempotent UUID retries.
- [ ] Formal payloads with empty/missing `glasses` fail validation.
- [ ] Analysis JSON reports assignment bucket distributions and exclusion counts for attention/straight-line rating behavior.
- [ ] Browser flow no longer shows a registration-index input in formal mode.
- [ ] Browser flow contains an unscored masked typing practice before scored trials.
- [ ] Refresh metadata includes multi-sample or distribution fields beyond only mean/sample count.
- [ ] README documents the revised design boundaries and sample-size rationale.
- [ ] Relevant Python and Node tests pass.

## Definition of Done

- Tests added/updated for backend API, validation, analysis, and browser-side design logic where practical.
- Lint/typecheck-equivalent syntax checks pass for edited JS/Python files.
- README updated for changed method claims.
- No unrelated worktree changes reverted.

## Technical Approach

- Backend owns formal assignment. It calculates occupancy by recomputing bucket indexes from formal participant rows and selects the least-filled bucket using deterministic tie-breaking.
- Frontend stores the assignment in state/sessionStorage and sends the server-provided registration index with all derived order fields.
- Backend and analysis share the existing `assignment_for_registration_index` logic so submitted rows, admin exports, and analysis reports remain internally consistent.
- Data-quality exclusions remain transparent rather than silently deleting rows: analysis emits audit reasons and JSON/CSV outputs include the relevant fields.

## Decision (ADR-lite)

**Context**: UUID-derived counterbalancing can collapse in small N and makes "Latin square" claims fragile. Restoring an operator `k` field fixes balance but reintroduces operator burden and participant-facing complexity.

**Decision**: Use server-side least-filled assignment (Claude option A) and keep backend validation as race protection. Do not expand typing to six conditions in this task; instead document that typing speed evidence is restricted to deployed-full vs control.

**Consequences**: The study can maintain counterbalance without asking participants for `k`, but assignment now depends on backend availability at session start. The current task avoids a larger experiment redesign, so claims about `n=2/3/4` must remain limited to subjective rating outcomes.

## Out of Scope

- Expanding scored typing trials from 4 to 6.
- Adding new population demographics beyond vision correction and optional typing-speed self-report if it already fits the existing form.
- Rewriting the whole WebStudy UI architecture.
- Changing paper manuscript text outside the WebStudy README in this task.

## Technical Notes

- Relevant files inspected:
  - `privacy-display/webstudy/server.py`
  - `privacy-display/webstudy/static/app.js`
  - `privacy-display/webstudy/static/design.js`
  - `privacy-display/webstudy/analyze_study.py`
  - `privacy-display/webstudy/README.md`
  - `privacy-display/tests/test_webstudy_server.py`
  - `privacy-display/tests/js/webstudy_design.test.js`
- Applicable project specs:
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/cross-layer-thinking-guide.md`
  - `.trellis/spec/guides/code-reuse-thinking-guide.md`
