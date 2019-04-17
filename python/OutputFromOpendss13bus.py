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
    
    with open(YmatrixFile,'r') as csvfileY:
        csvreaderY=csv.reader(csvfileY)
        mycsvY=list(csvreaderY)
        
        nodeNumber = len(mycsvY)-4 # delete 3 nodes for 13bus
        #nodeNumber = len(mycsvY) - 3 # for 123bus
        YGmatrix = numpy.zeros((nodeNumber,nodeNumber))
        YBmatrix = numpy.zeros((nodeNumber,nodeNumber))
        
        Zbase = 2.4*2.4*1000/100
        Ybase = 1/Zbase
        
        '''get matrix'''
        for i in range(3,len(mycsvY)-1): #delete sourcebus, rg60, 650 for 13bus
        #for i in range(3, len(mycsvY)): #for 123bus
            row = mycsvY[i]
            if row[-1] == "" or row[-1] == " ":
                row.pop()
            nodeName = row[0][:-2]
            nodesOrder.append(nodeName)
            networkGraph.add_vertex(name = nodeName)
            n = 0
            j = 5 #delete sourcebus and rg60
            while j < len(row)-2: #delete 650 for 13bus
            #while j < len(row): # for 123bus
                Gvalue = float(''.join((row[j]).split()))
                Bvalue = float(''.join((row[j+1]).split())[2:])
                YGmatrix[i-3][n] = Gvalue # pay attention to i
                YBmatrix[i-3][n] = Bvalue # pay attention to i
                j = j+2
                n = n+1
    YGmatrix = YGmatrix/(Ybase)
    YBmatrix = YBmatrix/(Ybase)
    return networkGraph, nodesOrder, YGmatrix, YBmatrix



'''add edge info'''
def getEdgeInfo(networkGraph, nodesOrder, LineFile, TransformerFile):
    
    '''read line file'''
    f1 = open(LineFile,'r')
    f11 = f1.readlines()
    for row in f11:
        if not row.startswith('!') and row != "\n":
            bus1 = re.findall(r'(?<=bus1=).+?(?= )',row)[0]
            bus2 = re.findall(r'(?<=bus2=).+?(?= )',row)[0]
            if isinstance(bus1, str):
                bus1 = bus1.upper()
            if isinstance(bus2, str):
                bus2 = bus2.upper()
            if bus1 in nodesOrder and bus2 in nodesOrder:
                networkGraph.add_edge(bus1,bus2)

    '''read transformer file'''
    f2 = open(TransformerFile,'r')
    f22 = f2.readlines()
    for x in f22:
        if not x.startswith('!') and x != "\n":
            buses = re.findall(r'(?<=buses=\[).+?(?=\ \])',x)[0]
            buses = ''.join(buses.split())
            buses = buses.split(",")
            bus1 = buses[0]
            bus2 = buses[1]
            if isinstance(bus1, str):
                bus1 = bus1.upper()
            if isinstance(bus2, str):
                bus2 = bus2.upper()
            if bus1 in nodesOrder and bus2 in nodesOrder:
                networkGraph.add_edge(bus1,bus2)
    return networkGraph    



'''set gen node, name and value'''
def getGenInfo(networkGraph, nodesOrder, GenFile):
    vs = networkGraph.vs
    for node in vs:
        node["type"] = "load" #initial every node to be load
        node["Pgen"] = 0
        node["Pload"] = 0
        node["QsupplyMax"] = 0
        node["Qdemand"] = 0
        node["Qsupply"] = 0
       
        

    f1 = open(GenFile,'r')
    f11 = f1.readlines()
    for x in f11:
        if not x.startswith('!') and x != "\n":
            bus1 = re.findall(r'(?<=bus1=).+?(?=\ )',x)[0]
            if isinstance(bus1, str):
                bus1 = bus1.upper()
            genName = re.findall(r'(?<=Generator\.).+?(?=\")',x)[0]
            genP = re.findall(r'(?<=kW=).+?(?=\ )',x)[0]
            genQ = re.findall(r'(?<=kvar=).',x)[0]
            nodeIndex = nodesOrder.index(bus1)
            vs[nodeIndex]["type"] = "gen"
            vs[nodeIndex]["genName"] = genName
            vs[nodeIndex]["Pgen"] = float(genP)/100
            vs[nodeIndex]["Qsupply"] = float(genQ)/100
    return networkGraph
    


'''set PQ load info'''
def getLoadInfo(networkGraph, nodesOrder, LoadFile):
    vs = networkGraph.vs        
        
    f1 = open(LoadFile,'r')
    f11 = f1.readlines()
    for x in f11:
        if not x.startswith('!') and x != "\n":
            Qdemand = re.findall(r'(?<=kvar=).+?(?=\n)',x)[0]
            PloadValue = re.findall(r'(?<=kW=).+?(?=\ )',x)[0]
            Vbase = re.findall(r'(?<=kV=).+?(?=\ )',x)[0]
            bus1 = re.findall(r'(?<=bus1=).+?(?=\ )',x)[0]
            if isinstance(bus1, str):
                bus1 = bus1.upper()

            nodeIndex = nodesOrder.index(bus1)
            vs[nodeIndex]["Pload"] = vs[nodeIndex]["Pload"] + float(PloadValue)/100
            vs[nodeIndex]["Qdemand"] = vs[nodeIndex]["Qdemand"] + float(Qdemand)/100
            vs[nodeIndex]["Vbase"] = Vbase
    return networkGraph    



'''set Q supply info'''
def getQsupplyInfo(networkGraph, nodesOrder, QsupplyFile):
    vs = networkGraph.vs
        
    with open(QsupplyFile,'r') as csvfileQs:
        csvreaderQs=csv.reader(csvfileQs)
        mycsvQs=list(csvreaderQs)
        for i in range(1,len(mycsvQs)):
            row = mycsvQs[i]
            bus1 = row[0]
            if isinstance(bus1, str):
                bus1 = bus1.upper()
            Qsupply = row[1]
            nodeIndex = nodesOrder.index(bus1)
            vs[nodeIndex]["QsupplyMax"] = float(Qsupply)/100
    return networkGraph


'''get voltage info'''
def getVoltageProfile(networkGraph, nodesOrder, VoltageFile):
    vs = networkGraph.vs
    nodeNumber = len(nodesOrder)
    Vmag = numpy.zeros(nodeNumber)
    Vang = numpy.zeros(nodeNumber)
    with open(VoltageFile,'r') as csvfileVoltage:
        csvreaderVoltage=csv.reader(csvfileVoltage)
        mycsvVoltage=list(csvreaderVoltage)
        for i in range(3, len(mycsvVoltage)-1): # skip source bus, rg60, 650 for 13bus
        #for i in range(3, len(mycsvVoltage)):
            row = mycsvVoltage[i]
            nodeName = row[0]
            if nodeName != "150R":
                nodeIndex = nodesOrder.index(row[0])
                vs[nodeIndex]["Vang"] = float(row[4])
                vs[nodeIndex]["Vmag"] = float(row[5])   #3 for actual 5 for pu   
                Vang[nodeIndex] = float(row[4])
                Vmag[nodeIndex] = float(row[5])  
    return networkGraph, Vmag, Vang


'''plot graph'''
def plotGraph(networkGraph):
    vs = networkGraph.vs
    for v in vs:
        v["label"] = v.index
 #   vs["label"] = vs["name"]
    vs["color"] = ["yellow" if (vertex["type"] == "load")  else "pink" for vertex in vs]
#    layout = networkGraph.layout("kk")
    igraph.plot(networkGraph,"13busPlot.png").show()
    return networkGraph


