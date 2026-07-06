"""Local Flask backend for the privacy-display user-study web demo."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, request, send_from_directory

try:  # pragma: no cover - import style differs between package and script execution.
    from .assignment import (
        RATING_CONDITION_ORDER,
        assignment_bucket_key,
        assignment_bucket_keys,
        assignment_for_registration_index,
    )
except ImportError:  # pragma: no cover
    from assignment import (  # type: ignore
        RATING_CONDITION_ORDER,
        assignment_bucket_key,
        assignment_bucket_keys,
        assignment_for_registration_index,
    )


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
DEFAULT_DB_PATH = ROOT / "study_formal.db"
FORMAL_MIN_REFRESH_HZ = 200.0
RATING_CONDITIONS = set(RATING_CONDITION_ORDER)
RATING_SPECS = {
    "control_anchor": (1, "none"),
    "n2_mask_noise": (2, "mask+noise"),
    "n3_mask_noise": (3, "mask+noise"),
    "n4_mask_noise": (4, "mask+noise"),
    "n4_mask_only": (4, "mask-only"),
    "deployed_full": (4, "mask+noise+anti-ocr+inversion"),
}


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_uuid TEXT NOT NULL UNIQUE,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    glasses TEXT DEFAULT '',
    major TEXT DEFAULT '',
    age INTEGER,
    gender TEXT DEFAULT '',
    consent_confirmed INTEGER NOT NULL DEFAULT 0,
    photosensitivity_screen_passed INTEGER NOT NULL DEFAULT 0,
    consented_at TEXT DEFAULT '',
    ts TEXT DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT DEFAULT '',
    submitted_at TEXT DEFAULT '',
    assumed_monitor_hz REAL,
    refresh_hz REAL,
    refresh_ok INTEGER NOT NULL DEFAULT 0,
    refresh_samples INTEGER,
    mean_frame_ms REAL,
    user_agent TEXT DEFAULT '',
    screen_json TEXT DEFAULT '{}',
    registration_index INTEGER NOT NULL DEFAULT -1,
    typing_order TEXT DEFAULT '',
    counterbalance_index INTEGER NOT NULL DEFAULT 0,
    rating_order_index INTEGER NOT NULL DEFAULT 0,
    environment_confirmed INTEGER NOT NULL DEFAULT 0,
    demo INTEGER NOT NULL DEFAULT 0,
    debug INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS typing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    condition TEXT NOT NULL,
    trial_index INTEGER NOT NULL DEFAULT 0,
    condition_repetition INTEGER NOT NULL DEFAULT 1,
    n INTEGER NOT NULL DEFAULT 0,
    requested_n INTEGER NOT NULL DEFAULT 0,
    components TEXT NOT NULL,
    target_text TEXT NOT NULL,
    typed_text TEXT NOT NULL,
    correct_chars INTEGER NOT NULL,
    correct_letters INTEGER NOT NULL DEFAULT 0,
    attempted_chars INTEGER NOT NULL DEFAULT 0,
    attempted_letters INTEGER NOT NULL DEFAULT 0,
    total_chars INTEGER NOT NULL,
    accuracy REAL NOT NULL,
    cpm REAL NOT NULL,
    wpm REAL NOT NULL,
    duration_s REAL NOT NULL,
    edit_distance INTEGER NOT NULL DEFAULT 0,
    aligned_target_chars INTEGER NOT NULL DEFAULT 0,
    msd_error_rate REAL NOT NULL DEFAULT 0,
    scoring_method TEXT NOT NULL DEFAULT '',
    first_key_latency_ms REAL,
    mask_meta_json TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    condition_label TEXT NOT NULL,
    display_label TEXT DEFAULT '',
    n INTEGER NOT NULL,
    requested_n INTEGER NOT NULL,
    components TEXT NOT NULL,
    stimulus_text TEXT NOT NULL DEFAULT '',
    readability INTEGER NOT NULL,
    flicker INTEGER NOT NULL,
    fatigue INTEGER NOT NULL,
    privacy INTEGER NOT NULL,
    order_index INTEGER NOT NULL,
    view_duration_ms INTEGER NOT NULL DEFAULT 0,
    view_started_at TEXT DEFAULT '',
    view_submitted_at TEXT DEFAULT '',
    mask_meta_json TEXT DEFAULT '{}'
);

"""


class ValidationError(ValueError):
    """Raised when an incoming study payload is malformed."""


def create_app(db_path: str | Path | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")
    app.config["DB_PATH"] = Path(db_path or os.environ.get("WEBSTUDY_DB", DEFAULT_DB_PATH))
    init_db(app.config["DB_PATH"])

    @app.get("/")
    def index() -> Response:
        return send_from_directory(STATIC_DIR, "index.html")

    @app.get("/admin")
    def admin() -> Response:
        return send_from_directory(STATIC_DIR, "admin.html")

    @app.get("/api/health")
    def health() -> Response:
        return jsonify({"ok": True, "db_path": str(app.config["DB_PATH"])})

    @app.get("/api/registration-status")
    def registration_status() -> Response:
        raw_index = request.args.get("registration_index", "")
        try:
            registration_index = int(raw_index)
        except (TypeError, ValueError):
            return jsonify({"error": "registration_index must be a non-negative integer"}), 400
        if registration_index < 0 or str(registration_index) != raw_index.strip():
            return jsonify({"error": "registration_index must be a non-negative integer"}), 400
        with get_conn(app.config["DB_PATH"]) as conn:
            occupied = formal_registration_occupied(conn, registration_index)
        return jsonify({
            "registration_index": registration_index,
            "available": not occupied,
        })

    @app.post("/api/next-assignment")
    def next_assignment() -> Response:
        with get_conn(app.config["DB_PATH"]) as conn:
            assignment = next_formal_assignment(conn)
            counts = formal_assignment_bucket_counts(conn)
        return jsonify({
            "assignment": assignment,
            "typing_order": "ABBA" if assignment["typing_order_index"] == 0 else "BAAB",
            "bucket_counts": counts,
        })

    @app.post("/api/submit")
    def submit() -> Response:
        try:
            payload = request.get_json(force=True)
            participant, session, typing_rows, rating_rows = validate_payload(payload)
            participant_id, created = save_submission(
                app.config["DB_PATH"],
                participant,
                session,
                typing_rows,
                rating_rows,
            )
        except ValidationError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:  # pragma: no cover - returned for lab operator diagnosis.
            return jsonify({"error": f"submit failed: {exc}"}), 500
        return jsonify({
            "ok": True,
            "participant_id": participant_id,
            "created": created,
            "typing_rows": len(typing_rows),
            "rating_rows": len(rating_rows),
        })

    @app.get("/admin/export.csv")
    def export_csv() -> Response:
        token_error = check_export_token()
        if token_error:
            return jsonify({"error": token_error}), 403
        content = build_export_csv(app.config["DB_PATH"], include_debug=requested_debug_rows())
        return Response(
            content,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=privacy_display_study.csv"},
        )

    @app.get("/admin/data.json")
    def admin_data() -> Response:
        token_error = check_export_token()
        if token_error:
            return jsonify({"error": token_error}), 403
        return jsonify(build_admin_data(app.config["DB_PATH"], include_debug=requested_debug_rows()))

    @app.get("/admin/stats")
    def stats() -> Response:
        token_error = check_export_token()
        if token_error:
            return jsonify({"error": token_error}), 403
        return jsonify(build_stats(app.config["DB_PATH"], include_debug=requested_debug_rows()))

    return app


def init_db(db_path: str | Path) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)
        ensure_columns(conn, "participants", {
            "session_uuid": "TEXT DEFAULT ''",
            "age": "INTEGER",
            "gender": "TEXT DEFAULT ''",
            "consent_confirmed": "INTEGER NOT NULL DEFAULT 0",
            "photosensitivity_screen_passed": "INTEGER NOT NULL DEFAULT 0",
            "consented_at": "TEXT DEFAULT ''",
            "registration_index": "INTEGER NOT NULL DEFAULT -1",
            "typing_order": "TEXT DEFAULT ''",
            "counterbalance_index": "INTEGER NOT NULL DEFAULT 0",
            "rating_order_index": "INTEGER NOT NULL DEFAULT 0",
            "environment_confirmed": "INTEGER NOT NULL DEFAULT 0",
            "demo": "INTEGER NOT NULL DEFAULT 0",
        })
        ensure_columns(conn, "typing", {
            "trial_index": "INTEGER NOT NULL DEFAULT 0",
            "condition_repetition": "INTEGER NOT NULL DEFAULT 1",
            "edit_distance": "INTEGER NOT NULL DEFAULT 0",
            "aligned_target_chars": "INTEGER NOT NULL DEFAULT 0",
            "msd_error_rate": "REAL NOT NULL DEFAULT 0",
            "scoring_method": "TEXT NOT NULL DEFAULT ''",
            "first_key_latency_ms": "REAL",
        })
        ensure_columns(conn, "ratings", {
            "view_duration_ms": "INTEGER NOT NULL DEFAULT 0",
            "view_started_at": "TEXT DEFAULT ''",
            "view_submitted_at": "TEXT DEFAULT ''",
        })
        conn.execute(
            "UPDATE participants SET session_uuid = 'legacy-' || id "
            "WHERE session_uuid IS NULL OR session_uuid = ''"
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_participants_session_uuid "
            "ON participants(session_uuid)"
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_participants_formal_registration "
            "ON participants(registration_index) "
            "WHERE debug = 0 AND demo = 0 AND registration_index >= 0"
        )


def ensure_columns(conn: sqlite3.Connection, table: str, definitions: dict[str, str]) -> None:
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    for name, definition in definitions.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def get_conn(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def formal_registration_occupied(conn: sqlite3.Connection, registration_index: int) -> bool:
    row = conn.execute(
        "SELECT 1 FROM participants "
        "WHERE registration_index = ? AND debug = 0 AND demo = 0 LIMIT 1",
        (registration_index,),
    ).fetchone()
    return row is not None


def formal_assignment_bucket_counts(conn: sqlite3.Connection) -> dict[str, int]:
    counts = {key: 0 for key in assignment_bucket_keys()}
    rows = conn.execute(
        "SELECT registration_index FROM participants "
        "WHERE debug = 0 AND demo = 0 AND registration_index >= 0"
    ).fetchall()
    for row in rows:
        assignment = assignment_for_registration_index(int(row["registration_index"]))
        counts[assignment_bucket_key(assignment)] += 1
    return counts


def next_formal_assignment(conn: sqlite3.Connection) -> dict[str, int]:
    counts = formal_assignment_bucket_counts(conn)
    occupied = {
        int(row["registration_index"])
        for row in conn.execute(
            "SELECT registration_index FROM participants "
            "WHERE debug = 0 AND demo = 0 AND registration_index >= 0"
        )
    }
    best_bucket = min(counts, key=lambda key: (counts[key], int(key.split(":")[1]), int(key.split(":")[0])))
    registration_index = 0
    while True:
        assignment = assignment_for_registration_index(registration_index)
        if registration_index not in occupied and assignment_bucket_key(assignment) == best_bucket:
            return assignment
        registration_index += 1


def validate_payload(payload: Any) -> tuple[dict, dict, list[dict], list[dict]]:
    if not isinstance(payload, dict):
        raise ValidationError("payload must be a JSON object")

    participant = clean_participant(payload.get("participant"))
    session = clean_session(payload.get("session"))
    is_nonformal = bool(session["debug"] or session["demo"])
    if not is_nonformal:
        if not session["refresh_ok"] or session["refresh_hz"] < FORMAL_MIN_REFRESH_HZ:
            raise ValidationError("formal study sessions require measured refresh >= 200 Hz")
        if not session["environment_confirmed"]:
            raise ValidationError("formal study sessions require environment confirmation")
    typing_rows = clean_typing_rows(payload.get("typing"), allow_adaptive_n=is_nonformal)
    rating_rows = clean_rating_rows(
        payload.get("ratings"),
        minimum_view_ms=1_000 if session["debug"] else 10_000,
    )
    expected_typing = (
        ["control", "masked", "masked", "control"]
        if session["counterbalance_index"] == 0
        else ["masked", "control", "control", "masked"]
    )
    actual_typing = [
        row["condition"] for row in sorted(typing_rows, key=lambda row: row["trial_index"])
    ]
    if actual_typing != expected_typing:
        raise ValidationError("typing rows do not match assigned order")
    if session["rating_order_index"] >= 0:
        expected_ratings = balanced_latin_order(RATING_CONDITION_ORDER, session["rating_order_index"])
        actual_ratings = [
            row["condition_label"] for row in sorted(rating_rows, key=lambda row: row["order_index"])
        ]
        if actual_ratings != expected_ratings:
            raise ValidationError("rating rows do not match assigned Latin order")
    return participant, session, typing_rows, rating_rows


def balanced_latin_order(items: tuple[str, ...], row_index: int) -> list[str]:
    first_row = [0]
    offset = 1
    while len(first_row) < len(items):
        first_row.append(offset)
        if len(first_row) < len(items):
            first_row.append(len(items) - offset)
        offset += 1
    shift = row_index % len(items)
    return [items[(index + shift) % len(items)] for index in first_row]


def clean_participant(raw: Any) -> dict:
    if not isinstance(raw, dict):
        raise ValidationError("participant must be an object")
    if raw.get("consent_confirmed") is not True:
        raise ValidationError("consent_confirmed must be true")
    if raw.get("photosensitivity_screen_passed") is not True:
        raise ValidationError("photosensitivity_screen_passed must be true")
    glasses = clean_text(raw.get("glasses"), 40)
    if not glasses:
        raise ValidationError("glasses is required")
    return {
        "student_id": "",
        "name": "",
        "glasses": glasses,
        "major": "",
        "age": None,
        "gender": "",
        "consent_confirmed": 1,
        "photosensitivity_screen_passed": 1,
        "consented_at": clean_text(raw.get("consented_at"), 80),
    }


def clean_session(raw: Any) -> dict:
    if not isinstance(raw, dict):
        raise ValidationError("session must be an object")
    session_uuid = clean_text(raw.get("session_uuid"), 80)
    try:
        session_uuid = str(uuid.UUID(session_uuid))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValidationError("session_uuid must be a valid UUID") from exc
    typing_order = clean_text(raw.get("typing_order"), 8)
    if typing_order not in {"ABBA", "BAAB"}:
        raise ValidationError("typing_order must be ABBA or BAAB")
    demo = 1 if raw.get("demo") else 0
    debug = 1 if raw.get("debug") else 0
    registration_index = clean_int(raw.get("registration_index"), default=-1)
    counterbalance_index = clean_int(raw.get("counterbalance_index"), default=-1)
    rating_order_index = clean_int(raw.get("rating_order_index"), default=-1)
    if not (demo or debug):
        if registration_index < 0:
            raise ValidationError("registration_index is required for formal sessions")
        expected = assignment_for_registration_index(registration_index)
        expected_typing_index = expected["typing_order_index"]
        expected_rating_index = expected["rating_order_index"]
        expected_typing_order = "ABBA" if expected_typing_index == 0 else "BAAB"
        if counterbalance_index != expected_typing_index:
            raise ValidationError("counterbalance_index does not match registration_index")
        if rating_order_index != expected_rating_index:
            raise ValidationError("rating_order_index does not match registration_index")
        if typing_order != expected_typing_order:
            raise ValidationError("typing_order does not match registration_index")
    return {
        "session_uuid": session_uuid,
        "registration_index": registration_index,
        "started_at": clean_text(raw.get("started_at"), 80),
        "submitted_at": clean_text(raw.get("submitted_at"), 80),
        "assumed_monitor_hz": clean_float(raw.get("assumed_monitor_hz"), default=240.0),
        "refresh_hz": clean_float(raw.get("refresh_hz"), default=0.0),
        "refresh_ok": 1 if raw.get("refresh_ok") else 0,
        "refresh_samples": clean_int(raw.get("refresh_samples"), default=0),
        "mean_frame_ms": clean_float(raw.get("mean_frame_ms"), default=0.0),
        "user_agent": clean_text(raw.get("user_agent"), 500),
        "screen_json": json.dumps(raw.get("screen") or {}, ensure_ascii=False, sort_keys=True),
        "typing_order": typing_order,
        "counterbalance_index": counterbalance_index,
        "rating_order_index": rating_order_index,
        "environment_confirmed": 1 if raw.get("environment_confirmed") else 0,
        "demo": demo,
        "debug": debug,
    }


def clean_typing_rows(raw: Any, *, allow_adaptive_n: bool = False) -> list[dict]:
    if not isinstance(raw, list) or len(raw) != 4:
        raise ValidationError("typing must contain exactly four scored rows")
    rows = []
    trial_indexes = set()
    condition_counts = {"control": 0, "masked": 0}
    repetitions = {"control": set(), "masked": set()}
    for idx, row in enumerate(raw):
        if not isinstance(row, dict):
            raise ValidationError(f"typing row {idx} must be an object")
        condition = clean_text(row.get("condition"), 40)
        if condition not in {"control", "masked"}:
            raise ValidationError(f"typing row {idx} has invalid condition")
        trial_index = clean_int(row.get("trial_index"), default=-1)
        if trial_index not in {0, 1, 2, 3} or trial_index in trial_indexes:
            raise ValidationError(f"typing row {idx} has invalid or duplicate trial_index")
        trial_indexes.add(trial_index)
        repetition = clean_int(row.get("condition_repetition"), default=0)
        if repetition not in {1, 2} or repetition in repetitions[condition]:
            raise ValidationError(f"typing row {idx} has invalid condition_repetition")
        repetitions[condition].add(repetition)
        condition_counts[condition] += 1
        n = clean_int(row.get("n"), default=0)
        requested_n = clean_int(row.get("requested_n"), default=n)
        if condition == "control" and (n != 1 or requested_n != 1):
            raise ValidationError("control typing rows must use n=1 source canvas")
        if condition == "masked" and not allow_adaptive_n and (n != 4 or requested_n != 4):
            raise ValidationError("formal masked typing rows must use n=4")
        rows.append({
            "condition": condition,
            "trial_index": trial_index,
            "condition_repetition": repetition,
            "n": n,
            "requested_n": requested_n,
            "components": clean_text(row.get("components"), 60),
            "target_text": clean_text(row.get("target_text"), 2000),
            "typed_text": clean_text(row.get("typed_text"), 2000),
            "correct_chars": clean_int(row.get("correct_chars"), default=0),
            "correct_letters": clean_int(row.get("correct_letters"), default=0),
            "attempted_chars": clean_int(row.get("attempted_chars"), default=0),
            "attempted_letters": clean_int(row.get("attempted_letters"), default=0),
            "total_chars": clean_int(row.get("total_chars"), default=0),
            "accuracy": clean_unit_float(row.get("accuracy"), "accuracy"),
            "cpm": clean_float(row.get("cpm"), default=0.0),
            "wpm": clean_float(row.get("wpm"), default=0.0),
            "duration_s": clean_float(row.get("duration_s"), default=20.0),
            "edit_distance": clean_nonnegative_int(row.get("edit_distance"), "edit_distance"),
            "aligned_target_chars": clean_nonnegative_int(row.get("aligned_target_chars"), "aligned_target_chars"),
            "msd_error_rate": clean_unit_float(row.get("msd_error_rate"), "msd_error_rate"),
            "scoring_method": clean_text(row.get("scoring_method"), 80),
            "first_key_latency_ms": clean_optional_float(row.get("first_key_latency_ms")),
            "mask_meta_json": json.dumps(row.get("mask_meta") or {}, ensure_ascii=False, sort_keys=True),
        })
    if condition_counts != {"control": 2, "masked": 2}:
        raise ValidationError("typing must contain two control and two masked rows")
    return rows


def clean_rating_rows(raw: Any, *, minimum_view_ms: int = 10_000) -> list[dict]:
    if not isinstance(raw, list) or len(raw) != 6:
        raise ValidationError("ratings must contain exactly six rows")
    rows = []
    seen_conditions = set()
    seen_order = set()
    for idx, row in enumerate(raw):
        if not isinstance(row, dict):
            raise ValidationError(f"rating row {idx} must be an object")
        condition_label = clean_text(row.get("condition_label"), 80)
        order_index = clean_int(row.get("order_index"), default=-1)
        if condition_label not in RATING_CONDITIONS or condition_label in seen_conditions:
            raise ValidationError(f"rating row {idx} has invalid or duplicate condition_label")
        if order_index not in range(6) or order_index in seen_order:
            raise ValidationError(f"rating row {idx} has invalid or duplicate order_index")
        view_duration_ms = clean_nonnegative_int(row.get("view_duration_ms"), "view_duration_ms")
        if view_duration_ms < minimum_view_ms:
            raise ValidationError(f"rating row {idx} view_duration_ms is below minimum")
        seen_conditions.add(condition_label)
        seen_order.add(order_index)
        n = clean_int(row.get("n"), default=0)
        requested_n = clean_int(row.get("requested_n"), default=n)
        components = clean_text(row.get("components"), 60)
        expected_n, expected_components = RATING_SPECS[condition_label]
        if n != expected_n or requested_n != expected_n or components != expected_components:
            raise ValidationError(f"rating row {idx} does not match condition specification")
        rows.append({
            "condition_label": condition_label,
            "display_label": clean_text(row.get("display_label"), 120),
            "n": n,
            "requested_n": requested_n,
            "components": components,
            "stimulus_text": clean_text(row.get("stimulus_text"), 2000),
            "readability": clean_rating(row.get("readability"), idx, "readability"),
            "flicker": clean_rating(row.get("flicker"), idx, "flicker"),
            "fatigue": clean_rating(row.get("fatigue"), idx, "fatigue"),
            "privacy": clean_rating(row.get("privacy"), idx, "privacy"),
            "order_index": order_index,
            "view_duration_ms": view_duration_ms,
            "view_started_at": clean_text(row.get("view_started_at"), 80),
            "view_submitted_at": clean_text(row.get("view_submitted_at"), 80),
            "mask_meta_json": json.dumps(row.get("mask_meta") or {}, ensure_ascii=False, sort_keys=True),
        })
    return rows


def clean_text(value: Any, max_len: int) -> str:
    return str(value or "").strip()[:max_len]


def clean_int(value: Any, default: int = 0) -> int:
    if value is None or value == "":
        return default
    return int(float(value))


def clean_optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return clean_int(value)


def clean_nonnegative_int(value: Any, name: str) -> int:
    out = clean_int(value)
    if out < 0:
        raise ValidationError(f"{name} must be non-negative")
    return out


def clean_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def clean_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    out = clean_float(value)
    if out < 0:
        raise ValidationError("optional timing values must be non-negative")
    return out


def clean_unit_float(value: Any, name: str) -> float:
    out = clean_float(value, default=0.0)
    if out < 0 or out > 1:
        raise ValidationError(f"{name} must be in [0, 1]")
    return out


def clean_rating(value: Any, row_idx: int, field: str) -> int:
    rating = clean_int(value)
    if rating < 1 or rating > 5:
        raise ValidationError(f"rating row {row_idx} {field} must be in [1, 5]")
    return rating


def save_submission(
    db_path: str | Path,
    participant: dict,
    session: dict,
    typing_rows: list[dict],
    rating_rows: list[dict],
) -> tuple[int, bool]:
    with get_conn(db_path) as conn:
        existing = conn.execute(
            "SELECT id FROM participants WHERE session_uuid = ?",
            (session["session_uuid"],),
        ).fetchone()
        if existing:
            return int(existing["id"]), False
        if not (session["debug"] or session["demo"]) and session["registration_index"] >= 0:
            if formal_registration_occupied(conn, session["registration_index"]):
                raise ValidationError("registration_index is already used by a formal session")
        try:
            cur = conn.execute(
                """
                INSERT INTO participants (
                    session_uuid, student_id, name, glasses, major, age, gender,
                    consent_confirmed, photosensitivity_screen_passed, consented_at,
                    started_at, submitted_at,
                    assumed_monitor_hz, refresh_hz, refresh_ok, refresh_samples,
                    mean_frame_ms, user_agent, screen_json, registration_index, typing_order,
                    counterbalance_index, rating_order_index, environment_confirmed,
                    demo, debug
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_uuid) DO NOTHING
                """,
                (
                    session["session_uuid"],
                    participant["student_id"],
                    participant["name"],
                    participant["glasses"],
                    participant["major"],
                    participant["age"],
                    participant["gender"],
                    participant["consent_confirmed"],
                    participant["photosensitivity_screen_passed"],
                    participant["consented_at"],
                    session["started_at"],
                    session["submitted_at"],
                    session["assumed_monitor_hz"],
                    session["refresh_hz"],
                    session["refresh_ok"],
                    session["refresh_samples"],
                    session["mean_frame_ms"],
                    session["user_agent"],
                    session["screen_json"],
                    session["registration_index"],
                    session["typing_order"],
                    session["counterbalance_index"],
                    session["rating_order_index"],
                    session["environment_confirmed"],
                    session["demo"],
                    session["debug"],
                ),
            )
        except sqlite3.IntegrityError as exc:
            if "registration_index" in str(exc):
                raise ValidationError("registration_index is already used by a formal session") from exc
            raise
        if cur.rowcount == 0:
            existing = conn.execute(
                "SELECT id FROM participants WHERE session_uuid = ?",
                (session["session_uuid"],),
            ).fetchone()
            if not existing:  # pragma: no cover - guards unexpected SQLite conflict behavior.
                raise RuntimeError("idempotent submission conflict could not be resolved")
            return int(existing["id"]), False
        participant_id = int(cur.lastrowid)
        conn.executemany(
            """
            INSERT INTO typing (
                participant_id, condition, trial_index, condition_repetition,
                n, requested_n, components, target_text,
                typed_text, correct_chars, correct_letters, attempted_chars,
                attempted_letters, total_chars, accuracy, cpm, wpm, duration_s,
                edit_distance, aligned_target_chars, msd_error_rate, scoring_method,
                first_key_latency_ms, mask_meta_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    participant_id,
                    row["condition"],
                    row["trial_index"],
                    row["condition_repetition"],
                    row["n"],
                    row["requested_n"],
                    row["components"],
                    row["target_text"],
                    row["typed_text"],
                    row["correct_chars"],
                    row["correct_letters"],
                    row["attempted_chars"],
                    row["attempted_letters"],
                    row["total_chars"],
                    row["accuracy"],
                    row["cpm"],
                    row["wpm"],
                    row["duration_s"],
                    row["edit_distance"],
                    row["aligned_target_chars"],
                    row["msd_error_rate"],
                    row["scoring_method"],
                    row["first_key_latency_ms"],
                    row["mask_meta_json"],
                )
                for row in typing_rows
            ],
        )
        conn.executemany(
            """
            INSERT INTO ratings (
                participant_id, condition_label, display_label, n, requested_n,
                components, stimulus_text, readability, flicker, fatigue, privacy,
                order_index, view_duration_ms, view_started_at, view_submitted_at,
                mask_meta_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    participant_id,
                    row["condition_label"],
                    row["display_label"],
                    row["n"],
                    row["requested_n"],
                    row["components"],
                    row["stimulus_text"],
                    row["readability"],
                    row["flicker"],
                    row["fatigue"],
                    row["privacy"],
                    row["order_index"],
                    row["view_duration_ms"],
                    row["view_started_at"],
                    row["view_submitted_at"],
                    row["mask_meta_json"],
                )
                for row in rating_rows
            ],
        )
        return participant_id, True


def check_export_token() -> str:
    expected = os.environ.get("WEBSTUDY_EXPORT_TOKEN", "")
    if not expected:
        return ""
    supplied = request.args.get("token", "")
    if supplied != expected:
        return "invalid or missing export token"
    return ""


def requested_debug_rows() -> bool:
    return request.args.get("include_debug", "") == "1"


def build_export_csv(db_path: str | Path, *, include_debug: bool = False) -> str:
    fieldnames = [
        "row_type", "participant_id", "session_uuid", "student_id", "name",
        "glasses", "major", "age", "gender", "consent_confirmed",
        "photosensitivity_screen_passed", "consented_at",
        "ts", "started_at", "submitted_at", "assumed_monitor_hz", "refresh_hz",
        "refresh_ok", "refresh_samples", "mean_frame_ms", "typing_order",
        "registration_index", "counterbalance_index", "rating_order_index", "environment_confirmed",
        "demo", "debug", "condition", "trial_index", "condition_repetition",
        "n", "requested_n", "components", "target_text", "typed_text",
        "correct_chars", "correct_letters", "attempted_chars", "attempted_letters",
        "total_chars", "accuracy", "cpm", "wpm", "duration_s", "edit_distance",
        "aligned_target_chars", "msd_error_rate", "scoring_method", "first_key_latency_ms",
        "condition_label", "display_label", "stimulus_text", "readability",
        "flicker", "fatigue", "privacy", "order_index", "view_duration_ms",
        "view_started_at", "view_submitted_at", "user_agent", "screen_json",
        "mask_meta_json",
    ]
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    with get_conn(db_path) as conn:
        participant_where = "" if include_debug else "WHERE debug = 0 AND demo = 0"
        participants = conn.execute(
            f"SELECT * FROM participants {participant_where} ORDER BY id"
        ).fetchall()
        for participant in participants:
            base = participant_base(participant)
            for row in conn.execute(
                "SELECT * FROM typing WHERE participant_id = ? ORDER BY id",
                (participant["id"],),
            ):
                writer.writerow({
                    **base,
                    "row_type": "typing",
                    "condition": row["condition"],
                    "trial_index": row["trial_index"],
                    "condition_repetition": row["condition_repetition"],
                    "n": row["n"],
                    "requested_n": row["requested_n"],
                    "components": row["components"],
                    "target_text": row["target_text"],
                    "typed_text": row["typed_text"],
                    "correct_chars": row["correct_chars"],
                    "correct_letters": row["correct_letters"],
                    "attempted_chars": row["attempted_chars"],
                    "attempted_letters": row["attempted_letters"],
                    "total_chars": row["total_chars"],
                    "accuracy": row["accuracy"],
                    "cpm": row["cpm"],
                    "wpm": row["wpm"],
                    "duration_s": row["duration_s"],
                    "edit_distance": row["edit_distance"],
                    "aligned_target_chars": row["aligned_target_chars"],
                    "msd_error_rate": row["msd_error_rate"],
                    "scoring_method": row["scoring_method"],
                    "first_key_latency_ms": row["first_key_latency_ms"],
                    "mask_meta_json": row["mask_meta_json"],
                })
            for row in conn.execute(
                "SELECT * FROM ratings WHERE participant_id = ? ORDER BY order_index, id",
                (participant["id"],),
            ):
                writer.writerow({
                    **base,
                    "row_type": "rating",
                    "condition_label": row["condition_label"],
                    "display_label": row["display_label"],
                    "n": row["n"],
                    "requested_n": row["requested_n"],
                    "components": row["components"],
                    "stimulus_text": row["stimulus_text"],
                    "readability": row["readability"],
                    "flicker": row["flicker"],
                    "fatigue": row["fatigue"],
                    "privacy": row["privacy"],
                    "order_index": row["order_index"],
                    "view_duration_ms": row["view_duration_ms"],
                    "view_started_at": row["view_started_at"],
                    "view_submitted_at": row["view_submitted_at"],
                    "mask_meta_json": row["mask_meta_json"],
                })
    return out.getvalue()


def participant_base(participant: sqlite3.Row) -> dict:
    return {
        "participant_id": participant["id"],
        "session_uuid": participant["session_uuid"],
        "student_id": participant["student_id"],
        "name": participant["name"],
        "glasses": participant["glasses"],
        "major": participant["major"],
        "age": participant["age"],
        "gender": participant["gender"],
        "consent_confirmed": participant["consent_confirmed"],
        "photosensitivity_screen_passed": participant["photosensitivity_screen_passed"],
        "consented_at": participant["consented_at"],
        "ts": participant["ts"],
        "started_at": participant["started_at"],
        "submitted_at": participant["submitted_at"],
        "assumed_monitor_hz": participant["assumed_monitor_hz"],
        "refresh_hz": participant["refresh_hz"],
        "refresh_ok": participant["refresh_ok"],
        "refresh_samples": participant["refresh_samples"],
        "mean_frame_ms": participant["mean_frame_ms"],
        "registration_index": participant["registration_index"],
        "typing_order": participant["typing_order"],
        "counterbalance_index": participant["counterbalance_index"],
        "rating_order_index": participant["rating_order_index"],
        "environment_confirmed": participant["environment_confirmed"],
        "demo": participant["demo"],
        "debug": participant["debug"],
        "user_agent": participant["user_agent"],
        "screen_json": participant["screen_json"],
    }


def build_admin_data(db_path: str | Path, *, include_debug: bool = False) -> dict:
    """Return all study rows in a shape that the operator dashboard can render."""
    with get_conn(db_path) as conn:
        participant_where = "" if include_debug else "WHERE debug = 0 AND demo = 0"
        event_where = "" if include_debug else "WHERE p.debug = 0 AND p.demo = 0"
        participant_rows = conn.execute(
            f"SELECT * FROM participants {participant_where} ORDER BY id DESC"
        ).fetchall()
        typing_rows = [
            enrich_event_row(row, "typing")
            for row in conn.execute(
                """
                SELECT t.*, p.student_id, p.name, p.refresh_hz, p.refresh_ok
                FROM typing t
                JOIN participants p ON p.id = t.participant_id
                {event_where}
                ORDER BY t.participant_id DESC, t.id
                """.format(event_where=event_where)
            )
        ]
        rating_rows = [
            enrich_event_row(row, "rating")
            for row in conn.execute(
                """
                SELECT r.*, p.student_id, p.name, p.refresh_hz, p.refresh_ok
                FROM ratings r
                JOIN participants p ON p.id = r.participant_id
                {event_where}
                ORDER BY r.participant_id DESC, r.order_index, r.id
                """.format(event_where=event_where)
            )
        ]

    typing_by_participant: dict[int, list[dict]] = {}
    for row in typing_rows:
        typing_by_participant.setdefault(row["participant_id"], []).append(row)

    ratings_by_participant: dict[int, list[dict]] = {}
    for row in rating_rows:
        ratings_by_participant.setdefault(row["participant_id"], []).append(row)

    participants = []
    paired_deltas = []
    for participant in participant_rows:
        pid = int(participant["id"])
        p_typing = typing_by_participant.get(pid, [])
        p_ratings = ratings_by_participant.get(pid, [])
        control_wpm = mean([row["wpm"] for row in p_typing if row["condition"] == "control"])
        masked_wpm = mean([row["wpm"] for row in p_typing if row["condition"] == "masked"])
        delta_wpm = None
        delta_pct = None
        if control_wpm is not None and masked_wpm is not None:
            delta_wpm = masked_wpm - control_wpm
            if control_wpm:
                delta_pct = delta_wpm / control_wpm
            paired_deltas.append({
                "participant_id": pid,
                "control_wpm": control_wpm,
                "masked_wpm": masked_wpm,
                "delta_wpm": delta_wpm,
                "delta_pct": delta_pct,
            })

        participants.append({
            **participant_base(participant),
            "typing_rows": len(p_typing),
            "rating_rows": len(p_ratings),
            "control_wpm": control_wpm,
            "masked_wpm": masked_wpm,
            "delta_wpm": delta_wpm,
            "delta_pct": delta_pct,
            "mean_readability": mean([row["readability"] for row in p_ratings]),
            "mean_flicker": mean([row["flicker"] for row in p_ratings]),
            "mean_fatigue": mean([row["fatigue"] for row in p_ratings]),
            "mean_privacy": mean([row["privacy"] for row in p_ratings]),
        })

    stats = build_stats(db_path, include_debug=include_debug)
    stats["paired_typing"] = summarize_paired_typing(paired_deltas)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": stats,
        "participants": participants,
        "typing": typing_rows,
        "ratings": rating_rows,
    }


def enrich_event_row(row: sqlite3.Row, row_type: str) -> dict:
    data = dict(row)
    data["row_type"] = row_type
    data["mask_meta"] = parse_json_object(data.pop("mask_meta_json", "{}"))
    return data


def parse_json_object(raw: Any) -> dict:
    try:
        parsed = json.loads(raw or "{}")
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def mean(values: list[float | int | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None
    return sum(clean) / len(clean)


def summarize_paired_typing(rows: list[dict]) -> dict:
    return {
        "n_pairs": len(rows),
        "control_wpm": mean([row["control_wpm"] for row in rows]),
        "masked_wpm": mean([row["masked_wpm"] for row in rows]),
        "delta_wpm": mean([row["delta_wpm"] for row in rows]),
        "delta_pct": mean([row["delta_pct"] for row in rows]),
    }


def build_stats(db_path: str | Path, *, include_debug: bool = False) -> dict:
    with get_conn(db_path) as conn:
        participant_where = "" if include_debug else "WHERE debug = 0 AND demo = 0"
        event_where = "" if include_debug else "WHERE p.debug = 0 AND p.demo = 0"
        participant_count = conn.execute(
            f"SELECT COUNT(*) FROM participants {participant_where}"
        ).fetchone()[0]
        typing = [
            dict(row)
            for row in conn.execute(
                """
                SELECT condition, COUNT(*) AS n_rows, AVG(wpm) AS mean_wpm,
                       AVG(cpm) AS mean_cpm, AVG(accuracy) AS mean_accuracy
                FROM typing t
                JOIN participants p ON p.id = t.participant_id
                {event_where}
                GROUP BY condition
                ORDER BY condition
                """.format(event_where=event_where)
            )
        ]
        ratings = [
            dict(row)
            for row in conn.execute(
                """
                SELECT condition_label, r.n, r.components, COUNT(*) AS n_rows,
                       AVG(readability) AS readability,
                       AVG(flicker) AS flicker,
                       AVG(fatigue) AS fatigue,
                       AVG(privacy) AS privacy
                FROM ratings r
                JOIN participants p ON p.id = r.participant_id
                {event_where}
                GROUP BY condition_label, r.n, r.components
                ORDER BY condition_label
                """.format(event_where=event_where)
            )
        ]
    return {
        "participants": participant_count,
        "typing": typing,
        "ratings": ratings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Privacy display user-study web demo")
    parser.add_argument("--host", default=os.environ.get("WEBSTUDY_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("WEBSTUDY_PORT", "5000")))
    parser.add_argument("--db", default=os.environ.get("WEBSTUDY_DB", str(DEFAULT_DB_PATH)))
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = create_app(args.db)
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
