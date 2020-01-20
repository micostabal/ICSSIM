from collections import namedtuple as nt

RMIBIN = nt('RMIBIN', 'loc id colour qty cap')
PFIBIN = nt('PFIBIN', 'loc id cap')
PACKBIN = nt('PACKBIN', 'loc id cap')
Order = nt('Order', 'id color size flavor pack qty')

from simulation import simular

def resumen_general():
    wo_time = 0
    total_time = 0
    total_cost = 0
    final_porcentaje = 0
    for i in range(1, 6):
        s_act = simular(str(i))
        print(s_act)
        wo_time = max(s_act['tiempo_wo'], wo_time)
        total_time = max(s_act['tiempo_total'], total_time)
        total_cost += s_act['costo_total']
        final_porcentaje += s_act['porcentaje_cubierto']

    return {
    'tiempo_wo': wo_time,
    'tiempo_total': total_time,
    'costo_total': total_cost,
    'demanda_cubierta': final_porcentaje
    }

if __name__ == '__main__':
    rg1 = resumen_general()

    print("---------------------\nResultados agregados\n")
    print(rg1)
