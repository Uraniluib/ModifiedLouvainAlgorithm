# -- coding: utf-8 --
"""
Created on Thu Jun 21 01:20:50 2018

@author: Jinglin
"""

import igraph
import numpy
import random
#import ClassFile
import copy
import Modification


# reset membership
def resetMembership(membership):

	new_membership = copy.deepcopy(membership)
	old_membership_list = list(set(membership))
	for new_clusters in range(0,len(old_membership_list)):
		sub_old = numpy.where(numpy.array(membership) == old_membership_list[new_clusters])[0]
		for sc in sub_old:
			new_membership[sc] = new_clusters  
				
	return new_membership

def newClusters(number_of_nodes):
    clusters = []
    for i in range(0,number_of_nodes):
        clusters.append([i])
    return clusters


def changeClustersToMembership(number_of_nodes, clusters):
    membership = numpy.arange(0,number_of_nodes,1)
    for i in range(0,len(clusters)):
        for j in clusters[i]:
            membership[j] = i    
    return membership
    
    
def randomOrder(clusters):
    cluster_random_order = numpy.arange(0,len(clusters),1)    
    random.shuffle(cluster_random_order)
    return cluster_random_order

def inEdgeWeight_multi(incident,clusters):
    edge_weight_in_cluster = numpy.zeros(len(clusters))
    for i in range(0,len(clusters)):
        for source in clusters[i]:
            for target in clusters[i]:
                edge_weight_in_cluster[i] += (incident[source][target] + incident[target][source])
    return edge_weight_in_cluster
            
def inEdgeWeight(incident,cluster):
    edge_weight_in_cluster = 0
    for source in cluster:
            for target in cluster:
                edge_weight_in_cluster += incident[source][target]
    return edge_weight_in_cluster

#def corss
    
	
def louvain(graph, SVQ):
    
    random.seed(10)
    is_update = True  #if updated
    number_of_nodes = graph.vcount()
    clusters = newClusters(number_of_nodes) #[[0],[1],[2]...,[12]]
    membership = changeClustersToMembership(number_of_nodes, clusters)
    node_weight = graph.degree()
    
    
    while is_update :
        is_update = False
        
        #temp data
        delta_Q_max = 0
        better_clusters = copy.deepcopy(clusters)
        better_node_weight = copy.deepcopy(node_weight)
            
        #random choose cluster
        out_random_order = randomOrder(clusters)
        
        for i in out_random_order: #put ith node/shrink cluster into another
            
            copy_clusters = copy.deepcopy(clusters)
            copy_node_weight = copy.deepcopy(node_weight)
            #i is like 0, moving_cluster is like [1,2]
            moving_cluster = copy_clusters.pop(i) #current move this cluster out and get the element from random order list
            moving_cluster_weight = copy_node_weight.pop(i)
            in_random_order = randomOrder(copy_clusters)
            
            for j in in_random_order: #move i to j
                #copy_clusters[j] = copy_clusters[j] + moving_cluster
                #copy_node_weight[j] = copy_node_weight[j] + moving_cluster_weight
                temp_list = copy_clusters[j] + moving_cluster
                temp_weight = copy_node_weight[j] + moving_cluster_weight
                delta_Q = inEdgeWeight(graph.get_adjacency(),temp_list)             
                
                if SVQ is None:
                    delta_Q = delta_Q - copy_node_weight[j] * moving_cluster_weight / graph.ecount()
                else:
                    temp_clusters = copy.deepcopy(copy_clusters)
                    temp_clusters[j] = temp_list
                    membership = changeClustersToMembership(number_of_nodes, temp_clusters) 
                    delta_Q = delta_Q - copy_node_weight[j] * moving_cluster_weight / graph.ecount() - Modification.modIndex(graph, igraph.Clustering(membership), SVQ)
                    
                
                if delta_Q > delta_Q_max and delta_Q > 0:
                    delta_Q_max = delta_Q
                    better_clusters = copy.deepcopy(copy_clusters)
                    better_clusters[j] = temp_list
                    better_node_weight = copy.deepcopy(copy_node_weight)
                    better_node_weight[j] = temp_weight
                    is_update = True
                
        print better_clusters
        membership = changeClustersToMembership(number_of_nodes, temp_clusters)
        print igraph.Graph.modularity(graph, membership)
        clusters = better_clusters
        node_weight = better_node_weight
        
    return changeClustersToMembership(number_of_nodes, clusters)