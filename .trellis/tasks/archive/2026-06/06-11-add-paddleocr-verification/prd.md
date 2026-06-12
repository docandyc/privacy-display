# Add PaddleOCR verification support

## Goal

After installing EasyOCR and PaddleOCR in the project virtual environment, make the project OCR evaluator detect and run PaddleOCR so multi-engine verification can include Tesseract, EasyOCR, and PaddleOCR.

## Requirements

* Preserve existing Tesseract and EasyOCR behavior.
* Detect `paddleocr` as an available engine when import succeeds.
* Add a PaddleOCR recognition path compatible with PaddleOCR 3.x.
* Keep tests lightweight and avoid downloading model weights in unit tests.
* Run import/version verification and project tests.

## Acceptance Criteria

* [ ] `OCREvaluator().engines` includes `paddleocr`.
* [ ] `recognize(..., "paddleocr")` can parse PaddleOCR-style outputs.
* [ ] Unit tests pass.

## Out of Scope

* Training OCR models.
* Changing privacy-display algorithms.
* Committing package cache or model weights.

## Technical Notes

* Main file: `privacy-display/src/attack/ocr_evaluator.py`.
* PaddleOCR 3.6 constructor accepts `lang` and exposes prediction APIs whose output shape can differ by version.
