# Sync Current English Manuscript to Chinese

## Objective

Translate the current `paper/main.tex` into publication-quality academic Chinese at `paper-Chinese/main.tex`, preserving the English manuscript's evidence scope, quantitative results, LaTeX structure, labels, citations, equations, tables, figures, and unresolved author/user-study placeholders.

## Source of Truth

- Content and structure: `paper/main.tex`
- Chinese build entry point: `paper-Chinese/build.sh`
- Bibliography: synchronize `paper-Chinese/refs.bib` with the citations required by the current English manuscript without inventing or changing reference facts.

## Translation Requirements

- Use refined English-to-Chinese academic translation.
- Prefer natural Chinese scholarly prose over literal English syntax.
- Keep terminology consistent, including:
  - Temporal pixel masking → 时序像素掩蔽
  - character recovery → 字符恢复率
  - exact match → 完全匹配率
  - readability-priority → 可读性优先档
  - high-suppression → 高抑制档
  - common-setting analysis → 共同设置分析
  - vision-language model → 视觉语言模型
- Preserve all numerical values, denominators, uncertainty intervals, comparison directions, and claim boundaries exactly.
- Preserve LaTeX commands, math, labels, citation keys, table/figure paths, and cross-references.
- Keep author information and unfinished user-study result placeholders unresolved.
- Reflect the author-confirmed facts that display brightness and acquisition phase were held fixed.
- Do not translate reference titles or author names in the BibTeX database.

## Acceptance Criteria

- `paper-Chinese/main.tex` mirrors the current English manuscript's section, label, table, and figure structure.
- All prose, headings, captions, table headers, footnotes, and availability/acknowledgment text are in academic Chinese except proper nouns, model names, code, paths, and necessary technical English.
- No stale numerical claims from the older Chinese manuscript remain.
- `paper-Chinese/build.sh` exits successfully.
- Final LaTeX logs contain no undefined citations or references.
- Rendered Chinese PDF has no clipped, overlapping, or unreadable content.
- A final terminology and number consistency review is completed against `paper/main.tex`.

## Out of Scope

- Completing the user study or filling its numerical placeholders.
- Filling author, affiliation, funding, or corresponding-author information.
- Translating embedded English text inside figures.
- Changing the scientific claims or adding new experimental evidence.
- Translating `paper/supplementary.tex` unless separately requested.
