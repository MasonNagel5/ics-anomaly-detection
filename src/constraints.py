def dead_pump_with_flow(reading):
    for pump_id, data in reading.pumps.items():
        if data["status"] == 0 and data["flow"] > 0.5:
            return True
    return False

def running_pump_with_no_flow(reading):
    for pump_id, data in reading.pumps.items():
        if data["status"] == 1 and data["flow"] < 0.5:
            return True
    return False 
    
def tank_dropping_too_fast(current, prev, thresholds):
    for tank_id in current.tanks:
        drop = prev.tanks[tank_id] - current.tanks[tank_id]
        if drop > thresholds[tank_id]:
            return True
    return False
    

def tank_level_too_high(reading, thresholds):
    for tank_id, level in reading.tanks.items():
        if level > thresholds[tank_id]:
            return True
    return False

def calculate_hourly_baselines(dataset):
    buckets = {}
    for reading in dataset:
        if reading.att_flag == 0:
            hour = int(reading.datetime.split(" ")[1])
            if hour not in buckets:
                buckets[hour] = {tank_id: [] for tank_id in reading.tanks}
            for tank_id, level in reading.tanks.items():
                buckets[hour][tank_id].append(level)
    baselines = {}
    for hour, tanks in buckets.items():
        baselines[hour] = {}
        for tank_id, values in tanks.items():
            mean = sum(values) / len(values)
            std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
            baselines[hour][tank_id] = (mean, std)
    return baselines

def tank_level_hourly_anomaly(reading, baselines, k=3.1):
    hour = int(reading.datetime.split(" ")[1])
    for tank_id, level in reading.tanks.items():
        mean, std = baselines[hour][tank_id]
        # Flag if any tank level is more than k standard deviations from its expected level for this hour
        if std > 0 and abs(level - mean) > k * std:
            return True
    return False

def multi_sensor_coorelation_anomaly(sensor):
    flags = [sensor.flag_r1, sensor.flag_r2, sensor.flag_r3, sensor.flag_r4, sensor.flag_r6]
    return sum(flags) >= 2 # Sum sees the bools as 1 or 0, so if 2 or more are true that means that there are 2 anomalies detected


############## Helper functions  ##############

## These calculate threshold functions are for dynamically changing datasets

def calculate_tank_thresholds(dataset):
    thresholds = {"T1": 0, "T2": 0, "T3": 0, "T4": 0, "T5": 0, "T6": 0, "T7": 0}
    
    for reading in dataset:
        if reading.att_flag == 0:
            for tank_id, level in reading.tanks.items():
                if level > thresholds[tank_id]:
                    thresholds[tank_id] = level
    
    return thresholds

# Tracks the largest tank level drop between consecutive normal readings per tank
# Any drop exceeding this in the test data is flagged as abnormal
def calculate_drop_thresholds(dataset): 
    thresholds = {"T1": 0, "T2": 0, "T3": 0, "T4": 0, "T5": 0, "T6": 0, "T7": 0}
    for i in range (1, len(dataset)):
        current = dataset[i]
        prev = dataset[i-1]
        if current.att_flag == 0 and prev.att_flag == 0:
            for tank_id, level in current.tanks.items():    
                drop = prev.tanks[tank_id] - current.tanks[tank_id]
                if drop > thresholds[tank_id]:
                    thresholds[tank_id] = drop
    return thresholds
