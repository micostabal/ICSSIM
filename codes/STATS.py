from collections import namedtuple as nt
import pickle
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm, normaltest
from random import choice, randint
import matplotlib.patches as mpatches

RMIBIN = nt('RMIBIN', 'loc id colour qty cap')
PFIBIN = nt('PFIBIN', 'loc id cap')
PACKBIN = nt('PACKBIN', 'loc id cap')
Order = nt('Order', 'id color size flavor pack qty')
with open('factory.pkl', 'rb') as f:
    factory = pickle.load(f)

sites = ['Detroit', 'Columbus', 'Green Bay', 'Springfield', 'Omaha']

pfo_stats = {site: {'avg': 0, 'std': 0} for site in sites}
pack_stats = {(site, cont): {'avg': 0, 'std': 0} for site in sites for cont in ['Bag', 'Box']}
plotear = False


## Estadísticas de Packing
for lugar in sites:
    for pack in ['Bag', 'Box']:
        data = []

        for size in range(1, 6):
            data += factory['pack_times'][(lugar, size, pack)]

        alpha = 0.001

        mu, std = norm.fit(data)
        pack_stats[(lugar, pack)]['avg'] = mu
        pack_stats[(lugar, pack)]['std'] = std

        if plotear:
            plt.figure()
            plt.hist(data, 50, density=True)
            xmin, xmax = plt.xlim()
            x = np.linspace(xmin, xmax, 100)
            p = norm.pdf(x, mu, std)
            plt.plot(x, p, 'k', linewidth=2)
            plt.title('Aggregated Packaging Rates of {} in {}'.format(lugar, pack))
            plt.xlabel('Rate of Packaging (Mean: {}, Std: {}, p-value: {})'.format(round(mu, 3), round(std, 3), round(normaltest(data).pvalue, 5)))
            plt.ylabel('Normalized Frequency')
            red_patch = mpatches.Patch(color='black', label='Normal Fit')
            blue_patch = mpatches.Patch(color=None, label='Data')
            plt.legend(handles=[red_patch, blue_patch])
            plt.show()
            plt.savefig('ImgsPACK\\{}_packing_{}.png'.format(lugar, pack))

            print(mu, std, mu/std)
            print("N: ", len(data))
            if normaltest(data).pvalue < alpha:
                print('Hay una distribución no significativa!')
            plt.clf()


"""
# Packing para un tipo en particular
lugar = 'Columbus'
pack = 'Bag'
size = 3
alpha = 0.001

data = factory['pack_times'][(lugar, size, pack)]
mu, std = norm.fit(data)
pack_stats[(lugar, pack)]['avg'] = mu
pack_stats[(lugar, pack)]['std'] = std

if plotear:
    plt.figure()
    plt.hist(data, 50, density=True)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2)
    plt.title('Packaging Rates of {}, size {} in {}'.format(lugar, size, pack))
    plt.xlabel('Rate of Packaging (Mean: {}, Std: {}, p-value: {})'.format(round(mu, 3), round(std, 3), round(normaltest(data).pvalue, 5)))
    plt.ylabel('Normalized Frequency')
    red_patch = mpatches.Patch(color='black', label='Normal Fit')
    blue_patch = mpatches.Patch(color=None, label='Data')
    plt.legend(handles=[red_patch, blue_patch])
    plt.show()
    #plt.savefig('ImgsPACK\\{}_packing_{}.png'.format(lugar, pack))

    print(mu, std, mu/std)
    print("N: ", len(data))
    if normaltest(data).pvalue < alpha:
        print('Hay una distribución no significativa!')
    plt.clf()
"""


# Estadísicas de PFO:
for lugar in sites:

    data = []
    for size in range(1, 6):
        for flavor in range(1, 13):
            data += factory['pfo_times'][(lugar, size, flavor)]

    alpha = 0.001

    mu, std = norm.fit(data)
    pfo_stats[lugar]['avg'] = mu
    pfo_stats[lugar]['std'] = std

    if plotear:
        plt.figure()
        plt.hist(data, 50, density=True)
        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mu, std)
        plt.plot(x, p, 'k', linewidth=2)
        plt.title('Aggregated Pre Finish processing rates in {}.'.format(lugar))
        plt.xlabel('Rate of Pre Finish (Mean: {}, Std: {}, p-value: {})'.format(round(mu, 3), round(std, 3), round(normaltest(data).pvalue, 5)))
        plt.ylabel('Normalized Frequency')
        red_patch = mpatches.Patch(color='black', label='Normal Fit')
        blue_patch = mpatches.Patch(color=None, label='Data')
        plt.legend(handles=[red_patch, blue_patch])
        plt.show()
        #plt.savefig('ImgsPFO\\{}_pfo.png'.format(lugar))

        print(mu, std, mu/std)
        print("N: ", len(data))
        if normaltest(data).pvalue < alpha:
            print('Hay una distribución no significativa!')
        plt.clf()



if __name__ == '__main__':
    # SE pueden ver las estadísticas.
    #print(pfo_stats)
    #print(pack_stats)
    pass
