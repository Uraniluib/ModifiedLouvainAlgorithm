# -- coding: utf-8 --
"""
Created on Thu Jun 21 01:20:50 2018

@author: Jinglin
"""

import igraph
#import ClassFile
#import Modification


def community_multilevel(graph, SVQ, weights=None, return_levels=False): 
    if graph.is_directed(): 
        raise ValueError("input graph must be undirected") 
   
    if return_levels: 
        levels, qs = community_multilevel(graph, SVQ, weights, True) 
        result = [] 
        for level, q in zip(levels, qs): 
             result.append(igraph.VertexClustering(graph, level, q, modularity_params=dict(weights=weights))) 
    else: 
        membership = community_multilevel(graph, SVQ, weights, False) 
        result = igraph.VertexClustering(graph, membership, modularity_params=dict(weights=weights)) 
    return result 
