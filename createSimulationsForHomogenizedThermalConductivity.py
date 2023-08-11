'''
This code creates the simulation directories and input files to compute effective thermal conductivity at different temperatures
'''
import sys
import os
import shutil
from replaceAstringInAFile import replaceAstringInAFile

def main():
    if len(sys.argv) != 7:
        text = """Six command line arguments are expected: \
                    \n\t(1) directory to look for reference input files \
                    \n\t(2) reference input file name \
                    \n\t(3) starting temperature for simulations\
                    \n\t(4) ending temperature for simulations \
                    \n\t(5) temperature increment \
                    \n\t(6) direction for applying thermal gradient (X/Y/Z)"""
        raise RuntimeError(text)
    
    source_dir_name = str(sys.argv[1])
    ref_inp_file_name = str(sys.argv[2])
    temperatureStart = float(sys.argv[3])
    temperatureEnd = float(sys.argv[4])
    incrementTemperature = float(sys.argv[5])
    directionThermalConductivity = str(sys.argv[6])
    pwd = os.getcwd()
    
    tolerance = 1E-3
    listTemperatures = []
    temperature = temperatureStart
    while temperature <= temperatureEnd:
        listTemperatures.append(temperature)
        temperature = temperature + incrementTemperature
    
    if abs(temperature-incrementTemperature-temperatureEnd) >= tolerance*incrementTemperature:
        listTemperatures.append(temperatureEnd)
    
    logFile = open('simulationInformation.log','w')
    for iTemperature in range(0,len(listTemperatures)):
        source_dir_path = str(source_dir_name)
        dest_dir_name = 'temperature_' + str(directionThermalConductivity) + '_' + str(iTemperature+1)
        dest_dir_path = str(pwd) + '\\' + str(dest_dir_name) + "\\"
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)
        
        print(source_dir_path)
        print(dest_dir_path)
        
        shutil.copytree(source_dir_path, dest_dir_path, dirs_exist_ok=True)        
        nameFile = dest_dir_path + '\\' + str(ref_inp_file_name)
        
        refDomainTemperature = listTemperatures[iTemperature]
        logFile.write("{0:50s}{1:10s}{2:30.15f}\n".format(dest_dir_name,directionThermalConductivity,refDomainTemperature))

        if directionThermalConductivity == "X":
            tempBoundary_negX = refDomainTemperature
            tempBoundary_posX = refDomainTemperature + 2.0
            tempBoundary_negY = refDomainTemperature
            tempBoundary_posY = refDomainTemperature
            tempBoundary_negZ = refDomainTemperature
            tempBoundary_posZ = refDomainTemperature
            print(tempBoundary_posX)
        elif directionThermalConductivity == "Y":
            tempBoundary_negX = refDomainTemperature
            tempBoundary_posX = refDomainTemperature
            tempBoundary_negY = refDomainTemperature
            tempBoundary_posY = refDomainTemperature + 2.0
            tempBoundary_negZ = refDomainTemperature
            tempBoundary_posZ = refDomainTemperature
        elif directionThermalConductivity == "Z":
            tempBoundary_negX = refDomainTemperature
            tempBoundary_posX = refDomainTemperature
            tempBoundary_negY = refDomainTemperature
            tempBoundary_posY = refDomainTemperature
            tempBoundary_negZ = refDomainTemperature
            tempBoundary_posZ = refDomainTemperature + 2.0
            
        success = replaceAstringInAFile(nameFile,"__initialTempDomain__",str(refDomainTemperature))
        success = replaceAstringInAFile(nameFile,"__tempBoundary_negX__",str(tempBoundary_negX))
        success = replaceAstringInAFile(nameFile,"__tempBoundary_posX__",str(tempBoundary_posX))
        success = replaceAstringInAFile(nameFile,"__tempBoundary_negY__",str(tempBoundary_negY))
        success = replaceAstringInAFile(nameFile,"__tempBoundary_posY__",str(tempBoundary_posY))
        success = replaceAstringInAFile(nameFile,"__tempBoundary_negZ__",str(tempBoundary_negZ))
        success = replaceAstringInAFile(nameFile,"__tempBoundary_posZ__",str(tempBoundary_posZ))
    
    logFile.close()
    
if __name__ == "__main__":
    main()