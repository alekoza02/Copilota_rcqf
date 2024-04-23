import numpy as np

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
    def rot_ax(axis: np.ndarray[float], ang: float) -> np.ndarray[np.ndarray[float]]:
        K = np.array([
            [0, -axis[2], axis[1], 0],
            [axis[2], 0, -axis[0], 0],
            [-axis[1], axis[0], 0, 0],
            [0, 0, 0, 0]
        ])

        return np.eye(4) + np.sin(ang) * K + (1 - np.cos(ang)) * np.dot(K, K)
    
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
    def inp2int(valore: str) -> int:
        try:
            return int(valore)
        except ValueError:
            return 0


    @staticmethod
    def inp2flo(valore: str) -> float:
        try:
            return float(valore)
        except ValueError:
            return 0


    @staticmethod
    def conversione_limite(text: str, exception: int | float, limit: int | float) -> int | float:
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