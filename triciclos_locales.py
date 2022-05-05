# -*- coding: utf-8 -*-
"""
3. 3-CICLOS LOCALES
Queremos calcular los 3-ciclos, pero sólamente aquellos que sean locales a cada 
uno de los cheros
"""
from pyspark import SparkContext
import sys

def get_edges(line): 
    edge = line.strip().split(',')
    n1 = edge[0]
    n2 = edge[1]
    if n1 < n2:
         return (n1,n2)
    elif n1 > n2:
         return (n2,n1)
    else:
        pass 
          
    
def get_rdd_distict_edges(sc, filename):
    return sc.textFile(filename).\
        map(get_edges).\
        filter(lambda x: x is not None).\
        distinct()


def adjacents(sc, filename):
    nodes = get_rdd_distict_edges(sc, filename)
    adj = nodes.groupByKey().mapValues(list)
    return adj


def tuples(tuple):
    list = []
    for i in range(len(tuple[1])):
        list.append(((tuple[0], tuple[1][i]), "exists"))
        if len(tuple[1]) > 1:
            for j in range(len(tuple[1])):
                k = j + 1
                while k < len(tuple[1]):
                    if tuple[1][k] > tuple[1][j]:
                        list.append(((tuple[1][j], tuple[1][k]), ("pending", tuple[0])))
                    else: 
                        list.append(((tuple[1][k], tuple[1][j]), ("pending", tuple[0])))
                    k += 1
    return list


def tricicles(tuple): 
    list = []
    for tup in tuple[1]:
        if tup == "exists":
            pass
        else:
            list.append([tuple[0][0], tuple[0][1], tup[1]])
    return list
   
    
def list_tricicles(sc, filenames):
    adj_list= []
    for file in filenames:
        adj = adjacents(sc, file).\
                flatMap(tuples).\
                distinct().\
                groupByKey().\
                mapValues(list).\
                filter(lambda x: "exists" in x[1] and len(x[1])>1).\
                flatMap(tricicles).\
                map(lambda x : (file, x))        
        tuple = []
        tuple.append([adj.collect()[0][0]])
        tuple.append([])
        for i in adj.collect():
            tuple[1].append(i[1])
        adj_list.append(tuple)
    return adj_list

    
def main(sc, filenames):
    result = list_tricicles(sc, filenames)
    print(result)
    
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: {0} <file1> <file2< ...".format(sys.argv[0]))
    else:
        with SparkContext() as sc:
            sc.setLogLevel("ERROR")
            main(sc, sys.argv[1:])

 
