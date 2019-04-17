# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 16:47:27 2019

@author: lusha
"""
import os
import numpy as np
import scipy.optimize as opt
    
def objFun(variables):
#    return sum([abs(number) for number in variables[:len(genList)]])    
#    return sum([abs(number) for number in variables[: genLen]])    
#    return abs(variables[0]) + abs(variables[1])
    return abs(variables[0])
    '''
    volDie = 0
    for i in range(len(genList), len(variables)):
        volDie = volDie + np.square(variables[i] - 1.05)
    return volDie
    '''
    '''
    abssum = 0
    for i in range(0, len(genList)):
        abssum = abssum + abs(variables[i])
    return abssum
    '''
    
def cons(variables, networkGraph, oneCluster, genList, SVQ):
    vs = networkGraph.vs
    genLen = len(genList)
    conslist = []
    
    
#    SVQ = lambda variables: Modification.getSVQ(YGmatrix, YBmatrix, Vmag, Vang, nodesOrder, genLen, oneCluster, variables)
    
    
    # Q generation limit
    
    for geni in range(0, len(genList)):
        gennode = genList[geni]
        conQ = {}
        conQ['type'] = 'ineq'
        conQ['fun'] = lambda variables, gennode = gennode, vs = vs, geni = geni: vs[gennode]["QsupplyMax"] - (vs[gennode]["Qsupply"] + variables[geni])    
        conslist.append(conQ)

  
    # voltage constraint for currentNode
    for nodei in range(0, len(oneCluster)):
        currentNode = oneCluster[nodei]
        Vinitial = vs[currentNode]["Vmag"]
        #SVQrow = [0]*genLen
        #SVQ = Modification.getSVQ(YGmatrix, YBmatrix, Vmag, Vang, nodesOrder, genLen, oneCluster, variables)
        SVQrow = []
        for genj in range(0, genLen):
            #SVQrow[genj] = lambda SVQ: SVQ[currentNode][genList[genj]]
            SVQrow.append(SVQ[currentNode][genList[genj]])       
        #print "SVQrow: ",SVQrow
        
        
        # power flow constraint
        conPowerFlow = {}
        conPowerFlow['type'] = 'eq'
        conPowerFlow['fun'] = lambda variables, nodei = nodei, genLen = genLen, Vinitial = Vinitial, SVQrow = SVQrow: variables[genLen + nodei] - Vinitial - np.dot(SVQrow, variables[:genLen])
        conslist.append(conPowerFlow)
        

        
        #upper constraint for Vnodei
        conVU = {}
        conVU['type'] = 'ineq'
        conVU['fun'] = lambda variables, genLen = genLen, nodei = nodei: 1.05 - variables[genLen + nodei]
        conslist.append(conVU)
        
        #lower constraint for Vnodei
        conVL = {}
        conVL['type'] = 'ineq'
        conVL['fun'] = lambda variables, genLen = genLen, nodei = nodei: variables[genLen + nodei] - 0.95
        conslist.append(conVL)
        
        
        # neighbor voltage constraint
        '''
        if currentNode in neighborConstraintInside:
            position = neighborConstraintInside.index(currentNode)
            neighborNode = neighborConstraintOutside[position]
            conVNei = {}
            conVNei['type'] = 'eq'
            conVNei['fun'] = lambda variables, genLen = genLen, nodei = nodei, vs = vs, neighborNode = neighborNode: variables[genLen + nodei] - vs[neighborNode]["Vmag"]
            conslist.append(conVNei)
        '''
   # print len(conslist)
    return conslist

def localControl(variables, networkGraph, oneCluster, genList, SVQ):
    process_id = os.getpid()
    print("Process ID: " + str(process_id))
    ControlResult = opt.minimize(objFun, variables, method = 'SLSQP', constraints = cons(variables, networkGraph, oneCluster, genList, SVQ))        
    print( ControlResult.x)
