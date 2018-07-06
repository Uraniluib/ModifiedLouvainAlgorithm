# -*- coding: utf-8 -*-
"""
Created on Tue Jul 03 17:30:29 2018

@author: Lusha
"""


import csv
import igraph
import numpy
import time
import sys
from jpype import JavaException


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
#SVQ=-Bmatrix

with open(str(sys.argv[3]),'rb') as csvfileQ:
    csvreaderQ=csv.reader(csvfileQ)
    mycsvQ=list(csvreaderQ)
    fQs = open('Qsupply.txt','w')
    fQd = open('Qdemand.txt','w')
    for row in mycsvQ:
        networkGraph.vs.select(int(row[0])-1)["Qsupply"]=float(row[1])
        networkGraph.vs.select(int(row[0])-1)["Qdemand"]=float(row[2])
        fQs.write(row[1]+'\n')
        fQd.write(row[2]+'\n')
    fQs.close()
    fQd.close()
    
fNI = open('networkInfo.txt','w')
es =  igraph.EdgeSeq(networkGraph)
for edge in es:
    print edge.tuple
    fNI.write(str(edge.tuple[0])+'\t')
    fNI.write(str(edge.tuple[1]))
    fNI.write('\n')
fNI.close()

fSVQ = open('SVQ.txt','w')
rowN, colN =  SVQ.shape
#print str(rowN)+' '+str(colN)
for x in range(0,rowN):
    for y in range(0,colN):
        fSVQ.write(str(SVQ[x,y])+'\t')
    fSVQ.write('\n')
    
fSVQ.close()

# using Louvain
start_time = time.time()
clusters=networkGraph.community_multilevel()
mod=networkGraph.modularity(clusters)

end_time = time.time()
print 'Degree distribution: ',networkGraph.degree_distribution()
print 'Running time: ',(end_time - start_time)
print 'New mod: ',mod
print clusters


'''cluster the network'''
#clusterResult = LV.community_multilevel(networkGraph)
print "========Begin========"
iteration = 10

start_time = time.time()

for i in range(0,iteration):
    membership = Louvain.louvain(networkGraph, None)
    clustering = igraph.Clustering(membership)
    print 'Modularity: ', igraph.Graph.modularity(networkGraph, membership)
    #print clustering

end_time = time.time()
#print result
#print 'Degree distribution: ',networkGraph.degree_distribution()
print 'Running time: ',(end_time - start_time)/iteration


networkGraph.vs["label"] = networkGraph.vs["name"]
pal = igraph.drawing.colors.ClusterColoringPalette(len(clusters))
networkGraph.vs['color'] = pal.get_many(clusters.membership)
igraph.plot(networkGraph).show()
