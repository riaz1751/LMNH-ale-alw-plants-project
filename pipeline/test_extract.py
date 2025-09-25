"""Testing the extract script."""
import json
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch,  mock_open, MagicMock
from extract import load_existing, fetch_one, fetch_updates
import extract


class DummyData:

    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self.data = data or {}

    def json(self):
        return self.data


def test_load_existing_valid_filepath():
    """Testing working pathway and valid data."""
    mock_data = [
        {"plant_id": 1, "name": "Test1"},
        {"plant_id": 2, "name": "Test2"}
    ]
    fake_plants = json.dumps(mock_data)
    with patch.object(Path, 'exists', return_value=True):
        with patch("builtins.open", mock_open(read_data=fake_plants)):
            result = load_existing()
    assert isinstance(result, list)
    assert "plant_id" in result[0]
    assert "name" in result[0]


def test_load_existing_invalid_filepath():
    """Testing non existent filepath."""
    with patch.object(Path, 'exists', return_value=False):
        result = load_existing()
    assert result == []
    assert len(result) == 0


def test_get_latest_timestamp():
    """Testing the get_latest_timestamp."""
    plants = [
        {"recording_taken": "2025-09-23T10:00:00.000Z"}
    ]
    ts = extract.get_latest_timestamp(plants)
    assert ts == datetime(2025, 9, 23, 10, 0, tzinfo=timezone.utc)


def test_fetch_one_adds_new(monkeypatch):
    """Test the fetch_one function."""
    plant = {
        "plant_id": 5,
        "name": "Mock Plant",
        "recording_taken": "2025-09-25T10:00:00.000Z"
    }

    extract.requests.get = MagicMock(return_value=DummyData(200, plant))

    latest_ts = datetime(2025, 9, 24, 12, 0, tzinfo=timezone.utc)
    extract.new_record.clear()
    extract.fetch_one(5, latest_ts)
    assert any(p["plant_id"] == 5 for p in extract.new_record)


def test_fetch_one_check_older():
    """Test fetch_one function for older data."""
    plant = {
        "plant_id": 6,
        "name": "Mock Plant",
        "recording_taken": "2025-09-20T10:00:00.000Z"
    }
    extract.requests.get = MagicMock(return_value=DummyData(200, plant))

    latest_ts = datetime(2025, 9, 24, 12, 0, tzinfo=timezone.utc)
    extract.new_record.clear()
    extract.fetch_one(6, latest_ts)
    assert all(p["plant_id"] != 6 for p in extract.new_record)


def test_fetch_one_no_ts():
    """Test the no timestamp case."""
    plant = {
        "plant_id": 7,
        "name": "Mock Plant",
        "recording_taken": "2025-09-20T10:00:00.000Z"
    }

    extract.requests.get = MagicMock(return_value=DummyData(200, plant))

    latest_ts = datetime.now(timezone.utc)
    extract.new_record.clear()
    extract.fetch_one(7, latest_ts)
    assert not extract.new_record


def test_fetch_one_handles_invalid_ts():
    """Test the invalid timestamp case."""
    plant = {
        "plant_id": 7,
        "name": "Mock Plant",
        "recording_taken": "Not a date"
    }
    extract.requests.get = MagicMock(return_value=DummyData(200, plant))

    extract.new_record.clear()
    extract.fetch_one(7, datetime.now(timezone.utc))
    assert not extract.new_record


def test_fetch_one_handles_error():
    """Test the error handling case."""
    extract.requests.get = MagicMock(return_value=DummyData(500))
    extract.new_record.clear()
    extract.fetch_one(9, datetime.now(timezone.utc))
    assert not extract.new_record


def test_fetch_updates_collect_new_skip_old():
    """Test if only updates are extracted to json."""
    data = {
        1: {"plant_id": 1, "name": "Old", "recording_taken": "2025-09-20T10:00:00.000Z"},
        2: {"plant_id": 2, "name": "New", "recording_taken": "2025-09-25T10:00:00.000Z"}
    }

    def fake_data(url, timeout=10):
        plant_id = int(url.split("/")[-1])
        if plant_id in data:
            return DummyData(200, data[plant_id])
        return DummyData(404)

    extract.requests.get = MagicMock(side_effect=fake_data)

    latest_ts = datetime(2025, 9, 23, tzinfo=timezone.utc)
    extract.new_record.clear()
    results = extract.fetch_updates(latest_ts, max_id=2, workers=2)

    ids = [p["plant_id"] for p in results]
    assert 2 in ids
