"""webstudy 弱反色帧（α=0.2）移植的源文件断言（沿用现有读文本断字符串模式）。

masked 打字试次须叠加弱反色并保持 temporal；ratings 中只有 deployed_full 使用反色。
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "webstudy" / "static" / "app.js"
MASK_JS = ROOT / "webstudy" / "static" / "mask.js"


def test_app_js_declares_inversion_constants_and_threads_them():
    app = APP_JS.read_text(encoding="utf-8")
    assert "const INSERT_INVERSION = true;" in app
    assert "const INVERSION_ALPHA = 0.2;" in app
    # masked 试次配置启用反色，并体现在 components 标签。
    assert "insertInversion: INSERT_INVERSION" in app
    assert "inversionAlpha: INVERSION_ALPHA" in app
    assert "mask+noise+anti-ocr+inversion" in app
    # 传入 player.load。
    assert "insertInversion: trial.insertInversion || false" in app
    # 闪烁提示（48Hz < 50Hz）。
    assert "inversionFlicker" in app
    assert "弱反色帧" in app


def test_mask_js_inserts_partial_inversion_and_records_meta():
    mask = MASK_JS.read_text(encoding="utf-8")
    # 选项解析与振幅缩放反色（朝黑、逐通道 alpha*(255-value)）。
    assert "const insertInversion = Boolean(options.insertInversion);" in mask
    assert "inversionAlpha * (255 - source.data[px + c])" in mask
    assert "if (insertInversion) {" in mask
    # 元数据字段（含每周期槽数与闪烁告警）。
    assert "insert_inversion: insertInversion" in mask
    assert "inversion_alpha: insertInversion ? inversionAlpha : null" in mask
    assert "per_cycle_slots: perCycleSlots" in mask
    assert "inversion_flicker_warn: inversionFlickerWarn" in mask
    # 加反色不回退静态：mode 仍按 refresh/n 计算。
    assert 'const mode = refreshHz > 0 && cycleHz < safeFlickerHz ? "static_fallback" : "temporal";' in mask


def test_ratings_only_threads_inversion_from_deployed_condition():
    app = APP_JS.read_text(encoding="utf-8")
    assert 'id: "deployed_full"' in app
    assert 'cycles: condition.id === "deployed_full" ? ANTI_CAPTURE_CYCLES : 1' in app
    assert "insertInversion: condition.insertInversion || false" in app
    assert "antiOcr: condition.antiOcr || null" in app
