from some_functions import *
from numpy import argmin
from collections import defaultdict
import pprint
import math
from decimal import *


def pfo_while(tiempo, classifier, prefinishmachines_d, packagingmachines_d, rmidrums_d, pfidrums_d, pidrums_d, workorders_vigentes_prefinish, workorders_vigentes_packaging, workorder_pfo, produced_colors_sizes, produced_colors_sizes_flavors, printear, desperdicios):
    # Si no está procesando PFO, hago que procese

    veces_setup = 0
    while pfo_not_working(prefinishmachines_d):

        pfi_vaciar, workorder_pfo = None, None
        pfi_vaciar, workorder_pfo = get_first_pfi_lleno(pfidrums_d, workorders_vigentes_prefinish, tiempo)

        # if len(desperdicios): print(pfi_vaciar, list(sorted(pfidrums_d, key=lambda pfi: pfi.tiempo_fifo[0]))[0])

        if not pfi_vaciar:
            break

        pfo_usar = get_pfo_not_working(prefinishmachines_d)

        desperdicio = False
        if not workorder_pfo:
            desperdicio = True

        pi_llenar = hay_pi(pidrums_d, pfi_vaciar, desperdicio, workorder_pfo)

        if desperdicio and pi_llenar:
            flavor = pfo_usar.flavor if pfo_usar.flavor else "F8"
            workorder_pfo = WorkOrder(pfi_vaciar.color, min(pfi_vaciar.inventory, pi_llenar.capacity - pi_llenar.inventory), pfi_vaciar.size, "Bag", flavor)

        if pi_llenar and workorder_pfo:
            cantidad_color_size = min(workorder_pfo.qty - produced_colors_sizes_flavors[workorder_pfo.color][workorder_pfo.size][workorder_pfo.flavor], pfi_vaciar.inventory, pi_llenar.capacity - pi_llenar.inventory)

            if not desperdicio:
                if pfi_vaciar.tiempo_fifo[0][1] - cantidad_color_size == 0:
                    pfi_vaciar.tiempo_fifo.popleft()
                elif pfi_vaciar.tiempo_fifo[0][1] - cantidad_color_size < 0 and pfi_vaciar.inventory != cantidad_color_size:

                    restante = cantidad_color_size - pfi_vaciar.tiempo_fifo[0][1]
                    pfi_vaciar.tiempo_fifo.popleft()
                    pfi_vaciar.tiempo_fifo[0][1] -= restante
                else:
                    pfi_vaciar.tiempo_fifo[0][1] -= cantidad_color_size

                if not pfi_vaciar.tiempo_fifo:
                    pfi_vaciar.tiempo_fifo.append([9999999999999999999999999999999, 0])


            pfi_vaciar.vaciandose = True
            pfo_usar.activo = True

            flavor_anterior = pfo_usar.flavor

            pfo_usar.flavor = workorder_pfo.flavor if (workorder_pfo.color == pfi_vaciar.color and workorder_pfo.size == pfi_vaciar.size) else (pfo_usar.flavor if pfo_usar.flavor else "F8")
            workorder_pfo.flavor = pfo_usar.flavor
            pfo_usar.color = pfi_vaciar.color
            pfo_usar.size = pfi_vaciar.size
            pfo_usar.pi_asignado = pi_llenar
            pfo_usar.pfi_asignado = pfi_vaciar



            pfi_vaciar.inventory -= cantidad_color_size

            if desperdicio:
                pfi_vaciar.tiempo_fifo = deque()
                pfi_vaciar.tiempo_fifo.append([9999999999999999999999999999999, 0])

            pfo_usar.processing = cantidad_color_size
            pfo_usar.workorder_actual = workorder_pfo
            pfo_usar.finish = tiempo + cantidad_color_size/pfo_usar.process_rate * 3600


            if flavor_anterior != pfo_usar.flavor:
                pfo_usar.finish += 60*5
                veces_setup += 1

            produced_colors_sizes_flavors[pfo_usar.color][pfo_usar.size][pfo_usar.flavor] += pfo_usar.processing


            if desperdicio:
                #print(f"Desperdicio: {pfo_usar.processing} de la WorkOrder {workorder_pfo}")
                desperdicios.append([pfo_usar.color, pfo_usar.size, float(pfo_usar.processing)])

                produced_colors_sizes[pfo_usar.color][pfo_usar.size] -= pfo_usar.processing
                if produced_colors_sizes[pfo_usar.color][pfo_usar.size] < 0:
                    print(f"Workorder procesando actual desperdicio: {workorder_pfo}")
                    if workorders_vigentes_prefinish:
                        print(print_state(classifier, pidrums_d, pfidrums_d, rmidrums_d, packagingmachines_d, prefinishmachines_d))
                        print(f"Workorder procesando real: {workorders_vigentes_prefinish[0]}")

                    print(produced_colors_sizes[pfo_usar.color][pfo_usar.size])
                    raise ValueError("Error creado por Caco, se restó algo negativo")

            pi_llenar.llenandose = True

            if pi_llenar.tiempo_fifo[0] == [9999999999999999999999999999999, 0]:
                x = pi_llenar.tiempo_fifo.popleft()
            pi_llenar.tiempo_fifo.append([tiempo, pfo_usar.processing])

            """
                Acá se actualiza la workorder
            """

            if workorder_pfo.qty <= produced_colors_sizes_flavors[workorder_pfo.color][workorder_pfo.size][workorder_pfo.flavor]:

                if not desperdicio:
                    workorders_vigentes_packaging.append(workorder_pfo)
                    workorders_vigentes_prefinish.remove(workorder_pfo)
                else:
                    workorders_vigentes_packaging.append(workorder_pfo)

                produced_colors_sizes_flavors[workorder_pfo.color][workorder_pfo.size][workorder_pfo.flavor] -= workorder_pfo.qty

            if printear:
                print(print_state(classifier, pidrums_d, pfidrums_d, rmidrums_d, packagingmachines_d, prefinishmachines_d))

        else:
            break
    return veces_setup


def pckg_while(tiempo, cantidad_total_workorders, classifier, prefinishmachines_d, rmidrums_d, pfidrums_d, pidrums_d, packagingmachines_d, workorders_vigentes_prefinish, workorders_vigentes_packaging, workorder_pckg, workorder_pfo, produced_colors_sizes, produced_colors_sizes_flavors, final_produced, final_inventory, workorders_inventory, printear):
    # Si no está procesando PCKG, hago que procese
    while workorders_vigentes_packaging:

        pi_vaciar, workorder_pckg = None, None
        pi_vaciar, workorder_pckg = get_first_pi_lleno(pidrums_d, workorders_vigentes_packaging)

        # Si no hay, recorremos las workorders

        # Buscamos la workorder
        if not workorder_pckg or not pi_vaciar:
            break

        if printear: print(pi_vaciar)

        pckg_usar = get_pckg_not_working(packagingmachines_d, workorder_pckg)

        if not pckg_usar:
            break


        pi_vaciar.vaciandose = True

        cantidad_color_size_flavor = min(workorder_pckg.qty - final_produced[workorder_pckg.color][workorder_pckg.size][workorder_pckg.flavor][workorder_pckg.package], pi_vaciar.inventory)
        pckg_usar.flavor = pi_vaciar.flavor
        pckg_usar.color = pi_vaciar.color
        pckg_usar.size = pi_vaciar.size
        pckg_usar.pi_asignado = pi_vaciar

        pi_vaciar.inventory -= cantidad_color_size_flavor

        if pi_vaciar.tiempo_fifo[0][1] - cantidad_color_size_flavor == 0:
            pi_vaciar.tiempo_fifo.popleft()
        elif pi_vaciar.tiempo_fifo[0][1] - cantidad_color_size_flavor < 0 and pi_vaciar.inventory != cantidad_color_size_flavor:
            restante = cantidad_color_size_flavor - pi_vaciar.tiempo_fifo[0][1]
            pi_vaciar.tiempo_fifo.popleft()
            pi_vaciar.tiempo_fifo[0][1] -= restante
        else:
            pi_vaciar.tiempo_fifo[0][1] -= cantidad_color_size_flavor

        if not pi_vaciar.tiempo_fifo:
            pi_vaciar.tiempo_fifo.append([9999999999999999999999999999999, 0])


        if pi_vaciar.inventory == 0:
            pi_vaciar.tiempo_fifo = deque()
            pi_vaciar.tiempo_fifo.append([9999999999999999999999999999999, 0])

        pckg_usar.processing = cantidad_color_size_flavor
        pckg_usar.activo = True
        pckg_usar.finish = tiempo + cantidad_color_size_flavor/pckg_usar.process_rate * 3600


        final_produced[pckg_usar.color][pckg_usar.size][pckg_usar.flavor][pckg_usar.type] += pckg_usar.processing
        final_inventory[pckg_usar.color][pckg_usar.size][pckg_usar.flavor][pckg_usar.type] += pckg_usar.processing
        if workorder_pckg.id < cantidad_total_workorders:
            workorders_inventory[pckg_usar.color][pckg_usar.size][pckg_usar.flavor][pckg_usar.type] += pckg_usar.processing

        """
            Acá se actualiza la workorder
        """
        if workorder_pckg.qty <= final_produced[workorder_pckg.color][workorder_pckg.size][workorder_pckg.flavor][workorder_pckg.package]:
            final_produced[workorder_pckg.color][workorder_pckg.size][workorder_pckg.flavor][workorder_pckg.package] -= workorder_pckg.qty
            workorders_vigentes_packaging.remove(workorder_pckg)

        if printear:
            print(print_state(classifier, pidrums_d, pfidrums_d, rmidrums_d, packagingmachines_d, prefinishmachines_d))
