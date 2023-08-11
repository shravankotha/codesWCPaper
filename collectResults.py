'''
This code extracts connectivity information and the nodal temperatures for all the abaqus steps at all time increments
'''
import sys
import os
import numpy as np

if len(sys.argv) != 5:
   text = """Four command line arguments are expected: \
            \n\t(1) directory substring \
            \n\t(2) starting directory number \
            \n\t(3) ending directory number \
            \n\t(4) file name to extract the results from"""
   raise RuntimeError(text)
    
# Settings
directorySubstring = str(sys.argv[1])
startingDirectoryNumber = int(sys.argv[2])
endingDirectoryNumber = int(sys.argv[3])
nameFileToExtractTheResultsFrom = str(sys.argv[4])
pwd = os.getcwd()

outputFileResults = open('allResults_' + nameFileToExtractTheResultsFrom,'w')

count = 0
for iDir in range(startingDirectoryNumber,endingDirectoryNumber + 1):
    count = count + 1
    filePath = pwd + '\\' + directorySubstring + str(iDir) + '\\' + nameFileToExtractTheResultsFrom
    print('Collecting results from:',str(filePath))
    with open(filePath) as fileCurrent:
        data = fileCurrent.readlines()
        if count == 1:            
            outputFileResults.write(data[0])
        
        data_to_copy = data[len(data)-1]
        outputFileResults.write(data_to_copy)
        print(data_to_copy)
    fileCurrent.close()    