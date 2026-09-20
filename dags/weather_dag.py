from datetime import datetime, timedelta
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from airflow import DAG
from airflow.operators.python import PythonOperator

from extraction.extract_weather import main as run_extract
from transformation.transform_weather import main as run_transform
from gold.gold import main as run_gold
from load.loader import main as run_load

default_args = {
    "owner": "atlasweather",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="atlasweather_pipeline",
    default_args=default_args,
    description="Morocco weather risk pipeline",
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
) as dag:

    task_extract = PythonOperator(
        task_id="extract_weather_bronze",
        python_callable=run_extract,
    )

    task_transform = PythonOperator(
        task_id="transform_weather_silver",
        python_callable=run_transform,
    )

    task_gold = PythonOperator(
        task_id="feature_engineering_gold",
        python_callable=run_gold,
    )

    task_load = PythonOperator(
        task_id="load_to_postgres",
        python_callable=run_load,
    )

    task_extract >> task_transform >> task_gold >> task_load
