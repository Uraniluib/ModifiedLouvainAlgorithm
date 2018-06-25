# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 20:51:01 2018

@author: Lusha
"""

import OutputFromOpendss
#import matplotlib.pyplot as pyplot
import win32com.client
import louvain.Louvain

# call OpenDSS
dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
dssText = dssObj.Text
dssCircuit = dssObj.ActiveCircuit
dssSolution = dssCircuit.Solution
dssElem = dssCircuit.ActiveCktElement
dssBus = dssCircuit.ActiveBus
dssText.Command = "compile '../opendss/13positivebus/Master.dss'"

# retrieve output of openDSS and plot voltage
voltageList = OutputFromOpendss.getVoltageProfile()
OutputFromOpendss.plotVoltageProfile(voltageList)

# chech voltage
nodeWithIssue = []
highestV = 0
nodeWithHighestV = -1
for i in list(voltageList.keys()):
    if voltageList.get(i) > highestV:
        nodeWithHighestV=i
        highestV = voltageList.get(i)
print nodeWithHighestV

if highestV > 1.05:
    # overvoltage issue
    print "overvoltage in node ",nodeWithHighestV
    # control part
    genName = "Generator.test"
    dssCircuit.Generators.Name = genName.split(".")[1]
    oldkvar = dssCircuit.Generators.kvar
    print oldkvar
    dssCircuit.Generators.kvar = oldkvar - 100
    dssSolution.Solve()
    dssText.Command = "Export Voltages"
    dssText.Command = "Plot Profile Phases=All"
    print dssCircuit.Generators.kvar
    voltageList = OutputFromOpendss.getVoltageProfile()
    OutputFromOpendss.plotVoltageProfile(voltageList)

else:
    # no voltage issue
    print "no voltage issue"

