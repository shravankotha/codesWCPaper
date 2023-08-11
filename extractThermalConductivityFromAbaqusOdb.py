'''
This code extracts connectivity information and the nodal temperatures for all the abaqus steps at all time increments
'''
from odbAccess import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *
from textRepr import *
import time as wallTime

if len(sys.argv) != 4:
   text = """Three command line arguments are expected: \
            \n\t(1) odbName with extension \
            \n\t(2) direction of the thermal gradient applied (X/Y/Z) \
            \n\t(3) frame increment Number"""
   raise RuntimeError(text)
    
# Settings
odbName = str(sys.argv[1])
directionGradientApplied = str(sys.argv[2]).upper()
frameNoInc = int(sys.argv[3])             # useful if no of frames are too large - first and last frames are always exported

# extract these from the odb
odb = openOdb(path = odbName)
stepName = odb.steps.keys(0)  # 0 indicates first step (for ex. a static step)
instanceName = odb.rootAssembly.instances.keys(0) # 0 indicates first instance
stepObject = odb.steps[stepName[0]]
assembly = odb.rootAssembly
elType = assembly.instances[instanceName[0]].elements[0].type
print('Element Type: ',str(elType))    
   
# open files for writing stresses and nodal disp for extensometer region
outputFileThermalConductivityEffective = open('homogenizedThermalConductivity.out','w')

if directionGradientApplied == "X":
    outputFileThermalConductivityEffective.write("{0:20s}{1:20s}{2:20s}{3:20s}{4:20s}{5:20s}\n".format('time','temperature','direction','<qx>/<GradT_x>','<qy>/<GradT_x>','qz/GradT_x>'))
elif  directionGradientApplied == "Y":
    outputFileThermalConductivityEffective.write("{0:20s}{1:20s}{2:20s}{3:20s}{4:20s}{5:20s}\n".format('time','temperature','direction','<qx>/<GradT_y>','<qy>/<GradT_y>','<qz>/<GradT_y>'))
elif  directionGradientApplied == "Z":
    outputFileThermalConductivityEffective.write("{0:20s}{1:20s}{2:20s}{3:20s}{4:20s}{5:20s}\n".format('time','temperature','direction','<qx>/<GradT_z>','<qy>/<GradT_z>','<qz>/<GradT_z>'))        
        
totalNoFrames = len(stepObject.frames) 
totalTimeSteps = totalNoFrames-1  

frameNosToExport = range(0, totalNoFrames-1, frameNoInc)
frameNosToExport.append(totalNoFrames-1)  # this ensures that the last time step is always exported

start = wallTime.clock()
for frameNumber in frameNosToExport:
    # get frame data and print time to both the files
    frameData = stepObject.frames[frameNumber]
    time = frameData.frameValue
    print 'Frame Number : ',frameNumber,'   Time : ',time
   
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
        
    volumetricHeatFlux_1 = -volumetricHeatFlux_1/totalVolume
    volumetricHeatFlux_2 = -volumetricHeatFlux_2/totalVolume
    volumetricHeatFlux_3 = -volumetricHeatFlux_3/totalVolume
    volumetricGradT_1 = volumetricGradT_1/totalVolume
    volumetricGradT_2 = volumetricGradT_2/totalVolume
    volumetricGradT_3 = volumetricGradT_3/totalVolume
    volumetricTemp = volumetricTemp/totalVolume
    
    #print('data:',totalVolume,volumetricHeatFlux_1,volumetricHeatFlux_2,volumetricHeatFlux_3,volumetricGradT_1,volumetricGradT_2,volumetricGradT_3)
    print('K_xx,K_xy,K_xz : ',volumetricHeatFlux_1/volumetricGradT_1,volumetricHeatFlux_1/volumetricGradT_2,volumetricHeatFlux_1/volumetricGradT_3)
    print('K_yx,K_yy,K_yz : ',volumetricHeatFlux_2/volumetricGradT_1,volumetricHeatFlux_2/volumetricGradT_2,volumetricHeatFlux_2/volumetricGradT_3)
    print('K_zx,K_zy,K_zz : ',volumetricHeatFlux_3/volumetricGradT_1,volumetricHeatFlux_3/volumetricGradT_2,volumetricHeatFlux_3/volumetricGradT_3)
    
    if directionGradientApplied == "X":
        K1 = volumetricHeatFlux_1/volumetricGradT_1 
        K2 = volumetricHeatFlux_2/volumetricGradT_1
        K3 = volumetricHeatFlux_3/volumetricGradT_1
    elif  directionGradientApplied == "Y":
        K1 = volumetricHeatFlux_1/volumetricGradT_2 
        K2 = volumetricHeatFlux_2/volumetricGradT_2
        K3 = volumetricHeatFlux_3/volumetricGradT_2
    elif  directionGradientApplied == "Z":
        K1 = volumetricHeatFlux_1/volumetricGradT_3
        K2 = volumetricHeatFlux_2/volumetricGradT_3
        K3 = volumetricHeatFlux_3/volumetricGradT_3
        
    outputFileThermalConductivityEffective.write("{0:30.15f}{1:30.15f}\t{2:20s}{3:30.15f}{4:30.15f}{5:30.15f}\n".format(time,volumetricTemp,str(directionGradientApplied),K1,K2,K3))
    
outputFileThermalConductivityEffective.close()       
odb.close()   
end = wallTime.clock()     

print "Time Taken for writing: ",(end-start), "seconds\n"