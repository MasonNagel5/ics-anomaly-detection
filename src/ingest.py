from pathlib import Path

import csv

from sensor_reading import SensorReading

DATA_FILENAME_1 = "BATADAL_dataset03.csv"
DATA_FILENAME_2 = "BATADAL_dataset04.csv"
DATA_FILENAME_3 = "BATADAL_test_dataset.csv"

dataset_03 = []
dataset_04 = []
test_dataset = []
# locate project root from this file to make sure dataset is found regardless of where the script is run from
data_file_1 = Path(__file__).resolve().parents[1] / "data" / DATA_FILENAME_1
data_file_2 = Path(__file__).resolve().parents[1] / "data" / DATA_FILENAME_2
data_file_3 = Path(__file__).resolve().parents[1] / "data" / DATA_FILENAME_3

if not data_file_1.exists():
    raise FileNotFoundError(f"Data file not found: {data_file_1}")

with data_file_1.open('r', newline='') as file:
    reader = csv.reader(file)
    header = next(reader)
    for row in reader:
        datetime = row[0]

        tanks = {
            "T1": float(row[1]), "T2": float(row[2]), "T3": float(row[3]),
            "T4": float(row[4]), "T5": float(row[5]), "T6": float(row[6]),
            "T7": float(row[7])
        }

        pumps = {
            "PU1":  {"flow": float(row[8]),  "status": int(float(row[9]))},
            "PU2":  {"flow": float(row[10]), "status": int(float(row[11]))},
            "PU3":  {"flow": float(row[12]), "status": int(float(row[13]))},
            "PU4":  {"flow": float(row[14]), "status": int(float(row[15]))},
            "PU5":  {"flow": float(row[16]), "status": int(float(row[17]))},
            "PU6":  {"flow": float(row[18]), "status": int(float(row[19]))},
            "PU7":  {"flow": float(row[20]), "status": int(float(row[21]))},
            "PU8":  {"flow": float(row[22]), "status": int(float(row[23]))},
            "PU9":  {"flow": float(row[24]), "status": int(float(row[25]))},
            "PU10": {"flow": float(row[26]), "status": int(float(row[27]))},
            "PU11": {"flow": float(row[28]), "status": int(float(row[29]))}
        }

        valve = {"flow": float(row[30]), "status": int(float(row[31]))} # fields such as 1.00 so we need float conversion and then int conversion

        pressures = {
            "J280": float(row[32]), "J269": float(row[33]), "J300": float(row[34]),
            "J256": float(row[35]), "J289": float(row[36]), "J415": float(row[37]),
            "J302": float(row[38]), "J306": float(row[39]), "J307": float(row[40]),
            "J317": float(row[41]), "J14":  float(row[42]), "J422": float(row[43])
        }

        att_flag = int(float(row[44]))

        sensor_reading = SensorReading(datetime, tanks, pumps, valve, pressures, att_flag)
        dataset_03.append(sensor_reading) # Populates an array with SensorReading objects, each one representing one row of the CSV
                                          # This allows for easier handling of the data later when we run our anomaly detection algorithms
