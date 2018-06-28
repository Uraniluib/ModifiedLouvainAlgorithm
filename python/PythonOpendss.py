# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 20:51:01 2018

@author: Lusha
"""

import OutputFromOpendss
import win32com.client
#import Louvain.Louvain as LV
#import VoltageControl

OpendssFile = '../opendss/13positivebus/Master.dss'
LineFile = 'Line.dss'
TransformerFile = 'Transformer.dss'
VoltageFile = 'ieee13nodeckt_EXP_VOLTAGES.CSV'
YmatrixFile = 'ieee13nodeckt_EXP_Y.CSV'

'''call OpenDSS'''
dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
dssText = dssObj.Text
dssCircuit = dssObj.ActiveCircuit
dssSolution = dssCircuit.Solution
dssElem = dssCircuit.ActiveCktElement
dssBus = dssCircuit.ActiveBus

'''run basic power flow'''
dssText.Command = "compile "+ OpendssFile


'''get igraph'''
[networkGraph, nodeOrder] = OutputFromOpendss.getGraphInfo(LineFile, TransformerFile)
'''Y matrix'''
[YGmatrix, YBmatrix] = OutputFromOpendss.getYmatrix(YmatrixFile, nodeOrder)
'''set voltage info in graph'''
networkGraph = OutputFromOpendss.getVoltageProfile(VoltageFile, networkGraph)
'''check and plot original voltage profile'''
[voltageIssueFlag, nodesWithIssue] = OutputFromOpendss.checkPlotVoltageProfile(networkGraph)

'''cluster the network'''
#clusterResult = LV.community_multilevel(networkGraph)



'''voltage control when there is voltage issue'''
if voltageIssueFlag == True:
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
    voltageList = OutputFromOpendss.getVoltageProfile(VoltageFile)
    OutputFromOpendss.plotVoltageProfile(voltageList)
else:
    print "No voltage issue"

