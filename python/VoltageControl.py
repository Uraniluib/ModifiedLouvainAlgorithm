# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:39:23 2018
@author: Lusha
"""
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as opt

def plotVoltage(Vmag, nodesOrder):
    x = []
    y = []   
    for i in range(0, len(nodesOrder)):
        x.append(i)
        y.append(Vmag[i])
    plt.ylim(0.99, 1.1)
    plt.scatter(x,y)
    plt.plot((0,len(y)),(1.05,1.05),'r')
    plt.show()
    
def VoltageProfile(vs):
    x = []
    y = []   
    for nodei in range(0, len(vs)):
        currentNodeVol = vs[nodei]["Vmag"]
        x.append(nodei)
        y.append(currentNodeVol)
    plt.ylim(0.99, 1.1)
    plt.scatter(x,y)
    plt.plot((0,len(y)),(1.05,1.05),'r')
    plt.show()    

def checkVoltage(Vmag, oneCluster):
    voltageIssueFlag = False
    for i in oneCluster:
        if Vmag[i] > 1.05:
            voltageIssueFlag = True
            return voltageIssueFlag
    return voltageIssueFlag



def calReactivePower(networkGraph, oneCluster, SVQ, YGmatrix, YBmatrix):
    vs = networkGraph.vs
    nodeIndexWithVoltageIssue = []
    genIndex = []
    VinCluster = []
    for nodeIndex in oneCluster:
        VinCluster.append(vs[nodeIndex]["Vmag"])
        if vs[nodeIndex]["Vmag"] > 1.05:
            nodeIndexWithVoltageIssue.append(nodeIndex)
        if vs[nodeIndex]["type"] == "gen":
            genIndex.append(nodeIndex)
#    issueNum = len(nodeIndexWithVoltageIssue)
    genNum = len(genIndex)
    
    dQ = np.zeros(genNum)
    variables = np.append(dQ,VinCluster)
    
    #conslist = cons(dQ, networkGraph, nodeIndexWithVoltageIssue, genIndex, SVQ)
    
#    res = opt.minimize(objFun, variables, method = 'SLSQP', constraints = cons(variables, networkGraph, nodeIndexWithVoltageIssue, genIndex, SVQ))
    res = opt.minimize(objFun, variables, method = 'SLSQP', constraints = cons(variables, networkGraph, genIndex, SVQ, oneCluster))
    
    return res.x, genIndex

def objFun(dQ):
    return sum([abs(number) for number in dQ])

'''
def cons(variables, networkGraph,  genIndex, SVQ, oneCluster, YGmatrix, YBmatrix):
    vs = networkGraph.vs
 
    
    genNum = len(genIndex)
    dQ = variables[:genNum]
    VinCluster = variables[genNum:]
    nodeNum = len(VinCluster)
    
    conslist = []
    #new
    for i in range(0,len(oneCluster)):
        nodeIndex = oneCluster[i]
        nodei = vs[nodeIndex]
        Pgen = nodei["Pgen"]
        Pload = nodei["Pload"]
        Qsupply = nodei["Qsupply"]
        Qdemand = nodei["Qdemand"]
        

        #upper constraint for Vnodei
        conU = {}
        conU['type'] = 'ineq'
        conU['fun'] = lambda dQ, VinCluster: 1.05 - V
        conslist.append(conU)
        
        #lower constraint for Vnodei
        conL = {}
        conL['type'] = 'ineq'
        conL['fun'] = lambda dQ: (vol + (SVQrow * dQ).sum()) - 0.95
        conslist.append(conL)    
    
    for i in range(0, issueNum):
        nodei = nodeIndexWithVoltageIssue[i]
        vol = vs[nodei]["Vmag"]
        SVQrow = []
        for j in range(0, genNum):
            SVQrow.append(SVQ[nodei][genIndex[j]])        
            

    print len(conslist)
    return conslist

'''
def cons(variables, networkGraph, nodeIndexWithVoltageIssue, genIndex, SVQ):
    vs = networkGraph.vs
    issueNum = len(nodeIndexWithVoltageIssue)
    genNum = len(genIndex)
    dQ = variables[:genNum]
    VinCluster = variables[genNum:]
    
    conslist = []
    
    for i in range(0, issueNum):
        nodei = nodeIndexWithVoltageIssue[i]
        vol = vs[nodei]["Vmag"]
        SVQrow = []
        for j in range(0, genNum):
            SVQrow.append(SVQ[nodei][genIndex[j]])        
            
        #upper constraint for Vnodei
        conU = {}
        conU['type'] = 'ineq'
        conU['fun'] = lambda dQ: 1.05 - (vol + (SVQrow * dQ).sum())
        conslist.append(conU)
        
        #lower constraint for Vnodei
        conL = {}
        conL['type'] = 'ineq'
        conL['fun'] = lambda dQ: (vol + (SVQrow * dQ).sum()) - 0.95
        conslist.append(conL)
    print(len(conslist))
    return conslist


def con(dQ, networkGraph, nodei, genIndex, SVQ):
    vs = networkGraph.vs
    genNum = len(genIndex)
    dV = 0
    for j in range(0, genNum):
        dV = dV + SVQ[nodei][genIndex[j]]*dQ[j]
    Vnew = vs[nodei]["Vmag"] + dV 
#    Ufun = 1.05 - Vnew
#    Lfun = Vnew - 0.95
        
    return Vnew

def bnds(genIndex):
    bnds = []
    for i in range(0, len(genIndex)):
        bnds.append((0,None))
    return bnds
