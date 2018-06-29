# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:39:23 2018

@author: Lusha
"""
import matplotlib.pyplot as plt
import numpy
import scipy


def checkVoltage(Vmag, nodeListInOrder):
    voltageIssueFlag = False
    regIndex = nodeListInOrder.index("rg60")
    x = []
    y = []   
    for i in range(0, len(Vmag)):
        if i != regIndex:
            x.append(i)
            y.append(Vmag[i])
            if Vmag[i] > 1.05:
                voltageIssueFlag = True
    plt.ylim(0.99, 1.06)
    plt.scatter(x,y)
    plt.plot((0,len(y)),(1.05,1.05),'r')
    plt.show()
    return voltageIssueFlag



def calReactivePower(networkGraph, oneCluster, SVQ):
    vs = networkGraph.vs
    nodeIndexWithVoltageIssue = []
    genIndex = []
    for nodeIndex in oneCluster:
        if vs[nodeIndex]["voltageMag"] > 1.05:
            nodeIndexWithVoltageIssue.append(nodeIndex)
        if vs[nodeIndex]["type"] == "gen":
            genIndex.append(nodeIndex)
    issueNum = len(nodeIndexWithVoltageIssue)
    genNum = len(genIndex)
    
    dQ = numpy.zeros(genNum)


    cons = cons()
   # res = minimize(objFun(dQ), method = 'SLSQP', constraints = cons)
        
    return NULL

def objFun(dQ):
    return sum(dQ)

def cons():
    cons = []
    
    
     for i in range(0, issueNum):
        for j in range(0, genNum):
            
        Vnew = vs[issueNum[i]]["voltageMag"] - dV
        conU[i] =  

   