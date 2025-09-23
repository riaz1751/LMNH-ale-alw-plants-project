"""Testing the extract script."""
import json
from pathlib import Path
from unittest.mock import patch,  mock_open
from extract import load_existing, fetch_one, fetch_updates


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


def test_fetch_one_1():
    pass
