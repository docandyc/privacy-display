import json

import pytest

from experiments.real_capture_shoot import merge_metadata, planned_matrix, try_set_exposure


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
