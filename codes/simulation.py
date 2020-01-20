
from some_functions import *
from create_workorders import crear_wo
from numpy import argmin
from collections import defaultdict
from collections import namedtuple as nt
import pprint
import math
from decimal import *
from all_process import *
import pickle
import csv

RMIBIN = nt('RMIBIN', 'loc id colour qty cap')
PFIBIN = nt('PFIBIN', 'loc id cap')
PACKBIN = nt('PACKBIN', 'loc id cap')
Order = nt('Order', 'id color size flavor pack qty')

from loading_city import *

ciudades = """

Hola

Elige una planta

Detroit: 1
Columbus: 2
Green Bay: 3
Springfield: 4
Omaha: 5

"""

"""
options = {"1": ("Detroit", "Detroit, MI"),
           "2": ("Columbus", "Columbus, OH"),
           "3": ("Green Bay", "Green Bay, WI"),
           "4": ("Springfield", "Springfield, MO"),
           "5": ("Omaha", "Omaha, NE")}

planta = input(ciudades)
while planta not in ["1", "2", "3", "4", "5"]:
    print()
    print("ERROR")
    print()
    print("Ingresa un número del 1 al 5")
    planta = input(ciudades)
"""

"""
Tengo:

porcentajes: diccionario con la proporcion de cada size al pasar un color
classifiers: todas las ClassifierMachine (site, rate, id)
pidrums: todos los PIDrum (id, site, capacity)
pfidrums: todos los PFIDrum (id, site, capacity)
rmidrums: todos los RMIDrum (id, site, color, capacity, inventory)
packagingmachines: todas las PackageMachine (site, size, type, rate)
prefinishmachines: todas las PrefinishMachine (site, size, flavor, rate)

"""

def simular(planta):


    options = {"1": ("Detroit", "Detroit, MI"),
               "2": ("Columbus", "Columbus, OH"),
               "3": ("Green Bay", "Green Bay, WI"),
               "4": ("Springfield", "Springfield, MO"),
               "5": ("Omaha", "Omaha, NE")}



    name, lname = options[planta]

    workorders = crear_wo(name)['workorders']
    demanda = crear_wo(name)['demanda']

    # Primero trabajaremos con la ciudad de Detroit
    classifier_d = [clas for clas in classifiers if clas.site == '"'+name+'"']
    pidrums_d = [drum for drum in pidrums if drum.site == lname]
    pfidrums_d = [drum for drum in pfidrums if drum.site == lname]
    rmidrums_d = [drum for drum in rmidrums if drum.site == name]
    packagingmachines_d = [pckg for pckg in packagingmachines if pckg.site == name]
    prefinishmachines_d = [pckg for pckg in prefinishmachines if pckg.site == name]

    eliminadas = []

    # Printeo
    pp = pprint.PrettyPrinter(indent=4)
    printear = False

    for x in rmidrums_d:
        demanda[x.color] -= x.inventory

    # pp.pprint(demanda)

    """
    Orden:

    RMI -> CLASSIFIER -> PREFINISH -> PFI -> PFO -> PI -> PACKAGING

    """

    capacidad_pfi = 10000*0.95
    capacidad_pi = 20000*0.95
    initial = 10
    over = False

    # Outputs
    desperdicios = []

    tiempo = 0 # En segundos
    terminado = False
    jellys = []
    workorder = None
    workorder_pfo = None
    workorder_pckg = None
    desperdicio = False
    veces_setup = 0
    vaciando_final = False
    imprimir_tiempo = False
    modificadas = []
    cantidad_total_workorders = len(workorders)

    # Workorders vigentes en cada máquina
    workorders_vigentes_prefinish = deque()
    workorders_vigentes_packaging = deque()

    # Cantidad producida de cada rama
    produced_colors_sizes = defaultdict(lambda: defaultdict(Decimal))
    produced_colors_sizes_flavors = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))
    final_produced = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal))))
    final_inventory = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal))))
    workorders_inventory = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal))))

    vaciando_rmi = False

    # Tiempos de todas las máquinas
    maquinas = classifier_d + packagingmachines_d + prefinishmachines_d
    classifier = classifier_d[0]

    if not printear:
        string = """
            Simulación ISC Competition

            Si quieres printear el estado de la simulación, cambia la variable printear a True

            Al final del código está el print con el inventario final

            Se printeará cada 100 horas si no está el printear activado

        """
        print(string)

    while (workorders or workorders_vigentes_packaging or workorders_vigentes_prefinish or not todo_vacio([rmidrums_d, pfidrums_d, pidrums_d], [classifier_d, packagingmachines_d, prefinishmachines_d])):

        if vaciando_final and not imprimir_tiempo:
            boolean = is_demand_complete(workorders, workorders_vigentes_prefinish, workorders_vigentes_packaging, cantidad_total_workorders)
            if boolean:
                print(f"\n\nTerminaron las WO's en {round(tiempo/3600/(24*30), 4)} meses. \n\n")
                tiempo_termino_wo = round(tiempo/3600/(24*30), 4)
                imprimir_tiempo = True

        # Si se acabó todo y quedan RMIS

        if not (workorders or (workorders_vigentes_prefinish and not vaciando_final) or (workorders_vigentes_packaging and not vaciando_final)) and get_first_rmi_faltante(rmidrums_d) and not classifier.activo:
            rmi_faltante = get_first_rmi_faltante(rmidrums_d)
            porcentajes_color_del_rmi = porcentajes[rmi_faltante.color]

            if not vaciando_final:
                x = input(f"Vaciando RMIS... Enter para seguir")
                print("Esto es lo que queda de los RMI")

                total_rmis = []

                for rmi in rmidrums_d:
                    print(rmi)
                    total_rmis.append([rmi.color, rmi.inventory])

                with open('generated/RMI_mod_sobrante.csv', 'w', newline='') as file:
                    writer = csv.writer(file, delimiter=',')
                    writer.writerow(['Location Name', 'Drum', 'Color', 'Qty', 'Capacity'])
                    for rmi in rmidrums:
                        writer.writerow([rmi.site, rmi.id, rmi.color, float(rmi.inventory), float(rmi.capacity)])

                print("\n")
                vaciando_final = True


            # Actualizamos inventario de RMI
            if rmi_faltante.inventory < 300:
                rmi_faltante.inventory = round(rmi_faltante.inventory, 1)


            # Creamos una workorder
            if Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S1"])) > 0:
                workorders.append(WorkOrder(rmi_faltante.color, Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S1"])), "S1", "Bag", "F1"))
            if Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S2"])) > 0:
                workorders.append(WorkOrder(rmi_faltante.color, Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S2"])), "S2", "Bag", "F1"))
            if Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S3"])) > 0:
                workorders.append(WorkOrder(rmi_faltante.color, Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S3"])), "S3", "Bag", "F1"))
            if Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S4"])) > 0:
                workorders.append(WorkOrder(rmi_faltante.color, Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S4"])), "S4", "Bag", "F1"))
            if Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S5"])) > 0:
                workorders.append(WorkOrder(rmi_faltante.color, Decimal(str(min(300, rmi_faltante.inventory)*porcentajes_color_del_rmi["S5"])), "S5", "Bag", "F1"))


            classifier.finish = tiempo

        proximo = min(maquinas, key=lambda maquina: maquina.finish)
        tiempo = proximo.finish


        if printear:
            print(f"Tiempo: {round(tiempo/3600, 4)} horas. Se viene {proximo}")

        if not printear and tiempo/3600 > initial:
            print(f"Tiempo: {tiempo//3600} horas. Aprox. {round(tiempo/3600/(24*30), 2)} meses")
            initial += 100

        if tiempo > 99999999999999:
            print("\nHubo un error en la simulación. Por favor avisarle al Caco con las workorders que metieron y la planta")
            print("Estas son las estadísticas por ahora\n")
            print(print_state(classifier, pidrums_d, pfidrums_d, rmidrums_d, packagingmachines_d, prefinishmachines_d))
            print("Workorders iniciales faltantes:", len(workorders), "Workorders prefinish faltantes:", len(workorders_vigentes_prefinish), "Workorders packaging faltantes:", len(workorders_vigentes_packaging))

            print(f"Cantidad de eliminadas: {len(eliminadas)}")
            print(f"Cambios de setup: {veces_setup}")

            for x in rmidrums_d:
                print(x)

            for wk in eliminadas:
                print(wk)


            over = True
            break



        # Si el próximo es el término de un Classifier
        if proximo == classifier:
            classifier.finish = 99999999999999999999999999999999999999999

            if classifier.activo:
                # Agrego inventario de los PFIS
                add_inventory_pfis(pfis_destino, cantidades_size, classifier.color, workorder)

                for pfi in pfis_destino:
                    pfi.llenandose = False
                    classifier.activo = False

                classifier.processing = 0

                if printear:
                    print(print_state(classifier, pidrums_d, pfidrums_d, rmidrums_d, packagingmachines_d, prefinishmachines_d))



            # Veo si con lo actual cubro las workorders vigentes
            if not vaciando_rmi and workorders:
                # Si es la primera workorder
                if not workorder:
                    workorder = workorders[0]
                # Si es otra
                else:
                    while workorder and workorder.qty <= produced_colors_sizes[workorder.color][workorder.size] and workorders:

                        produced_colors_sizes[workorder.color][workorder.size] -= workorder.qty


                        workorders_vigentes_prefinish.append(workorders.popleft())

                        # Actualizo workorders
                        if workorders:
                            workorder = workorders[0]
                        else:
                            workorder = None

            veces_setup += pfo_while(tiempo, classifier, prefinishmachines_d, packagingmachines_d, rmidrums_d, pfidrums_d, pidrums_d,
                workorders_vigentes_prefinish, workorders_vigentes_packaging,
                workorder_pfo, produced_colors_sizes, produced_colors_sizes_flavors, printear, desperdicios)


            if not vaciando_rmi and workorder:
                # Encuentro si hay RMI y registro si alcanza

                rmi_vaciar = hay_rmi(rmidrums_d, workorder.color)
                bool = alcanza_rmi(rmidrums_d, workorder.color, workorder, produced_colors_sizes, porcentajes, modificadas)

                while not bool:
                    #print(print_state(classifier, pidrums_d, pfidrums_d, rmidrums_d, packagingmachines_d, prefinishmachines_d))
                    x = input(f"Se acaba de eliminar la workorder {str(workorder)} porque no hay RMI disponible. \nDeseas continuar? Si no, corta el programa")
                    if not vaciando_final:
                        eliminadas.append(workorder)

                    workorders.remove(workorder)
                    workorder = None

                    if workorders:
                        workorder = workorders[0]
                        rmi_vaciar = hay_rmi(rmidrums_d, workorder.color)
                        bool = alcanza_rmi(rmidrums_d, workorder.color, workorder, produced_colors_sizes, porcentajes, modificadas)

                    else:
                        # Reviso si actualizo workorders
                        classifier.finish = tiempo
                        break

            if rmi_vaciar and workorder and not classifier.activo:
                # Cantidad a clasificar
                porcentaje = porcentajes[workorder.color][workorder.size]
                if produced_colors_sizes[workorder.color][workorder.size]:
                    cantidad_color = Decimal(str(min([rmi_vaciar.inventory, max((workorder.qty - produced_colors_sizes[workorder.color][workorder.size])/porcentaje, 0), capacidad_pfi])))
                else:
                    cantidad_color = Decimal(str(min([rmi_vaciar.inventory, workorder.qty/porcentaje, capacidad_pfi])))
                # Encuentro las cantidades por tamaño
                cantidades_size = proporciones_size(porcentajes, workorder.color, cantidad_color)

                # # Corrijo cantidades
                # for i in range(5):
                #     cantidad = cantidades_size[i]
                #     size = ["S1", "S2", "S3", "S4", "S5"][i]
                #     total = 0
                #     for wk in list(workorders):
                #         if wk.color == workorder.color and wk.size == size:
                #             if 0 < abs(wk.qty - cantidad) <= 0.1:
                #                 # print(cantidades_size, cantidad_color, sum(cantidades_size))
                #                 cantidades_size[i] = total + wk.qty
                #                 break
                #
                #             elif 0.1 < cantidad - wk.qty:
                #                 cantidad -= wk.qty
                #                 total += wk.qty
                #
                #             else:
                #                 break

                cantidad_color = sum(cantidades_size)

                # Obtengo los PFIS de destino si los hay
                pfis_destino = overflow_pfi(pfidrums_d, cantidades_size, workorder)

                # Si hay PFIS disponibles
                if pfis_destino:

                    rmi_vaciar.inventory -= cantidad_color
                    classifier.processing = cantidad_color
                    classifier.activo = True
                    classifier.color = workorder.color
                    classifier.finish = tiempo + cantidad_color/classifier.process_rate * 3600

                    i = 0
                    for pfi in pfis_destino:
                        if pfi.tiempo_fifo[0] == [9999999999999999999999999999999, 0]:
                            x = pfi.tiempo_fifo.popleft()
                        pfi.tiempo_fifo.append([tiempo, cantidades_size[i]])
                        pfi.llenandose = True
                        i += 1


                    i = 0
                    sizes = ["S1", "S2", "S3", "S4", "S5"]
                    for size in sizes:
                        produced_colors_sizes[classifier.color][size] += cantidades_size[i]
                        if size == workorder.size: pfis_destino[i].tiempo_fifo[-1][0] -= 1
                        i += 1


                    if rmi_vaciar.inventory == 0:
                        vaciando_rmi = False

                if printear:
                    print(print_state(classifier, pidrums_d, pfidrums_d, rmidrums_d, packagingmachines_d, prefinishmachines_d))



        elif proximo.name == "PFO":

            proximo.finish = 999999999999999999999999999999999999


            # Agrego inventario de los PIS
            add_inventory_pi(proximo, produced_colors_sizes_flavors)

            # Próximo evento revisar classifier. REVISO ANTERIOR
            if classifier.finish >= 99999999999999999999999999999999999999999: classifier.finish = tiempo

            if printear:
                print(print_state(classifier, pidrums_d, pfidrums_d, rmidrums_d, packagingmachines_d, prefinishmachines_d))

            if workorders_vigentes_packaging: workorder_pckg = workorders_vigentes_packaging[0]

            pckg_while(tiempo, cantidad_total_workorders, classifier, prefinishmachines_d, rmidrums_d, pfidrums_d, pidrums_d, packagingmachines_d,
                workorders_vigentes_prefinish, workorders_vigentes_packaging, workorder_pckg,
                workorder_pfo, produced_colors_sizes, produced_colors_sizes_flavors, final_produced, final_inventory, workorders_inventory, printear)

            veces_setup += pfo_while(tiempo, classifier, prefinishmachines_d, packagingmachines_d, rmidrums_d, pfidrums_d, pidrums_d,
                workorders_vigentes_prefinish, workorders_vigentes_packaging,
                workorder_pfo, produced_colors_sizes, produced_colors_sizes_flavors, printear, desperdicios)



        elif proximo.name == "PCKG":
            proximo.finish = 99999999999999999999999999999999999999999999

            # Próximo evento revisar classifier. REVISO ANTERIOR
            if classifier.finish == 99999999999999999999999999999999999999999: classifier.finish = tiempo

            # Agrego inventario de los PIS
            add_inventory_pckg(proximo, final_produced)

            if printear:
                print(print_state(classifier, pidrums_d, pfidrums_d, rmidrums_d, packagingmachines_d, prefinishmachines_d))

            pckg_while(tiempo, cantidad_total_workorders, classifier, prefinishmachines_d, rmidrums_d, pfidrums_d, pidrums_d, packagingmachines_d,
                workorders_vigentes_prefinish, workorders_vigentes_packaging, workorder_pckg,
                workorder_pfo, produced_colors_sizes, produced_colors_sizes_flavors, final_produced, final_inventory, workorders_inventory, printear)

            veces_setup += pfo_while(tiempo, classifier, prefinishmachines_d, packagingmachines_d, rmidrums_d, pfidrums_d, pidrums_d,
                workorders_vigentes_prefinish, workorders_vigentes_packaging,
                workorder_pfo, produced_colors_sizes, produced_colors_sizes_flavors, printear, desperdicios)


    if not over:
        print(f"Se eliminaron {len(eliminadas)} workorders.")
        print(f"Terminó! Tiempo total de demora: {tiempo/3600/24/30} meses")

        print(f"Costo total: ${get_cost(final_inventory, name)}")
        print(f"Veces de cambio de Flavor: {veces_setup}")

        x = input("Terminó todo. Apreta enter para ver las WO's modificadas (si las hay) y el porcentaje de demanda cubierto")

        for wk in modificadas:
            print(wk)

        with open("generated/workorders_eliminadas", "wb") as file:
            pickle.dump(eliminadas, file)
        with open("generated/desperdicios", "wb") as file:
            pickle.dump(desperdicios, file)

        porcentaje_cubierto(workorders_inventory)

    return {
    'tiempo_wo': round(float(tiempo_termino_wo), 3),
    'tiempo_total': round(float(tiempo/3600/24/30), 3),
    'costo_total': round(float(get_cost(final_inventory, name)), 3)
    }

if __name__ == '__main__':
    s1 = simular('3')
    print(s1)
