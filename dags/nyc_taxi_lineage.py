
import os
import requests
import pandas as pd
import psycopg2
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from openlineage.airflow import DAG as OpenLineageDAG
from openlineage.client.run import RunEvent, RunState, Run
from openlineage.client.transport import HttpTransport
import uuid

# OpenLineage Transport
transport = HttpTransport(url="http://localhost:5000")
run_id = str(uuid.uuid4())

# Dataset URL
DATASET_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"
LOCAL_FILE_PATH = "/tmp/nyc_taxi.parquet"
DB_CONN = "dbname=nyc_taxi user=airflow password=airflow host=localhost port=5432"

def send_openlineage_event(event_type, job_name):
    """Send OpenLineage event."""
    event = RunEvent(
        eventTime=datetime.utcnow().isoformat(),
        run=Run(runId=run_id),
        job=RunEvent.Job(
            namespace="default",
            name=job_name,
        ),
        eventType=event_type,
        producer="https://github.com/OpenLineage/OpenLineage",
    )
    transport.emit(event)

def extract_data():
    """Download dataset."""
    send_openlineage_event(RunState.START, "extract_data")
    response = requests.get(DATASET_URL)
    with open(LOCAL_FILE_PATH, "wb") as file:
        file.write(response.content)
    send_openlineage_event(RunState.COMPLETE, "extract_data")

def transform_data():
    """Clean data."""
    send_openlineage_event(RunState.START, "transform_data")
    df = pd.read_parquet(LOCAL_FILE_PATH)
    df = df[df["passenger_count"] > 0]
    df.to_parquet(LOCAL_FILE_PATH, index=False)
    send_openlineage_event(RunState.COMPLETE, "transform_data")

def load_data():
    """Load data into PostgreSQL."""
    send_openlineage_event(RunState.START, "load_data")
    conn = psycopg2.connect(DB_CONN)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nyc_taxi (
            id SERIAL PRIMARY KEY,
            pickup_time TIMESTAMP,
            dropoff_time TIMESTAMP,
            passenger_count INTEGER,
            trip_distance FLOAT,
            total_amount FLOAT
        )
    """)
    df = pd.read_parquet(LOCAL_FILE_PATH)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO nyc_taxi (pickup_time, dropoff_time, passenger_count, trip_distance, total_amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (row["tpep_pickup_datetime"], row["tpep_dropoff_datetime"], row["passenger_count"], row["trip_distance"], row["total_amount"]))
    conn.commit()
    cursor.close()
    conn.close()
    send_openlineage_event(RunState.COMPLETE, "load_data")

# Airflow Operators
extract_task = PythonOperator(task_id="extract", python_callable=extract_data, dag=dag)
transform_task = PythonOperator(task_id="transform", python_callable=transform_data, dag=dag)
load_task = PythonOperator(task_id="load", python_callable=load_data, dag=dag)

# Task Dependencies
extract_task >> transform_task >> load_task