from numba import njit
import numpy as np

class Triangle:
    def __init__(self) -> None:
        pass

    @staticmethod
    @njit()
    def rasterization(w: int, h: int, triangles: np.ndarray[np.ndarray[np.ndarray[float]]], bg_color: np.ndarray[float], plot_color: np.ndarray[float], l_min: float, l_max: float) -> np.ndarray[np.ndarray[float]]:
        
        v1 = triangles[:, 0, :]
        v2 = triangles[:, 1, :]
        v3 = triangles[:, 2, :]
        
        triangles = np.ones(triangles.shape)
        triangles[:, 0, :] = v1
        triangles[:, 1, :] = v3
        triangles[:, 2, :] = v2
        
        def cross_edge(vertex1, vertex2, p):
            edge12 = vertex1 - vertex2
            edge1p = vertex1 - p
            return edge12[0] * edge1p[1] - edge12[1] * edge1p[0]
        
        buffer = np.ones((w, h, 3)) * bg_color
        # buffer = np.zeros((w, h, 3))

        for triangle in triangles:
            
            min_x = round(np.min(triangle[:,0]))
            max_x = round(np.max(triangle[:,0]))
            min_y = round(np.min(triangle[:,1]))
            max_y = round(np.max(triangle[:,1]))
            
            if max_x < 0: continue
            if max_y < 0: continue
            if min_x > w: continue
            if min_y > h: continue
                            
            if max_x > w: max_x = w
            if max_y > h: max_y = h
            if min_x < 0: min_x = 0
            if min_y < 0: min_y = 0
                        
            v_1 = triangle[0]
            v_2 = triangle[1]
            v_3 = triangle[2]
            
            area = cross_edge(v_1, v_2, v_3)
            if area == 0: continue
            
            delta_w0_col = v_2[1] - v_3[1]
            delta_w1_col = v_3[1] - v_1[1]
            delta_w2_col = v_1[1] - v_2[1]
            
            delta_w0_row = v_3[0] - v_2[0]
            delta_w1_row = v_1[0] - v_3[0]
            delta_w2_row = v_2[0] - v_1[0]
            
            p0 = np.array([min_x, min_y]) + np.array([0.5, 0.51])

            w0_row = cross_edge(v_2, v_3, p0)
            w1_row = cross_edge(v_3, v_1, p0)
            w2_row = cross_edge(v_1, v_2, p0)
            
            for y in range(min_y, max_y):
                w0 = w0_row
                w1 = w1_row
                w2 = w2_row
                for x in range(min_x, max_x):
                    
                    alpha = w0 / area
                    beta = w1 / area
                    gamma = w2 / area
                    
                    if w0 >= 0 and w1 >= 0 and w2 >= 0:
                
                        progresso = 1 - (y - l_min) / (l_max - l_min) 

                        buffer[x, y, 0] = progresso * (plot_color[0] - bg_color[0]) + bg_color[0]
                        buffer[x, y, 1] = progresso * (plot_color[1] - bg_color[1]) + bg_color[1]
                        buffer[x, y, 2] = progresso * (plot_color[2] - bg_color[2]) + bg_color[2]
                
                    w0 += delta_w0_col 
                    w1 += delta_w1_col
                    w2 += delta_w2_col
                
                w0_row += delta_w0_row 
                w1_row += delta_w1_row
                w2_row += delta_w2_row
                    
        return buffer