import sys
# Python PowerFactory API
import powerfactory as pf
import numpy as np
import pandas as pd
import xml.dom.minidom
from bokeh.plotting import figure, show, output_file
import math
from bus import Busbar
from datetime import datetime

# Ergon Energy Helper Functions for Logging
sys.path.append(r'\\Ecasd01\WksMgmt\PowerFactory\Scripts\pfTextOutputs')
import pftextoutputs
# Ergon Energy Helper Functions for lots of stuff, inc Ecorp ID extraction
sys.path.append(r'\\Ecasd01\WksMgmt\PowerFactory\ScriptsDEV\pfSharedFunctions')
import pfsharedfunctions as pfsf

#import CSV
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

def extractCoord(row):
    '''
    Extracts the gps co-ordinates from a row and returns it as a string. This requires knowing
    ahead of time what the columns are that hold the co-ordinate information.
    '''
    return '%s,%s' % (row['Longitude'], row['Latitude'])


def createPlacemark(kmlDoc, row, order):
    '''
    Creates a placemark element in the kml file for each substation read in from the csv. 
    '''
    placemarkElement = kmlDoc.createElement('Placemark')  # tag containing all the information about a placemark

    # set the visibility to 1 (on)
    visibilityElement = kmlDoc.createElement('visibility')
    placemarkElement.appendChild(visibilityElement)
    visibilityValue = kmlDoc.createTextNode('1')
    visibilityElement.appendChild(visibilityValue)

    # create the Extended Data container and append to the Placemark instance 'placemarkElement'
    extElement = kmlDoc.createElement('ExtendedData')
    placemarkElement.appendChild(extElement)  # appendChild is a way of oragnising the data (see the .kml file for this)

    nameElement = kmlDoc.createElement('name')  # create the name element 'nameElement'
    nameText = kmlDoc.createTextNode(row['Name'])  # create a 'nameText' element and populate it with the name text from the row with the key 'Name'
    nameElement.appendChild(nameText)  # append the 'nameText' element (containing the name text from the row) to 'nameElement'
    placemarkElement.appendChild(nameElement)  # append 'nameElement' to 'placemarkElement'

    # Loop through the columns and create an element for every field that has a value.
    for key in order:  # order is the list of column headers
        if row[key]:
            dataElement = kmlDoc.createElement('Data')
            dataElement.setAttribute('name', key)
            valueElement = kmlDoc.createElement('value')
            dataElement.appendChild(valueElement)
            valueText = kmlDoc.createTextNode(row[key])
            valueElement.appendChild(valueText)
            extElement.appendChild(dataElement)

    pointElement = kmlDoc.createElement('Point')  # coordinates must be stored in a 'point' element
    placemarkElement.appendChild(pointElement)
    coordinates = extractCoord(row)
    coorElement = kmlDoc.createElement('coordinates')  # where the geographical coordinates are stored
    coorElement.appendChild(kmlDoc.createTextNode(coordinates))
    pointElement.appendChild(coorElement)
    return placemarkElement


def createFolder(kmlDoc, foldername):
    '''
    Adds appropriate placemarks to folders
    '''
    folderElement = kmlDoc.createElement('Folder')
    folderElement.setAttribute('id', foldername)
    nameElement = kmlDoc.createElement('name')
    nameText = kmlDoc.createTextNode(foldername)
    nameElement.appendChild(nameText)
    folderElement.appendChild(nameElement)
    # set the visibility to off (0) as the default is on
    visibilityElement = kmlDoc.createElement('visibility')
    folderElement.appendChild(visibilityElement)
    visibilityValue = kmlDoc.createTextNode('0')
    visibilityElement.appendChild(visibilityValue)
    return folderElement


def create_circle_placemark(kmlDoc, sub_coords, app):
    '''
    Generates the kml placemarker for a circle around a substation. Circle has 100km radius and is made up of 1km line segments
    '''
    coordinates = ''
    for theta in range(629):  # iterate through values of theta to trace a circle around the origin (sub_coords)
        if app.GetCurrentScript().circle_radius is None:
            radius = 100
        else:
            radius = app.GetCurrentScript().circle_radius
        const = radius * (1/111)
        x = float(sub_coords[0]) + const*math.cos(theta/100)  # radius*1/111*sin(theta) to approximately convert km to degrees
        y = float(sub_coords[1]) + const*math.sin(theta/100)
        coordinates = coordinates + str(x) + ',' + str(y) + ',' + '0 '  # format coordinates for kml 'x,y,z \n'
        # formula for this circle: (x-subcoords[0])^2 + (y-subcoords[1])^2 = 100^2

    placemarkElement = kmlDoc.createElement('Placemark')

    name_element = kmlDoc.createElement('name')
    name_value = kmlDoc.createTextNode('Circle Polygon')
    name_element.appendChild(name_value)
    placemarkElement.appendChild(name_element)

    style_element = kmlDoc.createElement('styleUrl')
    style_element_value = kmlDoc.createTextNode('#m_ylw-pushpin')
    style_element.appendChild(style_element_value)
    placemarkElement.appendChild(style_element)

    style_ID_element = kmlDoc.createElement('Style')

    polystyle_element = kmlDoc.createElement('PolyStyle')
    poly_color_element = kmlDoc.createElement('color')
    poly_color_element_value = kmlDoc.createTextNode('7fffffff')
    poly_color_element.appendChild(poly_color_element_value)
    polystyle_element.appendChild(poly_color_element)
    style_ID_element.appendChild(polystyle_element)

    linestyle_element = kmlDoc.createElement('LineStyle')
    line_color_element = kmlDoc.createElement('color')
    line_color_element_value = kmlDoc.createTextNode('00ffffff')
    line_color_element.appendChild(line_color_element_value)
    linestyle_element.appendChild(line_color_element)
    style_ID_element.appendChild(linestyle_element)

    placemarkElement.appendChild(style_ID_element)


    polygon_element = kmlDoc.createElement('Polygon')
    placemarkElement.appendChild(polygon_element)
    
    tessellate_element = kmlDoc.createElement('tessellate')
    tessellate_value = kmlDoc.createTextNode('1')
    tessellate_element.appendChild(tessellate_value)
    polygon_element.appendChild(tessellate_element)

    boundary_element = kmlDoc.createElement('outerBoundaryIs')
    polygon_element.appendChild(boundary_element)

    linear_ring_element = kmlDoc.createElement('LinearRing')
    boundary_element.appendChild(linear_ring_element)

    coordinates_element = kmlDoc.createElement('coordinates')
    coordinates_element_value = kmlDoc.createTextNode(coordinates)  # coordinate string for the circle (formatting above)
    coordinates_element.appendChild(coordinates_element_value)
    linear_ring_element.appendChild(coordinates_element)

    return placemarkElement


def createKML(csvReader, fileName, order, app):
    '''
    Constructs a KML file from the given csv
    '''
    kmlDoc = xml.dom.minidom.Document()
  
    kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2', 'kml')
    kmlElement.setAttribute('xmlns','http://earth.google.com/kml/2.2')
    kmlElement = kmlDoc.appendChild(kmlElement)
    documentElement = kmlDoc.createElement('Document')
    documentElement = kmlElement.appendChild(documentElement)

    # create the folder structure to sit under the document, i.e. uncommitted and committed
    # done by calling 'createFolder', and passing the Document ref and the name of the folder to be created
    # allows you to create however many folders here as you want
    folder1 = createFolder(kmlDoc, 'Uncommitted')
    documentElement.appendChild(folder1)

    folder2 = createFolder(kmlDoc, 'Committed')
    documentElement.appendChild(folder2)

    # Skip the header line.
    next(csvReader)

    for row in csvReader:
    #documentElement.appendChild(placemarkElement
	
	#if row.get('Committed','none') == 'Yes':
        parentFolder1 = documentElement.getElementsByTagName('Folder').item(0)
        parentFolder2 = kmlElement.getElementsByTagName('Folder').item(1)  
        placemarkElement = createPlacemark(kmlDoc, row, order)
        circle_placemark_element = create_circle_placemark(kmlDoc, extractCoord(row).split(','), app)
    
        foo = row.get('Committed')

        if foo == 'Yes':
            parentFolder2.appendChild(placemarkElement)
            parentFolder2.appendChild(circle_placemark_element)
        else: 
            parentFolder1.appendChild(placemarkElement)
            parentFolder1.appendChild(circle_placemark_element)
        
    kmlFile = open(fileName, 'w')
    kmlFile.write(kmlDoc.toprettyxml(indent = '  '))

def main(app, project):
    '''
    Calculates the AFL at each terminal element and creates the KML file for viewing
    '''
    app = pf.GetApplication()
    app.ClearOutputWindow()
    project = app.GetActiveProject()
    if project is None:
        logger.error("No Active Project or passed project, Ending Script")
        return
    
    current_script = app.GetCurrentScript()
    order = ['Name', 'Latitude', 'Longitude']
   
    study_case_folder = app.GetProjectFolder("study")

    current_time = datetime.datetime.now()
    dt_string = current_time.strftime("%d-%m-%Y %H-%M-%S")
    file_name =  'pia_results ' + dt_string

    # TODO: let the user pick the folder for PIA stuff
    base_case_PIA_summary = [case for case in study_case_folder.GetContents() if 'PIA' in case.loc_name][0].GetContents() 
    ElmTerms = app.GetCalcRelevantObjects('*.ElmTerm')
    buses = []  # list containing the bus objects from bus.py
    
    for bus in ElmTerms: # only use the first 10 buses for testing  
        try:
            if (bus.GPSlat != 0) or (bus.cpSubstat.GPSlat != 0):  # filter out the Powerlink ones with no GPS coordinates
                buses.append(Busbar(bus))
        except AttributeError:  # buses without a cpSubstat attribute will raise an AttributeError, these buses are still calc relevant
            if (bus.GPSlat != 0):
                buses.append(Busbar(bus))
    
    for study_case in base_case_PIA_summary:
        study_case.Activate()
        execute_short_circuit(app)  # calculate short circuit at every bus and junction node
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
    write_csv(app, buses, file_name + '.csv')
    
    csvreader = csv.DictReader(open(file_name + '.csv'),order)  # creates a dictionary with {column name: row[n]} pairing
    kml = createKML(csvreader, file_name + '.kml', order, app)


def execute_short_circuit(app, bus=None):
    '''
    Excecutes a short circuit study in the appropriate settings.
    If a bus object is passed in, it only calculates the fault at that particlar bus, this was primarily
    used for testing
    '''
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
    '''
    Writes the buses that will show up as circles in the csv file ready to be read by the create_kml function.
    Excludes duplicate locations
    '''
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
    '''
    Calculates the availible fault level for each bus, this data is stored in the bus object's attributes
    '''
    for bus in buses:
        bus.calculate_difference()  # result stored in bus.difference
        bus.calculate_AFL()     # result stored in bus.availible_fault_level
    return buses


if __name__ == '__main__':
    run_main()
