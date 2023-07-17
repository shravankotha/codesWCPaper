'''
This code extracts connectivity information and the nodal temperatures for all the abaqus steps at all time increments
'''
from odbAccess import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *
from textRepr import *
import time as wallTime

if len(sys.argv) != 6:
   text = """Five command line arguments are expected: \
            \n\t(1) odbName with extension \
            \n\t(2) output directory path \
            \n\t(3) direction of the thermal gradient applied (X/Y/Z) \
            \n\t(4) different in surface heat flux applied along the above direction (J/(m^2-sec)) \
            \n\t(5) frame increment Number"""
   raise RuntimeError(text)
    
# Settings
odbName = str(sys.argv[1])
outputPath = sys.argv[2]
directionGradientApplied = str(sys.argv[3])
appliedResultantHeatFlux = float(sys.argv[4])
frameNoInc = int(sys.argv[5])             # useful if no of frames are too large - first and last frames are always exported

# extract these from the odb
odb=openOdb(path=odbName)
stepName=odb.steps.keys(0)  # 0 indicates first step (for ex. a static step)
instanceName=odb.rootAssembly.instances.keys(0) # 0 indicates first instance
stepObject=odb.steps[stepName[0]]
assembly = odb.rootAssembly
elType=assembly.instances[instanceName[0]].elements[0].type
print('Element Type: ',str(elType))    
   
# open files for writing stresses and nodal disp for extensometer region
outputFileSpecificHeatEffective=open('effectiveSpecificHeat.out','w')

totalNoFrames=len(stepObject.frames) 
totalTimeSteps=totalNoFrames-1  

start = wallTime.clock()

time_old = 0
volumetricTemp_old = 0
volumetricHeatFlux_1_old = 0
for frameNumber in range(1,totalNoFrames):
    # get frame data and print time to both the files
    frameData = stepObject.frames[frameNumber]
    time=frameData.frameValue
    print('Frame Number : ',frameNumber,'   Time : ',time)
   
    elementIPVolumeObject = frameData.fieldOutputs['IVOL']
    elementIPVolumeFieldValues = elementIPVolumeObject.values
    elementHeatFluxObject = frameData.fieldOutputs['HFL']
    elementHeatFluxFieldValues = elementHeatFluxObject.values
    elementGradTObject = frameData.fieldOutputs['GRADT']
    elementGradTFieldValues = elementGradTObject.values
    elementTempObject = frameData.fieldOutputs['TEMP']
    elementTempFieldValues = elementTempObject.values
    
    totalVolume = 0
    volumetricHeatFlux_1 = 0
    volumetricHeatFlux_2 = 0
    volumetricHeatFlux_3 = 0
    volumetricGradT_1 = 0
    volumetricGradT_2 = 0
    volumetricGradT_3 = 0
    volumetricTemp = 0
    for iVol, iHeatFlux, iGradT, iTemp in zip(elementIPVolumeFieldValues,elementHeatFluxFieldValues,elementGradTFieldValues,elementTempFieldValues):
        volumeIP = iVol.data
        totalVolume = totalVolume + volumeIP
        volumetricHeatFlux_1 = volumetricHeatFlux_1 + iHeatFlux.data[0]*volumeIP
        volumetricHeatFlux_2 = volumetricHeatFlux_2 + iHeatFlux.data[1]*volumeIP
        volumetricHeatFlux_3 = volumetricHeatFlux_3 + iHeatFlux.data[2]*volumeIP
        volumetricGradT_1 = volumetricGradT_1 + iGradT.data[0]*volumeIP
        volumetricGradT_2 = volumetricGradT_2 + iGradT.data[1]*volumeIP
        volumetricGradT_3 = volumetricGradT_3 + iGradT.data[2]*volumeIP
        volumetricTemp = volumetricTemp + iTemp.data*volumeIP
        
    volumetricHeatFlux_1 = volumetricHeatFlux_1/totalVolume
    volumetricHeatFlux_2 = volumetricHeatFlux_2/totalVolume
    volumetricHeatFlux_3 = volumetricHeatFlux_3/totalVolume    
    volumetricGradT_1 = volumetricGradT_1/totalVolume
    volumetricGradT_2 = volumetricGradT_2/totalVolume
    volumetricGradT_3 = volumetricGradT_3/totalVolume
    volumetricTemp = volumetricTemp/totalVolume
    
    dT_dt_macroscopic = (volumetricTemp - volumetricTemp_old)/(time - time_old)
   
    specificHeat = appliedResultantHeatFlux/dT_dt_macroscopic
    specificHeat_ = (volumetricHeatFlux_1-volumetricHeatFlux_1_old)/dT_dt_macroscopic
    
    time_old = time
    volumetricTemp_old = volumetricTemp
    volumetricHeatFlux_1_old = volumetricHeatFlux_1
    
    print('data:',time,volumetricHeatFlux_1,volumetricHeatFlux_2,volumetricHeatFlux_3,volumetricTemp,specificHeat,specificHeat_)
    
       
    #data = str(time) + '    ' + str(K1) + '    ' + str(K2) + '    ' + str(K3) + '\n'
    #outputFileSpecificHeatEffective.write(data)
    


outputFileSpecificHeatEffective.close()
odb.close()
end = wallTime.clock()

print("Time Taken: ",(end-start), "seconds\n")