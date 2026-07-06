# WebStudy Manuscript Protocol Synchronization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Synchronize the English and Chinese user-study methods with the frozen WebStudy runtime and default exclusion logic before participant collection.

**Architecture:** Treat `privacy-display/webstudy/static/app.js` and `privacy-display/webstudy/analyze_study.py` as the protocol sources of truth. Update only the active English and Chinese manuscript sources, preserving equivalent meaning and the existing IEEE Access structure.

**Tech Stack:** LaTeX, XeLaTeX, latexmk, BibTeX

---

### Task 1: Update the English protocol

**Files:**
- Modify: `paper/main.tex`

1. Add the 8-second masked practice, 5-second countdown, pre-start stimulus exposure, and corrected first-keystroke latency origin.
2. Replace generic rating names with the four displayed labels and anchors.
3. Add the subjective anti-camera construct limitation.
4. Add the exact minimum-view straight-line exclusion to the pre-registered criteria.

### Task 2: Update the Chinese protocol

**Files:**
- Modify: `paper-Chinese/main.tex`

1. Mirror every English protocol change in idiomatic Chinese.
2. Preserve numerical thresholds and rating directions exactly.

### Task 3: Verify both manuscripts

1. Search both active manuscripts for stale user-study terminology.
2. Build `paper/main.tex` with a complete XeLaTeX/latexmk cycle.
3. Build `paper-Chinese/main.tex` with `./build.sh`.
4. Check logs for unresolved citations, references, and labels.

