# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 20:51:01 2018

@author: Lusha
"""


import win32com.client
import time
import igraph
import OutputFromOpendss
import Modification
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


'''node info and Y matrix'''
[networkGraph, nodesOrder, YGmatrix, YBmatrix] = OutputFromOpendss.getNodeAndYmatrix(YmatrixFile)
'''edge info'''
networkGraph = OutputFromOpendss.getEdgeInfo(networkGraph, nodesOrder, LineFile, TransformerFile)
'''generation info'''
networkGraph = OutputFromOpendss.getGenInfo(networkGraph, GenFile, nodesOrder)
'''Q denmand info'''
networkGraph = OutputFromOpendss.getQdemandInfo(networkGraph,LoadFile, nodesOrder)
'''Q supply info'''
networkGraph = OutputFromOpendss.getQsupplyInfo(networkGraph, QsupplyFile, nodesOrder)
'''voltage info'''
[networkGraph, Vmag, Vang] = OutputFromOpendss.getVoltageProfile(networkGraph, VoltageFile, nodesOrder)
'''plot graph'''
networkGraph = OutputFromOpendss.plotGraph(networkGraph)




'''calculate SVQ'''
SVQ = Modification.getSVQ(YGmatrix, YBmatrix, Vmag, Vang, nodesOrder)

'''cluster the network'''
#clusterResult = LV.community_multilevel(networkGraph)
print "========Begin========"
iteration = 10

start_time = time.time()

for i in range(0,iteration):
    membership = Louvain.louvain(networkGraph, SVQ)
    clustering = igraph.Clustering(membership)
    print 'Modularity: ', igraph.Graph.modularity(networkGraph, membership)
    #print clustering

end_time = time.time()
#print result
#print 'Degree distribution: ',networkGraph.degree_distribution()
print 'Running time: ',(end_time - start_time)/iteration



'''check and plot original voltage profile'''
voltageIssueFlag = VoltageControl.checkVoltage(Vmag, nodesOrder)

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

