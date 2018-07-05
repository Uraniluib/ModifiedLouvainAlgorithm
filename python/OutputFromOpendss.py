# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 14:16:10 2018

@author: Lusha
"""

import csv
import re
import numpy
import math
import igraph

'''read Ymatrix file and add vertex in graph'''
def getNodeAndYmatrix(YmatrixFile):
    networkGraph = igraph.Graph()
    nodesOrder = []
    
    with open(YmatrixFile,'rb') as csvfileY:
        csvreaderY=csv.reader(csvfileY)
        mycsvY=list(csvreaderY)
        nodeNumber = len(mycsvY)-4 # delete 3 nodes
        YGmatrix = numpy.zeros((nodeNumber,nodeNumber))
        YBmatrix = numpy.zeros((nodeNumber,nodeNumber))
        
        '''get matrix'''
        for i in range(3,len(mycsvY)-1): #delete sourcebus, rg60, 650
            row = mycsvY[i]
            if row[-1] == "" or row[-1] == " ":
                row.pop()
            nodeName = row[0][:-2]
            nodesOrder.append(nodeName)
            networkGraph.add_vertex(name = nodeName)
            n = 0
            j = 5 #delete sourcebus and rg60
            while j < len(row)-2: #delete 650
                Gvalue = float(''.join((row[j]).split()))
                Bvalue = float(''.join((row[j+1]).split())[2:])
                YGmatrix[i-3][n] = Gvalue # pay attention to i
                YBmatrix[i-3][n] = Bvalue # pay attention to i
                j = j+2
                n = n+1
    return networkGraph, nodesOrder, YGmatrix, YBmatrix



'''add edge info'''
def getEdgeInfo(networkGraph, nodesOrder, LineFile, TransformerFile):
    
    '''read line file'''
    f1 = open(LineFile,'r')
    f11 = f1.readlines()
    for x in f11:
        bus1 = re.findall(r'(?<=bus1=).+?(?= )',x)[0]
        bus2 = re.findall(r'(?<=bus2=).+?(?= )',x)[0]
        if bus1 in nodesOrder and bus2 in nodesOrder:
            networkGraph.add_edge(bus1,bus2)

    '''read transformer file'''
    f2 = open(TransformerFile,'r')
    f22 = f2.readlines()
    for x in f22:
        buses = re.findall(r'(?<=buses=\[).+?(?=\ \])',x)[0]
        buses = ''.join(buses.split())
        buses = buses.split(",")
        bus1 = buses[0]
        bus2 = buses[1]
        #if bus1 != "sourcebus" and bus2 != "sourcebus":        
        if bus1 in nodesOrder and bus2 in nodesOrder:
            networkGraph.add_edge(bus1,bus2)
    return networkGraph    



'''set gen node and name'''
def getGenInfo(networkGraph, GenFile, nodesOrder):
    vs = networkGraph.vs
    f1 = open(GenFile,'r')
    f11 = f1.readlines()
    for x in f11:
        if not x.startswith('!') and x != "\n":
            bus1 = re.findall(r'(?<=bus1=).+?(?=\ )',x)[0]
            genName = re.findall(r'(?<=Generator\.).+?(?=\")',x)[0]
            #if bus1 != "sourcebus":
            nodeIndex = nodesOrder.index(bus1)
            vs[nodeIndex]["type"] = "gen"
            vs[nodeIndex]["genName"] = genName
    return networkGraph
    


'''set Q demand info'''
def getQdemandInfo(networkGraph,LoadFile, nodesOrder):
    vs = networkGraph.vs
    f1 = open(LoadFile,'r')
    f11 = f1.readlines()
    for x in f11:
        if not x.startswith('!'):
            Qd = re.findall(r'(?<=kvar=).+?(?=\n)',x)[0]
            bus1 = re.findall(r'(?<=Load\.).+?(?=\")',x)[0]
            #if bus1 != "sourcebus":
            nodeIndex = nodesOrder.index(bus1)
            vs[nodeIndex]["Qd"] = float(Qd)
    for node in vs:
        if node["Qd"] is None:
            node["Qd"] = 0
    return networkGraph    



'''set Q supply info'''
def getQsupplyInfo(networkGraph, QsupplyFile, nodesOrder):
    vs = networkGraph.vs
    with open(QsupplyFile,'rb') as csvfileQs:
        csvreaderQs=csv.reader(csvfileQs)
        mycsvQs=list(csvreaderQs)
        for i in range(1,len(mycsvQs)):
            row = mycsvQs[i]
            bus1 = row[0]
            Qs = row[1]
            nodeIndex = nodesOrder.index(bus1)
            vs[nodeIndex]["Qs"] = float(Qs)
    for node in vs:
        if node["Qs"] is None:
            node["Qs"] = 0
    return networkGraph


'''get voltage info'''
def getVoltageProfile(networkGraph, VoltageFile, nodesOrder):
    vs = networkGraph.vs
    nodeNumber = len(nodesOrder)
    Vmag = numpy.zeros(nodeNumber)
    Vang = numpy.zeros(nodeNumber)
    with open(VoltageFile,'rb') as csvfileVoltage:
        csvreaderVoltage=csv.reader(csvfileVoltage)
        mycsvVoltage=list(csvreaderVoltage)
        for i in range(3, len(mycsvVoltage)-1): # skip source bus, rg60, 650
            row = mycsvVoltage[i]
            nodeIndex = nodesOrder.index(row[0])
            vs[nodeIndex]["Vang"] = float(row[4])
            vs[nodeIndex]["Vmag"] = float(row[5])       
            Vang[nodeIndex] = float(row[4])
            Vmag[nodeIndex] = float(row[5])  
    return networkGraph, Vmag, Vang


'''plot graph'''
def plotGraph(networkGraph):
    vs = networkGraph.vs
    for v in vs:
        v["label"] = v.index
    vs["color"] = ["pink" if (vertex["type"] == "gen")  else "yellow" for vertex in vs]
    layout = networkGraph.layout("kk")
    igraph.plot(networkGraph,"13busPlot.png",layout = layout).show()
    return networkGraph


