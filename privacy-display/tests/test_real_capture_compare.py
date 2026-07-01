from experiments.real_capture_compare import build_comparison, render_markdown


def _sim(off, overlay, deployed, capture_hardened):
    def block(v):
        return {"exact_match": {"mean": v}}
    return {"summary": {
        "block1/off": block(off),
        "block1/strong@overlay": block(overlay),
        "block1/strong@deployed": block(deployed),
        "block1/vlm": block(capture_hardened),
    }}


def _real(values, attack="video:temporal_mean"):
    return {"summary": {"by_ablation_attack": {
        f"{abl}|{attack}": {"exact_match": {"mean": v}} for abl, v in values.items()
    }}}


def test_build_comparison_aligns_labels_and_computes_gap():
    sim = _sim(0.80, 0.10, 0.02, 0.0)
    real = _real({"mask_noise": 0.70, "anti_ocr": 0.15, "deployed": 0.05, "vlm": 0.0})
    rows = build_comparison(real, sim)
    by_abl = {r["ablation"]: r for r in rows}
    assert by_abl["mask_noise"]["sim_key"] == "block1/off"
    assert by_abl["deployed"]["sim"] == 0.02
    assert by_abl["deployed"]["real"] == 0.05
    assert abs(by_abl["deployed"]["real_minus_sim"] - 0.03) < 1e-9
    assert by_abl["capture_hardened"]["sim_key"] == "block1/vlm"
    assert by_abl["capture_hardened"]["real"] == 0.0


def test_build_comparison_tolerates_missing_real_rows():
    sim = _sim(0.8, 0.1, 0.02, 0.0)
    rows = build_comparison({"summary": {}}, sim)
    assert all(r["real"] is None and r["real_minus_sim"] is None for r in rows)
    # render must not crash on n/a values
    assert "Real Camera vs Simulation" in render_markdown(
        rows, real_attack="video:temporal_mean", metric="exact_match")
