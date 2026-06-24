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
