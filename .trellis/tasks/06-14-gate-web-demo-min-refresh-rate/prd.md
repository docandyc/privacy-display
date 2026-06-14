# Gate web demo test by minimum refresh rate

## Goal

Prevent the web study demo from starting any typing or rating test when the measured browser refresh rate is below the minimum required by `技术交底书.md`.

## Requirements

* Use the technology disclosure's global minimum display refresh rate: `144Hz`.
* The refresh-rate step must keep the "开始试次" action disabled until a successful measurement is at or above `144Hz`.
* If the measured refresh rate is below `144Hz`, the UI must clearly say the test cannot start and tell the operator to switch to a higher refresh-rate display/mode.
* Keep recording `refresh_hz`, `refresh_ok`, sample count, and mean frame interval in the existing payload.
* Preserve the existing mask player `static_fallback` behavior for per-condition flicker safety after the global refresh gate passes.

## Acceptance Criteria

* [ ] A measured refresh rate below `144Hz` cannot advance from the refresh step to the typing step.
* [ ] A measured refresh rate at or above `144Hz` can advance as before.
* [ ] The displayed minimum accepted refresh rate is `144Hz`.
* [ ] The README no longer says low-refresh sessions may still continue.
* [ ] Relevant tests pass.

## Definition of Done

* Tests added or updated where practical.
* Existing lint/type/test commands relevant to the changed files pass.
* Documentation is updated for the changed web demo behavior.
* No unrelated files are changed.

## Technical Approach

Update the native JavaScript web demo gate in `privacy-display/webstudy/static/app.js` by changing the minimum threshold and disabling the start action based on `state.refresh.ok`, not merely the presence of a measurement. Add a defensive click guard before entering the typing step. Update `privacy-display/webstudy/README.md` to document the stricter start behavior.

## Decision (ADR-lite)

**Context**: The current demo records low refresh sessions and allows them to continue, with low-cycle masking falling back to static subframes. The user asked that tests must not start below the minimum specified by the disclosure document.

**Decision**: Enforce a global `144Hz` minimum gate before any test trial can start, while leaving the per-condition static fallback as a secondary safety mechanism.

**Consequences**: Operators on 60Hz or 120Hz displays must switch hardware/display settings before collecting data. This avoids collecting sessions that contradict the disclosure's stated minimum.

## Out of Scope

* Detecting the operating system's maximum supported refresh rate through EDID/DisplayID.
* Automatically changing display settings.
* Changing the Python desktop demo's refresh-rate adaptation logic.

## Technical Notes

* `技术交底书.md` states: "系统要求显示设备刷新率不低于 144Hz（推荐 240Hz 或更高）".
* `技术交底书.md` also defines `f_r >= 60n`; this web demo already keeps `static_fallback` for unsafe per-condition cycles.
* Current files inspected: `privacy-display/webstudy/static/app.js`, `privacy-display/webstudy/static/mask.js`, `privacy-display/webstudy/static/style.css`, `privacy-display/webstudy/README.md`.
