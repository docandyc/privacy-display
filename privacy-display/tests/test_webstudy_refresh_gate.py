from pathlib import Path


APP_JS = Path(__file__).resolve().parents[1] / "webstudy" / "static" / "app.js"
WEBSTUDY_GITIGNORE = Path(__file__).resolve().parents[1] / "webstudy" / ".gitignore"


def test_webstudy_formal_mode_requires_200hz_and_demo_keeps_144hz_path():
    app_js = APP_JS.read_text(encoding="utf-8")

    assert "const MIN_REFRESH_HZ = DEMO ? 144 : 200;" in app_js
    assert 'id="continueRefresh" ${state.refresh.ok && state.environmentConfirmed ? "" : "disabled"}' in app_js
    assert "if (!state.refresh.ok || !state.environmentConfirmed)" in app_js
    assert "if (!DEMO)" in app_js
    assert "return MASKED_TARGET_N;" in app_js
    assert "不能开始测试" in app_js


def test_webstudy_replaces_n8_with_temporal_n3_and_rebuilds_after_refresh():
    app_js = APP_JS.read_text(encoding="utf-8")

    assert 'id: "n3_mask_noise"' in app_js
    assert 'id: "n8_mask_noise"' not in app_js
    assert "resetExperimentPlan();" in app_js


def test_webstudy_followup_validity_guards_are_present():
    app_js = APP_JS.read_text(encoding="utf-8")

    assert 'fetch("/api/next-assignment"' in app_js
    assert "assignmentForRegistrationIndex(state.assignment.registration_index" in app_js
    assert "MASKED_PREVIEW_DURATION_S" in app_js
    assert "MASKED_PRACTICE_DURATION_S" in app_js
    assert 'input.addEventListener("paste"' in app_js
    assert "event.preventDefault();" in app_js
    assert "(meta.counts || []).reduce" in app_js
    assert 'DEMO ? `${ASSUMED_MONITOR_HZ} 赫兹 演示模式`' in app_js
    assert ': `${ASSUMED_MONITOR_HZ} 赫兹 受控实验`' in app_js


def test_registration_is_preflighted_and_mask_preview_starts_hidden():
    app_js = APP_JS.read_text(encoding="utf-8")

    assert 'id="registrationIndex"' not in app_js
    assert 'fetch("/api/next-assignment"' in app_js
    assert 'id="identityStatus"' in app_js
    assert 'id="stimulusCanvas" class="masked-canvas" hidden' in app_js
    assert "canvas.hidden = false;" in app_js


def test_formal_database_is_gitignored():
    ignored = WEBSTUDY_GITIGNORE.read_text(encoding="utf-8").splitlines()

    assert "study_formal.db" in ignored
