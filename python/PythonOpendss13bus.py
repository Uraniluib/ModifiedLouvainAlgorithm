# -*- coding: utf-8 -*-
"""
Created on Fri Jul 06 12:10:53 2018

@author: user
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 20:51:01 2018

@author: Lusha
"""


import win32com.client
import time
import igraph
import numpy as np
import OutputFromOpendss13bus
import OutputFromOpendss123bus
import Modification
import Louvain
import VoltageControl
import scipy.optimize as opt
from functools import partial

def objFun(variables):
#    return sum([abs(number) for number in variables[:len(genList)]])    
    return variables[0]  


def cons(variables, networkGraph, oneCluster, genList, SVQ, neighborConstraintInside, neighborConstraintOutside):
    vs = networkGraph.vs
#    delta_Q = variables[:len(genList)]
#    Vlist = variables[len(genList):]
    genLen = len(genList)
    conslist = []
    
    # Q generation limit
    '''
    for geni in range(0, len(genList)):
        gennode = genList[geni]
        conQ = {}
        conQ['type'] = 'ineq'
        conQ['fun'] = lambda variables: vs[gennode]["QsupplyMax"] - (vs[gennode]["Qsupply"] + variables[geni])    
        conslist.append(conQ)
    '''
    # voltage constraint for currentNode
    for nodei in range(0, len(oneCluster)):
        currentNode = oneCluster[nodei]
        Vinitial = vs[currentNode]["Vmag"]
        SVQrow = []
        for genj in range(0, genLen):
            SVQrow.append(SVQ[currentNode][genList[genj]])       
            
        # constraint for voltage and delta_Q
        conPowerFlow = {}
        conPowerFlow['type'] = 'eq'
        conPowerFlow['fun'] = lambda variables, nodei = nodei, genLen = genLen, Vinitial = Vinitial, SVQrow = SVQrow: variables[genLen + nodei] - Vinitial - np.dot(SVQrow, variables[:genLen])
        conslist.append(conPowerFlow)
        
        #upper constraint for Vnodei
        conVU = {}
        conVU['type'] = 'ineq'
        conVU['fun'] = lambda variables, genLen = genLen, nodei = nodei: 1.05 - variables[genLen + nodei]
        conslist.append(conVU)
        '''
        #lower constraint for Vnodei
        conVL = {}
        conVL['type'] = 'ineq'
        conVL['fun'] = lambda variables: variables[genLen + nodei] - 0.95
        conslist.append(conVL)
        
        
        # neighbor voltage constraint
        if nodei in neighborConstraintInside:
            position = neighborConstraintInside.index(currentNode)
            neighborNode = neighborConstraintOutside[position]
            conVNei = {}
            conVNei['type'] = 'eq'
            conVNei['fun'] = lambda variables: variables[genLen + nodei] - vs[neighborNode]["Vmag"]
            conslist.append(conVNei)
        '''
   # print len(conslist)
    return conslist




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
'''generation info'''
networkGraph = OutputFromOpendss13bus.getGenInfo(networkGraph, nodesOrder, GenFile)
'''Q denmand info'''
networkGraph = OutputFromOpendss13bus.getLoadInfo(networkGraph,nodesOrder, LoadFile)
'''Q supplyMax info'''
networkGraph = OutputFromOpendss13bus.getQsupplyInfo(networkGraph, nodesOrder, QsupplyFile)
'''voltage info'''
networkGraph, Vmag, Vang = OutputFromOpendss13bus.getVoltageProfile(networkGraph, nodesOrder, VoltageFile)
'''plot graph'''
networkGraph = OutputFromOpendss13bus.plotGraph(networkGraph)

# node edge list
vs = networkGraph.vs
es = networkGraph.es
edgeList = []
for edge in es:
    edgeList.append(edge.tuple)

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

for iterationtimes in range(0,iteration):
    membership = Louvain.louvain(networkGraph, SVQ)
    clustering = igraph.Clustering(membership)
    print 'Modularity: ', igraph.Graph.modularity(networkGraph, membership)
    
end_time = time.time()
#print result
#print 'Degree distribution: ',networkGraph.degree_distribution()
print 'Running time: ',(end_time - start_time)/iteration
print clustering

# neighbor information of clusters
connectionEdgeList = []
for edge in edgeList:
    firstEnd = edge[0]
    secondEnd = edge[1]
    if membership[firstEnd] != membership[secondEnd]:
        connectionEdgeList.append((firstEnd, secondEnd))
    
'''
#not clustering
membership  = [0] * len(nodesOrder)
clustering = igraph.Clustering(membership)
print clustering
'''


'''voltage control when there is voltage issue'''
start_time = time.time()

# check voltage issue in each cluster
highestVoltageList = []
voltageIssueFlag = []
for clusterId in range(0, len(clustering)):
    oneCluster = clustering[clusterId]
    tempHighest = -999;
    for nodeId in oneCluster:
        if vs[nodeId]["Vmag"] > tempHighest:
            tempHighest = vs[nodeId]["Vmag"]
    # set voltage issue flag
    if tempHighest > 1.05:
        voltageIssueFlag.append(True)
    else:
        voltageIssueFlag.append(False)
    highestVoltageList.append(tempHighest)
    
# the index of clusters in order of descending Vmag
clusterOrderByVol = sorted(range(len(highestVoltageList)), key=lambda k: highestVoltageList[k], reverse=True)
    
'''plot original voltage profile'''
VoltageControl.plotVoltage(Vmag, nodesOrder)


# control voltage for each cluster
for clusterId in clusterOrderByVol:
    if voltageIssueFlag[clusterId] == False:
        break
    oneCluster = clustering[clusterId]
    # find neighbors and connection nodes
    neighborConstraintEdge = []
    neighborConstraintInside = []
    neighborConstraintOutside = []
    for connectionEdge in connectionEdgeList:
        if connectionEdge[0] not in oneCluster and connectionEdge[1] not in oneCluster:
            continue
        if connectionEdge[0] in oneCluster:
            connectionNodeInside = connectionEdge[0]
            connectionNodeOutside = connectionEdge[1]
        if connectionEdge[1] in oneCluster:
            connectionNodeInside = connectionEdge[1]
            connectionNodeOutside = connectionEdge[0]
        neighborClusterId = membership[connectionNodeOutside]
        # check whether neighbor cluster has voltage issue
        # if no, the connection node voltage will be constrained to be the same of neighbor node voltage
        if voltageIssueFlag[neighborClusterId] == False:
            neighborConstraintInside.append(connectionNodeInside)
            neighborConstraintOutside.append(connectionNodeOutside)
            neighborConstraintEdge.append((connectionNodeInside,connectionNodeOutside))
    # optimization control inside the cluster
    genList = []
    Vlist = []
    for nodei in oneCluster:
        Vlist.append(vs[nodei]["Vmag"])
        if vs[nodei]["type"] == "gen":
            genList.append(nodei)
    delta_Q = [0]*(len(genList))
    variables = delta_Q + Vlist
    print 'initial variables: ', variables
    ControlResult = opt.minimize(objFun, variables, method = 'SLSQP', constraints = cons(variables, networkGraph, oneCluster, genList, SVQ, neighborConstraintInside, neighborConstraintOutside))
    variables = ControlResult.x
    print 'optimal variables: ',variables
    
'''    
    #check result with Opendss
    for i in range(0, len(genList)):
        genName = vs[genList[i]]["genName"]
        dQ = delta_Q[i]
        dssCircuit.Generators.Name = genName
        oldkvar = dssCircuit.Generators.kvar
        dssCircuit.Generators.kvar = oldkvar + dQ*100
    #print dssCircuit.Generators.kvar
    dssSolution.Solve()
    dssText.Command = "Export Voltages"
    networkGraph = OutputFromOpendss13bus.getGenInfo(networkGraph, nodesOrder, GenFile)
    networkGraph, Vmag, Vang = OutputFromOpendss13bus.getVoltageProfile(networkGraph, nodesOrder, VoltageFile)
    vs = networkGraph.vs
    voltageIssueFlag[clusterId] = False
    
 '''   
    # update information 
'''
    for i in range(0, len(genList)):
        gen = genList[i]
        vs[gen]["Qsupply"] = vs[gen]["Qsupply"] + delta_Q[i]
        
    for nodei in oneCluster:
        SVQrow = []
        for j in range(0, len(genList)):
            SVQrow.append(SVQ[nodei][genList[j]])     
        vs[nodei]["Vmag"] = vs[nodei]["Vmag"] + (SVQrow * delta_Q).sum()
 '''   
'''
for clusterId in range(0, len(clustering)):
    oneCluster = clustering[clusterId]
    voltageIssueFlag = VoltageControl.checkVoltage(Vmag, oneCluster)
    if voltageIssueFlag == True:
        print('voltage issue exists in cluster ', clusterId)
        dQlist, genIndex = VoltageControl.calReactivePower(networkGraph, oneCluster, SVQ, YGmatrix, YBmatrix)
        print dQlist
        for i in range(0, len(genIndex)):
            genName = vs[genIndex[i]]["genName"]
            dQ = dQlist[i]
            dssCircuit.Generators.Name = genName
            oldkvar = dssCircuit.Generators.kvar
            dssCircuit.Generators.kvar = oldkvar + dQ*100
            #print dssCircuit.Generators.kvar
        dssSolution.Solve()
        dssText.Command = "Export Voltages"
        networkGraph, Vmag, Vang = OutputFromOpendss13bus.getVoltageProfile(networkGraph, nodesOrder, VoltageFile)

    else:
        print "no voltage issue in cluster ", clusterId
'''   
     
end_time = time.time()      
print 'Running time: ',(end_time - start_time)
'''
dssText.Command = "Plot Profile Phases=All"
networkGraph, Vmag, Vang = OutputFromOpendss13bus.getVoltageProfile(networkGraph, nodesOrder, VoltageFile)
VoltageControl.plotVoltage(Vmag, nodesOrder)
for clusterId in range(0, len(clustering)):
    oneCluster = clustering[clusterId]
    voltageIssueFlag = VoltageControl.checkVoltage(Vmag, oneCluster)
    if voltageIssueFlag == True:
        print "voltage issue after control in cluster ", clusterId
    else:
        print "no voltage issue after control in cluster ", clusterId
'''









