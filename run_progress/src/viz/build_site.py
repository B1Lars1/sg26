from __future__ import annotations

import polars as pl
from config import GOLD_DIR, SITE_DIR, ASSETS_DIR


def export_weekly_to_json():
    weekly_path = GOLD_DIR / "weekly_progress.parquet"
    df = pl.read_parquet(weekly_path)

    # Lag en enkel label per uke, f.eks. "2025-W12"
    df = df.with_columns(
        pl.format("{}-W{}", "year", "week").alias("year_week")
    )

    json_str = df.select(
        [
            "year",
            "week",
            "year_week",
            "total_distance_km",
            "total_time_h",
            "n_runs",
            "avg_distance_km",
        ]
    ).write_json()

    out_path = ASSETS_DIR / "progression_weekly.json"
    out_path.write_text(json_str, encoding="utf-8")
    print(f"Wrote JSON to {out_path}")


def ensure_index_html():
    index_path = SITE_DIR / "index.html"
    if index_path.exists():
        print(f"index.html already exists at {index_path}")
        return

    html = """<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8" />
  <title>Løpeprogresjon</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; margin: 20px; }
    h1 { font-size: 1.8rem; }
    .chart-container { max-width: 900px; margin-top: 40px; }
    canvas { width: 100%%; height: 400px; }
  </style>
</head>
<body>
  <h1>Løpeprogresjon</h1>
  <p>Km per uke, basert på Garmin-data via Strava.</p>

  <div class="chart-container">
    <canvas id="weeklyDistanceChart"></canvas>
  </div>

  <script>
    async function loadData() {
      const res = await fetch("assets/progression_weekly.json");
      const data = await res.json();

      const labels = data.map(d => d.year_week);
      const distances = data.map(d => d.total_distance_km);

      const ctx = document.getElementById("weeklyDistanceChart").getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: {
          labels: labels,
          datasets: [{
            label: "Km per uke",
            data: distances,
            fill: false,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          interaction: {
            mode: "index",
            intersect: false
          },
          scales: {
            x: {
              title: { display: true, text: "Uke" }
            },
            y: {
              title: { display: true, text: "Km" }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: (ctx) => {
                  const v = ctx.parsed.y ?? 0;
                  return v.toFixed(1) + " km";
                }
              }
            }
          }
        }
      });
    }

    loadData();
  </script>
</body>
</html>
"""
    index_path.write_text(html, encoding="utf-8")
    print(f"Created {index_path}")


def main():
    export_weekly_to_json()
    ensure_index_html()


if __name__ == "__main__":
    main()
