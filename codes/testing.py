
from clases import *
from collections import defaultdict
import os, sys
import csv
from decimal import *
import pickle

with open("desperdicios", "rb") as file:
    data = pickle.load(file)

print(data)

with open("workorders_eliminadas", "rb") as file:
    data2 = pickle.load(file)

print(data2)
