import numpy as np
import ctypes
from time import perf_counter
import random

class LibrerieC:
    def __init__(self) -> None:

        self.c_array = None

        self.running = 0
        self.uscito_con_successo = 0
        self.fine_live_update = 0
        
        self.lib = ctypes.CDLL(".\\LIBRERIE\\bin\\libreria.dll")

        self.lib.main_loop.restype = ctypes.c_int
        self.lib.main_loop.argtypes = [
            ctypes.POINTER(ctypes.c_float),       # puntatore all'array
            ctypes.c_int,                       # x 
            ctypes.c_int,                       # y
            ctypes.POINTER(ctypes.c_double),     # array posizioni
            ctypes.c_int,                       # len(posizioni)
            ctypes.POINTER(ctypes.c_double),     # array raggi                               
            ctypes.c_int,                       # len(raggi)          
            ctypes.c_double,                     # fov
            ctypes.POINTER(ctypes.c_double),     # array pos camera                               
            ctypes.POINTER(ctypes.c_double),     # array axes camera                          
            ctypes.c_int,                       # cores                          
            ctypes.c_int,                       # samples                          
            ctypes.c_int,                       # bounces                        
            ctypes.POINTER(ctypes.c_double),     # materiale                          
            ctypes.c_double,                     # random seed
            ctypes.POINTER(ctypes.c_double),     # vertici modello
            ctypes.POINTER(ctypes.c_double),     # materiali modelli, 
            ctypes.POINTER(ctypes.c_int),         # indici modelli
            ctypes.c_int,                         # numero modelli
            ctypes.c_int                         # numero triangoli
        ]

        self.lib.exit_procedure.restype = None
        self.lib.exit_procedure.argtypes = None

        self.lib.start_procedure.restype = None
        self.lib.start_procedure.argtypes = None
        
        self.lib.free_array.restype = None
        self.lib.free_array.argtypes = [ctypes.POINTER(ctypes.c_float)]
        

        self.lib.reset_canvas.restype = None
        self.lib.reset_canvas.argtypes = [ctypes.POINTER(ctypes.c_float)]
        
        
        self.lib.create_array.restype = ctypes.POINTER(ctypes.c_float)
        self.lib.create_array.argtypes = [
            ctypes.c_int,       # larghezza
            ctypes.c_int,       # altezza
        ]
    
    
    def c_renderer(self, x, y, sfere, triangoli_imported, camera, info):
        
        self.uscito_con_successo = 0

        inizio = perf_counter()
        
        # preparazione dati

        # sfere hanno: pos, radius, materiale, indice, BB
        pos = [i.pos for i in sfere]
        radii = [i.radius for i in sfere]

        # materiali sfere
        colore = [i.materiale.colore for i in sfere]
        emissione_forza = [i.materiale.emissione_forza for i in sfere]
        emissione_colore = [i.materiale.emissione_colore for i in sfere]
        roughness = [i.materiale.roughness for i in sfere]
        glossiness = [i.materiale.glossiness for i in sfere]
        glass = [i.materiale.glass for i in sfere]
        IOR = [i.materiale.IOR for i in sfere]

        pos, radii = np.ravel(pos).astype(np.float64), np.ravel(radii).astype(np.float64)
        
        materiale = [[i[0], i[1], i[2], j, k[0], k[1], k[2], l, m, n, o] for i, j, k, l, m, n, o in zip(colore, emissione_forza, emissione_colore, roughness, glossiness, glass, IOR)]

        materiale = np.ravel(materiale).astype(np.float64)

        # metadata camera
        fov_camera = camera.fov
        pos_camera = camera.pos[:3].astype(np.float64)
        ax_camera = np.ravel([camera.rig[:3], camera.ups[:3], camera.dir[:3]]).astype(np.float64)
        
        # triangoli
        triangoli_c = [i.triangoli for i in triangoli_imported]
        triangoli_c = np.ravel(triangoli_c)

        indici_modelli = [i.indice for i in triangoli_imported]
        indici_modelli = np.ravel(indici_modelli)
        
        # materiali triangoli
        colore = [i.materiale.colore for i in triangoli_imported]
        emissione_forza = [i.materiale.emissione_forza for i in triangoli_imported]
        emissione_colore = [i.materiale.emissione_colore for i in triangoli_imported]
        roughness = [i.materiale.roughness for i in triangoli_imported]
        glossiness = [i.materiale.glossiness for i in triangoli_imported]
        glass = [i.materiale.glass for i in triangoli_imported]
        IOR = [i.materiale.IOR for i in triangoli_imported]

        pos, radii = np.ravel(pos).astype(np.float64), np.ravel(radii).astype(np.float64)
        
        materiale_triangoli = [[i[0], i[1], i[2], j, k[0], k[1], k[2], l, m, n, o] for i, j, k, l, m, n, o in zip(colore, emissione_forza, emissione_colore, roughness, glossiness, glass, IOR)]

        materiale_triangoli = np.ravel(materiale_triangoli).astype(np.float64)

        pos_ptr = pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        radii_ptr = radii.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        pos_camera_ptr = pos_camera.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        ax_camera_ptr = ax_camera.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        materiale_ptr = materiale.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        triangoli_c_ptr = triangoli_c.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        indici_modelli_ptr = indici_modelli.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        materiale_triangoli_ptr = materiale_triangoli.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        fine = perf_counter()

        self.lib.start_procedure()

        self.uscito_con_successo = self.lib.main_loop(self.c_array, x, y, pos_ptr, len(pos), radii_ptr, len(radii), fov_camera, pos_camera_ptr, ax_camera_ptr, info[2], info[0], info[1], materiale_ptr, random.random(), triangoli_c_ptr, materiale_triangoli_ptr, indici_modelli_ptr, len(indici_modelli), len(triangoli_imported[0].triangoli))
    
        return self.extract_C_array(x, y)
    

    def extract_C_array(self, x, y):
        numpy_array = np.array(np.ctypeslib.as_array(self.c_array, shape=(x, y, 5)), copy=True, dtype=float)
        numpy_array = np.transpose(numpy_array, (1, 0, 2))
        return numpy_array
    

    def C_init_canvas(self, x, y):
        self.running = 1
        self.c_array = self.lib.create_array(x, y)

    def C_reset_canvas(self, x, y):
        self.lib.reset_canvas(self.c_array, x, y)

    def C_free_canvas(self):
        self.lib.free_array(self.c_array)
    
    def C_exit(self):
        self.lib.exit_procedure()
        while self.uscito_con_successo == 0:
            ...
        self.running = 0