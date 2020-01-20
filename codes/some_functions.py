from clases import *
from decimal import *
from collections import defaultdict


def print_state(classifier, pidrums, pfidrums, rmidrums, packagingmachines, prefinishmachines):
    string = f"""
    ---------------------------
        Estado del sistema
    ---------------------------
    """
    if classifier.processing:
        string_classifier = f"""

            Máquina Classifier procesando {round(classifier.processing, 2)} de color {classifier.color}. Finish: {round(classifier.finish, 1)}

        """
    else:
        string_classifier = f"""

        """

    string_pfis = f"""
        Bins PFIs ocupados:

    """
    pfis_ocupados = [pfi for pfi in pfidrums if pfi.inventory > 0]
    for pfi in pfis_ocupados:
        string_pfis += f"""
            PFI id: {pfi.id}. Color: {pfi.color}. Size: {pfi.size}. Inventario: {pfi.inventory}. Ocupación: {round(pfi.inventory/pfi.capacity * 100, 2)}%
        """

    string_pfos = f"""
        Máquina PFOs ocupados:

    """

    pfos_ocupadas = [pfo for pfo in prefinishmachines if pfo.processing > 0]
    for pfo in pfos_ocupadas:
        string_pfos += f"""
            Máquina PFO id: {pfo.id}. Color: {pfo.color}. Size: {pfo.size}. Flavor: {pfo.flavor}. Procesando: {pfo.processing}. Finish: {round(pfo.finish, 1)}
        """

    string_pis = f"""
        Bins PIs ocupados:

    """
    pis_ocupados = [pi for pi in pidrums if pi.inventory > 0]
    for pi in pis_ocupados:
        string_pis += f"""
            PI id: {pi.id}. Color: {pi.color}. Size: {pi.size}. Flavor: {pi.flavor}. Inventario: {round(pi.inventory, 2)}. Ocupación: {round(pi.inventory/pi.capacity * 100, 2)}%
        """

    string_pckgs = f"""
        Máquina Packaging ocupadas:

    """

    pckg_ocupadas = [pckg for pckg in packagingmachines if pckg.processing > 0]
    for pckg in pckg_ocupadas:
        string_pckgs += f"""
            Máquina Packaging id: {pckg.id}. Color: {pckg.color}. Size: {pckg.size}. Flavor: {pckg.flavor}. Empaque: {pckg.type}. Procesando: {round(pckg.processing, 2)}. Finish: {round(pckg.finish, 2)}
        """

    return string + string_classifier + string_pfis + string_pfos + string_pis + string_pckgs

def proporciones_size(porcentajes, color, qty):
    """
        Lista con las cantidades para cada size
    """
    sizes = ["S1", "S2", "S3", "S4", "S5"]
    dicc = porcentajes[color]
    return [round(dicc[size]*qty, 3) for size in sizes]

def overflow_pfi(pfis, cantidades, workorder):
    """
        Entrega los PFIS a llenar si hay más de 5 y tienen la capacidad
    """
    sizes = ["S1", "S2", "S3", "S4", "S5"]
    final_pfis = []
    for size in sizes:
        counter = sizes.index(size)
        ready = False
        for pfi in pfis:
            if (pfi.capacity - pfi.inventory >= cantidades[counter] and pfi.color == workorder.color and pfi.size == size and pfi.inventory != 0) and not pfi.vaciandose and not pfi.llenandose:
                if pfi not in final_pfis:
                    final_pfis.append(pfi)
                    ready = True
                    break

        if not ready:
            for pfi in pfis:
                if pfi.inventory == 0 and not pfi.vaciandose and not pfi.llenandose:
                    if pfi not in final_pfis:
                        final_pfis.append(pfi)
                        break

    return False if len(final_pfis) != 5 else final_pfis

def get_first_rmi_faltante(rmis):
    for rmi in rmis:
        if rmi.inventory > 0:
            return rmi

def add_inventory_pfis(pfis, cantidades_size, color, workorder):
    """
        Actualiza inventario de PFIS luego de clasificar
    """
    i = 0
    sizes = ["S1", "S2", "S3", "S4", "S5"]
    for pfi in pfis:
        pfi.inventory = pfi.inventory + cantidades_size[i]
        pfi.color = color
        pfi.size = sizes[i]
        i += 1

def add_inventory_pi(pfo, dicc):
    """
        Actualiza inventario de PI luego de añadir flavor
    """
    pfo.pi_asignado.inventory += pfo.processing
    pfo.pi_asignado.color = pfo.color
    pfo.pi_asignado.size = pfo.size
    pfo.pi_asignado.flavor = pfo.flavor
    pfo.pi_asignado.llenandose = False
    pfo.pfi_asignado.vaciandose = False
    pfo.activo = False
    pfo.processing = 0

def add_inventory_pckg(pckg, final_produced):
    """
        Actualiza inventario de PCKG luego de añadir paquete
    """
    pckg.pi_asignado.vaciandose = False
    pckg.activo = False
    pckg.processing = 0

def raw_quantity_necessary(porcentajes, workorder):
    """
        Entrega la cantidad RAW de material del color para cierta workorder
    """
    color, qty, size = workorder.color, workorder.qty, workorder.size
    return qty/(porcentajes[color][size])

def todo_vacio(bins, maquinas):
    for conjunto in bins:
        for bin in conjunto:
            if bin.inventory > 0:
                return False
    for conjunto in maquinas:
        for maquina in conjunto:
            if maquina.activo:
                return False
    return True

def todo_vacio_post(bins, maquinas):
    for conjunto in bins:
        for bin in conjunto:
            if bin.inventory > 0:
                print(bin)
                return False
    for conjunto in maquinas:
        for maquina in conjunto:
            if maquina.activo:
                print(maquina)
                return False
    return True

def hay_rmi(rmis, color):
    for rmi in rmis:
        if rmi.color == color and rmi.inventory > 0 and rmi.inventory < 0.1:
            #print(f"Se vacía RMI {rmi.color} porque tenía inventario {rmi.inventory} que por aproximación no sirve")
            rmi.inventory = 0
        if rmi.color == color and rmi.inventory > 0:
            return rmi

def alcanza_rmi(rmis, color, workorder, dicc, porcentajes, modificadas):
    suma = 0
    for rmi in rmis:
        if rmi.color == color and rmi.inventory > 0:
            suma += rmi.inventory
    if 0.1 > workorder.qty - round(suma*porcentajes[workorder.color][workorder.size], 3) - dicc[workorder.color][workorder.size] > 0:
        if round(suma*porcentajes[workorder.color][workorder.size], 3) + dicc[workorder.color][workorder.size]:
            #print(f"Modificando WorkOrder {workorder} que le falta menos de 0.1 para que alcance el RMI")
            workorder.qty = round(suma*porcentajes[workorder.color][workorder.size], 3) + dicc[workorder.color][workorder.size]
            modificadas.append((workorder, str(workorder), workorder.qty, round(suma*porcentajes[workorder.color][workorder.size], 3) + dicc[workorder.color][workorder.size]))

    return round(suma*porcentajes[workorder.color][workorder.size], 3) + dicc[workorder.color][workorder.size] >= workorder.qty


def pfo_not_working(pfos):
    for pfo in pfos:
        if not pfo.activo:
            return True
    return False

def get_pfo_not_working(pfos):
    for pfo in pfos:
        if not pfo.activo:
            return pfo

def get_total_bins(color, size, bins):
    inv = 0
    for bin in bins:
        if bin.color == color and bin.size == size:
            inv += bin.inventory
    return inv

def get_first_pfi_lleno(pfis, wks, tiempo):
    posible = None
    for pfi in sorted(pfis, key=lambda pfi: pfi.inventory):
        if pfi.inventory > 0 and not pfi.llenandose and not pfi.vaciandose:
            if not posible: posible = pfi
            for wk in wks:
                if wk.color == pfi.color and wk.size == pfi.size:
                    return pfi, wk

    if posible:
        return posible, None
    else:
        return None, None

def pckg_not_working(pckgs, package):
    for pckg in pckgs:
        if not pckg.activo and pckg.type == package:
            return True
    return False

def get_pckg_not_working(pckgs, wk):
    package = wk.package

    # Verificación de que no haya el mismo SKU procesando
    for pckg in pckgs:
        distinto = "Bag" if package == "Box" else "Box"
        if pckg.activo and pckg.color == wk.color and pckg.size == wk.size and pckg.flavor == wk.flavor and pckg.type == distinto:
            # Retorno que no se puede
            return None

    for pckg in pckgs:
        if not pckg.activo and pckg.type == package:
            return pckg

def get_first_pi_lleno(pis, wks):
    for pi in sorted(pis, key=lambda pi: pi.inventory):
        if pi.inventory > 0 and not pi.llenandose and not pi.vaciandose:
            for wk in wks:
                if pi.color == wk.color and pi.size == wk.size and pi.flavor == wk.flavor:
                    return pi, wk
    return None, None

def hay_pi(pis, pfi_vaciar, desperdicio, wk):
    """
    Puede recibir la workorder y el pfi_vaciar y completar un PI
    """
    prioridad1 = []
    prioridad2 = []
    for pi in pis:
        if (pi.capacity - pi.inventory > 0 and pi.color == pfi_vaciar.color and pi.size == pfi_vaciar.size and (not desperdicio and pi.flavor == wk.flavor)) and not pi.llenandose and not pi.vaciandose:
            prioridad1.append(pi)
        elif pi.inventory == 0 and not pi.llenandose and not pi.vaciandose:
            prioridad2.append(pi)
    if prioridad1:
        # return list(sorted(prioridad1, key=lambda pi: (pi.capacity-pi.inventory), reverse=True))[0]
        return prioridad1[0]
    elif prioridad2:
        # return list(sorted(prioridad2, key=lambda pi: (pi.capacity-pi.inventory), reverse=True))[0]
        return prioridad2[0]

def get_cost(finished, city):
    dicc_costs = {"Detroit": (1.052, 0,9976),
                "Columbus": (1.1, 1.0452),
                "Springfield": (1.152, 1.0924),
                "Omaha": (1, 0.954),
                "Green Bay": (1.02, 0.9692)}

    costo_total = 0

    for color in finished:
        for size in finished[color]:
            for flavor in finished[color][size]:
                for pckg in finished[color][size][flavor]:
                    if pckg == "Bag":
                        costo_total += finished[color][size][flavor][pckg] * Decimal(str(dicc_costs[city][0]))
                    else:
                        costo_total += finished[color][size][flavor][pckg] * Decimal(str(dicc_costs[city][1]))
    return costo_total

def actualizar_color_size(dicc, pfis):
    for color in dicc:
        for size in dicc[color]:
            cantidad = dicc[color][size]
            comparar = 0
            for pfi in pfis:
                if pfi.color == color and pfi.size == size:
                    comparar += pfi.inventory
            if cantidad > comparar:
                dicc[color][size] = comparar

def actualizar_color_size_flavor(dicc, pis):
    for color in dicc:
        for size in dicc[color]:
            for flavor in dicc[color][size]:
                cantidad = dicc[color][size][flavor]
                comparar = 0
                for pi in pis:
                    if pi.color == color and pi.size == size and pi.flavor == flavor:
                        comparar += pi.inventory
                if cantidad > comparar:
                    dicc[color][size][flavor] = comparar

def porcentaje_cubierto(final_inv):
    necesario = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal))))
    total = 0
    with open("../data/Order Bank.csv", "r") as file:
        for linea in file.readlines()[1:]:
            color, size, flavor, pckg, qty = linea.strip().split(",")[1:]
            necesario[color.replace("Color", "Coloring")][size][flavor][pckg] += Decimal(int(qty)*0.25 if pckg == "Bag" else int(qty)*2.5)
            total += int(qty)*0.25 if pckg == "Bag" else int(qty)*2.5

    for color in final_inv:
        for size in final_inv[color]:
            for flavor in final_inv[color][size]:
                for pckg in final_inv[color][size][flavor]:
                    if necesario[color][size][flavor][pckg] >= final_inv[color][size][flavor][pckg]:
                        necesario[color][size][flavor][pckg] -= final_inv[color][size][flavor][pckg]
                    else:
                        #print(f"Resta negativa {color} {size} {flavor} {pckg}. Demanda: {necesario[color][size][flavor][pckg]}. Tengo: {final_inv[color][size][flavor][pckg]}")
                        necesario[color][size][flavor][pckg] -= final_inv[color][size][flavor][pckg]
    sobrante = 0
    for color in necesario:
        for size in necesario[color]:
            for flavor in necesario[color][size]:
                for pckg in necesario[color][size][flavor]:
                    sobrante += float(necesario[color][size][flavor][pckg])

    return (1 - sobrante/total)*100

def verificar_completo(producido, workorders, modificadas):
    for wk in workorders:
        if wk.id in [x[0].id for x in modificadas]:
            wk = x[0]
        producido[wk.color][wk.size][wk.flavor][wk.package] -= wk.qty

    for color in producido:
        for size in producido[color]:
            for flavor in producido[color][size]:
                for package in producido[color][size][flavor]:
                    if producido[color][size][flavor][package] != 0:
                        print(f"Color: {color}, Size: {size}, Flavor: {flavor}, Package: {package}, Sobró/Faltó: {producido[color][size][flavor][package]}")

def is_demand_complete(wks1, wks2, wks3, cant):
    for wk in wks1:
        if wk.id < cant:
            print(wk, cant)
            return False
    for wk in wks2:
        if wk.id < cant:
            print(wk, cant)
            return False
    for wk in wks3:
        if wk.id < cant:
            print(wk, cant)
            return False
    return True
