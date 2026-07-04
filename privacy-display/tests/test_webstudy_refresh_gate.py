from pathlib import Path


APP_JS = Path(__file__).resolve().parents[1] / "webstudy" / "static" / "app.js"
MAIN_TEX = Path(__file__).resolve().parents[2] / "paper" / "main.tex"
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

    assert "assignmentForRegistrationIndex(state.registrationIndex" in app_js
    assert "MASKED_PREVIEW_DURATION_S" in app_js
    assert 'input.addEventListener("paste"' in app_js
    assert "event.preventDefault();" in app_js
    assert "(meta.counts || []).reduce" in app_js
    assert 'DEMO ? `${ASSUMED_MONITOR_HZ} 赫兹 演示模式`' in app_js
    assert ': `${ASSUMED_MONITOR_HZ} 赫兹 受控实验`' in app_js


def test_paper_contains_non_dangling_data_availability_section():
    main_tex = MAIN_TEX.read_text(encoding="utf-8")

    assert "\\section*{数据与代码可用性}" in main_tex


def test_registration_is_preflighted_and_mask_preview_starts_hidden():
    app_js = APP_JS.read_text(encoding="utf-8")

    assert 'fetch(`/api/registration-status?${query}`,' in app_js
    assert 'id="identityStatus"' in app_js
    assert 'id="stimulusCanvas" class="masked-canvas" hidden' in app_js
    assert "canvas.hidden = false;" in app_js


def test_paper_describes_final_assignment_without_internal_history():
    main_tex = MAIN_TEX.read_text(encoding="utf-8")

    assert "保证联合顺序分配的确定性与均衡性" in main_tex
    assert "哈希随机碰运气" not in main_tex


def test_formal_database_is_gitignored():
    ignored = WEBSTUDY_GITIGNORE.read_text(encoding="utf-8").splitlines()

    assert "study_formal.db" in ignored
