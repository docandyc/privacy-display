# 同步中英文论文 WebStudy 预声明协议

## Goal

Before formal participant collection begins, align the English and Chinese manuscripts with the implemented WebStudy protocol and its default analysis exclusions.

## Requirements

- Add the default minimum-view straight-line rating exclusion to both manuscripts as a pre-registered criterion. Match the implementation: all six rating rows have `view_duration_ms <= 11,000`, and all four dimensions within each row have the same score.
- Add the 8-second unscored masked typing practice after the 10-second masked preview and before the four scored trials.
- State that every typing attempt uses a 5-second countdown after Start is clicked.
- State that the typing stimulus is already visible and playing before Start in both conditions.
- Define first-keystroke latency from the end of the countdown, when the input is enabled, to the first valid input event.
- Replace generic rating names with the actual four item labels and anchors used by the WebStudy UI.
- State that higher scores mean better outcomes for stability, comfort, and subjective anti-camera protection.
- Explicitly limit the anti-camera rating to a subjective impression because participants are not shown camera-captured output.
- Keep the English and Chinese protocol descriptions semantically equivalent.

## Acceptance Criteria

- [x] `paper/main.tex` contains all protocol details above.
- [x] `paper-Chinese/main.tex` contains the equivalent Chinese details.
- [x] Old user-study wording that reverses or obscures rating direction is removed from both active manuscripts.
- [x] Both manuscripts complete their checked-in/full `latexmk` build path without unresolved references.

## Out of Scope

- Changing WebStudy runtime or analysis code.
- Addressing `.gitignore` or previously committed Playwright artifacts.
