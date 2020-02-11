import sys
# Python PowerFactory API
import powerfactory as pf
import numpy as np
import pandas as pd
from bokeh.plotting import figure, show, output_file
from bus import Busbar
from datetime import datetime
# Ergon Energy Helper Functions for Logging
sys.path.append(r'\\Ecasd01\WksMgmt\PowerFactory\Scripts\pfTextOutputs')
import pftextoutputs

# Ergon Energy Helper Functions for lots of stuff, inc Ecorp ID extraction
sys.path.append(r'\\Ecasd01\WksMgmt\PowerFactory\ScriptsDEV\pfSharedFunctions')
import pfsharedfunctions as pfsf

# import CSV
import csv

# Logging, A more efficient way to print
import logging

logger = logging.getLogger(__name__)

# Ergon Energy Helper Functions for getting members
sys.path.append(
    r"\\Ecasd01\WksMgmt\PowerFactory\ScriptsDEV\ShortPFScripts\PrintScripts\PrintPFObjectMembers"
)
import printPFObjectV2_descs as printmembers

import datetime

import os


def run_main():
    app = pf.GetApplication()
    app.ClearOutputWindow()

    start_stuff(app)


def start_stuff(app, project=None):
    """
    This function can be handed app and a project and do
    whatever is required. This allows it to be run by
    another script if required
    """
    with pftextoutputs.PowerFactoryLogging(
            pf_app=app,
            add_handler=True,
            handler_level=logging.DEBUG,
            logger_to_use=logger,
            formatter=pftextoutputs.PFFormatter(
                '%(module)s: Line: %(lineno)d: %(message)s'  # format for printing stuff to the console
            )
    ) as pflogger:
        main(app, project)


def main(app, project=None):
    """
    In Here is where you actually start doing stuff to the model.
    Iterate through stuff, call other functions. Etc.
    """
    project = app.GetActiveProject()
    if project is None:
        logger.error("No Active Project or passed project, Ending Script")
        return

    current_script = app.GetCurrentScript()
    study_case_folder = app.GetProjectFolder("study")

    current_time = datetime.datetime.now()
    dt_string = current_time.strftime("%d-%m-%Y %H-%M-%S")
    file_name =  'pia_results ' + dt_string + '.csv'

    # TODO: let the user pick the folder for PIA stuff
    base_case_PIA_summary = [case for case in study_case_folder.GetContents() if 'PIA' in case.loc_name][0].GetContents() 
    # TODO: check if length is greater than one then give the option to select if so
    ElmTerms = app.GetCalcRelevantObjects('*.ElmTerm')
    buses = []  # list containing the bus objects from bus.py
    
    for bus in ElmTerms: # only use the first 10 buses for testing  
        try:
            if (bus.GPSlat != 0) or (bus.cpSubstat.GPSlat != 0):  # filter out the Powerlink ones with no GPS coordinates
                buses.append(Busbar(bus))
        except AttributeError:
            if (bus.GPSlat != 0):
                buses.append(Busbar(bus))
    
    for study_case in base_case_PIA_summary:
        study_case.Activate()
        # put short circuit up here for final
        execute_short_circuit(app)  # short circuit calculation currently set up like this for testing 10 cases
        for bus in buses:
            try:
                Skss = str(bus.bus_obj.GetAttribute('m:Skss'))
                if 'Sync' in study_case.loc_name:
                    bus.sync_gens_only_MVA = float(Skss)
                elif 'All' in study_case.loc_name:
                    bus.all_gens_MVA = float(Skss)
            except AttributeError:
                logger.debug('bus: {} is removed from calculation'.format(bus.bus_obj))  # buses without a fault power loss get removed

    buses = write_bus_attributes(app, buses)
    write_csv(app, buses, file_name)


def execute_short_circuit(app, bus=None):
    if not bus:
        shc = app.GetFromStudyCase('ComShc')
        shc.iopt_asc = False  # dont show in output window
        shc.iopt_mde = 1  # 60909 method
        shc.iopt_allbus = 1  # fault at user's selection (2 for all buses, 1 for all buses and junctions)
        shc.cfac = 1  # user defined equivalent voltage source factor (this might have to be 1.1)
        shc.Execute()
    else:
        shc = app.GetFromStudyCase('ComShc')
        shc.iopt_asc = False
        shc.iopt_mde = 1  # 60909 method
        shc.iopt_allbus = 0 # fault at user's selection (2 for all buses)
        shc.shcobj = bus  # execute the short at this bus
        shc.cfac = 1  # user defined equivalent voltage source factor (this might have to be 1.1)
        shc.Execute()


def write_csv(app, buses, file_name):
    #TODO: remove duplicates
    with open(file_name, 'w') as results_file:
        results_file.write('Name,Lat,Long,Gen Type \n')
        seen = set()
        dupe_buses = [bus for bus in buses if bus.is_circle()]
        nondupe_buses = []

        logger.debug('Buses: {}'.format(nondupe_buses))
        for bus in dupe_buses:
            try:
                if bus.bus_obj.cpSubstat.loc_name not in seen:
                    seen.add(bus.bus_obj.cpSubstat.loc_name)
                    # results_file.write('{}V,{},{},{},{},{},{},\n'.format(bus.bus_obj.cpSubstat.loc_name + ' ' + str(bus.bus_obj.uknom), bus.bus_obj.cpSubstat.GPSlat, 
                    #                                                     bus.bus_obj.cpSubstat.GPSlon, bus.all_gens_MVA, bus.sync_gens_only_MVA, bus.availible_fault_level, bus.is_circle()))
                    results_file.write('{},{},{}\n'.format(bus.bus_obj.cpSubstat.loc_name + ' ' + str(bus.bus_obj.uknom), bus.bus_obj.cpSubstat.GPSlat, bus.bus_obj.cpSubstat.GPSlon))
            except AttributeError:
                if bus.bus_obj.loc_name not in seen:
                    seen.add(bus.bus_obj.loc_name)
                    # results_file.write('{}V,{},{},{},{},{},{},\n'.format(bus.bus_obj.loc_name + ' ' + str(bus.bus_obj.uknom), bus.bus_obj.GPSlat, bus.bus_obj.GPSlon, 
                    #                                                     bus.sync_gens_only_MVA, bus.all_gens_MVA, bus.availible_fault_level, bus.is_circle()))
                    results_file.write('{},{},{}\n'.format(bus.bus_obj.loc_name + ' ' + str(bus.bus_obj.uknom), bus.bus_obj.GPSlat, bus.bus_obj.GPSlon))                                                    


def write_bus_attributes(app, buses):
    for bus in buses:
        bus.calculate_difference()  # result stored in bus.difference
        bus.calculate_AFL()     # result stored in bus.availible_fault_level
    return buses


if __name__ == '__main__':
    run_main()
