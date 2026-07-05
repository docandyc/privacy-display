# GPT-Image prompt for Figure 1

Use case: scientific-educational

Asset type: publication-ready Figure 1 concept and threat schematic for an IEEE Access paper, sized for a single journal column

Input images: Image 1 is a style reference only. Match its flat vector-like scientific style, white background, dark-navy outlines, sans-serif typography, green human branch, and orange-red camera branch. Do not copy its pipeline layout or formulas.

Primary request: Create a concise two-panel scientific concept figure explaining a smartphone visual-eavesdropping threat and the core perceptual asymmetry of a temporal pixel-masking privacy display.

Composition/framing: landscape 3:2 canvas suitable for one-column placement. Two balanced panels separated by a thin vertical divider. Large readable labels, generous whitespace, no title inside the figure.

Left panel, label exactly "(a) Physical visual eavesdropping":

- Show a clean office scene as simple flat line art: an authorized user seated directly in front of a desktop display reading sensitive information.
- The display visibly contains the exact sample text "PRIVATE DATA".
- From an oblique or distant position, show one unauthorized smartphone camera aimed at the display.
- Use subtle orange-red dashed capture rays or a view cone from the smartphone toward the screen.
- Add the exact labels "Authorized user", "Sensitive display", and "Smartphone camera".
- Make it unmistakably a physical smartphone camera-capture threat, not a digital screenshot or network attack.
- IMPORTANT: show no smart glasses, no eyeglasses, no wearable camera, and no second attacker device.

Right panel, label exactly "(b) Asymmetric perception":

- In the center, show a compact horizontal sequence of four different sparse complementary subframe thumbnails with a fast time arrow, labeled exactly "Rapid complementary subframes".
- Upper green branch: an eye icon accumulates all four subframes, followed by a clean readable display thumbnail containing "PRIVATE DATA". Use the exact labels "Human eye", "Temporal integration ≈ 50 ms", and "Readable".
- Lower orange-red branch: a camera icon with a narrow shutter bracket selects only one subframe, followed by a sparse unreadable fragment and a crossed-out OCR symbol. Use the exact labels "Camera", "Instantaneous sampling", and "Unreadable fragment".
- The human path must visibly sum the full sequence; the camera path must visibly sample only one moment.
- In the camera path, highlight exactly one selected subframe with a narrow shutter bracket. Do not place plus signs between all four camera-path thumbnails, because that would incorrectly imply temporal summation by the camera.

Style/medium: flat vector-like scientific infographic, crisp simple geometry, restrained IEEE journal aesthetic, consistent medium-weight sans-serif typography, thin dark-navy outlines. Use navy and cyan for the display/subframes, green only for the human-readable path, orange-red only for the unauthorized smartphone and unreadable path.

Text constraints: Render every quoted label verbatim and only once. Keep text large enough for reduction to a single journal column. No caption, no in-figure title, no citations, no numerical performance claims.

Scientific constraints: Do not imply encryption, wireless interception, screenshot blocking, or permanent information destruction. The distinction is specifically human temporal integration versus short-exposure camera sampling. Keep this conceptual; do not include ChaCha20, Fisher–Yates, GPU, adversarial noise, inversion, or implementation formulas because those belong in Figure 2.

Avoid: smart glasses, eyeglasses, wearable devices, multiple cameras, photorealism, 3D, gradients, drop shadows, dark background, dense prose, decorative circuitry, fake logos, watermark, extra labels, tiny text, spelling errors.

Style reference: `paper/figures/method_pipeline_gpt_image.png`.
