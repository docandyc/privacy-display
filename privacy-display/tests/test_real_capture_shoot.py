import json

import cv2
import pytest

from experiments.real_capture_shoot import (
    exposure_log2_to_seconds,
    get_camera_backends,
    merge_metadata,
    planned_matrix,
    try_set_exposure,
)


class FakeCapture:
    def __init__(self):
        self.props = {}

    def get(self, prop):
        return self.props.get(prop, 0.0)

    def set(self, prop, value):
        self.props[prop] = value
        return True

    def read(self):
        return True, None


def test_try_set_exposure_without_value_is_not_value_honored():
    cap = FakeCapture()

    result = try_set_exposure(cap, manual=True, value=None)

    assert result["requested_manual"] is True
    assert result["requested_value"] is None
    assert result["honored"] is False


def test_try_set_exposure_uses_windows_dshow_manual_values():
    cap = FakeCapture()

    result = try_set_exposure(cap, manual=True, value=-8, backend_name="dshow")

    assert cap.props[cv2.CAP_PROP_AUTO_EXPOSURE] == 0.25
    assert cap.props[cv2.CAP_PROP_EXPOSURE] == -8
    assert result["honored"] is True


def test_try_set_exposure_uses_windows_msmf_manual_values():
    cap = FakeCapture()

    result = try_set_exposure(cap, manual=True, value=-6, backend_name="msmf")

    assert cap.props[cv2.CAP_PROP_AUTO_EXPOSURE] == 0
    assert cap.props[cv2.CAP_PROP_EXPOSURE] == -6
    assert result["honored"] is True


def test_exposure_log2_to_seconds_maps_directshow_values():
    assert exposure_log2_to_seconds(-8) == pytest.approx(1 / 256)
    assert exposure_log2_to_seconds(-6) == pytest.approx(1 / 64)
    assert exposure_log2_to_seconds(None) is None


def test_get_camera_backends_prefers_windows_msmf_then_dshow():
    names = [name for name, _ in get_camera_backends(system="Windows")]

    assert names[:2] == ["msmf", "dshow"]


def test_merge_metadata_rejects_malformed_existing_file(tmp_path):
    path = tmp_path / "metadata.json"
    path.write_text(json.dumps({"captures": {}}), encoding="utf-8")

    with pytest.raises(ValueError):
        merge_metadata(tmp_path, "metadata.json", [])

    assert json.loads(path.read_text(encoding="utf-8")) == {"captures": {}}


def test_planned_matrix_rejects_unknown_condition():
    class Args:
        conditions = "protected,unknown"
        condition = "protected"
        ns = ""
        n = 4
        distances = "1"
        angles = "0"

    with pytest.raises(ValueError):
        planned_matrix(Args())
