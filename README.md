# SG26 - Løpeprogresjon

Et prosjekt for innhenting, prosessering og visualisering av løpedata fra Strava.

## Oversikt

Prosjektet følger en **data lakehouse-arkitektur** med tre lag:

- **Bronze**: Rådata fra Strava API (JSON og Parquet)
- **Silver**: Transformert og renset data (Parquet)
- **Gold**: Aggregert og forretningsklart data (Parquet)
- **Viz**: Visualisering som HTML-nettsted

## Struktur

```
SG26/
├── src/
│   ├── config.py                    # Sentral konfigurering
│   ├── ingestion/
│   │   ├── fetch_activities.py      # Hent data fra Strava API
│   │   └── strava_auth.py           # Strava autentisering
│   ├── processing/
│   │   ├── bronze_to_silver.py      # Bronze → Silver transformasjon
│   │   └── silver_to_gold.py        # Silver → Gold aggregering
│   └── viz/
│       └── build_site.py            # Bygg HTML-nettsted
├── data/
│   ├── bronze/                      # Rådata fra Strava
│   ├── silver/                      # Renset løpedata
│   └── gold/                        # Aggregert ukesdata
├── site/
│   ├── index.html                   # Hovedside
│   └── assets/
│       └── progression_weekly.json   # Ukesdata som JSON
├── pyproject.toml                   # Prosjektkonfigurering
└── README.md
```

## Oppsett

### Forutsetninger

- Python 3.12+
- `uv` (UV package manager)

### Installasjon

1. Klon repositoriet
2. Installer dependencies:
   ```bash
   uv sync
   ```

3. Opprett `.env`-fil med Strava-autentisering:
   ```env
   STRAVA_CLIENT_ID=<din-client-id>
   STRAVA_CLIENT_SECRET=<din-client-secret>
   STRAVA_REFRESH_TOKEN=<din-refresh-token>
   ```

## Bruk

### 1. Hent data fra Strava

```bash
uv run python -m src.ingestion.fetch_activities
```

Dette lagrer rådata i `data/bronze/` som JSON og Parquet.

### 2. Transformér Bronze → Silver

```bash
uv run python -m src.processing.bronze_to_silver
```

Filtrerer ut løpinger og renset data lagres i `data/silver/`.

### 3. Aggreger Silver → Gold

```bash
uv run python -m src.processing.silver_to_gold
```

Lager ukesaggregater som lagres i `data/gold/`.

### 4. Bygg nettsted

```bash
uv run python -m src.viz.build_site
```

Genererer `site/index.html` og eksporterer data som JSON til `site/assets/`.

### Kjør hele pipelinen

```bash
uv run python -m src.ingestion.fetch_activities && \
uv run python -m src.processing.bronze_to_silver && \
uv run python -m src.processing.silver_to_gold && \
uv run python -m src.viz.build_site
```

## Visning

Åpne nettstedet lokalt:

```bash
python -m http.server 8000
```

Besøk deretter `http://localhost:8000/site/index.html` i nettleseren.

## Git-ignorering

Alle datafiler (`.json`, `.parquet`) ignoreres av Git, men mappestrukturen bevares gjennom `.gitkeep`-filer. Dette sikrer at prosjektet kan klones og kjøres uten at data-lagrene er fylt.

## Komponenter

### `src/config.py`
Sentral konfigurering med stier og miljøvariabler:
- `BRONZE_DIR`, `SILVER_DIR`, `GOLD_DIR`
- `SITE_DIR`, `ASSETS_DIR`
- Strava-autentisering

### `src/ingestion/`
Henter aktiviteter fra Strava API og lagrer som JSON og Parquet.

### `src/processing/`
Transformerer data gjennom lagene:
- Filtrerer ut løpinger
- Beregner avstander i km, tid i timer
- Aggregerer på ukebasis

### `src/viz/`
Bygger interaktiv HTML-visualisering med Chart.js.

## Lisens

MIT
