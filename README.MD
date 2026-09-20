# AtlasWeather Pipeline

End-to-end data pipeline (Bronze -> Silver -> Gold) to track weather risk for logistics and delivery in Moroccan cities.

## Architecture

1. Bronze: Raw JSON files from Open-Meteo API saved per city in `bronze/`.
2. Silver: Cleaned data with proper types, merged with city details in `silver/data.csv`.
3. Gold: Weather categories and risk score (0 to 100) in `gold/data.csv`.
4. PostgreSQL: Tables `cities` and `weather_forecast` with upsert.
5. Streamlit: Simple dashboard to filter and view weather risks.
6. Airflow: Daily DAG to run the whole pipeline.

## Weather Risk Score (0 to 100)

The risk score helps logistics teams spot dangerous delivery conditions:

- Precipitation (`precipitation_sum`):
  - >= 20 mm: +30 points
  - >= 5 mm: +10 points
  - > 0 mm: +5 points
- Wind gusts (`wind_gusts_10m_max`):
  - >= 80 km/h: +20 points
  - >= 50 km/h: +12 points
  - >= 30 km/h: +4 points
- Max temperature (`temperature_2m_max`):
  - >= 45 C: +15 points
  - >= 38 C: +10 points
  - <= 0 C: +8 points
- Rain probability (`precipitation_probability_max`):
  - >= 70%: +10 points
  - >= 40%: +5 points
- Wind speed (`wind_speed_10m_max`):
  - >= 60 km/h: +25 points
  - >= 40 km/h: +15 points
  - >= 20 km/h: +5 points

Total score is capped at 100 (`min(score, 100)`).

Risk Levels:
- 0 to 19: Low
- 20 to 39: Medium
- 40 to 100: High

## How to Run

### 1. Setup environment

```bash
pip install -r requirements.txt
```

Make sure `.env` has:
```env
POSTGRES_USER=atlasweather
POSTGRES_PASSWORD=atlasweather123
POSTGRES_DB=atlasweather
POSTGRES_PORT=5432
DB_HOST=localhost
```

### 2. Start PostgreSQL

```bash
docker compose up -d postgres
```

### 3. Run Pipeline Scripts

```bash
python extraction/extract_weather.py
python transformation/transform_weather.py
python gold/gold.py
python load/loader.py
```

### 4. Run Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

Open `http://localhost:8501`.

### 5. Run with Docker Compose

To run postgres, streamlit and airflow together:

```bash
docker compose up -d
```

- Streamlit: `http://localhost:8501`
- Airflow: `http://localhost:8080`

## SQL Analysis

The file `sql/queries.sql` has 5 queries:
1. Cities with highest max temperatures.
2. Cities with highest precipitation.
3. Cities with highest average risk score.
4. Dates with maximal risk score.
5. For each city, the period with the highest risk score.