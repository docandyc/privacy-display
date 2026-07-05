# Visio export pitfalls discovered during Figure 2 reconstruction

## Text-block margins

Visio's ShapeSheet text-block margin cells are `LeftMargin`, `RightMargin`, `TopMargin`, and `BottomMargin`.
Writing `TxtMarginLeft`/`TxtMarginRight` silently leaves the default margins in place. At a 7.16-inch paper width,
the retained margins can force short English words such as `PRIVATE`, `CAMERA`, and `Unreadable` to break even when
the shape `Width`, `TxtWidth`, and font size are otherwise correct.

Verification contract:

- Inspect the rendered PNG/PDF, not only the scene validator.
- For compact text shapes, set the four correct ShapeSheet margin cells explicitly.
- Reopen the saved VSDX before the final export; exporting immediately after Unicode text replacement can briefly
  use stale Visio rendering state.
- Confirm the final PDF by rasterizing it at the publication resolution.

## Publication raster output

Visio's default PNG export was 144 dpi in this environment. The publication PNG was therefore rasterized from the
final vector PDF at 300 dpi, producing 2148 x 859 pixels for a 7.16 x 2.862 inch page.

