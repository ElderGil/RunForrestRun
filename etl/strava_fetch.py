"""Fetch activities from Strava and maintain the versioned raw store.

Incremental by design (ADR-001): `data/activities_raw.json` IS the store of
record, versioned in Git. Each run fetches only activities newer than the
latest one already stored (with a small overlap), then merges deduping by id.
On a fresh checkout with no store, it backfills from Jun/2024.

Location fields are stripped before storing (ADR-003 rule 5).
"""

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
RAW_PATH = DATA_DIR / "activities_raw.json"

TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"

HISTORY_START = datetime(2024, 6, 1, tzinfo=timezone.utc)
OVERLAP_SECONDS = 2 * 24 * 3600  # re-fetch a 2-day window to catch edits

# Strip these to honour "no location" (ADR-003).
LOCATION_FIELDS = {"start_latlng", "end_latlng", "map", "location_city",
                   "location_state", "location_country", "timezone", "utc_offset"}


def get_access_token() -> str:
    resp = requests.post(TOKEN_URL, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def load_store() -> list[dict]:
    if RAW_PATH.exists():
        return json.loads(RAW_PATH.read_text())
    return []


def latest_epoch(store: list[dict]) -> int:
    """Epoch of the newest stored activity, minus an overlap window."""
    if not store:
        return int(HISTORY_START.timestamp())
    newest = max(
        a.get("start_date") or a.get("start_date_local") or "2000-01-01"
        for a in store
    )
    dt = datetime.fromisoformat(newest[:19].replace("Z", "")).replace(tzinfo=timezone.utc)
    return int(dt.timestamp()) - OVERLAP_SECONDS


def strip_location(a: dict) -> dict:
    return {k: v for k, v in a.items() if k not in LOCATION_FIELDS}


def fetch_since(token: str, after_epoch: int) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    fetched, page, per_page = [], 1, 100
    while True:
        resp = requests.get(ACTIVITIES_URL, headers=headers, params={
            "after": after_epoch, "per_page": per_page, "page": page,
        }, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        fetched.extend(strip_location(a) for a in batch)
        print(f"  page {page}: {len(batch)} activities")
        if len(batch) < per_page:
            break
        page += 1
        time.sleep(0.5)
    return fetched


def merge(store: list[dict], fresh: list[dict]) -> list[dict]:
    by_id = {str(a["id"]): a for a in store}
    for a in fresh:
        by_id[str(a["id"])] = a  # fresh wins (captures edits)
    merged = list(by_id.values())
    merged.sort(key=lambda a: a.get("start_date_local") or a.get("start_date") or "")
    return merged


def main():
    print("Refreshing access token...")
    token = get_access_token()

    store = load_store()
    after = latest_epoch(store)
    mode = "backfill" if not store else "incremental"
    print(f"Mode: {mode} (after={datetime.fromtimestamp(after, timezone.utc).isoformat()})")

    fresh = fetch_since(token, after)
    print(f"Fetched {len(fresh)} activities")

    merged = merge(store, fresh)
    new_count = len(merged) - len(store)
    RAW_PATH.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    print(f"Store: {len(store)} -> {len(merged)} (+{new_count} new)")


if __name__ == "__main__":
    main()
