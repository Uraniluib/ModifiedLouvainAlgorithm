# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 16:01:17 2018

@author: lusha
"""
import numpy
import operator

def modification(modularity,graph_silm,SVQ,initial_clusters):
    sensitivity=[]
    Qbalance=[]
    #for v in graph_silm.vs:
        #print float(graph_silm.vs.select(v.index)['Qsupply'][0])
    #for v in graph_silm.vs:
       # print float(graph_silm.vs.select(v.index)['Qdemand'][0])
    for one_cluster in initial_clusters: 
        Qs=0
        Qd=0
        nodes_in_one_cluster=[]
        for vertex_index in one_cluster:
            
            nodes_in_one_cluster.append(vertex_index)
            
            Qs=Qs+float(graph_silm.vs.select(vertex_index)['Qsupply'][0])
            Qd=Qd+float(graph_silm.vs.select(vertex_index)['Qdemand'][0])
        if Qs>Qd or Qd==0:
            Qbalance.append(0)
        else:
            Qbalance.append(1-abs(Qs/Qd))
            
        #print nodes_in_one_cluster
        evq=0
        com_number=0
        for i in range(len(nodes_in_one_cluster)):
            for j in range(i+1,len(nodes_in_one_cluster)):
                evq=evq+SVQ[nodes_in_one_cluster[i],nodes_in_one_cluster[j]]
                com_number=com_number+1
    
        avgevq=evq/com_number
        sensitivity.append(avgevq)
        
    #print SVQ
    #print Qbalance
    #print sensitivity
    print sensitivity
    print Qbalance  
    allmod=map(operator.add, Qbalance,sensitivity)
    mod=numpy.mean(allmod)
    newmod=modularity-mod
    #print newmod
    return newmod
    