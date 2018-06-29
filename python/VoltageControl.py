# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:39:23 2018

@author: Lusha
"""
import matplotlib.pyplot as plt
import numpy
import scipy


def checkVoltage(networkGraph, Vmag, nodeOrder, clustering):
    vs = networkGraph.vs
    voltageIssueFlag = False
    regIndex = nodeOrder.index("reg60")
 
    

    x = []
    y = []   
    nodesWithIssueOneCluster = []
    genNodesOneCluster = []
    nodesWithIssue = []
    genNodes = []

    for i in range(0,len(clustering)):
        onecluster = clustering[i]
        for j in range(0,len(onecluster)):
            
            
            
            nodeIndex = onecluster[j]
            if vs[nodeIndex]["type"] == "gen":
                genNodesOneCluster.append(nodeIndex)
            if vs[nodeIndex]["voltageMag"] > 1.05:
                voltageIssueFlag = True
                nodesWithIssueOneCluster.append(nodeIndex)
            x.append(vs[nodeIndex]["name"])
            y.append(vs[nodeIndex]["voltageMag"])
        nodesWithIssue.append(nodesWithIssueOneCluster)
        genNodes.append(genNodesOneCluster)
            
    plt.ylim(0.99, 1.06)
    plt.scatter(x,y)
    plt.plot((0,len(vs)),(1.05,1.05),'r')
    plt.show()
    
    return voltageIssueFlag, nodesWithIssue, genNodes

def calReactivePower(networkGraph, nodesWithIssueOneCluster, genNodesOneCluster, SVQ):
    vs = networkGraph.vs

            
        
    return NULL