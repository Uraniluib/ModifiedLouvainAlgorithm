# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:39:23 2018
@author: Lusha
"""
import matplotlib.pyplot as plt
import numpy
import scipy.optimize as opt


def checkVoltage(networkGraph, nodesOrder):
    voltageIssueFlag = False
    vs = networkGraph.vs
    x = []
    y = []   
    for i in range(0, len(nodesOrder)):
        Vmag = vs[i]["Vmag"]
        x.append(i)
        y.append(Vmag)
        if Vmag > 1.05:
            voltageIssueFlag = True
    plt.ylim(0.99, 1.1)
    plt.scatter(x,y)
    plt.plot((0,len(y)),(1.05,1.05),'r')
    plt.show()
    if voltageIssueFlag == True:
        print "overvoltage detected!"
    else:
        print "no voltage issue!"
    return voltageIssueFlag



def calReactivePower(networkGraph, oneCluster, SVQ):
    vs = networkGraph.vs
    nodeIndexWithVoltageIssue = []
    genIndex = []
    for nodeIndex in oneCluster:
        if vs[nodeIndex]["Vmag"] > 1.05:
            nodeIndexWithVoltageIssue.append(nodeIndex)
        if vs[nodeIndex]["type"] == "gen":
            genIndex.append(nodeIndex)
#    issueNum = len(nodeIndexWithVoltageIssue)
    genNum = len(genIndex)
    
    dQ = numpy.zeros(genNum)
    
    #conslist = cons(dQ, networkGraph, nodeIndexWithVoltageIssue, genIndex, SVQ)
    
    res = opt.minimize(objFun, dQ, method = 'SLSQP', constraints = cons(dQ, networkGraph, nodeIndexWithVoltageIssue, genIndex, SVQ))
        
    return res.x, genIndex

def objFun(dQ):
    return sum(numpy.absolute(dQ))


def cons(dQ, networkGraph, nodeIndexWithVoltageIssue, genIndex, SVQ):
    vs = networkGraph.vs
    issueNum = len(nodeIndexWithVoltageIssue)
    genNum = len(genIndex)
    conslist = []
    '''
    for i in range(0, issueNum):
        nodei = nodeIndexWithVoltageIssue[i]
        conU = {}
        conL = {}
#        [Ufun, Lfun] = con(dQ, networkGraph, nodei, genIndex, SVQ) 
        conU['type'] = 'ineq'
        conU['fun'] = lambda dQ: 1.05 - con(dQ, networkGraph, nodei, genIndex, SVQ)
        conL['type'] = 'ineq'
        conL['fun'] = lambda dQ: con(dQ, networkGraph, nodei, genIndex, SVQ) - 0.95
        conslist.append(conU)
        conslist.append(conL)
    '''
    for i in range(0, issueNum):
        nodei = nodeIndexWithVoltageIssue[i]
        SVQrow = []
        for j in range(0, genNum):
            SVQrow.append(SVQ[nodei][genIndex[j]])        
            
        '''upper constraint for Vnodei'''
        conU = {}
        conU['type'] = 'ineq'
        conU['fun'] = lambda dQ: 1.05 - (vs[nodei]["Vmag"] + (SVQrow * dQ).sum())
        conslist.append(conU)
        
        '''lower constraint for Vnodei'''
        conL = {}
        conL['type'] = 'ineq'
        conL['fun'] = lambda dQ: (vs[nodei]["Vmag"] + (SVQrow * dQ).sum()) - 0.95
        conslist.append(conL)
    print len(conslist)
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
