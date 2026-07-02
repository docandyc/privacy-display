# Terminology Ledger

| Canonical term | First-use form | Variants to replace or explain |
|---|---|---|
| temporal pixel masking | temporal pixel masking | temporal masking, temporal fragmentation (use only descriptively) |
| unprotected | unprotected display | original, clean (retain only in dataset condition names) |
| deployed profile | deployed profile | deployed mode, readable profile |
| capture-hardened profile | capture-hardened profile | capture_hardened, legacy `vlm` label |
| short-exposure capture | short-exposure capture | snapshot, short, single subframe (the physical rolling-shutter image is not a pure subframe) |
| long-exposure capture | long-exposure capture | long |
| temporal-average attack | video temporal-average attack | video:temporal_mean, integration attack |
| character recovery rate | character recovery rate | char recovery, character accuracy |
| exact-match rate | exact-match rate | exact, exact match |
| sensitive-token recall | sensitive-token recall | sensitive token |
| leakage rate | leakage rate | leak rate; define threshold as character recovery >=20% |
| flicker proxy index (FPI) | flicker proxy index (FPI) | FPI |
| mutual-information proxy (MI) | mutual-information proxy (MI) | MI; explicitly label as a proxy |
| structural similarity index (SSIM) | structural similarity index (SSIM) | SSIM |
| CIEDE2000 colour difference | CIEDE2000 colour difference, Delta E 00 | Delta E |
| greedy ByteTrack-style fallback | greedy ByteTrack-style fallback tracker | ByteTrack (do not claim the official implementation) |

Decisions:

- Keep the current manuscript in Chinese. English terminology in tables,
  metrics, and condition names follows the canonical forms above.
- Use `camera capture` for the general threat but limit guarantees to the named
  capture modes.
- Use `mitigates` or `reduces`, not `defeats`, `prevents`, or `blocks`, unless a
  zero result is explicitly tied to a tested condition.
