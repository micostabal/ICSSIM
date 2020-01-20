from collections import deque
from decimal import *
from numpy.random import normal as sample_normal

class ClassifierMachine:
    """
        Classifier Machine
    """
    def __init__(self, site, rate, id):
        self.site = site
        self.process_rate = rate
        self.processing = Decimal("0")
        self.id = id
        self.finish = 0
        self.color = None
        self.activo = False

    def __str__(self):
        return f"ClassifierMachine ID = {self.id}, Processing = {round(self.processing,2)} "

class RMIDrum:
    """
        Raw-Material Inventory
    """
    def __init__(self, id, site, color, inventory, capacity):
        self.id = id
        self.site = site
        self.color = color
        self.inventory = inventory
        self.capacity = capacity

    def __str__(self):
        return f"RMIDrum ID = {self.id}, Inventario = {self.inventory}, Ocupación = {round(self.inventory/self.capacity *100, 2)}% Color: {self.color}"

class PFIDrum:
    """
        Pre-Finish Inventory
    """
    def __init__(self, id, site, capacity):
        self.id = id
        self.site = site
        self.inventory = Decimal("0")
        self.capacity = capacity*Decimal("0.95")
        self.llenandose = False
        self.vaciandose = False
        self.color = None
        self.size = None
        self.tiempo_fifo = deque()
        self.tiempo_fifo.append([9999999999999999999999999999999, 0])

    def __str__(self):
        return f"PFIDrum ID = {self.id}, Ocupación = {self.inventory}"

class PIDrum:
    """
        Pack Inventory
    """
    def __init__(self, id, site, capacity):
        self.id = id
        self.site = site
        self.inventory = Decimal("0")
        self.capacity = capacity*Decimal("0.95")
        self.color = None
        self.size = None
        self.flavor = None
        self.vaciandose = False
        self.llenandose = False
        self.tiempo_fifo = deque()
        self.tiempo_fifo.append([9999999999999999999999999999999, 0])


    def __str__(self):
        return f"PIDrum ID = {self.id}, Ocupación = {round(self.inventory/self.capacity *100, 2)}%"

class PrefinishMachine:
    """
        Prefinish Machine
    """
    id = 0

    def __init__(self, site, avg_rate, std_rate):
        self.name = "PFO"
        self.site = site
        self.size = None
        self.id = PrefinishMachine.id
        PrefinishMachine.id += 1
        self.flavor = None
        self._process_rate = avg_rate
        self.processing = 0
        self.activo = False
        self.finish = 9999999999999999999999
        self.color = None
        self.size = None
        self.pi_asignado = None
        self.pfi_asignado = None
        self.workorder_actual = None
        self.avg_rate = avg_rate
        self.std_rate = std_rate

    @property
    def process_rate(self):
        return Decimal(sample_normal(self.avg_rate, self.std_rate))

    def __str__(self):
        return f"PrefinishMachine ID = {self.id}, Processing = {round(self.processing,2)}"

class PackageMachine:
    """
        Package Machine
    """
    id = 0

    def __init__(self, site, type, avg_rate, std_rate):
        self.name = "PCKG"
        self.site = site
        self.type = type
        self.color = None
        self.size = None
        self.flavor = None
        self.processing = 0
        self.activo = False
        self.id = PackageMachine.id
        PackageMachine.id += 1
        self._process_rate = avg_rate
        self.finish = 9999999999999999999999
        self.pi_asignado = None
        self.avg_rate = avg_rate
        self.std_rate = std_rate

    @property
    def process_rate(self):
        return Decimal(sample_normal(self.avg_rate, self.std_rate))

    def __str__(self):
        return f"PackageMachine ID = {self.id}, Processing = {round(self.processing,2)} Tipo: {self.type}"


class WorkOrder:
    id = 0

    def __init__(self, color, qty, size, package, flavor):
        self.id = WorkOrder.id
        WorkOrder.id += 1
        self.color = color
        self.qty = qty
        self.size = size
        self.package = package
        self.flavor = flavor

    def __str__(self):
        return f"WorkOrder ID: {self.id} Color: {self.color} Size: {self.size} Flavor: {self.flavor} Pckg: {self.package} Qty: {self.qty}"
