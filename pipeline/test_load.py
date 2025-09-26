"""Testing script for the load script of the ETL pipeline."""
# pylint:skip-file

from unittest.mock import patch, MagicMock
import pytest
import pandas as pd
from load import load_data


@pytest.fixture
def sample_df():
    """Sample data from for testing."""
    return pd.DataFrame([{
        "origin_location": {"city": "London",
                            "country": "England",
                            "latitude": 51.5,
                            "longitude": -0.12},
        "name": "Rose",
        "scientific_name": ["Rosa rubiginosa"],
        "last_watered": "2025-09-22T13:51:41.000Z",
        "temperature": 22.5,
        "soil_moisture": 35.0,
        "recording_taken": "2025-09-23T08:53:53.653Z",
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "phone_valid": "123-456-7890",
    }])


@pytest.fixture
def mock_conn():
    """Mock connection for testing."""
    conn = MagicMock()
    cursor = conn.cursor.return_value.__enter__.return_value
    return conn


@patch("load.clean_valid_data")
@patch("load.get_connection")
@patch("load.insert_db")
@patch("load.get_mapping")
def test_load_data_inserts_new_records(
    mock_get_mapping, mock_insert_db, mock_get_connection, mock_clean_valid_data, sample_df, mock_conn
):
    """Ensure new countries, cities, botanists, plants, and readings are inserted."""
    mock_get_connection.return_value = mock_conn
    mock_clean_valid_data.return_value = sample_df

    # Side effects for all get_mapping calls
    mock_get_mapping.side_effect = [
        {}, {"England": 1},
        {}, {"alice@example.com": 2},
        {}, {("Rose", 10): 20},
    ]

    cursor = mock_conn.cursor.return_value.__enter__.return_value
    cursor.fetchall.side_effect = [
        [],
        [(10, "London", 1)],
        [],
        [(20, "Rose", 10)],
    ]

    load_data()

    # Country inserted
    mock_insert_db.assert_any_call(
        mock_conn,
        "INSERT INTO beta.Country (country_name) VALUES (?)",
        ("England",),
    )
    # Botanist inserted
    mock_insert_db.assert_any_call(
        mock_conn,
        "INSERT INTO beta.Botanist (first_name, last_name, email, phone_number) VALUES (?, ?, ?, ?)",
        ("Alice", "Smith", "alice@example.com", "123-456-7890"),
    )
    # Plant inserted
    assert any("INSERT INTO beta.Plant" in call[0][1]
               for call in mock_insert_db.call_args_list)
    # Reading inserted
    assert any("INSERT INTO beta.Reading" in call[0][1]
               for call in mock_insert_db.call_args_list)


@patch("load.clean_valid_data")
@patch("load.get_connection")
@patch("load.insert_db")
@patch("load.get_mapping")
def test_load_data_skips_existing_records(
    mock_get_mapping, mock_insert_db, mock_get_connection, mock_clean_valid_data, sample_df, mock_conn
):
    """Ensure no duplicates are inserted if mappings already exist."""
    mock_get_connection.return_value = mock_conn
    mock_clean_valid_data.return_value = sample_df

    mock_get_mapping.side_effect = [
        {"England": 1}, {"England": 1},
        {"alice@example.com": 2}, {"alice@example.com": 2},
        {("Rose", 10): 20}, {("Rose", 10): 20},
    ]

    cursor = mock_conn.cursor.return_value.__enter__.return_value
    cursor.fetchall.side_effect = [
        [(10, "London", 1)],
        [(10, "London", 1)],
        [(20, "Rose", 10)],
        [(20, "Rose", 10)],
    ]

    load_data()

    insert_calls = [call[0][1] for call in mock_insert_db.call_args_list]
    assert not any("INSERT INTO beta.Country" in q for q in insert_calls)
    assert not any("INSERT INTO beta.Botanist" in q for q in insert_calls)
    assert not any("INSERT INTO beta.Plant" in q for q in insert_calls)
