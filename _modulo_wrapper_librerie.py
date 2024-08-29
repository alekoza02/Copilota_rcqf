import numpy as np
import ctypes
from time import perf_counter
import random

class LibrerieC:
    def __init__(self) -> None:
        self.lib = ctypes.CDLL(".\\LIBRERIE\\bin\\libreria.dll")

        self.lib.tester.restype = ctypes.POINTER(ctypes.c_int)
        self.lib.tester.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        
        self.lib.renderer_dispatcher.restype = ctypes.POINTER(ctypes.c_double)
        self.lib.renderer_dispatcher.argtypes = [
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

        self.lib.free_array.argtypes = [ctypes.POINTER(ctypes.c_double)]


    def tester(self, d):
        return np.array(
        np.ctypeslib.as_array(
            self.lib.tester(d[0], d[1], d[2]), shape=d
        ), copy = True, dtype=int
    )
    
    
    def c_renderer(self, x, y, sfere, triangoli_imported, camera, info):
        
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

        # print(f"Preparazione dati Python ha impiegato: {fine - inizio:.6f}")

        # lancio funzione
        c_array = self.lib.renderer_dispatcher(x, y, pos_ptr, len(pos), radii_ptr, len(radii), fov_camera, pos_camera_ptr, ax_camera_ptr, info.cores, info.sample_packet, info.bounces, materiale_ptr, random.random(), triangoli_c_ptr, materiale_triangoli_ptr, indici_modelli_ptr, len(indici_modelli), len(triangoli_imported[0].triangoli))

        numpy_array = np.array(np.ctypeslib.as_array(c_array, shape=(x, y, 12)), copy = True, dtype=float)
        numpy_array = np.transpose(numpy_array, (1, 0, 2))

        self.lib.free_array(c_array)

        return numpy_array