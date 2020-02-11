import csv
import xml.dom.minidom
import sys

def extractCoord(row):
  # This extracts the gps co-ordinates from a row and returns it as a string. This requires knowing
  # ahead of time what the columns are that hold the co-ordinate information.
  return '%s,%s' % (row['Longitude'], row['Latitude'])
  
#def createStylemap (row):
# This creates the style element the Placemark uses to determine its image icon.
# There are presently 8 different icons to represent the different types of generators,
# i.e. coal, solar, wind, hydro, bioenergy, gas, geothermal, other
#styleMapElement = kmlDoc.createElement('StyleMap')

def create_style(kmlDoc, style_id, icon_href):
  # Create a new style for different placemark icons.
  styleElement = kmlDoc.createElement('Style')
  styleElement.setAttribute('id', style_id)
  icon_style = kmlDoc.createElement('IconStyle')
  styleElement.appendChild(icon_style)
  icon = kmlDoc.createElement('Icon')
  icon_style.appendChild(icon)
  href = kmlDoc.createElement('href')
  icon.appendChild(href)
  href_text = kmlDoc.createTextNode(icon_href)
  href.appendChild(href_text)
  return styleElement
  
def createFolder(kmlDoc, foldername):
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

def createPlacemark(kmlDoc, row, order):
  # This creates a  element for a row of data.
  # A row is a dict.
  placemarkElement = kmlDoc.createElement('Placemark')
  
  # set the visibility to off (0) as the default is on
  visibilityElement = kmlDoc.createElement('visibility')
  placemarkElement.appendChild(visibilityElement)
  visibilityValue = kmlDoc.createTextNode('0')
  visibilityElement.appendChild(visibilityValue)
  
  # create the Extended Data container and append to the Placemark instance 'placemarkElement'
  extElement = kmlDoc.createElement('ExtendedData')
  placemarkElement.appendChild(extElement)
  
  # create the name element 'nameElement';
  # create a 'nameText' element and populate it with the name text from the row with the key 'Name';
  # append the 'nameText' element (containing the name text from the row) to 'nameElement';
  # append 'nameElement' to 'placemarkElement'
  nameElement = kmlDoc.createElement('name')
  nameText = kmlDoc.createTextNode(row['Name'])
  nameElement.appendChild(nameText)
  placemarkElement.appendChild(nameElement)

  # Loop through the columns and create a  element for every field that has a value.
  for key in order:
    if row[key]:
      dataElement = kmlDoc.createElement('Data')
      dataElement.setAttribute('name', key)
      valueElement = kmlDoc.createElement('value')
      dataElement.appendChild(valueElement)
      valueText = kmlDoc.createTextNode(row[key])
      valueElement.appendChild(valueText)
      extElement.appendChild(dataElement)
  
  
  # create a styleURL tag with the value from the row with the key 'Gen_Type'
  style_url = kmlDoc.createElement("styleUrl")
  placemarkElement.appendChild(style_url)
  style_url_text = kmlDoc.createTextNode(row.get('Gen_Type','none'))
  style_url.appendChild(style_url_text)
  
  pointElement = kmlDoc.createElement('Point')
  placemarkElement.appendChild(pointElement)
  coordinates = extractCoord(row)
  coorElement = kmlDoc.createElement('coordinates')
  coorElement.appendChild(kmlDoc.createTextNode(coordinates))
  pointElement.appendChild(coorElement)
  return placemarkElement

def createKML(csvReader, fileName, order):
  # This constructs the KML document from the CSV file.
  kmlDoc = xml.dom.minidom.Document()
  
  kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2', 'kml')
  kmlElement.setAttribute('xmlns','http://earth.google.com/kml/2.2')
  kmlElement = kmlDoc.appendChild(kmlElement)
  documentElement = kmlDoc.createElement('Document')
  documentElement = kmlElement.appendChild(documentElement)
  
  # create the style IDs for each icon by calling the 'create_style' function; 
  # this allows future sytle changes or additions easily
  
  style = create_style(kmlDoc, 'Bioenergy', 'icons/bioenergy.png')
  documentElement.appendChild(style)
  
  style = create_style(kmlDoc, 'Coal', 'icons/coal.png')
  documentElement.appendChild(style)
    
  style = create_style(kmlDoc, 'Gas', 'icons/gas.png')
  documentElement.appendChild(style)
 	
  style = create_style(kmlDoc, 'Geothermal', 'icons/geothermal.png')
  documentElement.appendChild(style)
  
  style = create_style(kmlDoc, 'Hydro', 'icons/hydro.png')
  documentElement.appendChild(style)
 	
  style = create_style(kmlDoc, 'Pumped hydro', 'icons/hydro.png')
  documentElement.appendChild(style)

  style = create_style(kmlDoc, 'Other', 'icons/other.png')
  documentElement.appendChild(style)
  
  style = create_style(kmlDoc, 'Solar PV', 'icons/solar.png')
  documentElement.appendChild(style)

  style = create_style(kmlDoc, 'Solar', 'icons/solar.png')
  documentElement.appendChild(style)
  
  style = create_style(kmlDoc, 'Wind', 'icons/wind.png')
  documentElement.appendChild(style)

  style = create_style(kmlDoc, 'Battery', 'icons/battery.png')
  documentElement.appendChild(style)
  
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
    
    foo = row.get('Committed')

    if foo == 'Yes':
      parentFolder2.appendChild(placemarkElement)
    else: parentFolder1.appendChild(placemarkElement)
	
  kmlFile = open(fileName, 'w')
  kmlFile.write(kmlDoc.toprettyxml(indent = '  '))

def main():
  # This reader opens up 'google-addresses.csv', which should be replaced with your own file you want to open.
  # In this instance it is 'Test_GE_Layer.csv'.
  # It creates a KML file called 'google.kml', or whatever you choose to name it (here it is 'doc.kml').
  
  # If an argument was passed to the script, it splits the argument on a comma
  # and uses the resulting list to specify an order for when columns get added.
  # Otherwise, it defaults to the order used in the sample.
  
  if len(sys.argv) >1: order = sys.argv[1].split(',')
  else: order = ['Name','Proponent','WR','Connect_Voltage','NCP','Capacity_MW','Gen_Type','Committed','Connect_Status','Yr_Commissioned','OEM','SCR','Sponsor','Latitude','Longitude','GPS']
  #                         file                       fieldnames
  csvreader = csv.DictReader(open('generators_GE.csv'),order)  # creates a dictionary with {order: cell} pairing
  kml = createKML(csvreader, 'generators_GE.kml', order)


if __name__ == '__main__':
  main()
