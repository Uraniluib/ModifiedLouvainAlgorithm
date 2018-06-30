# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 20:51:01 2018

@author: Lusha
"""

import OutputFromOpendss
import win32com.client
import time
import igraph
import Louvain
import VoltageControl

OpendssFile = '../opendss/13positivebus/Master.dss'
LineFile = 'Line.dss'
TransformerFile = 'Transformer.dss'
VoltageFile = 'ieee13nodeckt_EXP_VOLTAGES.CSV'
YmatrixFile = 'ieee13nodeckt_EXP_Y.CSV'
GenFile = "Generator.dss"
LoadFile = "Load.dss"
QsupplyFile = "Qsupply.CSV"

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
[networkGraph, nodeListInOrder, Vmag, Vang] = OutputFromOpendss.getGraphInfo(LineFile, TransformerFile, GenFile, VoltageFile, LoadFile, QsupplyFile )
'''Y matrix'''
[YGmatrix, YBmatrix] = OutputFromOpendss.getYmatrix(YmatrixFile, nodeListInOrder)
'''SVQ'''
SVQ = OutputFromOpendss.getSVQ(YGmatrix, YBmatrix, Vmag, Vang, nodeListInOrder)



'''cluster the network'''
#clusterResult = LV.community_multilevel(networkGraph)
print "========Begin========"
iteration = 10

start_time = time.time()

for i in range(0,iteration):
    membership = Louvain.louvain(networkGraph,SVQ)
    clustering = igraph.Clustering(membership)
    print 'Modularity: ', igraph.Graph.modularity(networkGraph, membership)
    #print clustering

end_time = time.time()
#print result
#print 'Degree distribution: ',networkGraph.degree_distribution()
print 'Running time: ',(end_time - start_time)/iteration


'''check and plot original voltage profile'''
voltageIssueFlag = VoltageControl.checkVoltage(Vmag, nodeListInOrder)

'''voltage control when there is voltage issue'''
if voltageIssueFlag == True:
    # control voltage for every cluster
    for oneCluster in clustering:
        neededQ = VoltageControl.calReactivePower(networkGraph, oneCluster, SVQ)

        
    genName = "Generator.g1"
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

