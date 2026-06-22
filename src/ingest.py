from pathlib import Path
import csv

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
        dataset_03.append(row) # Storing each row of the CSV file into the dataset03 list

if not data_file_2.exists():
    raise FileNotFoundError(f"Data file not found: {data_file_2}")

with data_file_2.open('r', newline='') as file:
    reader = csv.reader(file)
    header = next(reader)
    for row in reader:
        dataset_04.append(row) # Storing each row of the CSV file into the dataset04 list

if not data_file_3.exists():
    raise FileNotFoundError(f"Data file not found: {data_file_3}")

with data_file_3.open('r', newline='') as file:
    reader = csv.reader(file)
    header = next(reader)
    for row in reader:
        test_dataset.append(row) # Storing each row of the CSV file into the test_dataset list

