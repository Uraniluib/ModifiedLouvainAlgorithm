# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 10:20:46 2018

@author: Lusha
"""

import numpy

def getAvgSensitivity(oneCluster, SVQ):
    sumAVQ = 0
    count = 0
    for i in range(0, len(oneCluster)):
        for j in range(i+1, len(oneCluster)):
            indexi =  oneCluster[i]
            indexj = oneCluster[j]
            Aij = (SVQ[indexi][indexj]+SVQ[j][i])/2
            sumAVQ = sumAVQ + Aij
            count = count +1
    avgAVQ = sumAVQ/count
    return avgAVQ


def getQbalanceDegree(oneCluster, networkGraph):
    vs = networkGraph.vs
    Qd = 0
    Qs = 0
    for i in range(0, len(oneCluster)):
        nodeIndex = oneCluster[i]
        Qd = Qd + vs[nodeIndex]["Qd"]
        Qs = Qs + vs[nodeIndex]["Qs"]
    if Qs > Qd or Qd == 0:
        QbalanceDegree = 1
    else:
        QbalanceDegree = numpy.absolute(Qs/Qd)
    return QbalanceDegree