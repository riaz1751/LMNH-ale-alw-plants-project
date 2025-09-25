"""ETL pipeline script for extracting, cleaning and loading plant records from API to RDS."""
from extract import extract
from transform import clean_valid_data
from load import load_data


def run_pipeline():
    """Run pipeline in one command."""
    extract()
    clean_valid_data()
    load_data()


if __name__ == "__main__":
    run_pipeline()
