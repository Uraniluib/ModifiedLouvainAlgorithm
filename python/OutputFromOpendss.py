# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 14:16:10 2018

@author: Lusha
"""

import csv
import matplotlib.pylab as plt
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

def getYmatrix(YmatrixFile):
    nodesOrder = []
    with open(YmatrixFile,'rb') as csvfileY:
        csvreaderY=csv.reader(csvfileY)
        mycsvY=list(csvreaderY)
        nodeNumber = int(mycsvY[0][0])
        YGmatrix = numpy.zeros((nodeNumber,nodeNumber))
        YBmatrix = numpy.zeros((nodeNumber,nodeNumber))
        for i in range(1,len(mycsvY)):
            row = mycsvY[i]
            nodesOrder.append(row[0][:-2])
            if row[-1] == "" or row[-1] == " ":
                row.pop()
            m = 0
            j = 1
            while j < len(row):
                Gvalue = float(''.join((row[j]).split()))
                Bvalue = float(''.join((row[j+1]).split())[2:])
                YGmatrix[i-1][m] = Gvalue
                YBmatrix[i-1][m] = Bvalue
                j = j+2
                m = m+1
    print nodesOrder
    print YGmatrix
    print YBmatrix
               

def getVoltageProfile(VoltageFile):
    voltageList={}
    with open(VoltageFile,'rb') as csvfileVoltage:
        csvreaderVoltage=csv.reader(csvfileVoltage)
        mycsvVoltage=list(csvreaderVoltage)
        for row in mycsvVoltage:
            if  row[0]!= str("Bus") and row[0]!=str("RG60") and row[0]!=str("SOURCEBUS") and row[0]!=str("650"):
                voltageList[row[0]]=float(row[5])
            if row[0]==str("650"):
                voltageList["1"] = float(row[5])
    print voltageList
    print list(voltageList.values())
    return voltageList
    

def plotVoltageProfile(voltageList):
    lists = sorted(voltageList.items())
    x,y = zip(*lists)
    plt.ylim(0.99, 1.06)
    plt.plot(x,y)
    plt.plot((0,692),(1.05,1.05),'r')
    plt.show()
    
    
YmatrixFile = '../opendss/13positivebus/ieee13nodeckt_EXP_Y.CSV'
getYmatrix(YmatrixFile)


