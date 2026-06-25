class SensorReading:
    def __init__(self, datetime, tanks, pumps, valve, pressures, att_flag):
        self.datetime = datetime
        self.tanks = tanks        # dict
        self.pumps = pumps        # dict
        self.valve = valve        # dict
        self.pressures = pressures  # dict
        self.att_flag = att_flag # BOOL flag 1 or 0
        
        # Flags for each of the 6 rules, initialized to FALSE
        self.flagged = False
        self.flag_r1 = False
        self.flag_r2 = False
        self.flag_r3 = False
        self.flag_r4 = False
        self.flag_r5 = False
        self.flag_r6 = False