class Busbar:
    def __init__(self, bus_obj=None, difference=0, sync_gens_only_MVA=0, all_gens_MVA=0,availible_fault_level=0):
        self.bus_obj = bus_obj
        self.difference = difference
        self.availible_fault_level = availible_fault_level
        self.sync_gens_only_MVA = sync_gens_only_MVA
        self.all_gens_MVA = all_gens_MVA

    def is_circle(self):
        return (float(self.availible_fault_level) < 0) and (float(self.availible_fault_level) > -10000000)

    # calculate AFL
    def calculate_AFL(self):
        self.availible_fault_level = float(self.sync_gens_only_MVA) - self.difference
    
    
    # calculate difference
    def calculate_difference(self):
        self.difference = float(self.all_gens_MVA) - float(self.sync_gens_only_MVA)


    def __str__(self):
        # AFL at loc_name = AFL --- circle = is_circle
        return 'AFL at {} = {} --- circle = {}'.format(self.bus_obj, self.availible_fault_level, self.is_circle())

