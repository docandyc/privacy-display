"""Apply reviewed Figure 1 text corrections to the final vector PDF.

The original PDF uses an A4 media box with the actual figure in the lower-left
viewport consumed by ``paper/main.tex``.  This overlay preserves the Visio
vector export and changes only the two reviewed text areas.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from pypdf.generic import ContentStream


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "final" / "figure1_concept_threat.pdf"


def main() -> None:
    reader = PdfReader(str(PDF))
    page = reader.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    # Remove the original text operators (and a previous generated overlay, if
    # this script is rerun) so PDF text extraction cannot surface stale labels.
    content = ContentStream(page.get_contents(), reader)
    kept = []
    for operands, operator in content.operations:
        if operator in (b"Tj", b"TJ"):
            flattened = "".join(
                str(item)
                for operand in operands
                for item in (operand if isinstance(operand, list) else [operand])
                if not isinstance(item, (int, float))
            )
            if flattened in {"Instantaneous", "50 ms", "Short-exposure", "\x01,"}:
                continue
        kept.append((operands, operator))
    content.operations = kept
    page.replace_contents(content)

    packet = BytesIO()
    layer = canvas.Canvas(packet, pagesize=(width, height))

    # Remove the unsupported fixed human-integration time. The original line
    # spacing overlaps the lower edge of "integration", so redraw that word.
    layer.setFillColorRGB(1, 1, 1)
    layer.rect(207.5, 96.4, 36.0, 14.8, fill=1, stroke=0)
    integration = "integration"
    integration_font = "Helvetica-Bold"
    integration_size = 6.48
    integration_width = stringWidth(integration, integration_font, integration_size)
    layer.setFont(integration_font, integration_size)
    layer.setFillColorRGB(23 / 255, 122 / 255, 54 / 255)
    layer.drawString(225.5 - integration_width / 2, 103.2, integration)

    # Replace the zero-duration implication while preserving the second line.
    layer.setFillColorRGB(1, 1, 1)
    layer.rect(168.0, 43.8, 48.0, 9.2, fill=1, stroke=0)
    label = "Short-exposure"
    font = "Helvetica-Bold"
    size = 6.48
    label_width = stringWidth(label, font, size)
    layer.setFont(font, size)
    layer.setFillColorRGB(217 / 255, 71 / 255, 34 / 255)
    layer.drawString(192.0 - label_width / 2, 45.0, label)

    layer.save()
    packet.seek(0)
    page.merge_page(PdfReader(packet).pages[0])

    writer = PdfWriter()
    writer.add_page(page)
    with NamedTemporaryFile(dir=PDF.parent, suffix=".pdf", delete=False) as tmp:
        temp_path = Path(tmp.name)
        writer.write(tmp)
    try:
        temp_path.replace(PDF)
    finally:
        temp_path.unlink(missing_ok=True)

    print(f"patched {PDF}")


if __name__ == "__main__":
    main()
