import numpy as np
import ctypes
from time import perf_counter
import random

class LibrerieC:
    def __init__(self) -> None:
        self.lib = ctypes.CDLL(".\\LIBRERIE\\bin\\libreria.dll")

        self.lib.tester.restype = ctypes.POINTER(ctypes.c_int)
        self.lib.tester.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        
        self.lib.renderer_dispatcher.restype = ctypes.POINTER(ctypes.c_float)
        self.lib.renderer_dispatcher.argtypes = [
            ctypes.c_int,                       # x 
            ctypes.c_int,                       # y
            ctypes.POINTER(ctypes.c_float),     # array posizioni
            ctypes.c_int,                       # len(posizioni)
            ctypes.POINTER(ctypes.c_float),     # array raggi                               
            ctypes.c_int,                       # len(raggi)          
            ctypes.c_float,                     # fov
            ctypes.POINTER(ctypes.c_float),     # array pos camera                               
            ctypes.POINTER(ctypes.c_float),     # array axes camera                          
            ctypes.c_int,                       # cores                          
            ctypes.c_int,                       # samples                          
            ctypes.c_int,                       # bounces                        
            ctypes.POINTER(ctypes.c_float),     # materiale                          
            ctypes.c_float,                     # random seed
        ]

        self.lib.free_array.argtypes = [ctypes.POINTER(ctypes.c_float)]


    def tester(self, d):
        return np.array(
        np.ctypeslib.as_array(
            self.lib.tester(d[0], d[1], d[2]), shape=d
        ), copy = True, dtype=int
    )
    
    
    def c_renderer(self, x, y, oggetti, camera, info):
        
        inizio = perf_counter()
        
        # preparazione dati

        # sfere hanno: pos, radius, materiale, indice, BB
        pos = [i.pos for i in oggetti]
        radii = [i.radius for i in oggetti]

        colore = [i.materiale.colore for i in oggetti]
        emissione_forza = [i.materiale.emissione_forza for i in oggetti]
        emissione_colore = [i.materiale.emissione_colore for i in oggetti]
        roughness = [i.materiale.roughness for i in oggetti]
        glossiness = [i.materiale.glossiness for i in oggetti]
        glass = [i.materiale.glass for i in oggetti]
        IOR = [i.materiale.IOR for i in oggetti]
        
        pos, radii = np.ravel(pos).astype(np.float32), np.ravel(radii).astype(np.float32)
        
        materiale = [[i[0], i[1], i[2], j, k[0], k[1], k[2], l, m, n, o] for i, j, k, l, m, n, o in zip(colore, emissione_forza, emissione_colore, roughness, glossiness, glass, IOR)]

        materiale = np.ravel(materiale).astype(np.float32)

        fov_camera = camera.fov
        pos_camera = camera.pos[:3].astype(np.float32)
        ax_camera = np.ravel([camera.rig[:3], camera.ups[:3], camera.dir[:3]]).astype(np.float32)
        
        pos_ptr = pos.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        radii_ptr = radii.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        pos_camera_ptr = pos_camera.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        ax_camera_ptr = ax_camera.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        materiale_ptr = materiale.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        
        fine = perf_counter()

        # print(f"Preparazione dati Python ha impiegato: {fine - inizio:.6f}")

        # lancio funzione
        c_array = self.lib.renderer_dispatcher(x, y, pos_ptr, len(pos), radii_ptr, len(radii), fov_camera, pos_camera_ptr, ax_camera_ptr, info.cores, 1, info.bounces, materiale_ptr, random.random())

        numpy_array = np.array(np.ctypeslib.as_array(c_array, shape=(x, y, 3)), copy = True, dtype=float)

        self.lib.free_array(c_array)

        return numpy_array