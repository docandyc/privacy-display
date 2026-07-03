"""Create a transactionally consistent daily snapshot of the WebStudy database."""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).with_name("study_formal.db")


def backup_database(
    source: str | Path,
    backup_dir: str | Path,
    *,
    timestamp: str | None = None,
) -> Path:
    source_path = Path(source)
    if not source_path.is_file():
        raise FileNotFoundError(f"study database not found: {source_path}")
    destination_dir = Path(backup_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = destination_dir / f"{source_path.stem}-{stamp}{source_path.suffix or '.db'}"
    with sqlite3.connect(source_path) as source_conn, sqlite3.connect(destination) as destination_conn:
        source_conn.backup(destination_conn)
        integrity = destination_conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"backup integrity check failed: {integrity}")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Back up the privacy-display WebStudy SQLite database")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--output", default=str(Path(__file__).with_name("backups")))
    args = parser.parse_args()
    print(backup_database(args.db, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
