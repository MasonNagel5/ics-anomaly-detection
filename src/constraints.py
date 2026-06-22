def dead_pump_with_flow(state, flow):
    if state == 0 and flow > 0.5:
        return True

def running_pump_with_no_flow(state, flow):
    if state == 1 and flow < 0.5:
        return True
def tank_dropping_too_fast():
    # this requires finding the max legit drop rate from the normal data.
    return True

def tank_level_too_high():
    # this requires finding the max legit tank level from the normal data.
    return True

def multi_sensor_coorelation_anomaly(sensor1, sensor2):
    #If two related sensors are simultaneously anomalous, that is a stronger signal
    if sensor1.anomalous() and sensor2.anomalous():
        return True # this means coorelated