import sys
# Python PowerFactory API
import powerfactory as pf
import numpy as np
import pandas as pd
from bokeh.plotting import figure, show, output_file

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

    base_case_PIA_summary = study_case_folder.GetContents()[3].GetContents()
    variations = app.GetProjectFolder('scheme').GetContents()[0].GetContents()
    ElmTerms = app.GetCalcRelevantObjects('*.ElmTerm')
    buses = [bus for bus in ElmTerms if bus.iUsage == 0][:10]  # filter out all the ElmTerms that arnt busbars
    base_results = []  # stores the results from each study case as different elements
    variation_results = []
    for study_case in base_case_PIA_summary:
        study_case.Activate()
        study_case_results = []  # the results from each individual study

        for bus in buses:
            execute_short_circuit(app, bus)  # short circuit calculation currently set up like this for testing 10 cases
            try:
                Skss = str(bus.GetAttribute('m:Skss'))
                name = bus
                study_case_results.append((name, Skss))
            except AttributeError:
                logger.debug('bus: {} is removed from calculation'.format(bus))
        base_results.append(study_case_results)

    logger.debug('Sync Gens: {}'.format(base_results[0]))
    logger.debug('All Gens: {}'.format(base_results[1]))
    

    # AFL = Syn gens - (All gens - Sync gens)
    # if AFL < 0, return loc_name and coordinates
    availible_fault_level = []
    difference = []
    for i in range(len(base_results[1])):
        bus_name = base_results[0][i][0]
        sync_gens_FL = float(base_results[0][i][1])
        all_gens_FL = float(base_results[1][i][1])
        difference.append(all_gens_FL - sync_gens_FL)
        availible_fault_level.append(sync_gens_FL - difference[i])

        logger.debug('AFL at {} = {} --- circle: {}'.format(bus_name, availible_fault_level[i], str(availible_fault_level[i] < 0)))

    with open('pia_results.csv', 'w') as results_file:
            results_file.write('Bus Name,Sync Gens,All Gens,Difference,AFL,Circle \n')
            for i in range(len(base_results[1])):
                #                   bus_name, Sync_gens, All_gens, Diff, AFL, Circle
                results_file.write('{},{},{},{},{},{}\n'.format(base_results[0][i][0].loc_name, base_results[0][i][1], base_results[1][i][1], difference[i], availible_fault_level[i], str(availible_fault_level[i] < 0)))

    
def execute_short_circuit(app, bus):
    shc = app.GetFromStudyCase('ComShc')
    shc.iopt_mde = 1  # 60909 method
    shc.iopt_allbus = 0  # fault at user's selection
    shc.shcobj = bus  # execute the short at this bus
    shc.cfac = 1  # user defined equivalent voltage source factor (this might have to be 1.1)
    shc.Execute()


if __name__ == '__main__':
    run_main()
