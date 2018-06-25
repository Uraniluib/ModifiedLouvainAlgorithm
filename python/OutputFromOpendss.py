# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 14:16:10 2018

@author: Lusha
"""

import csv
import matplotlib.pylab as plt
def getVoltageProfile():
    voltageList={}
    with open('ieee13nodeckt_EXP_VOLTAGES.CSV','rb') as csvfileVoltage:
        csvreaderVoltage=csv.reader(csvfileVoltage)
        mycsvVoltage=list(csvreaderVoltage)
        for row in mycsvVoltage:
            if  row[0]!= str("Bus") and row[0]!=str("RG60") and row[0]!=str("SOURCEBUS") and row[0]!=str("650"):
                voltageList[row[0]]=float(row[5])
            if row[0]==str("650"):
                voltageList["1"] = float(row[5])
    
            
    print voltageList
    print list(voltageList.values())
    
    return voltageList
    
def plotVoltageProfile(voltageList):
    # plot original voltage
    lists = sorted(voltageList.items())
    x,y = zip(*lists)
    plt.ylim(0.99, 1.06)
    plt.plot(x,y)
    plt.plot((0,692),(1.05,1.05),'r')
    plt.show()
    
