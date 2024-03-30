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