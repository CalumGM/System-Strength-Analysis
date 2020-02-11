This program performs a Preliminary Impact Assessment study on all buses in the given model. 

The model must be set out in the a particular way in order for the script to run properly:
A folder with 'PIA' in the name must be placed in the study case folder (Study Cases.IntPrjFolder). If more than one of these folders exists, the script
will automatically choose the first folder in the directory, future expansions will allow for the selection of a folder in the case of multiple folders 
existing. The selected folder must contain two study cases, a case with only synchronous generation and a case with all generation. The order of these 
study cases is irrelevant, because the script filters the data by name. 

Only busbars are faulted in the current working version of the script. Junction nodes and other terminal elements could be included (i forgot why they werent though)

The short circuit calculation is based on the following assumptions:
- c factor = 1
- fault method = IEC60909
- fault location = all buses

The radius of the circles is given as a script input in powerfactory, set as 100km my default. 

Execute kml_info.py in the desired PowerFactory model, the output will be a .kml file and a csv containing the names and coordinates of the placemarkers