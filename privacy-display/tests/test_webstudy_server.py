import csv
import io
import sqlite3

from webstudy.server import DEFAULT_DB_PATH, build_export_csv, create_app, init_db


RATING_CONDITIONS = [
    "control_anchor",
    "n2_mask_noise",
    "n3_mask_noise",
    "n4_mask_noise",
    "n4_mask_only",
    "deployed_full",
]


def balanced_latin_order(items, row_index):
    first_row = [0]
    offset = 1
    while len(first_row) < len(items):
        first_row.append(offset)
        if len(first_row) < len(items):
            first_row.append(len(items) - offset)
        offset += 1
    return [items[(index + row_index) % len(items)] for index in first_row]


def make_payload(
    *,
    session_uuid="00000000-0000-4000-8000-000000000001",
    registration_index=0,
    debug=False,
    demo=False,
):
    typing_order_index = registration_index % 2
    rating_order_index = (registration_index // 2) % len(RATING_CONDITIONS)
    typing_conditions = (
        ("control", "masked", "masked", "control")
        if typing_order_index == 0
        else ("masked", "control", "control", "masked")
    )
    typing = []
    repetition_counts = {"control": 0, "masked": 0}
    for trial_index, condition in enumerate(typing_conditions):
        repetition_counts[condition] += 1
        typing.append({
            "condition": condition,
            "trial_index": trial_index,
            "condition_repetition": repetition_counts[condition],
            "n": 1 if condition == "control" else 4,
            "requested_n": 1 if condition == "control" else 4,
            "components": "none" if condition == "control" else "mask+noise+anti-ocr+inversion",
            "target_text": "hello world",
            "typed_text": "helo world",
            "correct_chars": 10,
            "correct_letters": 9,
            "attempted_chars": 10,
            "attempted_letters": 9,
            "total_chars": 11,
            "accuracy": 10 / 11,
            "cpm": 30,
            "wpm": 6,
            "duration_s": 20,
            "edit_distance": 1,
            "aligned_target_chars": 11,
            "msd_error_rate": 1 / 11,
            "scoring_method": "msd_target_prefix_v1",
            "first_key_latency_ms": 420,
            "mask_meta": {
                "mode": "source_control" if condition == "control" else "temporal",
                "observed_effective_cycle_hz": 60 if condition == "masked" else 240,
                "dropped_frames": 0,
            },
        })
    ratings = []
    rating_conditions = balanced_latin_order(RATING_CONDITIONS, rating_order_index)
    for order_index, condition in enumerate(rating_conditions):
        n_by_condition = {
            "control_anchor": 1,
            "n2_mask_noise": 2,
            "n3_mask_noise": 3,
            "n4_mask_noise": 4,
            "n4_mask_only": 4,
            "deployed_full": 4,
        }
        components_by_condition = {
            "control_anchor": "none",
            "n4_mask_only": "mask-only",
            "deployed_full": "mask+noise+anti-ocr+inversion",
        }
        ratings.append({
            "condition_label": condition,
            "display_label": condition,
            "n": n_by_condition[condition],
            "requested_n": n_by_condition[condition],
            "components": components_by_condition.get(condition, "mask+noise"),
            "stimulus_text": "rating text",
            "readability": 4,
            "flicker": 4,
            "fatigue": 4,
            "privacy": 3,
            "order_index": order_index,
            "view_duration_ms": 10_500,
            "view_started_at": "2026-07-03T01:00:00Z",
            "view_submitted_at": "2026-07-03T01:00:11Z",
            "mask_meta": {"mode": "source_control" if condition == "control_anchor" else "temporal"},
        })
    return {
        "participant": {
            "student_id": "20260001",
            "name": "测试被试",
            "glasses": "none",
            "major": "计算机",
            "age": 22,
            "gender": "prefer_not_to_say",
            "consent_confirmed": True,
            "photosensitivity_screen_passed": True,
            "consented_at": "2026-07-03T00:59:00Z",
        },
        "session": {
            "session_uuid": session_uuid,
            "registration_index": registration_index,
            "started_at": "2026-07-03T00:58:00Z",
            "submitted_at": "2026-07-03T01:10:00Z",
            "assumed_monitor_hz": 240,
            "refresh_hz": 240,
            "refresh_ok": True,
            "refresh_samples": 200,
            "mean_frame_ms": 4.167,
            "typing_order": "ABBA" if typing_order_index == 0 else "BAAB",
            "counterbalance_index": typing_order_index,
            "rating_order_index": rating_order_index,
            "environment_confirmed": True,
            "demo": demo,
            "debug": debug,
        },
        "typing": typing,
        "ratings": ratings,
    }


def test_submit_is_idempotent_and_stores_four_typing_six_ratings(tmp_path):
    db = tmp_path / "study.db"
    client = create_app(db).test_client()
    payload = make_payload()

    first = client.post("/api/submit", json=payload)
    second = client.post("/api/submit", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.get_json()["created"] is True
    assert second.get_json()["created"] is False
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM participants").fetchone()[0] == 1
        assert conn.execute("SELECT registration_index FROM participants").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM typing").fetchone()[0] == 4
        assert conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0] == 6


def test_validation_rejects_incomplete_design_and_short_rating_view(tmp_path):
    client = create_app(tmp_path / "study.db").test_client()
    payload = make_payload()
    payload["typing"].pop()
    assert client.post("/api/submit", json=payload).status_code == 400

    payload = make_payload(session_uuid="00000000-0000-4000-8000-000000000002")
    payload["ratings"][0]["view_duration_ms"] = 9_999
    assert client.post("/api/submit", json=payload).status_code == 400

    payload = make_payload(session_uuid="00000000-0000-4000-8000-000000000005")
    payload["participant"]["photosensitivity_screen_passed"] = False
    assert client.post("/api/submit", json=payload).status_code == 400

    payload = make_payload(session_uuid="00000000-0000-4000-8000-000000000006")
    payload["session"]["refresh_hz"] = 199.9
    assert client.post("/api/submit", json=payload).status_code == 400

    payload = make_payload(session_uuid="00000000-0000-4000-8000-000000000007")
    payload["typing"][1]["n"] = 3
    assert client.post("/api/submit", json=payload).status_code == 400

    payload = make_payload(session_uuid="00000000-0000-4000-8000-000000000008")
    payload["ratings"][2]["components"] = "mask-only"
    assert client.post("/api/submit", json=payload).status_code == 400

    payload = make_payload(session_uuid="00000000-0000-4000-8000-000000000009")
    payload["session"]["rating_order_index"] = 3
    assert client.post("/api/submit", json=payload).status_code == 400

    payload = make_payload(session_uuid="00000000-0000-4000-8000-000000000010")
    payload["ratings"][0]["order_index"], payload["ratings"][1]["order_index"] = 1, 0
    assert client.post("/api/submit", json=payload).status_code == 400


def test_formal_registration_index_is_unique(tmp_path):
    client = create_app(tmp_path / "study.db").test_client()
    assert client.post("/api/submit", json=make_payload()).status_code == 200
    duplicate = make_payload(session_uuid="00000000-0000-4000-8000-000000000099")
    response = client.post("/api/submit", json=duplicate)
    assert response.status_code == 400
    assert "registration_index" in response.get_json()["error"]


def test_registration_status_rejects_invalid_and_only_counts_formal_rows(tmp_path):
    client = create_app(tmp_path / "study.db").test_client()

    assert client.get("/api/registration-status?registration_index=0").get_json() == {
        "available": True,
        "registration_index": 0,
    }
    assert client.get("/api/registration-status").status_code == 400
    assert client.get("/api/registration-status?registration_index=-1").status_code == 400
    assert client.get("/api/registration-status?registration_index=1.5").status_code == 400

    debug_payload = make_payload(
        session_uuid="00000000-0000-4000-8000-000000000090",
        registration_index=1,
        debug=True,
    )
    assert client.post("/api/submit", json=debug_payload).status_code == 200
    assert client.get("/api/registration-status?registration_index=1").get_json()["available"] is True

    demo_payload = make_payload(
        session_uuid="00000000-0000-4000-8000-000000000091",
        registration_index=2,
        demo=True,
    )
    assert client.post("/api/submit", json=demo_payload).status_code == 200
    assert client.get("/api/registration-status?registration_index=2").get_json()["available"] is True

    assert client.post("/api/submit", json=make_payload()).status_code == 200
    assert client.get("/api/registration-status?registration_index=0").get_json() == {
        "available": False,
        "registration_index": 0,
    }


def test_formal_workflows_default_to_fresh_database_name():
    from webstudy.analyze_study import DEFAULT_DB_PATH as ANALYSIS_DB_PATH
    from webstudy.backup_db import DEFAULT_DB_PATH as BACKUP_DB_PATH

    assert DEFAULT_DB_PATH.name == "study_formal.db"
    assert ANALYSIS_DB_PATH.name == "study_formal.db"
    assert BACKUP_DB_PATH.name == "study_formal.db"


def test_stats_and_exports_exclude_debug_and_demo_by_default(tmp_path):
    db = tmp_path / "study.db"
    client = create_app(db).test_client()
    assert client.post("/api/submit", json=make_payload()).status_code == 200
    assert client.post("/api/submit", json=make_payload(
        session_uuid="00000000-0000-4000-8000-000000000003", debug=True
    )).status_code == 200
    assert client.post("/api/submit", json=make_payload(
        session_uuid="00000000-0000-4000-8000-000000000004", demo=True
    )).status_code == 200

    assert client.get("/admin/stats").get_json()["participants"] == 1
    assert client.get("/admin/stats?include_debug=1").get_json()["participants"] == 3

    production_rows = list(csv.DictReader(io.StringIO(build_export_csv(db))))
    all_rows = list(csv.DictReader(io.StringIO(build_export_csv(db, include_debug=True))))
    assert len(production_rows) == 10
    assert len(all_rows) == 30
    assert {row["debug"] for row in production_rows} == {"0"}
    assert {row["demo"] for row in production_rows} == {"0"}


def test_init_db_migrates_legacy_schema_without_losing_rows(tmp_path):
    db = tmp_path / "legacy.db"
    with sqlite3.connect(db) as conn:
        conn.executescript("""
            CREATE TABLE participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL, name TEXT NOT NULL,
                glasses TEXT DEFAULT '', major TEXT DEFAULT '',
                ts TEXT DEFAULT CURRENT_TIMESTAMP, started_at TEXT DEFAULT '',
                submitted_at TEXT DEFAULT '', assumed_monitor_hz REAL,
                refresh_hz REAL, refresh_ok INTEGER NOT NULL DEFAULT 0,
                refresh_samples INTEGER, mean_frame_ms REAL,
                user_agent TEXT DEFAULT '', screen_json TEXT DEFAULT '{}',
                debug INTEGER NOT NULL DEFAULT 0
            );
            INSERT INTO participants (student_id, name) VALUES ('old', 'legacy');
        """)

    init_db(db)

    with sqlite3.connect(db) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(participants)")}
        assert {"session_uuid", "registration_index", "age", "gender", "demo", "typing_order"} <= columns
        row = conn.execute("SELECT student_id, session_uuid, registration_index FROM participants").fetchone()
        assert row[0] == "old"
        assert row[1].startswith("legacy-")
        assert row[2] == -1


def test_analysis_generates_auditable_json_csv_and_latex_outputs(tmp_path):
    from webstudy.analyze_study import analyze_study

    db = tmp_path / "study.db"
    client = create_app(db).test_client()
    for index in range(6):
        payload = make_payload(
            session_uuid=f"00000000-0000-4000-8000-{index + 10:012d}",
            registration_index=index,
        )
        payload["participant"]["student_id"] = f"2026{index:04d}"
        for row in payload["typing"]:
            row["wpm"] = 30 + index - (4 if row["condition"] == "masked" else 0)
            row["cpm"] = row["wpm"] * 5
        assert client.post("/api/submit", json=payload).status_code == 200

    output = tmp_path / "analysis"
    report = analyze_study(db, output, bootstrap_samples=200)

    assert report["sample"]["included"] == 6
    assert report["sample"]["target_n"] == 24
    assert (output / "analysis_report.json").exists()
    assert (output / "typing_participant_means.csv").exists()
    assert (output / "typing_table.tex").exists()
    assert (output / "ratings_table.tex").exists()


def test_analysis_excludes_any_session_with_under_five_attempted_chars(tmp_path):
    from webstudy.analyze_study import analyze_study

    db = tmp_path / "study.db"
    client = create_app(db).test_client()
    payload = make_payload()
    payload["typing"][2]["typed_text"] = "abcd"
    payload["typing"][2]["attempted_chars"] = 4
    assert client.post("/api/submit", json=payload).status_code == 200

    report = analyze_study(db, tmp_path / "analysis", bootstrap_samples=50)

    assert report["sample"]["included"] == 0
    assert report["exclusions"]["typing_trial_below_5_attempted_chars"] == 1


def test_backup_uses_consistent_sqlite_snapshot(tmp_path):
    from webstudy.backup_db import backup_database

    source = tmp_path / "study.db"
    init_db(source)
    destination = backup_database(source, tmp_path / "backups", timestamp="20260703T120000Z")

    assert destination.name == "study-20260703T120000Z.db"
    with sqlite3.connect(destination) as conn:
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
