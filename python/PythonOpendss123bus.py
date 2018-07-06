# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 20:51:01 2018

@author: Lusha
"""


import win32com.client
import time
import igraph
import OutputFromOpendss
import OutputFromOpendss123bus
import Modification
import Louvain
import VoltageControl

'''
OpendssFile = '../opendss/13positivebus/Master.dss'
LineFile = 'Line.dss'
TransformerFile = 'Transformer.dss'
VoltageFile = 'ieee13nodeckt_EXP_VOLTAGES.CSV'
YmatrixFile = 'ieee13nodeckt_EXP_Y.CSV'
GenFile = "Generator.dss"
LoadFile = "Load.dss"
QsupplyFile = "Qsupply.CSV"
'''

OpendssFile = '../opendss/123positivebus/Master.dss'
LineFile = 'Line.dss'
TransformerFile = 'Transformer.dss'
VoltageFile = 'ieee123_EXP_VOLTAGES.CSV'
YmatrixFile = 'ieee123_EXP_Y.CSV'
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
[networkGraph, nodesOrder, YGmatrix, YBmatrix] = OutputFromOpendss123bus.getNodeAndYmatrix(YmatrixFile)
'''edge info'''
networkGraph = OutputFromOpendss123bus.getEdgeInfo(networkGraph, nodesOrder, LineFile, TransformerFile)
'''Q denmand info'''
networkGraph = OutputFromOpendss123bus.getQdemandInfo(networkGraph,nodesOrder, LoadFile)
'''Q supply info'''
networkGraph = OutputFromOpendss123bus.getQsupplyInfo(networkGraph, nodesOrder, QsupplyFile)
'''generation info'''
networkGraph = OutputFromOpendss123bus.getGenInfo(networkGraph, nodesOrder, GenFile)
'''voltage info'''
[networkGraph, Vmag, Vang] = OutputFromOpendss123bus.getVoltageProfile(networkGraph, nodesOrder, VoltageFile)
'''plot graph'''
networkGraph = OutputFromOpendss123bus.plotGraph(networkGraph)

vs = networkGraph.vs


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
        dQlist, genIndex = VoltageControl.calReactivePower(networkGraph, oneCluster, SVQ)
        print dQlist
        for i in range(0, len(genIndex)):
            genName = vs[genIndex[i]]["genName"]
            dQ = dQlist[i]
            dssCircuit.Generators.Name = genName
            oldkvar = dssCircuit.Generators.kvar
            dssCircuit.Generators.kvar = oldkvar + dQ*200
            print dssCircuit.Generators.kvar
        dssSolution.Solve()
    dssText.Command = "Export Voltages"
    dssText.Command = "Plot Profile Phases=All"
    networkGraph, Vmag, Vang = OutputFromOpendss.getVoltageProfile(networkGraph, nodesOrder, VoltageFile)
    VoltageControl.checkVoltage(Vmag, nodesOrder)
else:
    print "No voltage issue"

