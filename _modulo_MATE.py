import numpy as np
from math import log, sqrt, cos, sin
import time
from numba import njit

class Mate:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def modulo(v: np.ndarray[float] | np.ndarray[np.ndarray[float]]) -> float:
        if type(v[0]) == np.ndarray:
            return np.linalg.norm(v, axis=1)
        else:     
            return np.linalg.norm(v)
        
    @staticmethod
    def versore(v: np.ndarray[float] | np.ndarray[np.ndarray[float]]) -> np.ndarray[float]:
        if type(v[0]) == np.ndarray:
            return np.divide(v, Mate.modulo(v)[:,None])
        else:     
            return v / Mate.modulo(v)
    
    @staticmethod
    def screen_world() -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [1,0,0,0],
            [0,0,1,0],
            [0,-1,0,0],
            [0,0,0,1]
        ])

    @staticmethod
    def camera_world(camera) -> np.ndarray[np.ndarray[float]]:
        return np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [-camera.pos[0], -camera.pos[1], -camera.pos[2], 1]]
        ) @ np.array(
            [[camera.rig[0], camera.dir[0], camera.ups[0], 0],
             [camera.rig[1], camera.dir[1], camera.ups[1], 0],
             [camera.rig[2], camera.dir[2], camera.ups[2], 0],
             [0, 0, 0, 1]]
        )

    @staticmethod
    def rotx(ang: float) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [1, 0, 0, 0],
            [0, np.cos(ang), np.sin(ang), 0],
            [0, -np.sin(ang), np.cos(ang), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def roty(ang: float) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [np.cos(ang), 0, np.sin(ang), 0],
            [0, 1, 0, 0],
            [-np.sin(ang), 0, np.cos(ang), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rotz(ang: float) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [np.cos(ang), np.sin(ang), 0, 0],
            [-np.sin(ang), np.cos(ang), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rot_ax(axis: np.ndarray[float], ang: float) -> np.ndarray[np.ndarray[float]]:
        K = np.array([
            [0, -axis[2], axis[1], 0],
            [axis[2], 0, -axis[0], 0],
            [-axis[1], axis[0], 0, 0],
            [0, 0, 0, 1]
        ])

        return np.eye(4) + np.sin(ang) * K + (1 - np.cos(ang)) * np.dot(K, K)
    
    @staticmethod
    def centra_schermo(W, H):
        return np.array([
            [W/2, 0, 0, 0],
            [0, H/2, 0, 0],
            [0, 0, 1, 0],
            [W/2, H/2, 0, 1]
        ])
    
    @staticmethod
    def scalotrasla(obj):
        return np.array([
            [obj.sx, 0, 0, 0],
            [0, obj.sy, 0, 0],
            [0, 0, obj.sz, 0],
            [obj.x, obj.y, obj.z, 1]
        ])
    
    @staticmethod
    def scala(value):
        return np.array([
            [value, 0, 0, 0],
            [0, value, 0, 0],
            [0, 0, value, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def frustrum(W: int, H: int, h_fov: float) -> np.ndarray[np.ndarray[float]]:
        # qua c'è un meno per sistemare l'orientamento della camera, altrimenti ottieni un'immagine specchiata in prospettiva
        v_fov = h_fov * H / W
        ori = np.tan(h_fov / 2)
        ver = np.tan(v_fov / 2)
        return np.array([
            [1 / ori, 0, 0, 0],
            [0, 1 / ver, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 0]
        ])
        
    @staticmethod
    def proiezione(vertici: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        ris = vertici / vertici[:, -1].reshape(-1, 1)
        ris[(ris < -2) | (ris > 2)] = 0
        return ris

    @staticmethod
    def add_homogenous(v: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        '''
        Aggiungo la 4 coordinata alla fine dei vettori con 3 coordinate. Supporto strutture come triangoli e liste di vettori
        '''
        shape = v.shape
        
        if len(shape) == 3:
            ones = np.ones((v.shape[0], v.shape[1], 4))
            ones[:, :, :3] = v
        
        elif len(shape) == 2:
            ones = np.ones((v.shape[0], 4))
            ones[:, :3] = v
        
        else:
            err_msg = f"Invalid vector shape: {shape}"
            raise IndexError(err_msg)
            
        return ones


    @staticmethod
    def hex2rgb(colore: str) -> list[int]:
        '''Accetta SOLO il formato: #123456'''
        try:
            r = int(colore[1:3], base=16)
            g = int(colore[3:5], base=16)
            b = int(colore[5:7], base=16)
            return [r,g,b]
        except ValueError:
            return [255, 0, 255]


    @staticmethod
    def rgb2hex(colore: list[int]) -> str:
        '''Accetta SOLO il formato: [255, 255, 255]'''
        try:
            r = hex(colore[0])
            g = hex(colore[1])
            b = hex(colore[2])

            if colore[0] == 0:
                r += "0"
            if colore[1] == 0:
                g += "0"
            if colore[2] == 0:
                b += "0"

            return f"#{r[2:]}{g[2:]}{b[2:]}"
        except ValueError:
            return "#ff00ff"

    
    @staticmethod
    def inp2int(valore: str, std_return: int = 0) -> int:
        try:
            return int(valore)
        except ValueError:
            return std_return


    @staticmethod
    def inp2flo(valore: str, std_return: float = 0.0) -> float:
        try:
            return float(valore)
        except ValueError:
            return std_return


    @staticmethod
    def conversione_limite(text: str, exception: int | float, limit: int | float) -> int | float:
        
        # TODO sai cosa fare
        # UPDATE: non so cosa fare

        tipologia = type(limit)
        try:
            if tipologia == int:
                ris = int(text)
            elif tipologia == float:
                ris = float(text)
        except:
            ris = exception
        
        if ris > limit:
            ris = limit

        return ris
    

    @staticmethod
    def media_accumulativa(vecchia_media, numero_elementi, nuovo_valore):
        peso = 1 / (numero_elementi + 1)
        return vecchia_media * (1 - peso) + nuovo_valore * peso


class RandomAle:
    def __init__(self, seed = None):
        self.modulus = 2**32
        self.a = 1103515245
        self.c = 12345
        
        if seed is None:
            self.state = time.time_ns()
        else:
            self.state = seed

    def next(self):
        self.state = (self.a * self.state + self.c) % self.modulus
        return self.state

    def random_uniform(self):
        return self.next() / self.modulus
    
    def random_normal(self):
        theta = 2 * 3.1415926 * self.random_uniform()
        rho = sqrt(-2 * log(self.random_uniform()))
        
        return rho * cos(theta)


class AcceleratedFoo:
    def __init__(self) -> None:
        pass

    @staticmethod
    @njit(fastmath=True)
    def any_fast(v: np.ndarray[float], a: float, b: float) -> bool:
        return np.any((v == a) | (v == b))


if __name__ == "__main__":

    randale = RandomAle()


    start = time.perf_counter_ns()

    randale.random_normal()
    
    print(time.perf_counter_ns() - start)
    

    start = time.perf_counter_ns()

    np.random.normal()

    print(time.perf_counter_ns() - start)