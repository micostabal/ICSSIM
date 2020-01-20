from clases import *
from collections import defaultdict
from collections import namedtuple as nt
import os, sys
import csv
from decimal import *

RMIBIN = nt('RMIBIN', 'loc id colour qty cap')
PFIBIN = nt('PFIBIN', 'loc id cap')
PACKBIN = nt('PACKBIN', 'loc id cap')
Order = nt('Order', 'id color size flavor pack qty')

from STATS import pack_stats, pfo_stats



# Cargamos los porcentajes de clasificación en un diccionario
porcentajes = defaultdict(dict)

with open('../data/Classifier Split.csv', "r") as file:
    for linea in file.readlines()[1:]:
        color, size, p = linea.strip("\r").strip("\n").split(",")
        porcentajes[color][size] = Decimal(p)/100

# Cargamos los distintos Classifiers
classifiers = []

with open("../data/Classifier.csv", "r") as file:
    for linea in file.readlines()[1:]:
        site, id, rate = linea.strip("\r").strip("\n").split(",")
        classifiers.append(ClassifierMachine(site, Decimal(rate.strip('"')), id))

# Cargamos los PIDrum
pidrums = []

with open('../data/Pack inventory Drum.csv', "r") as file:
    for linea in list(csv.reader(file, delimiter=","))[1:]:
        site, id, cap = linea
        pidrums.append(PIDrum(id, site, Decimal(cap.strip('"').replace(",", ""))))

# Cargamos las distintas PackageMachine
packagingmachines = []

with open('../data/Packaging.csv', "r") as file:
    rate_sum = 0
    lineas = 0
    counter = 0
    dicc = defaultdict(lambda: defaultdict(dict))
    site2, size2, type2, rate2 = ["", "", "", ""]
    for linea in file.readlines()[1:]:
        site, size, type, rate = linea.strip("\r").strip("\n").split(",")
        if ([site, size, type] == [site2, size2, type2]) or not lineas:
            rate_sum += int(rate)
            counter += 1
        else:
            dicc[site2][type2][size2] = int(rate_sum)/counter
            rate_sum = 0
            counter = 0
        site2, size2, type2, rate2 = linea.strip("\r").strip("\n").split(",")
        lineas += 1
    dicc[site2][type2][size2] = int(rate_sum)/counter

    """
    for site in dicc:
        if site == "Detroit" or site == "Springfield" or site == "Green Bay" or site == "Omaha":
            packagingmachines.append(PackageMachine(site, "Bag", dicc[site]["Bag"]))
            packagingmachines.append(PackageMachine(site, "Box", dicc[site]["Box"]))
        elif site == "Columbus":
            packagingmachines.append(PackageMachine(site, "Bag", dicc[site]["Bag"]))
            packagingmachines.append(PackageMachine(site, "Bag", dicc[site]["Bag"]))
            packagingmachines.append(PackageMachine(site, "Box", dicc[site]["Box"]))
    """
    for site in dicc:
        if site == "Detroit" or site == "Springfield" or site == "Green Bay" or site == "Omaha":
            packagingmachines.append(PackageMachine(site, "Bag", pack_stats[(site, 'Bag')]['avg'], pack_stats[(site, 'Bag')]['std']))
            packagingmachines.append(PackageMachine(site, "Box", pack_stats[(site, 'Bag')]['avg'], pack_stats[(site, 'Bag')]['std']))
        elif site == "Columbus":
            packagingmachines.append(PackageMachine(site, "Bag", pack_stats[(site, 'Bag')]['avg'], pack_stats[(site, 'Bag')]['std']))
            packagingmachines.append(PackageMachine(site, "Bag", pack_stats[(site, 'Bag')]['avg'], pack_stats[(site, 'Bag')]['std']))
            packagingmachines.append(PackageMachine(site, "Box", pack_stats[(site, 'Bag')]['avg'], pack_stats[(site, 'Bag')]['std']))



# Cargamos los PFIDrum
pfidrums = []

with open('../data/Pre-finish Inventory Drum.csv', "r") as file:
    for linea in list(csv.reader(file, delimiter=","))[1:]:
        site, id, cap = linea
        pfidrums.append(PFIDrum(id, site, Decimal(cap.strip('"').replace(",", ""))))


# Cargamos las PrefinishMachine
prefinishmachines = []

with open('../data/Pre-finish.csv', "r") as file:
    rate_sum = 0
    lineas = 0
    counter = 0
    dicc = defaultdict(lambda: defaultdict(dict))
    site2, size2, flavor2, rate2 = ["", "", "", ""]
    for linea in file.readlines()[1:]:
        site, size, flavor, rate = linea.strip("\r").strip("\n").split(",")
        if [site, size, flavor] == [site2, size2, flavor2] or not lineas:
            rate_sum += int(rate)
            counter += 1
        else:
            dicc[site2][size2][flavor2] = int(rate_sum)/counter
            rate_sum = 0
            counter = 0
        site2, size2, flavor2, rate2 = linea.strip("\r").strip("\n").split(",")
        lineas += 1
    dicc[site2][size2][flavor2] = int(rate_sum)/counter

    """
    for site in dicc:
        if site == "Detroit" or site == "Green Bay":
            prefinishmachines.append(PrefinishMachine(site, dicc[site]))
            prefinishmachines.append(PrefinishMachine(site, dicc[site]))
        elif site == "Columbus" or site == "Omaha":
            prefinishmachines.append(PrefinishMachine(site, dicc[site]))
            prefinishmachines.append(PrefinishMachine(site, dicc[site]))
            prefinishmachines.append(PrefinishMachine(site, dicc[site]))
        elif site == "Springfield":
            prefinishmachines.append(PrefinishMachine(site, dicc[site]))
    """
    for site in dicc:
        if site == "Detroit" or site == "Green Bay":
            prefinishmachines.append(PrefinishMachine(site, pfo_stats[site]['avg'], pfo_stats[site]['std']))
            prefinishmachines.append(PrefinishMachine(site, pfo_stats[site]['avg'], pfo_stats[site]['std']))
        elif site == "Columbus" or site == "Omaha":
            prefinishmachines.append(PrefinishMachine(site, pfo_stats[site]['avg'], pfo_stats[site]['std']))
            prefinishmachines.append(PrefinishMachine(site, pfo_stats[site]['avg'], pfo_stats[site]['std']))
            prefinishmachines.append(PrefinishMachine(site, pfo_stats[site]['avg'], pfo_stats[site]['std']))
        elif site == "Springfield":
            prefinishmachines.append(PrefinishMachine(site, pfo_stats[site]['avg'], pfo_stats[site]['std']))


# Cargamos los RMIDrum
rmidrums = []

with open('../data/RMI_mod.csv', "r") as file:
    for linea in list(csv.reader(file, delimiter=","))[1:]:
        site, id, color, inventory, cap = linea
        inventory = inventory if inventory else 0
        rmidrums.append(RMIDrum(id, site, color, Decimal(inventory), Decimal(cap)))
