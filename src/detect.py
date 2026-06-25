from ingest import load_dataset, data_file_1, data_file_2
from constraints import *
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

dataset_03 = load_dataset(data_file_1)
dataset_04 = load_dataset(data_file_2)

tank_thresholds = calculate_tank_thresholds(dataset_03)
drop_thresholds = calculate_drop_thresholds(dataset_03)
hourly_baselines = calculate_hourly_baselines(dataset_03)

for reading in dataset_04:
    if dead_pump_with_flow(reading):
        reading.flag_r1 = True
        reading.flagged = True
    if running_pump_with_no_flow(reading):
        reading.flag_r2 = True
        reading.flagged = True
    if tank_level_too_high(reading, tank_thresholds):
        reading.flag_r4 = True
        reading.flagged = True

for i in range(1, len(dataset_04)):
    current = dataset_04[i]
    prev = dataset_04[i-1]
    if tank_dropping_too_fast(current, prev, drop_thresholds):
        current.flag_r3 = True
        current.flagged = True

for reading in dataset_04:
    if tank_level_hourly_anomaly(reading, hourly_baselines):
        reading.flag_r6 = True
        reading.flagged = True

for reading in dataset_04:
    if multi_sensor_coorelation_anomaly(reading):
        reading.flag_r5 = True
        reading.flagged = True

for reading in dataset_04:
    if reading.flagged == True:
        cursor.execute("UPDATE sensor_readings SET detected = 1, flag_r6 = %s WHERE datetime = %s",
        (1 if reading.flag_r6 else 0, reading.datetime)
)

conn.commit()