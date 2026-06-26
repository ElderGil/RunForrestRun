"""Fetch activities from Strava API and save raw JSON to data/."""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
ATHLETE_URL = "https://www.strava.com/api/v3/athlete"
ZONES_URL = "https://www.strava.com/api/v3/athlete/zones"

# History start: June 2024
HISTORY_START_EPOCH = int(datetime(2024, 6, 1, tzinfo=timezone.utc).timestamp())


def get_access_token() -> str:
    resp = requests.post(TOKEN_URL, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_all_activities(token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    activities = []
    page = 1
    per_page = 100

    while True:
        resp = requests.get(ACTIVITIES_URL, headers=headers, params={
            "after": HISTORY_START_EPOCH,
            "per_page": per_page,
            "page": page,
        }, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        activities.extend(batch)
        print(f"  page {page}: {len(batch)} activities")
        if len(batch) < per_page:
            break
        page += 1
        time.sleep(0.5)  # respect rate limits

    return activities


def fetch_athlete(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(ATHLETE_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_zones(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(ZONES_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    print("Refreshing access token...")
    token = get_access_token()

    print("Fetching athlete profile...")
    athlete = fetch_athlete(token)
    (DATA_DIR / "athlete.json").write_text(json.dumps(athlete, indent=2))

    print("Fetching HR/pace zones...")
    zones = fetch_zones(token)
    (DATA_DIR / "zones.json").write_text(json.dumps(zones, indent=2))

    print("Fetching activities (since Jun 2024)...")
    activities = fetch_all_activities(token)
    print(f"Total: {len(activities)} activities")
    (DATA_DIR / "activities_raw.json").write_text(json.dumps(activities, indent=2))

    print("Done. Raw data saved to data/")


if __name__ == "__main__":
    main()
