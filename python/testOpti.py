# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 21:11:50 2018

@author: lusha
"""

import numpy as numpy
import scipy.optimize as opt

SVQ = numpy.matrix('1 2 1 1 5; 2 4 4 5 7; 3 3 3 3 3; 4 2 4 4 6; 1 5 5 4 5')
dQ = numpy.zeros(2)
genIndex = [1,4]



def objFun(dQ):
    return sum(dQ)


def cons(dQ, genIndex, SVQ):
    conslist = []
    for i in range(0, 2):
        
        conU = {}
        # [Ufun, Lfun] = con(dQ, networkGraph, nodei, genIndex, SVQ) 
        conU['type'] = 'ineq'
        
        genNum = len(genIndex)
        tempSVQ = []
        for j in range(0, genNum):
            tempSVQ.append(SVQ[i,genIndex[j]])
        print tempSVQ
        conU['fun'] = lambda dQ: 6 -  (tempSVQ * dQ).sum()
        conslist.append(conU)
        
        conL = {}
        conL['type'] = 'ineq'
        print tempSVQ
        conL['fun'] = lambda dQ:  (tempSVQ * dQ).sum() - 2
        conslist.append(conL)
    print len(conslist)
    return conslist

res = opt.minimize(objFun, dQ, method = 'SLSQP', constraints = cons(dQ, genIndex, SVQ))
print res.x