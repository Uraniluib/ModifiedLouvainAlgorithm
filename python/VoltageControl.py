# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:39:23 2018
@author: Lusha
"""
import matplotlib.pyplot as plt
import numpy
import scipy.optimize as opt


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
    genNum = len(genIndex)
    
    dQ = numpy.zeros(genNum)
    #conslist = cons(dQ, networkGraph, nodeIndexWithVoltageIssue, genIndex, SVQ)
    res = opt.minimize(objFun(dQ), numpy.zeros(genNum), method = 'SLSQP', constraints = cons(dQ, networkGraph, nodeIndexWithVoltageIssue, genIndex, SVQ))
        
    return res

def objFun(dQ):
    return sum(dQ)

def cons(dQ, networkGraph, nodeIndexWithVoltageIssue, genIndex, SVQ):
    vs = networkGraph.vs
    issueNum = len(nodeIndexWithVoltageIssue)
    genNum = len(genIndex)
    conslist = []
    for i in range(0, issueNum):
        conU = {}
        conL = {}
        dV = 0
        for j in range(0, genNum):
            dV = dV + SVQ[nodeIndexWithVoltageIssue[i]][genIndex[j]]*dQ[j]
        Vnew = vs[nodeIndexWithVoltageIssue[i]]["voltageMag"] - dV # not sure add or minus
        conU['type'] = 'ineq'
        conU['fun'] = 1.05 - Vnew
        conL['type'] = 'ineq'
        conL['fun'] = Vnew - 0.95
        conslist.append(conU)
        conslist.append(conL)
        
    return conslist
