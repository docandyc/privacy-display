"""Local Flask backend for the privacy-display user-study web demo."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, request, send_from_directory


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
DEFAULT_DB_PATH = ROOT / "study.db"


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    glasses TEXT DEFAULT '',
    major TEXT DEFAULT '',
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
    debug INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS typing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    condition TEXT NOT NULL,
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

    @app.get("/api/health")
    def health() -> Response:
        return jsonify({"ok": True, "db_path": str(app.config["DB_PATH"])})

    @app.post("/api/submit")
    def submit() -> Response:
        try:
            payload = request.get_json(force=True)
            participant, session, typing_rows, rating_rows = validate_payload(payload)
            participant_id = save_submission(
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
            "typing_rows": len(typing_rows),
            "rating_rows": len(rating_rows),
        })

    @app.get("/admin/export.csv")
    def export_csv() -> Response:
        token_error = check_export_token()
        if token_error:
            return jsonify({"error": token_error}), 403
        content = build_export_csv(app.config["DB_PATH"])
        return Response(
            content,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=privacy_display_study.csv"},
        )

    @app.get("/admin/stats")
    def stats() -> Response:
        token_error = check_export_token()
        if token_error:
            return jsonify({"error": token_error}), 403
        return jsonify(build_stats(app.config["DB_PATH"]))

    return app


def init_db(db_path: str | Path) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)


def get_conn(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def validate_payload(payload: Any) -> tuple[dict, dict, list[dict], list[dict]]:
    if not isinstance(payload, dict):
        raise ValidationError("payload must be a JSON object")

    participant = clean_participant(payload.get("participant"))
    session = clean_session(payload.get("session"))
    typing_rows = clean_typing_rows(payload.get("typing"))
    rating_rows = clean_rating_rows(payload.get("ratings"))
    return participant, session, typing_rows, rating_rows


def clean_participant(raw: Any) -> dict:
    if not isinstance(raw, dict):
        raise ValidationError("participant must be an object")
    student_id = clean_text(raw.get("student_id"), 80)
    name = clean_text(raw.get("name"), 80)
    if not student_id:
        raise ValidationError("student_id is required")
    if not name:
        raise ValidationError("name is required")
    return {
        "student_id": student_id,
        "name": name,
        "glasses": clean_text(raw.get("glasses"), 40),
        "major": clean_text(raw.get("major"), 120),
    }


def clean_session(raw: Any) -> dict:
    if not isinstance(raw, dict):
        raise ValidationError("session must be an object")
    return {
        "started_at": clean_text(raw.get("started_at"), 80),
        "submitted_at": clean_text(raw.get("submitted_at"), 80),
        "assumed_monitor_hz": clean_float(raw.get("assumed_monitor_hz"), default=240.0),
        "refresh_hz": clean_float(raw.get("refresh_hz"), default=0.0),
        "refresh_ok": 1 if raw.get("refresh_ok") else 0,
        "refresh_samples": clean_int(raw.get("refresh_samples"), default=0),
        "mean_frame_ms": clean_float(raw.get("mean_frame_ms"), default=0.0),
        "user_agent": clean_text(raw.get("user_agent"), 500),
        "screen_json": json.dumps(raw.get("screen") or {}, ensure_ascii=False, sort_keys=True),
        "debug": 1 if raw.get("debug") else 0,
    }


def clean_typing_rows(raw: Any) -> list[dict]:
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValidationError("typing must contain exactly two rows")
    rows = []
    seen = set()
    for idx, row in enumerate(raw):
        if not isinstance(row, dict):
            raise ValidationError(f"typing row {idx} must be an object")
        condition = clean_text(row.get("condition"), 40)
        if condition not in {"control", "masked"}:
            raise ValidationError(f"typing row {idx} has invalid condition")
        if condition in seen:
            raise ValidationError(f"typing condition {condition} appears more than once")
        seen.add(condition)
        rows.append({
            "condition": condition,
            "n": clean_int(row.get("n"), default=0),
            "requested_n": clean_int(row.get("requested_n"), default=clean_int(row.get("n"), default=0)),
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
            "mask_meta_json": json.dumps(row.get("mask_meta") or {}, ensure_ascii=False, sort_keys=True),
        })
    return rows


def clean_rating_rows(raw: Any) -> list[dict]:
    if not isinstance(raw, list) or len(raw) != 4:
        raise ValidationError("ratings must contain exactly four rows")
    rows = []
    for idx, row in enumerate(raw):
        if not isinstance(row, dict):
            raise ValidationError(f"rating row {idx} must be an object")
        rows.append({
            "condition_label": clean_text(row.get("condition_label"), 80),
            "display_label": clean_text(row.get("display_label"), 120),
            "n": clean_int(row.get("n"), default=0),
            "requested_n": clean_int(row.get("requested_n"), default=clean_int(row.get("n"), default=0)),
            "components": clean_text(row.get("components"), 60),
            "stimulus_text": clean_text(row.get("stimulus_text"), 2000),
            "readability": clean_rating(row.get("readability"), idx, "readability"),
            "flicker": clean_rating(row.get("flicker"), idx, "flicker"),
            "fatigue": clean_rating(row.get("fatigue"), idx, "fatigue"),
            "privacy": clean_rating(row.get("privacy"), idx, "privacy"),
            "order_index": clean_int(row.get("order_index"), default=idx),
            "mask_meta_json": json.dumps(row.get("mask_meta") or {}, ensure_ascii=False, sort_keys=True),
        })
    return rows


def clean_text(value: Any, max_len: int) -> str:
    return str(value or "").strip()[:max_len]


def clean_int(value: Any, default: int = 0) -> int:
    if value is None or value == "":
        return default
    return int(float(value))


def clean_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


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
) -> int:
    with get_conn(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO participants (
                student_id, name, glasses, major, started_at, submitted_at,
                assumed_monitor_hz, refresh_hz, refresh_ok, refresh_samples,
                mean_frame_ms, user_agent, screen_json, debug
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                participant["student_id"],
                participant["name"],
                participant["glasses"],
                participant["major"],
                session["started_at"],
                session["submitted_at"],
                session["assumed_monitor_hz"],
                session["refresh_hz"],
                session["refresh_ok"],
                session["refresh_samples"],
                session["mean_frame_ms"],
                session["user_agent"],
                session["screen_json"],
                session["debug"],
            ),
        )
        participant_id = int(cur.lastrowid)
        conn.executemany(
            """
            INSERT INTO typing (
                participant_id, condition, n, requested_n, components, target_text,
                typed_text, correct_chars, correct_letters, attempted_chars,
                attempted_letters, total_chars, accuracy, cpm, wpm, duration_s,
                mask_meta_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    participant_id,
                    row["condition"],
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
                order_index, mask_meta_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    row["mask_meta_json"],
                )
                for row in rating_rows
            ],
        )
        return participant_id


def check_export_token() -> str:
    expected = os.environ.get("WEBSTUDY_EXPORT_TOKEN", "")
    if not expected:
        return ""
    supplied = request.args.get("token", "")
    if supplied != expected:
        return "invalid or missing export token"
    return ""


def build_export_csv(db_path: str | Path) -> str:
    fieldnames = [
        "row_type", "participant_id", "student_id", "name", "glasses", "major",
        "ts", "started_at", "submitted_at", "assumed_monitor_hz", "refresh_hz",
        "refresh_ok", "refresh_samples", "mean_frame_ms", "debug", "condition",
        "n", "requested_n", "components", "target_text", "typed_text",
        "correct_chars", "correct_letters", "attempted_chars", "attempted_letters",
        "total_chars", "accuracy", "cpm", "wpm", "duration_s",
        "condition_label", "display_label", "stimulus_text", "readability",
        "flicker", "fatigue", "privacy", "order_index", "user_agent", "screen_json",
    ]
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    with get_conn(db_path) as conn:
        participants = conn.execute("SELECT * FROM participants ORDER BY id").fetchall()
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
                })
    return out.getvalue()


def participant_base(participant: sqlite3.Row) -> dict:
    return {
        "participant_id": participant["id"],
        "student_id": participant["student_id"],
        "name": participant["name"],
        "glasses": participant["glasses"],
        "major": participant["major"],
        "ts": participant["ts"],
        "started_at": participant["started_at"],
        "submitted_at": participant["submitted_at"],
        "assumed_monitor_hz": participant["assumed_monitor_hz"],
        "refresh_hz": participant["refresh_hz"],
        "refresh_ok": participant["refresh_ok"],
        "refresh_samples": participant["refresh_samples"],
        "mean_frame_ms": participant["mean_frame_ms"],
        "debug": participant["debug"],
        "user_agent": participant["user_agent"],
        "screen_json": participant["screen_json"],
    }


def build_stats(db_path: str | Path) -> dict:
    with get_conn(db_path) as conn:
        participant_count = conn.execute("SELECT COUNT(*) FROM participants").fetchone()[0]
        typing = [
            dict(row)
            for row in conn.execute(
                """
                SELECT condition, COUNT(*) AS n_rows, AVG(wpm) AS mean_wpm,
                       AVG(cpm) AS mean_cpm, AVG(accuracy) AS mean_accuracy
                FROM typing
                GROUP BY condition
                ORDER BY condition
                """
            )
        ]
        ratings = [
            dict(row)
            for row in conn.execute(
                """
                SELECT condition_label, n, components, COUNT(*) AS n_rows,
                       AVG(readability) AS readability,
                       AVG(flicker) AS flicker,
                       AVG(fatigue) AS fatigue,
                       AVG(privacy) AS privacy
                FROM ratings
                GROUP BY condition_label, n, components
                ORDER BY condition_label
                """
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
