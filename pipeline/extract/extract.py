"""Extracting Plant data from respective API."""
import requests
import json
import logging
from pathlib import Path
from datetime import datetime
import threading
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

BASE_URL = "https://sigma-labs-bot.herokuapp.com/api/plants/"
OUT_FILE = Path("plants.json")

new_record = []
lock = threading.Lock()


def load_existing() -> list[dict]:
    """Loads all pre-existing plant data to a json file and starts fresh if file is corrupted."""
    if OUT_FILE.exists():
        try:
            with OUT_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.warning("plants.json corrupted, starting fresh.")
    return []


def get_latest_timestamp(plants: list[dict]) -> datetime | None:
    """Returns latest recorded timestamp to avoid duplicate data."""
    timestamps = []
    for p in plants:
        ts = p.get("recording_taken")
        if ts:
            try:
                timestamps.append(datetime.fromisoformat(
                    ts.replace("Z", "+00:00")))
            except ValueError:
                pass
    return max(timestamps) if timestamps else None


def fetch_one(plant_id: int, latest_ts: datetime) -> dict | None:
    """Returns plant data as a dictionary from one API endpoint."""
    url = f"{BASE_URL}{plant_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        plant = resp.json()

    except requests.RequestException as e:
        logging.error(f"Error fetching plant {plant_id}: {e}")

    ts_str = plant.get("recording_taken")
    if not ts_str:
        logging.debug(f"Plant {plant_id} has not recording taken.")
        return None

    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return None

    if not latest_ts or ts > latest_ts:
        with lock:
            new_record.append(plant)
        logging.info(
            f"Update found {plant['plant_id']}: {plant['name']} at {ts_str}")


def fetch_updates(latest_ts: datetime, max_id: int = 200, workers: int = 20) -> list[dict]:
    """Fetch plants data efficiently using threading."""

    new_records = []

    run_time = time.perf_counter()

    for plant_id in range(1, max_id + 1):
        thread = threading.Thread(target=fetch_one, args=(plant_id, latest_ts))
        new_records.append(thread)
        thread.start()

        if len(new_records) >= workers:
            for record in new_records:
                record.join()
            new_records = []

    for record in new_records:
        record.join()

    elapsed = time.perf_counter() - run_time
    logging.info(f"Time take: {elapsed:.2f} seconds")

    return new_record


def extract():
    """Main block functions."""
    plants = load_existing()
    latest_ts = get_latest_timestamp(plants)
    logging.info(f"Latest known recording: {latest_ts}")

    new_plants = fetch_updates(latest_ts, max_id=200, workers=10)

    if new_plants:
        plants.extend(new_plants)
        with OUT_FILE.open("w", encoding="utf-8") as f:
            json.dump(plants, f, indent=2, ensure_ascii=False)
        logging.info(
            f"Added {len(new_plants)} new/updated records. Total now {len(plants)}")
    else:
        logging.info("No new data found.")


if __name__ == "__main__":
    extract()
