# ISCompetition

En la capeta /codes hay 5 modulos.

  - clases.py -> Todos los objetos de cada entidad de la simulación (máquinas, workorders, bins) con sus atributos y métodos
    >>> ClassifierMachine(site, rate, id, processing, finish) <<<
    >>> RMIDrum(id, site, color, capacity, inventory)
    >>> PFIDrum(id, site, capacity, inventory)
    >>> PIDrum(id, site, capacity, inventory)
    >>> PrefinishMachine(site, size, flavor, rate, processing, finish)
    >>> PackageMachine(site, size, type, rate, processing, finish)
    >>> WorkOrder(id, color, qty, size, package, flavor)
    >>> JellyPack(color, qty, size, package, flavor)

  - create_workorders.py -> Se carga la BD de BankOrder e idealmente se generan las workorders ahí

  - loading_city.py -> Parsea todas las BD, construyendo instancias de los objetos para luego usarlos en la simulación

  - some_functions.py -> Funciones que entregan bools y otros para la realización de la simulación.
      >>> proporciones_size(porcentajes, color, qty)
      >>> overflow_pfi(pfis, cantidades)
      >>> add_inventory_pfis(pfis, cantidades)
      >>> raw_quantity_necessary(porcentajes, workorder)

  - simulation.py -> Realiza una simulación para una ciudad, partimos con Detroit

En la carpeta /data está la BD entregada por ISC.

En diagram.pdf está la estructura de la modelación
