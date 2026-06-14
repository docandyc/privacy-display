from pathlib import Path


APP_JS = Path(__file__).resolve().parents[1] / "webstudy" / "static" / "app.js"


def test_webstudy_blocks_tests_below_disclosure_minimum_refresh_rate():
    app_js = APP_JS.read_text(encoding="utf-8")

    assert "const MIN_REFRESH_HZ = 144;" in app_js
    assert 'id="continueRefresh" ${state.refresh.ok ? "" : "disabled"}' in app_js
    assert "if (!state.refresh.ok)" in app_js
    assert "不能开始测试" in app_js
