# Add Chen Xing as Corresponding Second Author

## Goal

Complete the English IEEE Access manuscript's author metadata by adding Chen Xing as the second and corresponding author, using the first author's institutional affiliation, the supplied email address, portrait, and biography.

## Requirements

* Add Chen Xing as the second author in `paper/main.tex` and associate him with affiliation 1.
* Identify Chen Xing as the corresponding author with `xingch@zuwe.edu.cn`.
* Preserve the existing affiliation text used by Zheyuan Huang.
* Copy the supplied portrait into `paper/profiles/` under a stable descriptive filename and use it in Chen Xing's IEEE biography block.
* Add the supplied English biography text without changing its factual content.
* Preserve the first author's metadata and biography.

## Acceptance Criteria

* [x] The author line lists Zheyuan Huang first and Chen Xing second, both linked to affiliation 1.
* [x] The correspondence line names Chen Xing and contains `xingch@zuwe.edu.cn` with no remaining correspondence placeholder.
* [x] A second `IEEEbiography` block contains Chen Xing's portrait and all supplied biography statements.
* [x] The portrait is stored inside the repository and resolves during compilation.
* [x] The complete manuscript build exits successfully with no undefined citations or references.
* [x] The generated PDF visibly contains the updated author line, correspondence line, and Chen Xing biography.

## Definition of Done

* Manuscript source and portrait are updated.
* The checked-in LaTeX build path is run to completion.
* Build logs and rendered PDF are checked for missing assets, unresolved references, and visible layout regressions.

## Technical Approach

Follow the manuscript's existing IEEE Access conventions: use `\authorrefmark{1}` for the shared affiliation, `\corresp{...}` for the corresponding-author declaration, and a second `IEEEbiography` environment after the first author's biography.

## Decision (ADR-lite)

**Context:** The repository contains multiple manuscript copies, but `paper/main.tex` is the current English manuscript with Zheyuan Huang already populated and explicit placeholders for the additional and corresponding author.

**Decision:** Update only the current English manuscript under `paper/` and place the new portrait under `paper/profiles/`.

**Consequences:** The Chinese and archival manuscript copies remain unchanged. They can be synchronized in a separate translation task if required.

## Out of Scope

* Editing unrelated submission placeholders such as funding and acknowledgment.
* Translating the biography or synchronizing older Chinese/archive manuscript copies.
* Retouching or otherwise altering the supplied portrait.

## Technical Notes

* Current manuscript: `paper/main.tex`.
* Existing first-author portrait pattern: `paper/profiles/hzy.JPG`.
* Build verification follows `.trellis/spec/guides/latex-paper-build-thinking-guide.md`.
