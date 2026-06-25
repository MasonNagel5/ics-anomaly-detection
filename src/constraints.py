
def dead_pump_with_flow(pump_state_sensor, flow_sensor):
    if pump_state_sensor.value == 0 and flow_sensor.value > 0.5:
        return True

def running_pump_with_no_flow(pump_state_sensor, flow_sensor):
    if pump_state_sensor.value == 1 and flow_sensor.value < 0.5:
        return True
def tank_dropping_too_fast():
    # this requires finding the max legit drop rate from the normal data.
    return True

def tank_level_too_high(reading, thresholds):
    for tank_id, level in reading.tanks.items():
        if level > thresholds[tank_id]:
            return True
    return False

def multi_sensor_coorelation_anomaly(sensor):
    flags = [sensor.flag_r1, sensor.flag_r2, sensor.flag_r3, sensor.flag_r4]
    return sum(flags) >= 2 # Sum sees the bools as 1 or 0, so if 2 or more are true that means that there are 2 anomalies detected


############## Helper functions  ##############
def calculate_tank_thresholds(dataset):
    thresholds = {"T1": 0, "T2": 0, "T3": 0, "T4": 0, "T5": 0, "T6": 0, "T7": 0}
    
    for reading in dataset:
        if reading.att_flag == 0:
            for tank_id, level in reading.tanks.items():
                if level > thresholds[tank_id]:
                    thresholds[tank_id] = level
    
    return thresholds

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
