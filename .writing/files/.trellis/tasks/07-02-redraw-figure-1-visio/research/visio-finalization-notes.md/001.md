# Visio finalization notes

- Use the ShapeSheet cells `LeftMargin`, `RightMargin`, `TopMargin`, and `BottomMargin` for Visio text margins. The `Txt*` variants do not address the intended text-block margins.
- Reopen the saved `.vsdx` before the authoritative PDF export. Visio can retain a stale rendering cache after repeated COM-driven edits; a fresh document session avoids black or stale PDF output.
- Validate the publication raster preview independently from the editable Visio source: rasterize the final single-page PDF at 300 dpi and verify its dimensions, typography, connectors, and Unicode symbols.
- These are task-local diagram-production notes, not backend/frontend/API contracts, so no `.trellis/spec/` code-spec update is required.
