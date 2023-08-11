'''
This code extracts connectivity information and the nodal temperatures for all the abaqus steps at all time increments
'''
from odbAccess import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *
from textRepr import *
import time as wallTime
import numpy as np

#from performLinearInterpolation import performLinearInterpolation

def main():
    if len(sys.argv) != 5:
        text = """Four command line arguments are expected: \
                    \n\t(1) odbName with extension \
                    \n\t(2) Volumetric heat flux (typical units: J/(m^3-sec)) \
                    \n\t(3) Frame increment Number \
                    \n\t(4) Nickel element set name """
        raise RuntimeError(text)
        
    # Settings
    odbName = str(sys.argv[1])
    volumetricHeatFlux = float(sys.argv[2])
    frameNoInc = int(sys.argv[3])
    elementSetName_Nickel = str(sys.argv[4]).upper()
    
    # extract these from the odb
    odb = openOdb(path = odbName)
    stepName = odb.steps.keys(0)  # 0 indicates first step (for ex. a static step)
    densityTableObject_Nickel = odb.materials['NICKEL'].density.table
    npArrayTemperatures_Nickel = np.array([])
    npArrayDensities_Nickel = np.array([])
    for ii in range(0,len(densityTableObject_Nickel)):
        npArrayTemperatures_Nickel = np.append(npArrayTemperatures_Nickel,densityTableObject_Nickel[ii][1])
        npArrayDensities_Nickel = np.append(npArrayDensities_Nickel,densityTableObject_Nickel[ii][0])
            
    densityTableObject_WC = odb.materials['TUNGSTEN_CARBIDE'].density.table
    npArrayTemperatures_WC = np.array([])
    npArrayDensities_WC = np.array([])
    for ii in range(0,len(densityTableObject_WC)):
        npArrayTemperatures_WC = np.append(npArrayTemperatures_WC,densityTableObject_WC[ii][1])
        npArrayDensities_WC = np.append(npArrayDensities_WC,densityTableObject_WC[ii][0])
        
    instanceName = odb.rootAssembly.instances.keys(0) # 0 indicates first instance
    stepObject = odb.steps[stepName[0]]
    assembly = odb.rootAssembly
    elType = assembly.instances[instanceName[0]].elements[0].type
    totalNoFrames = len(stepObject.frames)
    totalTimeSteps = totalNoFrames - 1
    print('Element Type: ',str(elType))    
    
    # loop over all elements and assign material names for later use
    odbObjectAllElements = assembly.instances[instanceName[0]]
    nElements = len(odbObjectAllElements.elements)
    odbObjectNickel = assembly.instances[instanceName[0]].elementSets[elementSetName_Nickel]
    dict_elementMaterialPairs = {}

    for jElement in odbObjectNickel.elements:
        dict_elementMaterialPairs[jElement.label] = 'NICKEL'    # un-assigned elements are of WC material type
    
    # open files for writing stresses and nodal disp for extensometer region
    outputFileSpecificHeatEffective = open('homogenizedSpecificHeat.out','w')
    outputFileSpecificHeatEffective.write("{0:35s}{1:35s}{2:35s}{3:35s}{4:35s}{5:75s}{6:35s}\n".format('time','volumeFractionNickel','volumeFractionWC','homogenizedDensity','InitialTemp','volumetricTemperature(**should be close to initial temp)','homogenizedSpecificHeat'))

    frameNosToExport = range(0, totalNoFrames-1, frameNoInc)
    frameNosToExport.append(totalNoFrames-1)  # this ensures that the last time step is always exported
    
    start = wallTime.clock()
    for frameNumber in frameNosToExport:
        frameData = stepObject.frames[frameNumber]
        time = frameData.frameValue

        elementIPVolumeObject = frameData.fieldOutputs['IVOL']
        elementIPVolumeFieldValues = elementIPVolumeObject.values
        elementTempObject = frameData.fieldOutputs['TEMP']
        elementTempFieldValues = elementTempObject.values
        elementHeatFluxObject = frameData.fieldOutputs['HFL']
        elementHeatFluxFieldValues = elementHeatFluxObject.values
    
        totalVolume = 0
        volumetricTemp = 0
        volumetricHeatFlux_1 = 0
        volumetricHeatFlux_2 = 0
        volumetricHeatFlux_3 = 0
        
        if frameNumber == 0:
            volumetricTemp_initial = 0
            for iVol, iTemp in zip(elementIPVolumeFieldValues,elementTempFieldValues):
                volumeIP = iVol.data
                totalVolume = totalVolume + volumeIP
                volumetricTemp_initial = volumetricTemp_initial + iTemp.data*volumeIP
                    
            volumetricTemp_initial = volumetricTemp_initial/totalVolume
            
            print('volumetricTemp_initial:',volumetricTemp_initial)
            
            density_Nickel_interpolated = performLinearInterpolation(npArrayTemperatures_Nickel,npArrayDensities_Nickel,volumetricTemp_initial)
            print('density_Nickel_interpolated:',density_Nickel_interpolated)
            
            density_WC_interpolated = performLinearInterpolation(npArrayTemperatures_WC,npArrayDensities_WC,volumetricTemp_initial)
            print('density_WC_interpolated:',density_WC_interpolated)
            #    
            volumetricDensity = 0
            volumeNickel = 0
            volumeWC = 0
            for iVol in elementIPVolumeFieldValues:
                elementNumber = iVol.elementLabel
                #material_name = str(assembly.instances[instanceName[0]].elements[elementNumber-1].sectionCategory).split("<")[1].split(">")[0].strip() <--- does not work as abaqus has a bug in getting correct material/section combinations
                volumeIP = iVol.data
                if elementNumber in dict_elementMaterialPairs:
                    volumeNickel = volumeNickel + volumeIP
                else:
                    volumeWC = volumeWC + volumeIP
            
            volumetricDensity = (density_Nickel_interpolated*volumeNickel + density_WC_interpolated*volumeWC)/totalVolume
            volumeFractionNickel = volumeNickel/totalVolume
            volumeFractionWC = volumeWC/totalVolume
            
        else:
            for iVol, iTemp, iHeatFlux in zip(elementIPVolumeFieldValues,elementTempFieldValues,elementHeatFluxFieldValues):
                volumeIP = iVol.data
                totalVolume = totalVolume + volumeIP
                volumetricTemp = volumetricTemp + iTemp.data*volumeIP
                volumetricHeatFlux_1 = volumetricHeatFlux_1 + iHeatFlux.data[0]*volumeIP
                volumetricHeatFlux_2 = volumetricHeatFlux_2 + iHeatFlux.data[1]*volumeIP
                volumetricHeatFlux_3 = volumetricHeatFlux_3 + iHeatFlux.data[2]*volumeIP
                
            volumetricTemp = volumetricTemp/totalVolume
            dT_dt_macroscopic = (volumetricTemp - volumetricTemp_initial)/time
            specificHeat = volumetricHeatFlux/(dT_dt_macroscopic*volumetricDensity)
            volumetricHeatFlux_1 = -volumetricHeatFlux_1/totalVolume
            volumetricHeatFlux_2 = -volumetricHeatFlux_2/totalVolume
            volumetricHeatFlux_3 = -volumetricHeatFlux_3/totalVolume
            
            print('data:',time,volumeFractionNickel,volumeFractionWC,volumetricDensity,volumetricTemp_initial,volumetricTemp,specificHeat)
            outputFileSpecificHeatEffective.write("{0:25.10f}{1:25.10f}{2:25.10f}{3:25.10f}{4:25.10f}{5:25.10f}{6:25.10f}\n".format(time,volumeFractionNickel,volumeFractionWC,volumetricDensity,volumetricTemp_initial,volumetricTemp,specificHeat))
        
    outputFileSpecificHeatEffective.close()
    odb.close()
    end = wallTime.clock()
    print("Time Taken: ",(end-start), "seconds\n")
    
def performLinearInterpolation(npArrayXref,npArrayYref,xTarget):
    if len(npArrayXref) != len(npArrayYref):
        raise RuntimeError('Length of numpy arrays X and Y must be same for linear interpolation')
    
    eps = abs(1E-10*min(npArrayXref))
    
    sorted_indices = np.argsort(npArrayXref)
    listXref_sorted = [npArrayXref[ii] for ii in sorted_indices]
    listYref_sorted = [npArrayYref[ii] for ii in sorted_indices]
    
    if xTarget <= listXref_sorted[0]:
        return listYref_sorted[0]
    elif xTarget >= listXref_sorted[len(listXref_sorted)-1]:
        return listYref_sorted[len(listXref_sorted)-1]
    else:    
        for ii in range(0,len(listXref_sorted)):
            if xTarget >= listXref_sorted[ii]:
                index_lower = ii
                break
        for jj in range(0,len(listXref_sorted)):                
            if xTarget < listXref_sorted[jj]:
                index_upper = jj
                break
        numerator = listYref_sorted[index_upper] - listYref_sorted[index_lower]
        denominator = listXref_sorted[index_upper] - listXref_sorted[index_lower] + eps
        
        yTarget = listYref_sorted[index_lower] + (numerator/denominator)*(xTarget-listXref_sorted[index_lower])
    
        return yTarget    
    
if __name__ == "__main__":
    main()    