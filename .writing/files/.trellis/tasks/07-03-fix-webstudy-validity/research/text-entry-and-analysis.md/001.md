# Text-entry scoring and analysis notes

## Text-entry accuracy

- Soukoreff and MacKenzie, “Metrics for text entry research: An evaluation of MSD and KSPC, and a new unified error metric,” CHI 2003, pp. 113–120, DOI `10.1145/642611.642632`, establishes minimum string distance (Levenshtein/MSD) as a text-entry error metric and explains why raw position-by-position comparison is inadequate.
- This experiment is time-limited and presents a target longer than participants are expected to finish. Therefore untyped target suffixes must not count as errors. The implementation should align the complete transcription against the best target prefix, then calculate MSD error rate over the longer of the transcription and aligned prefix.
- Corrected keystrokes are not currently captured as an input stream, so the full unified corrected/uncorrected error framework cannot be reconstructed. The stored method label must state this limitation instead of claiming the full framework.

## Within-subject analysis

- Average the two repetitions within each condition before paired inference so the participant, not the trial, is the unit of analysis.
- Report paired mean/median differences with deterministic participant-level bootstrap confidence intervals.
- Use paired t tests when paired differences pass the predeclared normality check; otherwise use Wilcoxon signed-rank. Report Cohen's `dz` for the paired t path and matched-pairs rank-biserial correlation for Wilcoxon.
- Treat the six 1–5 rating conditions as repeated ordinal outcomes: omnibus Friedman per dimension, followed by pairwise Wilcoxon signed-rank tests with Holm correction when appropriate.
- Default exclusions: debug/demo sessions, incomplete rows, refresh below 200Hz, non-temporal scored mask trials, observed effective base cycle below 50Hz, and mean control accuracy below 50%. Keep an exclusion audit in every report.

## Design convergence

- N=24 is both within the reviewer's approximate 80%-power range for medium-to-large paired effects and divisible by the six rating-order rows.
- ABBA/BAAB controls first-order practice/fatigue within a participant while providing two repetitions per condition.
- For six conditions, a Williams-style balanced row and its cyclic shifts balance first-order carryover better than unconstrained randomization.
