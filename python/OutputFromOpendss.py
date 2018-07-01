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

def getGraphInfo(LineFile, TransformerFile, GenFile, VoltageFile, LoadFile, QsupplyFile):
    networkGraph = igraph.Graph()

    '''line and transformer info'''
    networkGraph = getEdgeInfo(LineFile, TransformerFile, networkGraph)
    
    nodeListInOrder = []
    for v in networkGraph.vs:
        nodeListInOrder.append(v["name"])
    
    '''voltage info'''
    [networkGraph, Vmag, Vang] = getVoltageProfile(VoltageFile,networkGraph, nodeListInOrder)
    
    '''generator info'''
    networkGraph = getGenInfo(GenFile, networkGraph, nodeListInOrder)
    
    '''Qdemand Qsupply info'''
    networkGraph = getQdemandInfo(LoadFile, networkGraph, nodeListInOrder)
    networkGraph = getQsupplyInfo(QsupplyFile, networkGraph, nodeListInOrder)    
    
    return networkGraph, nodeListInOrder, Vmag, Vang

def getEdgeInfo(LineFile, TransformerFile, networkGraph):
    verticesList = []
    
    '''read line file'''
    f1 = open(LineFile,'r')
    f11 = f1.readlines()
    for x in f11:
        bus1 = re.findall(r'(?<=bus1=).+?(?= )',x)[0]
        bus2 = re.findall(r'(?<=bus2=).+?(?= )',x)[0]
        #if bus1 != "sourcebus" and bus2 != "sourcebus":     
        if bus1 not in verticesList:
            networkGraph.add_vertex(name=bus1)
            verticesList.append(bus1)
        if bus2 not in verticesList:
            networkGraph.add_vertex(name=bus2)
            verticesList.append(bus2)
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
        if bus1 not in verticesList:
            networkGraph.add_vertex(name=bus1)
            verticesList.append(bus1)
        if bus2 not in verticesList:
            networkGraph.add_vertex(name=bus2)
            verticesList.append(bus2)
        networkGraph.add_edge(bus1,bus2)
    return networkGraph    


def getVoltageProfile(VoltageFile, networkGraph, nodeListInOrder):
    vs = networkGraph.vs
    nodeNumber = len(nodeListInOrder)
    Vmag = numpy.zeros(nodeNumber)
    Vang = numpy.zeros(nodeNumber)
    with open(VoltageFile,'rb') as csvfileVoltage:
        csvreaderVoltage=csv.reader(csvfileVoltage)
        mycsvVoltage=list(csvreaderVoltage)
        for i in range(1, len(mycsvVoltage)):
            row = mycsvVoltage[i]
            if i ==1 or i ==2:
                nodeIndex = nodeListInOrder.index(row[0].lower())
            else:
                nodeIndex = nodeListInOrder.index(row[0])
            vs[nodeIndex]["voltageAngle"] = float(row[4])
            vs[nodeIndex]["voltageMag"] = float(row[5])       
            Vang[nodeIndex] = float(row[4])
            Vmag[nodeIndex] = float(row[5])  
            '''
            for node in networkGraph.vs:
                if row[0] == node["name"]:
                    node["voltageAngle"] = float(row[4])
                    node["voltageMag"] = float(row[5])
            '''
    return networkGraph, Vmag, Vang


def getGenInfo(GenFile, networkGraph, nodeListInOrder):
    vs = networkGraph.vs
    f1 = open(GenFile,'r')
    f11 = f1.readlines()
    for x in f11:
        if not x.startswith('!') and x != "\n":
            bus1 = re.findall(r'(?<=bus1=).+?(?=\ )',x)[0]
            genName = re.findall(r'(?<=Generator\.).+?(?=\")',x)[0]
            #if bus1 != "sourcebus":
            nodeIndex = nodeListInOrder.index(bus1)
            vs[nodeIndex]["type"] = "gen"
            vs[nodeIndex]["genName"] = genName
    return networkGraph

def getQdemandInfo(LoadFile, networkGraph, nodeListInOrder):
    vs = networkGraph.vs
    f1 = open(LoadFile,'r')
    f11 = f1.readlines()
    for x in f11:
        if not x.startswith('!'):
            Qd = re.findall(r'(?<=kvar=).+?(?=\n)',x)[0]
            nodeName = re.findall(r'(?<=Load\.).+?(?=\")',x)[0]
            #if bus1 != "sourcebus":
            nodeIndex = nodeListInOrder.index(nodeName)
            vs[nodeIndex]["Qd"] = float(Qd)
    for node in vs:
        if node["Qd"] == None:
            node["Qd"] = 0
    return networkGraph    

def getQsupplyInfo(QsupplyFile, networkGraph, nodeListInOrder):
    vs = networkGraph.vs
    with open(QsupplyFile,'rb') as csvfileQs:
        csvreaderQs=csv.reader(csvfileQs)
        mycsvQs=list(csvreaderQs)
        for i in range(1,len(mycsvQs)):
            row = mycsvQs[i]
            nodeName = row[0]
            Qs = row[1]
            nodeIndex = nodeListInOrder.index(nodeName)
            vs[nodeIndex]["Qs"] = float(Qs)
    for node in vs:
        if node["Qs"] == None:
            node["Qs"] = 0
    return networkGraph

def getYmatrix(YmatrixFile, nodeListInOrder):
    nodesInYFile = []
    with open(YmatrixFile,'rb') as csvfileY:
        csvreaderY=csv.reader(csvfileY)
        mycsvY=list(csvreaderY)
        nodeNumber = len(mycsvY)-1
        YGmatrix = numpy.zeros((nodeNumber,nodeNumber))
        YBmatrix = numpy.zeros((nodeNumber,nodeNumber))
        
        '''record node order in Y file'''
        for i in range(1,len(mycsvY)):
            row = mycsvY[i]
            nodesInYFile.append(row[0][:-2])
        
        '''find corresponding index order'''
        indexOrder = []
        for nodeName in nodesInYFile:
            indexOrder.append(nodeListInOrder.index(nodeName.lower())) 
            print nodeName
            print indexOrder
        
        '''get matrix'''
        for i in range(1,len(mycsvY)):
            row = mycsvY[i]
            if row[-1] == "" or row[-1] == " ":
                row.pop()
            n = 0
            j = 3
            while j < len(row):
                left = indexOrder[i-2]
                right = indexOrder[n]
                Gvalue = float(''.join((row[j]).split()))
                Bvalue = float(''.join((row[j+1]).split())[2:])
                YGmatrix[left][right] = Gvalue
                YBmatrix[left][right] = Bvalue
                j = j+2
                n = n+1
    return YGmatrix, YBmatrix
               


def getSVQ(YGmatrix, YBmatrix, Vmag, Vang, nodeListInOrder):
    nodeNumber = len(nodeListInOrder)
    Qcal = numpy.zeros(nodeNumber)
    JVQ = numpy.zeros((nodeNumber,nodeNumber))
    for i in range(0,nodeNumber):
        temp = 0
        for j in range(0, nodeNumber):
            if i!=j:
                Yij = complex(YGmatrix[i][j], YBmatrix[i][j])
                temp = temp-Vmag[i]*Vmag[j]*numpy.absolute(Yij)*math.sin(numpy.angle(Yij, deg=True)+Vang[j]-Vang[i])
            else:
                temp = temp-Vmag[i]*Vmag[i]*YBmatrix[i][i]
        Qcal[i] = temp
    
    for i in range(0, nodeNumber):
        for j in range(0, nodeNumber):
            if i != j:
                Yij = complex(YGmatrix[i][j], YBmatrix[i][j])
                JVQ[i,j] = -Vmag[i]*Vmag[j]*numpy.absolute(Yij)*math.sin(numpy.angle(Yij, deg=True)+Vang[j]-Vang[i])
            else:
                JVQ[i,i] = Qcal[i]-Vmag[i]*Vmag[i]*YBmatrix[i][i]
    
    SVQ = numpy.linalg.inv(JVQ)
    return SVQ
    


    
    
    
    
    
'''
YmatrixFile = '../opendss/13positivebus/ieee13nodeckt_EXP_Y.CSV'
getYmatrix(YmatrixFile)


'''