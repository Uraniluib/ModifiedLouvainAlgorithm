# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 14:16:10 2018

@author: Lusha
"""

import csv
import matplotlib.pyplot as plt
import re
import numpy
import igraph

def getGraphInfo(LineFile,TransformerFile):
    networkGraph = igraph.Graph()
    verticesList = []
    f1 = open(LineFile,'r')
    f11 = f1.readlines()
    for x in f11:
        bus1 = re.findall(r'(?<=bus1\=).+?(?=\ )',x)[0]
        bus2 = re.findall(r'(?<=bus2\=).+?(?=\ )',x)[0]
        if bus1 != "sourcebus" and bus2 != "sourcebus":     
            if bus1 not in verticesList:
                networkGraph.add_vertex(name=bus1)
                verticesList.append(bus1)
            if bus2 not in verticesList:
                networkGraph.add_vertex(name=bus2)
                verticesList.append(bus2)
            networkGraph.add_edge(bus1,bus2)
        
    f2 = open(TransformerFile,'r')
    f22 = f2.readlines()
    for x in f22:
        buses = re.findall(r'(?<=buses\=\[).+?(?=\ \])',x)[0]
        buses = ''.join(buses.split())
        buses = buses.split(",")
        bus1 = buses[0]
        bus2 = buses[1]
        if bus1 != "sourcebus" and bus2 != "sourcebus":        
            if bus1 not in verticesList:
                networkGraph.add_vertex(name=bus1)
                verticesList.append(bus1)
            if bus2 not in verticesList:
                networkGraph.add_vertex(name=bus2)
                verticesList.append(bus2)
            networkGraph.add_edge(bus1,bus2)
        
    print networkGraph
    for v in networkGraph.vs:
        print v.index , v["name"]
    return networkGraph

def getYmatrix(YmatrixFile,networkGraph):
    vs = networkGraph.vs
    nodesOrder = []
    with open(YmatrixFile,'rb') as csvfileY:
        csvreaderY=csv.reader(csvfileY)
        mycsvY=list(csvreaderY)
        nodeNumber = int(mycsvY[0][0])-1
        YGmatrixOri = numpy.zeros((nodeNumber,nodeNumber))
        YBmatrixOri = numpy.zeros((nodeNumber,nodeNumber))
        
        '''record original node order'''
        for i in range(2,len(mycsvY)):
            row = mycsvY[i]
            nodesOrder.append(row[0][:-2])
        
        '''find corresponding index order'''
        indexOrder = []
        for nodeName in nodesOrder:
            indexOrder.append(vs.find("name" == nodeName).index) #index all 0, how to fix this problem
            print nodeName
            print indexOrder
        
        '''get matrix'''
        for i in range(2,len(mycsvY)):
            row = mycsvY[i]
            if row[-1] == "" or row[-1] == " ":
                row.pop()
            m = 0
            j = 3
            while j < len(row):
                Gvalue = float(''.join((row[j]).split()))
                Bvalue = float(''.join((row[j+1]).split())[2:])
                YGmatrixOri[i-1][m] = Gvalue
                YBmatrixOri[i-1][m] = Bvalue
                j = j+2
                m = m+1
    
    return nodesOrder,YGmatrix, YBmatrix
               

def getVoltageProfile(VoltageFile,networkGraph):
    with open(VoltageFile,'rb') as csvfileVoltage:
        csvreaderVoltage=csv.reader(csvfileVoltage)
        mycsvVoltage=list(csvreaderVoltage)
        for row in mycsvVoltage:
            for node in networkGraph.vs:
                if row[0] == node["name"]:
                    node["voltageAngle"] = float(row[4])
                    node["voltageMag"] = float(row[5])
    return networkGraph
    

def checkPlotVoltageProfile(networkGraph):
    x = []
    y = []
    voltageIssueFlag = False
    nodesWithIssue = []
    nodes = networkGraph.vs
    for node in nodes:
        x.append(node["name"])
        y.append(node["voltageMag"])
        if node["voltageMag"]:
            voltageIssueFlag = True
            nodesWithIssue.append(node)
    plt.ylim(0.99, 1.06)
    plt.scatter(x,y)
    plt.plot((0,len(nodes)),(1.05,1.05),'r')
    plt.show()
    
    return voltageIssueFlag, nodesWithIssue
    
'''
YmatrixFile = '../opendss/13positivebus/ieee13nodeckt_EXP_Y.CSV'
getYmatrix(YmatrixFile)


'''