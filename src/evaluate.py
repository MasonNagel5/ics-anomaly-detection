import psycopg2
from dotenv import load_dotenv
import os
import csv
from pathlib import Path
load_dotenv()

from datetime import datetime

alerts_file = Path(__file__).resolve().parents[1] / "output" / "alerts.csv"


conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()


attack_windows = [
    ("13/09/16 23", "16/09/16 00"),
    ("26/09/16 11", "27/09/16 10"),
    ("09/10/16 09", "11/10/16 20"),
    ("29/10/16 19", "02/11/16 16"),
    ("26/11/16 17", "29/11/16 04"),
    ("06/12/16 07", "10/12/16 04"),
    ("14/12/16 15", "19/12/16 04"),
]

cursor.execute("SELECT datetime FROM sensor_readings WHERE detected = 1")
flagged_datetimes = cursor.fetchall()

true_positives = 0
false_positives = 0

# Need to convert my dates to datetimes
for window in flagged_datetimes:
    flagged_dt = datetime.strptime(window[0], "%d/%m/%y %H")
    for dt in attack_windows:
        start = datetime.strptime(dt[0], "%d/%m/%y %H")
        end = datetime.strptime(dt[1], "%d/%m/%y %H")
        if start <= flagged_dt <= end:
            true_positives += 1
            break
    else:
        false_positives += 1

print(f"True positives: {true_positives}")
print(f"False positives: {false_positives}")
print(f"Total flagged: {true_positives + false_positives}")

events_detected = 0

for dt in attack_windows:
    start = datetime.strptime(dt[0], "%d/%m/%y %H")
    end = datetime.strptime(dt[1], "%d/%m/%y %H")
    for window in flagged_datetimes:
        flagged_dt = datetime.strptime(window[0], "%d/%m/%y %H")
        if start <= flagged_dt <= end:
            events_detected += 1
            break

print(f"Attack events detected: {events_detected} / 7")

with alerts_file.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["datetime", "classification"])
    for window in flagged_datetimes:
        flagged_dt = datetime.strptime(window[0], "%d/%m/%y %H")
        label = "FP"
        for dt in attack_windows:
            start = datetime.strptime(dt[0], "%d/%m/%y %H")
            end = datetime.strptime(dt[1], "%d/%m/%y %H")
            if start <= flagged_dt <= end:
                label = "TP"
                break
        writer.writerow([window[0], label])