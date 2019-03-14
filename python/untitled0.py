# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 13:46:58 2018

@author: xingg
"""

import win32com.client
import time
import igraph
import numpy
import OutputFromOpendss13bus
import OutputFromOpendss123bus
import Modification
import Louvain1
import VoltageControl


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
'''


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
[networkGraph, nodesOrder, YGmatrix, YBmatrix] = OutputFromOpendss13bus.getNodeAndYmatrix(YmatrixFile)
'''edge info'''
networkGraph = OutputFromOpendss13bus.getEdgeInfo(networkGraph, nodesOrder, LineFile, TransformerFile)
'''Q denmand info'''
networkGraph = OutputFromOpendss13bus.getQdemandInfo(networkGraph,nodesOrder, LoadFile)
'''Q supply info'''
networkGraph = OutputFromOpendss13bus.getQsupplyInfo(networkGraph, nodesOrder, QsupplyFile)
'''generation info'''
networkGraph = OutputFromOpendss13bus.getGenInfo(networkGraph, nodesOrder, GenFile)
'''voltage info'''
networkGraph, Vmag, Vang = OutputFromOpendss13bus.getVoltageProfile(networkGraph, nodesOrder, VoltageFile)
'''plot graph'''
#networkGraph = OutputFromOpendss13bus.plotGraph(networkGraph)

vs = networkGraph.vs

'''calculate SVQ'''
SVQ = Modification.getSVQ(YGmatrix, YBmatrix, Vmag, Vang, nodesOrder)

'''
#louvain algorithm in igraph
originalClustering = networkGraph.community_multilevel()
print originalClustering
print "modularity = ", networkGraph.modularity(originalClustering.membership)

#cluster the network
#clusterResult = LV.community_multilevel(networkGraph)'''
print "========Begin========"
iteration = 1

start_time = time.time()

#cluster = networkGraph.community_multilevel()

for i in range(0,iteration):
    membership = Louvain1.louvain(networkGraph, SVQ)
    clustering = igraph.Clustering(membership)
    print 'Modularity: ', igraph.Graph.modularity(networkGraph, membership)
    #print clustering

end_time = time.time()
#print result
#print 'Degree distribution: ',networkGraph.degree_distribution()
print 'Running time: ',(end_time - start_time)/iteration

print clustering