from __future__ import annotations

import time
import json
from datetime import datetime
from pathlib import Path
import requests
import polars as pl

from ..config import BRONZE_DIR
from .strava_auth import get_access_token

ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"

def fetch_activities(after_epoch: int | None = None,
                     per_page: int = 50,
                     max_pages: int = 10) -> list[dict]:
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    all_acts: list[dict] = []

    for page in range(1, max_pages + 1):
        params: dict[str, int] = {"page": page, "per_page": per_page}
        if after_epoch is not None:
            params["after"] = after_epoch

        r = requests.get(ACTIVITIES_URL, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not data:
            break

        all_acts.extend(data)
        time.sleep(0.2)

    return all_acts

def save_to_bronze(activities: list[dict]) -> Path:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    json_path = BRONZE_DIR / f"strava_activities_{ts}.json"
    parquet_path = BRONZE_DIR / f"strava_activities_{ts}.parquet"

    # Raw JSON
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(activities, f)

    # Parquet via Polars
    if activities:
        df = pl.DataFrame(activities)
        df.write_parquet(parquet_path)

    return parquet_path

def main():
    acts = fetch_activities()
    path = save_to_bronze(acts)
    print(f"Saved {len(acts)} activities to {path}")

if __name__ == "__main__":
    main()