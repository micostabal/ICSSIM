# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 20:20:22 2020

@author: savas
"""

with open('RMI_mod.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(['Location Name', 'Drum', 'Color', 'Qty', 'Capacity'])
    for p in P:
        for i in x[p]:
            writer.writerow([p, i[0], i[1], round(x[p][i], 5), Capacity_RMI[p]])
        for b in B[p]:
            if b not in [j[0] for j in x[p].keys()]:
                writer.writerow([p, b, '', '', Capacity_RMI[p]])