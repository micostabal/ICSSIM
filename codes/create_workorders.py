import os, sys
import csv
from collections import defaultdict, deque
from clases import *
import pickle
from decimal import *
import pprint

def crear_wo(lugar):
    pp = pprint.PrettyPrinter(indent=4)

    items = defaultdict(int)

    file1 = open("WO/WO_{}".format(lugar),'rb')
    WO = pickle.load(file1)

    # Aquí va la decisión
    workorders = deque()
    workorders_verificacion = deque()

    demanda = defaultdict(int)

    i = 0
    for w in WO:
        if Decimal(str(round(w[1], 3))) > 0:
            wk = WorkOrder(w[0], Decimal(str(round(w[1], 3))), w[2],w[3],w[4])
            workorders.append(wk)
            workorders_verificacion.append(wk)


            demanda[w[0]] += Decimal(str(round(w[1], 3)))
    return {
    'workorders': workorders,
    'demanda': demanda
    }



if __name__ == '__main__':
    pass
