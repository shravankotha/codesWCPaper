'''
This code extracts connectivity information and the nodal temperatures for all the abaqus steps at all time increments
'''
from odbAccess import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *
from textRepr import *
import time as wallTime

if len(sys.argv) != 7:
   text = """Six command line arguments are expected: \
            \n\t(1) odbName with extension \
            \n\t(2) Output directory path \
            \n\t(3) Volumetric heat flux (J/(m^3-sec)) \
            \n\t(4) Initial temperature \
            \n\t(5) Homogenized density \
            \n\t(6) Frame increment Number"""
   raise RuntimeError(text)
    
# Settings
odbName = str(sys.argv[1])
outputPath = sys.argv[2]
volumetricHeatFlux = float(sys.argv[3])
volumetricTemp_initial = float(sys.argv[4])
density = float(sys.argv[5])
frameNoInc = int(sys.argv[6])             # useful if no of frames are too large - first and last frames are always exported

# extract these from the odb
odb=openOdb(path=odbName)
stepName=odb.steps.keys(0)  # 0 indicates first step (for ex. a static step)
instanceName=odb.rootAssembly.instances.keys(0) # 0 indicates first instance
stepObject=odb.steps[stepName[0]]
assembly = odb.rootAssembly
elType=assembly.instances[instanceName[0]].elements[0].type
print('Element Type: ',str(elType))    
totalNoFrames=len(stepObject.frames) 
totalTimeSteps=totalNoFrames-1     
   
# open files for writing stresses and nodal disp for extensometer region
outputFileSpecificHeatEffective=open('homogenizedSpecificHeat.out','w')
outputFileSpecificHeatEffective.write("{0:35s}{1:35s}{2:35s}{3:35s}{4:35s}\n".format('time','homogenizedDensity','InitialTemp','volumetricTemperature','homogenizedSpecificHeat'))

start = wallTime.clock()
for frameNumber in range(1,totalNoFrames):
    frameData = stepObject.frames[frameNumber]
    time=frameData.frameValue
   
    elementIPVolumeObject = frameData.fieldOutputs['IVOL']
    elementIPVolumeFieldValues = elementIPVolumeObject.values
    elementTempObject = frameData.fieldOutputs['TEMP']
    elementTempFieldValues = elementTempObject.values
    
    totalVolume = 0
    volumetricTemp = 0
    for iVol, iTemp in zip(elementIPVolumeFieldValues,elementTempFieldValues):
        volumeIP = iVol.data
        totalVolume = totalVolume + volumeIP
        volumetricTemp = volumetricTemp + iTemp.data*volumeIP
        
    volumetricTemp = volumetricTemp/totalVolume    
    dT_dt_macroscopic = (volumetricTemp - volumetricTemp_initial)/time
    specificHeat = volumetricHeatFlux/(dT_dt_macroscopic*density)
    
    print('data:',time,volumetricTemp,specificHeat)        
    outputFileSpecificHeatEffective.write("{0:25.10f}{1:25.10f}{2:25.10f}{3:25.10f}{4:25.10f}\n".format(time,density,volumetricTemp_initial,volumetricTemp,specificHeat))
    
outputFileSpecificHeatEffective.close()
odb.close()
end = wallTime.clock()
print("Time Taken: ",(end-start), "seconds\n")