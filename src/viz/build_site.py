from __future__ import annotations

import polars as pl
from ..config import GOLD_DIR, SITE_DIR, ASSETS_DIR


def export_weekly_to_json():
    weekly_path = GOLD_DIR / "weekly_progress.parquet"
    
    if not weekly_path.exists():
        print(f"Warning: {weekly_path} not found. Skipping JSON export.")
        return
    
    df = pl.read_parquet(weekly_path)

    # Create a simple label per week, e.g. "2025-W12"
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


def export_activities_to_json():
    """Export individual activities from silver data to JSON for the table."""
    silver_path = GOLD_DIR.parent / "silver" / "runs.parquet"
    
    if not silver_path.exists():
        print(f"Warning: {silver_path} not found. Skipping activities JSON export.")
        return
    
    df = pl.read_parquet(silver_path)
    
    # Sort by start_date_local in descending order (newest first)
    df = df.sort("start_date_local", descending=True)
    
    # Convert distance from meters to km and moving_time from seconds to minutes
    df = df.with_columns(
        distance_km=pl.col("distance") / 1000,
        moving_time_min=pl.col("moving_time") / 60,
    )
    
    # Select relevant columns for the table
    df_export = df.select([
        pl.col("start_date_local").alias("date"),
        "name",
        "distance_km",
        "moving_time_min",
        "average_speed",
        "max_speed",
        "total_elevation_gain",
    ])
    
    json_str = df_export.write_json()
    out_path = ASSETS_DIR / "activities.json"
    out_path.write_text(json_str, encoding="utf-8")
    print(f"Wrote activities JSON to {out_path}")


def ensure_index_html():
    index_path = SITE_DIR / "index.html"
    if index_path.exists():
        print(f"index.html already exists at {index_path}")
        return

    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Running Progress</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; margin: 20px; }
    h1 { font-size: 1.8rem; }
    .chart-container { max-width: 900px; margin-top: 40px; }
    canvas { width: 100%; height: 400px; }
    table { width: 100%; margin-top: 40px; border-collapse: collapse; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    th { background-color: #f2f2f2; font-weight: bold; }
    tr:nth-child(even) { background-color: #f9f9f9; }
    tr:hover { background-color: #f0f0f0; }
  </style>
</head>
<body>
  <h1>Running Progress</h1>
  <p>Km per week, based on Garmin data via Strava.</p>

  <div class="chart-container">
    <canvas id="weeklyDistanceChart"></canvas>
  </div>

  <h2 style="margin-top: 40px;">Activities</h2>
  <table id="activitiesTable">
    <thead>
      <tr>
        <th>Date</th>
        <th>Name</th>
        <th>Distance (km)</th>
        <th>Time (min)</th>
        <th>Avg Speed (m/s)</th>
        <th>Max Speed (m/s)</th>
        <th>Elevation Gain (m)</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>

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
            label: "Km per week",
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
              title: { display: true, text: "Week" }
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

    async function loadActivities() {
      const res = await fetch("assets/activities.json");
      const activities = await res.json();
      
      const tbody = document.querySelector("#activitiesTable tbody");
      
      activities.forEach(activity => {
        const row = document.createElement("tr");
        const date = new Date(activity.date);
        const dateStr = date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
        
        row.innerHTML = `
          <td>${dateStr}</td>
          <td>${activity.name}</td>
          <td>${(activity.distance_km).toFixed(2)}</td>
          <td>${Math.round(activity.moving_time_min)}</td>
          <td>${(activity.average_speed).toFixed(2)}</td>
          <td>${(activity.max_speed).toFixed(2)}</td>
          <td>${Math.round(activity.total_elevation_gain)}</td>
        `;
        tbody.appendChild(row);
      });
    }

    loadData();
    loadActivities();
  </script>
</body>
</html>
"""
    index_path.write_text(html, encoding="utf-8")
    print(f"Created {index_path}")


def main():
    export_weekly_to_json()
    export_activities_to_json()
    ensure_index_html()


if __name__ == "__main__":
    main()
