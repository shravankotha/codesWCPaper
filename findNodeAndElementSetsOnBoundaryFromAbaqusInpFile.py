'''
This code parses the abaqus inp file to get nodes and elements connectivity
'''
import sys
import os
from parseAbqInpFileForNodalCoords import parseAbqFileForNodalCoordinates
from parseAbqInpFileForElementConnectivity import parseAbqFileForElementConnectivity
from findNodesAndElementsOnDomainBoundary import findNodesAndElementsOnDomainBoundary
from findDomainBoundaries import findDomainBoundaries


def main():
    if len(sys.argv) != 2:
        text = """One command line arguments are expected: \
                    \n\t(1) Abaqus input file name including extension """
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
        for iBoundarySet in range(0,len(listNamesNodeSets)):
            if listNodesOnBoundaries[iBoundarySet] != []:
                iColumnLineEnd = 7
                fileOut.write('*NSET, NSET=' + str(listNamesNodeSets[iBoundarySet]) + '\n')
                str_to_write = '    '
                if len(listNodesOnBoundaries[iBoundarySet]) == 1:
                   fileOut.write(str_to_write + str(listNodesOnBoundaries[iBoundarySet][0]) + '\n') 
                else:
                    for iNode in range(0,len(listNodesOnBoundaries[iBoundarySet])):
                        if iNode == len(listNodesOnBoundaries[iBoundarySet])-1:
                            str_to_write = str_to_write + str(listNodesOnBoundaries[iBoundarySet][iNode])
                        else:
                            str_to_write = str_to_write + str(listNodesOnBoundaries[iBoundarySet][iNode]) + ',   '                        
                            
                        if iNode != 0:
                            if iNode == iColumnLineEnd or iNode == len(listNodesOnBoundaries[iBoundarySet])-1:
                                fileOut.write(str_to_write + '\n')
                                str_to_write = '    '
                                iColumnLineEnd = iColumnLineEnd + 8
    fileOut.close()
    success = True
    return success
    
    
def writeElementSetsInAbaqusInpFormat(pathFileOut,listNamesElementSets,listElementsOnBoundaries):
    success = False
    with open (pathFileOut,'a') as fileOut:
        for iBoundarySet in range(0,len(listNamesElementSets)):
            for iSurface in range(0,len(listNamesElementSets[0])):
                if listElementsOnBoundaries[iBoundarySet][iSurface] != []:
                    iColumnLineEnd = 7
                    fileOut.write('*ELSET, ELSET=' + str(listNamesElementSets[iBoundarySet][iSurface]) + '\n')
                    str_to_write = '    '
                    for iElement in range(0,len(listElementsOnBoundaries[iBoundarySet][iSurface])):
                        if iElement == len(listElementsOnBoundaries[iBoundarySet][iSurface])-1:
                            str_to_write = str_to_write + str(listElementsOnBoundaries[iBoundarySet][iSurface][iElement])
                        else:
                            str_to_write = str_to_write + str(listElementsOnBoundaries[iBoundarySet][iSurface][iElement]) + ',   '                        
                            
                        if iElement != 0:
                            if iElement == iColumnLineEnd or iElement == len(listElementsOnBoundaries[iBoundarySet][iSurface])-1:
                                fileOut.write(str_to_write + '\n')
                                str_to_write = '    '
                                iColumnLineEnd = iColumnLineEnd + 8
    fileOut.close()
    success = True
    return success
    
if __name__ == "__main__":
    main()