'''
This code computes the homogenized density from phase densities and volume fractions
'''
import sys
import os
import numpy as np
from performLinearInterpolation import performLinearInterpolation

def main():

    pathFileOut = 'homogenizedDensity_Ni60W.out'
    
    listTempRef_Ni = np.array([298,373,473,573,673,773,873,973,1073,1273])
    listDensityRef_Ni = np.array([8565.11,8536.86,8497.22,8455.53,8412.03,8366.93,8320.45,8272.8,8224.18,8124.82])
    volumeFraction_Ni = 0.3843

    listTempRef_WC = np.array([298.15,373.15,473.15,573.15,673.15,783.15,873.15,973.15,1073.15,1173.15,1273.15,1373.15,1473.15,1573.15,1673.15,1773.15,1873.15,1973.15,2073.15,2173.15,2273.15,2373.15,2473.15,2573.15,2673.15,2773.15,2903.77])
    listDensityRef_WC = np.array([16330.34,16310.28,16283.35,16256.2,16228.85,16198.43,16173.2,16145.07,16116.67,16087.96,16058.86,16029.22,15998.66,15966.48,15931.58,15892.57,15847.85,15795.72,15734.71,15663.8,15582.63,15491.49,15391.17,15167.16,14681.14,13875.24,11563.59])
    volumeFraction_WC = 0.6157
    
    listTempTarget = np.array([298.15,348.15,398.15,448.15,498.15,548.15,598.15,648.15,698.15,748.15,798.15,848.15,898.15,948.15,998.15,1048.15,1098.15,1148.15,1198.15,1248.15,1298.15,1348.15,1398.15,1448.15,1498.15,1548.15,1598.15,1648.15,1698.15,1748.15,1798.15,1848.15,1898.15,1948.15,1998.15,2048.15,2098.15,2148.15,2198.15])
    
    
    with open (pathFileOut,'w') as fileOut:
        fileOut.write("{0:35s}{1:35s}\n".format('Temperature','density'))
        
        for iTemp in range(0,len(listTempTarget)):
            density_Ni = performLinearInterpolation(listTempRef_Ni,listDensityRef_Ni,listTempTarget[iTemp])
            density_WC = performLinearInterpolation(listTempRef_WC,listDensityRef_WC,listTempTarget[iTemp])
            density_Ni60WC = density_Ni*volumeFraction_Ni + density_WC*volumeFraction_WC            
            fileOut.write("{0:25.10f}{1:25.10f}\n".format(listTempTarget[iTemp],density_Ni60WC))
                    
    fileOut.close()
    
if __name__ == "__main__":
    main()