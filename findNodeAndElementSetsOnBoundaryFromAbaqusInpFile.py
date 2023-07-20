'''
This code parses the abaqus inp file to get nodes and elements connectivity
'''
import sys
import os
from parseAbqInpFileForNodalCoords import parseAbqFileForNodalCoordinates
from parseAbqInpFileForElementConnectivity import parseAbqFileForElementConnectivity
from findNodesAndElementsOnDomainBoundary import findNodesAndElementsOnDomainBoundary
from findDomainBoundaries import findDomainBoundaries
from writeElementSetsInAbaqusInpFormat import writeElementSetsInAbaqusInpFormat

def main():
    if len(sys.argv) != 2:
        text = """One command line arguments are expected: \
                    \n\t(1) Abaqus input file name including """
        raise RuntimeError(text)
    
    nameFile = str(sys.argv[1])
    nFacesElement = 4    
    pathFileOut = 'nodeAndElementSetsOnDomainBoundaries.inp'
    
    listNodeIDs, listNodalCoordinates = parseAbqFileForNodalCoordinates(nameFile)
    listElementIDs, listElementConnectivity = parseAbqFileForElementConnectivity(nameFile)
    listCoordMinDomainBoundary,listCoordMaxDomainBoundary = findDomainBoundaries(listNodeIDs, listNodalCoordinates)    
    listNamesElementSets, listElementsOnBoundaries, listNamesNodeSets, listNodesOnBoundaries = findNodesAndElementsOnDomainBoundary(listCoordMinDomainBoundary,listCoordMaxDomainBoundary,listElementIDs,listElementConnectivity,listNodalCoordinates,nFacesElement)    
    success = writeNodeSetsInAbaqusInpFormat(pathFileOut,listNamesNodeSets,listNodesOnBoundaries)
    success = writeElementSetsInAbaqusInpFormat(pathFileOut,listNamesElementSets,listElementsOnBoundaries)

def writeNodeSetsInAbaqusInpFormat(pathFileOut,listNamesNodeSets,listNodesOnBoundaries):
    success = False
    with open (pathFileOut,'w') as fileOut:
        for iBoundary in range(0,len(listNamesElementSets)):
            for iSurface in range(0,len(listNamesElementSets[0])):
                if listElementsOnBoundaries[iBoundary][iSurface] != []:
                    fileOut.write('*NSET, NSET=' + str(listNamesElementSets[iBoundary][iSurface]) + '\n')
                    str_to_write = '    '
                    for iElement in range(0,len(listElementsOnBoundaries[iBoundary][iSurface])):
                        if iElement == len(listElementsOnBoundaries[iBoundary][iSurface])-1:
                            str_to_write = str_to_write + str(listElementsOnBoundaries[iBoundary][iSurface][iElement])
                        else:
                            str_to_write = str_to_write + str(listElementsOnBoundaries[iBoundary][iSurface][iElement]) + ',   '                        
                            
                        if iElement != 0:
                            if iElement%7 == 0 or iElement == len(listElementsOnBoundaries[iBoundary][iSurface])-1:
                                fileOut.write(str_to_write + '\n')
                                str_to_write = '    '
    fileOut.close()
    success = True
    return success
    
    
def writeElementSetsInAbaqusInpFormat(pathFileOut,listNamesElementSets,listElementsOnBoundaries):
    success = False
    with open (pathFileOut,'a') as fileOut:
        for iBoundary in range(0,len(listNamesElementSets)):
            for iSurface in range(0,len(listNamesElementSets[0])):
                if listElementsOnBoundaries[iBoundary][iSurface] != []:
                    fileOut.write('*ELSET, ELSET=' + str(listNamesElementSets[iBoundary][iSurface]) + '\n')
                    str_to_write = '    '
                    for iElement in range(0,len(listElementsOnBoundaries[iBoundary][iSurface])):
                        if iElement == len(listElementsOnBoundaries[iBoundary][iSurface])-1:
                            str_to_write = str_to_write + str(listElementsOnBoundaries[iBoundary][iSurface][iElement])
                        else:
                            str_to_write = str_to_write + str(listElementsOnBoundaries[iBoundary][iSurface][iElement]) + ',   '                        
                            
                        if iElement != 0:
                            if iElement%7 == 0 or iElement == len(listElementsOnBoundaries[iBoundary][iSurface])-1:
                                fileOut.write(str_to_write + '\n')
                                str_to_write = '    '
    fileOut.close()
    success = True
    return success
    
if __name__ == "__main__":
    main()