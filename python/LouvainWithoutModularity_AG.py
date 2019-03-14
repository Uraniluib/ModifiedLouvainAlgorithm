# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 15:45:04 2018

@author: Jinglin
"""

import csv
import igraph
import numpy
import time
import sys
import random

# louvain algorithm
def louvain(graph, SVQ):
    
    random.seed(10)
    is_update = True  #if updated
    node_number = graph.vcount()    # For example, like node_number = 9
    membership = numpy.arange(0,node_number,1) # initial one node to one cluster, {0,1,2,3,4,5,6,7,8}
    random_order = numpy.arange(0,node_number,1) # get a random order list of nodes
    random.shuffle(random_order)
        
    
    while is_update :#or is_update 
	#AG outer loop, this is the number of levels of grouping
        
        # If there's no update, break the loop
        node = 0   # which node
        is_update = False
        better_membership = membership.copy()
        better_modularity = igraph.Graph.modularity(graph, membership)
        random_order_copy = list(random_order.copy()) # HNC you will need to randomize the order of the reduced network at each step, not just copy the same random ordering from earlier
        
        for node in random_order_copy:
		#AG This copy should be a random ordering of node CLUSTERS not nodes themselves. On the first iteration each node is its own cluster, but on subsequent iterations the network should be reduced down so that each cluster correponds to a single node, with weighted edges to the other cluster-nodes. It looks to me like you are making a bunch of copies of the whole network, but never making  the reduced network, which is what makes Louvian efficient.
            origial_node_cluster = membership[node]  #get the original cluster number
            original_clusters = list(set(membership)) 
            original_clusters.remove(origial_node_cluster)
            subcluster = numpy.where(numpy.array(membership) == origial_node_cluster)[0]
			#AG This code moves a single node to a different cluster. It would work correctly if you were working with cluster composite nodes at iterations i >1, but as is, you're going through the full network over and over again. At the end of each iteration, you should have a new, smaller network to use in the following iteration. The only thing you do with the original is keep track of which nodes belong to which composite nodes.  https://en.wikipedia.org/wiki/Louvain_Modularity#Algorithm Read that last paragraph (In the second phase of the algorithm...) carefully. 
            
            # add this node to the other cluster
            for new_node_cluster in original_clusters:
                temp_membership = membership.copy()
                # move i to another cluster
                for sc in subcluster:
                    temp_membership[sc] = new_node_cluster
                temp_modularity = igraph.Graph.modularity(graph, temp_membership)
                if temp_modularity > better_modularity:  #find better clusters
                    is_update = True
                    better_membership = temp_membership.copy()
                    better_modularity = igraph.Graph.modularity(graph, better_membership)
            for sc in subcluster:
                if sc in random_order_copy:
                    random_order_copy.remove(sc)
        membership = better_membership.copy()   # After running the whole random_list, set the best as new membership
    
    # reset the membership array. For example, [4,4,2,2,1] to [0,0,1,1,2]
    new_membership = membership.copy()
    old_membership_list = list(set(membership))
    for new_clusters in range(0,len(old_membership_list)):
            sub_old = numpy.where(numpy.array(membership) == old_membership_list[new_clusters])[0]
            for sc in sub_old:
                new_membership[sc] = new_clusters        
    
    return new_membership

# main program
print "Input Original File..."
print "Use these information to create a graph..."

sys.argv = ["network_test.py", "../data/118busnode.csv", "../data/118busbranch.csv", "../data/118busQ.csv"]

# create graph for the network
networkGraph=igraph.Graph() 

with open(str(sys.argv[1]),'rb') as csvfileNode:
    csvreaderNode=csv.reader(csvfileNode)
    mycsvNode=list(csvreaderNode)
    for row in mycsvNode:
        networkGraph.add_vertex(name=row[0])
        
nodeNumber=networkGraph.vcount()
Bmatrix=numpy.zeros((nodeNumber,nodeNumber))
SVQ=numpy.zeros((nodeNumber,nodeNumber))

with open(str(sys.argv[2]),'rb') as csvfileBranch:
    csvreaderBranch=csv.reader(csvfileBranch)
    mycsvBranch=list(csvreaderBranch)
    for row in mycsvBranch:
        B=(1/complex(float(row[2]),float(row[3]))).imag
        networkGraph.add_edge(row[0],row[1])
        Bmatrix[int(row[0])-1,int(row[1])-1]=-B
        Bmatrix[int(row[1])-1,int(row[0])-1]=-B

for i in range(nodeNumber):
    for j in range(nodeNumber):
        if j!=i:
            Bmatrix[i,i]=Bmatrix[i,i]-Bmatrix[i,j]
        
SVQ=-numpy.linalg.pinv(Bmatrix)

print "Output Information..."

with open(str(sys.argv[3]),'rb') as csvfileQ:
    csvreaderQ=csv.reader(csvfileQ)
    mycsvQ=list(csvreaderQ)
    fQs = open('../data/Qsupply.txt','w')
    fQd = open('../data/Qdemand.txt','w')
    for row in mycsvQ:
        networkGraph.vs.select(int(row[0])-1)["Qsupply"]=float(row[1])
        networkGraph.vs.select(int(row[0])-1)["Qdemand"]=float(row[2])
        fQs.write(row[1]+'\n')
        fQd.write(row[2]+'\n')
    fQs.close()
    fQd.close()
    
fNI = open('../data/networkInfo.txt','w')
es =  igraph.EdgeSeq(networkGraph)
for edge in es:
    #print edge.tuple
    fNI.write(str(edge.tuple[0])+'\t')
    fNI.write(str(edge.tuple[1]))
    fNI.write('\n')
fNI.close()

fSVQ = open('../data/SVQ.txt','w')
rowN, colN =  SVQ.shape
for x in range(0,rowN):
    for y in range(0,colN):
        fSVQ.write(str(SVQ[x,y])+'\t')
    fSVQ.write('\n')
    
fSVQ.close()
# Here ends the file input part and the clustering algorithm starts

print "========Begin========"
Iteration = 10 # run the algrithm for 10 times

start_time = time.time()

for i in range(0,Iteration):
    membership = louvain(networkGraph, SVQ)
    clustering = igraph.Clustering(membership)
    print 'Modularity: ', igraph.Graph.modularity(networkGraph, membership)

end_time = time.time()
print 'Running time: ',(end_time - start_time)/Iteration

