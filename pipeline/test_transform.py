import pytest
import pandas as pd
from transform import (
    validate_data_types,
    process_columns,
    clean_emails,
    clean_names,
    clean_phone_numbers,
    clean_soil_moisture_data,
    clean_valid_data,
)


# Fixtures

@pytest.fixture
def sample_raw_df():
    """Basic valid row of raw plant data."""
    return pd.DataFrame([{
        "plant_id": 1,
        "name": "Rose",
        "scientific_name": ["Rosa rubiginosa"],
        "last_watered": "2025-09-20T10:00:00Z",
        "recording_taken": "2025-09-21T12:00:00Z",
        "temperature": 20.5,
        "soil_moisture": -15.0,
        "images": ["http://example.com/img.png"],
        "botanist": {
            "name": "Dr. Alice Smith Jr.",
            "email": "alice@example.com",
            "phone": "123-456-7890 x123",
        },
    }])


@pytest.fixture
def bad_email_df(sample_raw_df):
    """Row with invalid email."""
    df = sample_raw_df.copy()
    df.at[0, "botanist"] = {"name": "Bob",
                            "email": "bad-email", "phone": "123456"}
    return df


@pytest.fixture
def bad_phone_df(sample_raw_df):
    """Row with invalid phone."""
    df = sample_raw_df.copy()
    df.at[0, "botanist"] = {"name": "Charlie",
                            "email": "charlie@example.com", "phone": "not-a-phone"}
    return df


# Tests

def test_validate_data_types_removes_images_and_casts(sample_raw_df):
    df = validate_data_types(sample_raw_df)
    assert "images" not in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["last_watered"])
    assert pd.api.types.is_datetime64_any_dtype(df["recording_taken"])


def test_process_columns_filters_nulls():
    df = pd.DataFrame([
        {"plant_id": 1, "name": "Rose", "temperature": 20,
            "soil_moisture": 30, "recording_taken": pd.Timestamp("2025-01-01")},
        {"plant_id": None, "name": "Tulip", "temperature": 20,
            "soil_moisture": 30, "recording_taken": pd.Timestamp("2025-01-01")},
    ])
    result = process_columns(df)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "Rose"


def test_clean_emails_filters_invalid(bad_email_df):
    df = validate_data_types(bad_email_df)
    df = clean_emails(df)
    assert len(df) == 0


def test_clean_emails_accepts_valid(sample_raw_df):
    df = validate_data_types(sample_raw_df)
    df = clean_emails(df)
    assert df.iloc[0]["email"] == "alice@example.com"


def test_clean_names_splits_and_strips(sample_raw_df):
    df = validate_data_types(sample_raw_df)
    df = clean_names(df)
    assert df.iloc[0]["first_name"] == "Alice"
    assert df.iloc[0]["last_name"] == "Smith"


def test_clean_phone_numbers_filters_invalid(bad_phone_df):
    df = validate_data_types(bad_phone_df)
    df = clean_phone_numbers(df)
    assert len(df) == 0


def test_clean_phone_numbers_accepts_valid(sample_raw_df):
    df = validate_data_types(sample_raw_df)
    df = clean_phone_numbers(df)
    assert "phone_cleaned" in df.columns
    assert df.iloc[0]["phone_cleaned"].startswith("123-456-7890")


def test_clean_soil_moisture_data_abs(sample_raw_df):
    df = validate_data_types(sample_raw_df)
    df = clean_soil_moisture_data(df)
    assert df.iloc[0]["soil_moisture"] >= 0


def test_clean_valid_data_runs_end_to_end(monkeypatch, sample_raw_df):
    monkeypatch.setattr("transform.load_json", lambda: sample_raw_df)
    df = clean_valid_data()
    assert not df.empty
    assert "first_name" in df.columns
    assert "last_name" in df.columns
    assert "email" in df.columns
    assert "phone_cleaned" in df.columns
    assert df.iloc[0]["soil_moisture"] >= 0
