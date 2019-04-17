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
import Modification
import Louvain
import VoltageControl
import scipy.optimize as opt
from multiprocessing import Process, Pipe, Queue

import localControl

'''
def Optmz(objFun, variables, networkGraph, oneCluster, genList, SVQ):
    ControlResult = opt.minimize(objFun, variables, method = 'SLSQP', constraints = cons(variables, networkGraph, oneCluster, genList, SVQ))        
    process_id = os.getpid()
    print ("Process ID: " + str(process_id))
    print ControlResult.x
'''

if __name__ == '__main__':
    
    OpendssFile = '../13positivebus/Master.dss'
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
        
    '''
    #not clustering
    membership  = [0] * len(nodesOrder)
    clustering = igraph.Clustering(membership)
    print clustering
    '''
    
    # neighbor information of clusters
    connectionEdgeList = []
    for edge in edgeList:
        firstEnd = edge[0]
        secondEnd = edge[1]
        if membership[firstEnd] != membership[secondEnd]:
            connectionEdgeList.append((firstEnd, secondEnd))
            
    
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
    
    print voltageIssueFlag
        
    # the index of clusters in order of descending Vmag
    clusterOrderByVol = sorted(range(len(highestVoltageList)), key=lambda k: highestVoltageList[k], reverse=True)
        
    '''plot original voltage profile'''
    #VoltageControl.plotVoltage(Vmag, nodesOrder)
    #VoltageControl.VoltageProfile(Vmag)
    
    VoltageControl.VoltageProfile(vs)   
    for v in vs: print v["name"],' ',v["Vmag"] 
    
    # control voltage for each cluster
    processes = []
    for clusterId in clusterOrderByVol:
        if voltageIssueFlag[clusterId] == False:
            break
        oneCluster = clustering[clusterId]
        '''
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
        '''
        # optimization control inside the cluster
        genList = []
        Vlist = []
        for nodei in oneCluster:
            Vlist.append(vs[nodei]["Vmag"])
            if vs[nodei]["type"] == "gen":
                genList.append(nodei)
        delta_Q = [0]*(len(genList))
        genLen = len(genList)
        print genList
        variables = delta_Q + Vlist
        print 'initial variables: ', variables
        
        process = Process(target = localControl, args = (variables, networkGraph, oneCluster, genList, SVQ))
        processes.append(process)
        process.start()
        
        #localControl.localControl(variables, networkGraph, oneCluster, genList, SVQ)

        
        '''
        ControlResult = opt.minimize(objFun, variables, method = 'SLSQP', constraints = cons(variables, networkGraph, oneCluster, genList, SVQ))        
        variables = ControlResult.x
        print 'optimal variables: ',variables
        # update Qsupply, V information
        delta_Q = variables[:genLen]
        Vlist = variables[genLen:]
        for geni in range(0, genLen):
            currentGen = genList[geni]
            vs[currentGen]["Qsupply"] = vs[currentGen]["Qsupply"] + delta_Q[geni]
        for nodei in range(0, len(oneCluster)):
            currentNode = oneCluster[nodei]
            vs[currentNode]["Vmag"] = Vlist[nodei]    
        voltageIssueFlag[clusterId] = False
        
        # save change in OpenDSS
        for geni in range(0, genLen):
            genName = vs[genList[geni]]["genName"]
            dQ = delta_Q[geni]
            dssCircuit.Generators.Name = genName
            oldkvar = dssCircuit.Generators.kvar
            dssCircuit.Generators.kvar = oldkvar + dQ*100    
            print dssCircuit.Generators.kvar
    
        '''
        
    
    '''
    # plot voltage after update
    VoltageControl.VoltageProfile(vs)    
    for v in vs: print v["name"],' ',v["Vmag"]
    
    end_time = time.time()      
    print 'Running time: ',(end_time - start_time)
    
    # run OpenDSS to check result
    dssSolution.Solve()
    dssText.Command = "Export Voltages"
    dssText.Command = "Plot Profile Phases=All"
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
    
    
    
    
    
    
    
    
    
