# IEEE figure constraints and implementation mapping

## IEEE publication constraints

- IEEE recommends vector graphics for diagrams that may be resized. PDF is an accepted vector format.
- Standard final widths are 3.5 in (one column) and 7.16 in (two columns).
- Raster color or grayscale graphics should exceed 300 dpi; black-and-white line art should exceed 600 dpi.
- IEEE recommends Arial, Helvetica, Times New Roman, Cambria, or Symbol, with type appearing at approximately 9--10 pt at final size.
- Meaning should not rely on color alone. This task also uses solid/dashed paths, explicit labels, and distinct eye/camera shapes.

Sources:

- https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/resolution-and-size/
- https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/file-formatting/
- https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/

## Code-to-figure mapping

- `privacy-display/src/core/mask_generator.py`
  - HMAC-SHA256 derives a cycle-dependent ChaCha20 subkey.
  - Rejection sampling produces an unbiased slot-index matrix `R(x,y)`.
  - Binary masks are `M_k = [R = k]` and satisfy per-pixel complementarity.
  - Fisher--Yates generates the randomized temporal output permutation; it does not directly construct the spatial masks.
- `privacy-display/src/core/noise_injector.py`
  - FGSM/PGD shadow-model noise is optional reinforcement.
  - `split_complementary` enforces `sum_k N_k = 0`.
- `privacy-display/src/core/subframe_composer.py` and `privacy-display/src/gpu/renderer.py`
  - The main synthesis is `I_k = I * M_k + N_k`, followed by display compensation/clipping.
  - The renderer emits subframes in the Fisher--Yates permutation.
- `privacy-display/src/core/timing_controller.py`
  - Subframe advancement is synchronized to VBlank.
  - The physical refresh rate is divided across `n` temporal slots.
- `paper/main.tex`
  - Human perception integrates the sequence over approximately 50 ms.
  - The short-exposure camera condition is approximately 4 ms and captures roughly one subframe.

## Visual decisions

- Figure 2 is a deterministic editable Draw.io diagram and is exported as a two-column vector PDF with embedded diagram XML.
- Figure 1 is a high-resolution GPT Image raster illustration for a one-column conceptual overview.
- Both figures use white backgrounds, Arial-like sans-serif labels, navy/cyan method elements, green human perception, and orange-red camera sampling.
- Figure 2 uses dashed borders for optional reinforcement and a dashed camera path, so the semantics remain visible in grayscale.
