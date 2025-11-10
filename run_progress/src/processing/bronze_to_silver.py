from __future__ import annotations

from pathlib import Path
import polars as pl

from config import BRONZE_DIR, SILVER_DIR


def get_latest_bronze_file() -> Path:
    files = sorted(BRONZE_DIR.glob("strava_activities_*.parquet"))
    if not files:
        raise FileNotFoundError("No bronze parquet files found")
    return files[-1]


def bronze_to_silver():
    bronze_file = get_latest_bronze_file()
    df = pl.read_parquet(bronze_file)

    # Sjekk gjerne én gang hva kolonner faktisk heter:
    # print(df.columns)

    df_run = (
        df
        .filter(pl.col("type") == "Run")
        .select(
            pl.col("id").alias("activity_id"),
            pl.col("name"),
            pl.col("start_date_local"),
            pl.col("distance"),
            pl.col("moving_time"),
            pl.col("elapsed_time"),
            pl.col("total_elevation_gain"),
            pl.col("average_speed"),
            pl.col("max_speed"),
        )
        .with_columns(
            pl.col("start_date_local")
              .str.to_datetime(time_zone="UTC", strict=False)
        )
    )

    out_path = SILVER_DIR / "runs.parquet"
    df_run.write_parquet(out_path)
    print(f"Silver: {df_run.height} rows -> {out_path}")


if __name__ == "__main__":
    bronze_to_silver()
