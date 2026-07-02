# Review Evidence for the IEEE Access Revision

## Journal criteria

- IEEE Access requires original contribution, technically sound and sufficiently
  described experiments/statistics, conclusions supported by data, standard
  English, and appropriate prior-work coverage.
- IEEE Access uses a binary decision model. Material methodological corrections
  correspond to reject-with-resubmission rather than minor-edit acceptance.

Canonical pages:

- https://ieeeaccess.ieee.org/authors/preparing-your-article/
- https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/
- https://ieeeaccess.ieee.org/authors/submission-guidelines/

## Directly relevant prior art

- Yerazunis and Carbone, *Privacy-Enhanced Displays by Time-Masking Images*,
  OzCHI 2001 / MERL TR2002-11. It alternates private and mask images above the
  normal frame rate, explicitly discusses persistence-of-vision integration,
  camera attacks, monitor gamma, brightness trade-offs, and reconstruction
  limits. Canonical PDF: https://www.merl.com/publications/docs/TR2002-11.pdf
- Lim, *Defeat Spyware with Anti-Screen Capture Technology Using Visual
  Persistence*, SOUPS 2007. The current paper already cites this work, but must
  treat temporal fragmentation as prior art rather than a new principle.
  Canonical PDF: https://cups.cs.cmu.edu/soups/2007/posters/p147_lim.pdf
- Wu and Zhai, *Temporal Psychovisual Modulation: A New Paradigm of Information
  Display*, IEEE Signal Processing Magazine, 2013. Relevant to temporal display
  modulation and should be distinguished from the naked-eye/camera threat model.

## Authoritative local evidence

- `real_capture_ocr.json` contains 10,575 captures across nine positions, but
  the condition counts are unbalanced and include component and parameter
  studies. It is not a `9 x 7 x 3` balanced factorial experiment.
- The attacker-favourable best-of-engine table is in `real_capture_ocr.md`.
  It reports original/deployed/capture-hardened short-exposure recovery of
  92.5%/14.1%/4.2%, but deployed and hardened temporal-average recovery remains
  65.4% and 42.3%.
- Physical `mask_noise` short-exposure recovery (24.7%) is worse than
  `mask_only` (17.5%); the noise module is not an unconditional improvement.
- `real_capture_mot_tracking.json` identifies the tracker as
  `greedy_bytetrack_fallback`, the physical capture as stop-motion, and the
  position as 1.5 m at 0 degrees.
- The simulated MOT artifact also uses `greedy_bytetrack_fallback`; HOTA was not
  available for that run.
- `publication_summary.md` records the usability pilot as missing. FPI, MI,
  Delta E, and SSIM values are model-derived proxies, not participant evidence.

## Claim boundaries

- The linear completeness condition that enables human temporal integration
  also enables complete-cycle camera reconstruction. CSPRNG secrecy does not
  prevent averaging once the displayed subframes have been captured.
- The base configuration may support short-exposure mitigation. The hardened
  configuration partially reduces long-exposure and temporal-average recovery,
  but it visibly degrades the image and lacks completed user evidence.
- One webcam, one display, and stop-motion target-tracking capture cannot support
  unrestricted cross-device camera-defeat claims.

