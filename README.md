# SG26 — Running progress

This project ingests, processes and visualizes running activities from Strava.

## Overview

The project follows a simple data lakehouse pattern with three layers:

- **Bronze**: Raw activity data from the Strava API (JSON and Parquet)
- **Silver**: Cleaned and filtered runs (Parquet)
- **Gold**: Aggregated, business-ready data (Parquet)
- **Viz**: A small static HTML visualization

## Project structure

```
SG26/
├── src/
│   ├── config.py                    # Central configuration
│   ├── ingestion/
│   │   ├── fetch_activities.py      # Fetch activities from Strava
│   │   └── strava_auth.py           # Strava authentication helper
│   ├── processing/
│   │   ├── bronze_to_silver.py      # Bronze -> Silver transformation
│   │   └── silver_to_gold.py        # Silver -> Gold aggregation
│   └── viz/
│       └── build_site.py            # Build the static site
├── data/
│   ├── bronze/                      # Raw data
│   ├── silver/                      # Cleaned runs
│   └── gold/                        # Aggregated weekly data
├── site/
│   ├── index.html                   # Static site
│   └── assets/
│       └── progression_weekly.json  # JSON used by the frontend
├── pyproject.toml
└── README.md
```

## Setup

Requirements:

- Python 3.12+
- `uv` (UV package manager)

Install dependencies:

```bash
uv sync
```

Create a `.env` file in the repository root with your Strava credentials:

```env
STRAVA_CLIENT_ID=<your-client-id>
STRAVA_CLIENT_SECRET=<your-client-secret>
STRAVA_REFRESH_TOKEN=<your-refresh-token>
```

## Usage

Run the pipeline step by step:

1. Fetch raw activities (Bronze):

```bash
uv run python -m src.ingestion.fetch_activities
```

2. Transform Bronze -> Silver:

```bash
uv run python -m src.processing.bronze_to_silver
```

3. Aggregate Silver -> Gold:

```bash
uv run python -m src.processing.silver_to_gold
```

4. Build the static site (export JSON + create index):

```bash
uv run python -m src.viz.build_site
```

You can also run the full sequence in one line:

```bash
uv run python -m src.ingestion.fetch_activities && \
uv run python -m src.processing.bronze_to_silver && \
uv run python -m src.processing.silver_to_gold && \
uv run python -m src.viz.build_site
```

## View the site locally

Start a simple HTTP server from the repo root and open the page:

```bash
python -m http.server 8000
# then visit http://localhost:8000/site/index.html
```

## Git policy for data

Data files (`.json`, `.parquet`) are ignored in Git but the directory structure is kept via `.gitkeep` files. This allows the repository to contain the empty folders while preventing sensitive or large data files from being committed.

## Components

- `src/config.py`: path constants and environment variable loading
- `src/ingestion/`: Strava API ingestion
- `src/processing/`: transformation pipeline (bronze -> silver -> gold)
- `src/viz/`: generate the static site and JSON used by the frontend

## License

MIT
