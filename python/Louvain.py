# -- coding: utf-8 --
"""
Created on Thu Jun 21 01:20:50 2018

@author: Jinglin
"""

import igraph
import numpy
import random
#import ClassFile
import Modification


# reset membership
def resetMembership(membership):

	new_membership = membership.copy()
	old_membership_list = list(set(membership))
	for new_clusters in range(0,len(old_membership_list)):
		sub_old = numpy.where(numpy.array(membership) == old_membership_list[new_clusters])[0]
		for sc in sub_old:
			new_membership[sc] = new_clusters  
				
	return new_membership
	
def louvain(graph, SVQ):
    
    random.seed(10)
    is_update = True  #if updated
    #iteration = 0  #iteration
    #node_weight = graph.vs.degree() #node weight array g.vs.degree() {1,1,1,3,2,3,2,3,2}
    node_number = graph.vcount()    # node number = 9
    membership = numpy.arange(0,node_number,1) # initial one node one cluster {0,1,2,3,4,5,6,7,8}
    #total_edge_weight = graph.ecount() * 2  # total_edge_weight = 18
    #resolution = 1 / total_edge_weight
    random_order = numpy.arange(0,node_number,1)
    random.shuffle(random_order)
        
    
    while is_update :#or is_update
        # If there's no update or iteration exceeded
        # clusters weight = {1. 1. 1. 3. 2. 3. 2. 3. 2.}
        #node_weight_per_cluster = numpy.zeros(len(set(membership)))
        #for i in range(0,len(membership)):
            #node_weight_per_cluster[membership[i]] += node_weight[i]
        #enum_time = 0 # Enumeration times, to n, represents all points that have been traversed without moving
        node = 0   # which node
        is_update = False
        membership = resetMembership(membership)
        better_membership = membership.copy()
        if SVQ is None:
            better_modularity = igraph.Graph.modularity(graph, membership)
        else:
            better_modularity = igraph.Graph.modularity(graph, membership) - Modification.modIndex(graph, igraph.Clustering(membership), SVQ)
        random_order_copy = list(random_order.copy())
        #move_i = False
        #while enum_time < len(set(membership)):
        for node in random_order_copy:
            #enum_time = 0
            origial_node_cluster = membership[node]  #get the original cluster number
            original_clusters = list(set(membership))
            original_clusters.remove(origial_node_cluster)
            subcluster = numpy.where(numpy.array(membership) == origial_node_cluster)[0]
            
            # add this node to the other cluster
            for new_node_cluster in original_clusters:
                temp_membership = membership.copy()
                # move i to another cluster
                #temp_membership[origial_node_cluster] = new_node_cluster
                for sc in subcluster:
                    temp_membership[sc] = new_node_cluster
                temp_membership = resetMembership(temp_membership)
                if SVQ is None:
                    temp_modularity = igraph.Graph.modularity(graph, temp_membership)
                else:
                    temp_modularity = igraph.Graph.modularity(graph, temp_membership) - Modification.modIndex(graph, igraph.Clustering(temp_membership), SVQ)
                if temp_modularity > better_modularity:  #find better clusters
                    #enum_time = 0
                    is_update = True
                    better_membership = temp_membership.copy()
                    if SVQ is None:
                        better_modularity = igraph.Graph.modularity(graph, better_membership)
                    else:
                        better_modularity = igraph.Graph.modularity(graph, better_membership) - Modification.modIndex(graph, igraph.Clustering(membership), SVQ)
                #else:
                    #enum_time += 1
            #fjowieaf = 0
            '''
            for sc in subcluster:
                if sc in random_order_copy:
                    random_order_copy.remove(sc)
            '''
            #fjowieaf = 0
            #after all cluster is tested
            #node = (node + 1) % node_number
            
        membership = better_membership.copy()
    
    # reset the membership array
    membership = resetMembership(membership)
    
    return membership
    

	
	
	
	
	
	
	
	
	
	
	
	
	
