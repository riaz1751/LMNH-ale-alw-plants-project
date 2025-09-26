"""Transform script of the ETL pipeline."""
import re
import logging
import pandas as pd
from extract import OUT_FILE

# Validate dictionaries with required data: name, plant_id, last_watered, scientific_name
# Reading:temperature, soil_moisture, recording_taken
# Botanist: first_name, last_name, email, phone_number
# City: city name, country name, lat, long
# Remove the image dictionary
# Not all scientific names are present
# Separate full name of botanist into first name and last name
# Clean botanist phone number to not have x in it
# Standardise time stamps

# pylint:disable=unsupported-assignment-operation
# pylint:disable=unsubscriptable-object

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def load_json():
    """Read json data."""
    return pd.read_json(OUT_FILE)


def validate_data_types(data: pd.DataFrame) -> pd.DataFrame:
    """Validate the plant dictionaries."""
    df = pd.DataFrame(data)
    df = df.drop(columns=['images'])
    df["name"] = df["name"].astype(str)
    df["scientific_name"] = df["scientific_name"].astype(str)
    df["last_watered"] = pd.to_datetime(
        df["last_watered"], errors="coerce")
    df["recording_taken"] = pd.to_datetime(
        df["recording_taken"], errors="coerce")
    return df


def process_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Processes dataframe required columns."""
    data = pd.DataFrame(data)

    logging.debug("Validating name & plant_id are not null.")
    data = data[data['name'].notnull() & data['plant_id'].notnull()]

    logging.debug("Validating temperature & soil_moisture are not null.")
    data = data[data['temperature'].notnull(
    ) & data['soil_moisture'].notnull()]

    logging.debug("Validating recording_take is not null.")
    data = data[data['recording_taken'].notnull()]

    return data


def clean_emails(data: pd.DataFrame) -> pd.DataFrame:
    """Transform botanist emails to a valid format."""

    data["email"] = data["botanist"].apply(
        lambda x: x.get("email") if x else None)
    data["email_valid"] = data["email"].apply(
        lambda x: bool(
            re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", str(x)))
        if pd.notnull(x) else False
    )

    data = data[data['email_valid']]

    return data


def clean_names(data: pd.DataFrame) -> pd.DataFrame:
    """Transform botanist names to a valid format."""
    data["botanist_cleaned"] = (
        data["botanist"].apply(lambda x: x.get("name") if x else None)
        .str.replace(r'^(Mr\.|Mrs\.|Ms\.|Dr\.)\s*', '', regex=True)
        .str.replace(r'\s+(Jr\.|MD|DVM|[IVXLCDM]+)\s*$', '', regex=True)
    )
    data[["first_name", "last_name"]
         ] = data["botanist_cleaned"].str.split(' ', expand=True)
    data["first_name"] = data["first_name"].str.strip()
    data["last_name"] = data["last_name"].str.strip()
    return data


def clean_phone_numbers(data: pd.DataFrame) -> pd.DataFrame:
    """This function processes the phone numbers so that they are normalised and clean."""

    data["phone"] = data["botanist"].apply(
        lambda x: x.get("phone") if x else None)

    data["phone_valid"] = data["phone"].apply(
        lambda x: bool(
            re.match(r"^\s*(?:\+?\d{1,3}[-.\s]?)?"
                     r"(?:\(?\d{2,4}\)?[-.\s]?)?"
                     r"\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}"
                     r"(?:\s*x\d+)?\s*$",
                     str(x)
                     )
        )
        if pd.notnull(x) else False
    )

    data.loc[data["phone_valid"], "phone_cleaned"] = (
        data.loc[data["phone_valid"], "phone"].str.replace(
            r"\.", "-", regex=True)
    )
    data = data.drop(columns=["phone"])
    data = data[data['phone_valid']]

    return data


def clean_soil_moisture_data(data: pd.DataFrame) -> pd.DataFrame:
    """Convert negative soil moisture readings to their absolute value"""
    data['soil_moisture'] = data["soil_moisture"].abs()

    return data


def clean_valid_data():
    """Calling functions for data validation, cleaning and transformation."""
    data = load_json()
    processed_data = process_columns(data)
    valid_data = validate_data_types(processed_data)
    data = clean_names(valid_data)
    data = clean_emails(data)
    data = clean_phone_numbers(data)
    data = clean_soil_moisture_data(data)
    return data


if __name__ == "__main__":
    clean_data = clean_valid_data()
    print(clean_data.head())
