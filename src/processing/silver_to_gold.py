from __future__ import annotations

import polars as pl
from ..config import SILVER_DIR, GOLD_DIR


def silver_to_gold_weekly():
    runs_path = SILVER_DIR / "runs.parquet"
    df = pl.read_parquet(runs_path)

    # For safety: check dtype
    # print(df.dtypes)
    # print(df.select("start_date_local").head())

    df = df.with_columns(
        pl.col("start_date_local").dt.week().alias("week"),
        pl.col("start_date_local").dt.year().alias("year"),
        (pl.col("distance") / 1000).alias("distance_km"),
        (pl.col("moving_time") / 3600).alias("moving_time_h"),
    )

    weekly = (
        df.group_by(["year", "week"])
        .agg(
            total_distance_km=pl.col("distance_km").sum(),
            total_time_h=pl.col("moving_time_h").sum(),
            n_runs=pl.len(),
            avg_distance_km=pl.col("distance_km").mean(),
        )
        .sort(["year", "week"])
    )

    out_path = GOLD_DIR / "weekly_progress.parquet"
    weekly.write_parquet(out_path)
    print(f"Gold weekly: {weekly.height} rows -> {out_path}")


if __name__ == "__main__":
    silver_to_gold_weekly()
