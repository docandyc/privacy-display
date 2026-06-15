"""Tests for the TrackEval/HOTA integration.

TrackEval itself is a heavyweight optional dependency that only runs on the
server, so here we cover the parts that must be correct regardless: the
MOTChallenge export layout/content, the summary parser, and graceful degradation
when TrackEval is not installed.
"""

import configparser

from src.evaluation.mot import (
    MOTObject,
    _parse_trackeval_summary,
    prepare_trackeval_workspace,
    run_trackeval_hota,
)


def _box():
    return (10.0, 12.0, 40.0, 52.0)  # xyxy -> xywh = 10,12,30,40


def test_prepare_trackeval_workspace_writes_motchallenge_layout(tmp_path):
    gt = {
        "S": {
            1: [MOTObject("S", 1, 7, _box(), 1.0)],
            2: [MOTObject("S", 2, 7, _box(), 1.0)],
        }
    }
    trackers = {
        "m__clean": {
            "S": {
                1: [MOTObject("S", 1, 3, _box(), 0.9)],
                2: [MOTObject("S", 2, 3, _box(), 0.9)],
            }
        }
    }

    info = prepare_trackeval_workspace(tmp_path / "ws", gt, trackers, split="all")

    sub = "PRIVACY-all"
    gt_file = tmp_path / "ws" / "gt" / sub / "S" / "gt" / "gt.txt"
    seqinfo = tmp_path / "ws" / "gt" / sub / "S" / "seqinfo.ini"
    seqmap = tmp_path / "ws" / "gt" / "seqmaps" / f"{sub}.txt"
    tracker_file = tmp_path / "ws" / "trackers" / sub / "m__clean" / "data" / "S.txt"

    assert gt_file.exists() and seqinfo.exists() and seqmap.exists() and tracker_file.exists()

    # GT row: frame,id,x,y,w,h,conf=1,class=1,visibility=1
    assert gt_file.read_text().splitlines()[0] == "1,7,10.00,12.00,30.00,40.00,1,1,1"
    # Tracker row: frame,id,x,y,w,h,score,-1,-1,-1
    assert tracker_file.read_text().splitlines()[0] == "1,3,10.00,12.00,30.00,40.00,0.9000,-1,-1,-1"

    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(seqinfo)
    assert parser["Sequence"]["seqLength"] == "2"

    assert "S" in seqmap.read_text().splitlines()
    assert info["benchmark"] == "PRIVACY"
    assert info["trackers"] == ["m__clean"]


def test_parse_trackeval_summary_converts_percentages_to_fractions():
    text = "HOTA DetA AssA LocA MOTA MOTP IDF1\n63.2 70.1 57.0 85.0 75.0 80.0 68.0\n"
    parsed = _parse_trackeval_summary(text)
    assert parsed["hota"] == 0.632
    assert parsed["deta"] == 0.701
    assert parsed["assa"] == 0.57
    assert parsed["idf1"] == 0.68


def test_parse_trackeval_summary_drops_leading_label_column():
    text = "HOTA DetA AssA\nCOMBINED 63.2 70.1 57.0\n"
    parsed = _parse_trackeval_summary(text)
    assert parsed["hota"] == 0.632
    assert parsed["assa"] == 0.57


def test_run_trackeval_hota_graceful_without_root(monkeypatch):
    monkeypatch.delenv("TRACKEVAL_ROOT", raising=False)
    info = {"trackers": [], "benchmark": "PRIVACY", "split": "all"}
    result = run_trackeval_hota(info, trackeval_root=None)
    assert result["available"] is False
    assert result["reason"] == "trackeval_root_not_set"


def test_run_trackeval_hota_graceful_when_script_missing(tmp_path):
    info = {
        "trackers": ["m__clean"],
        "gt_folder": str(tmp_path / "gt"),
        "trackers_folder": str(tmp_path / "trackers"),
        "seqmap_file": str(tmp_path / "seqmap.txt"),
        "benchmark": "PRIVACY",
        "split": "all",
    }
    result = run_trackeval_hota(info, trackeval_root=tmp_path / "nonexistent")
    assert result["available"] is False
    assert result["reason"].startswith("script_not_found")
