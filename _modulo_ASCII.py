from math import sin, cos

def main_loop(iterations: int = 0, ris: int = 1):
    
    W, H = 370 // 2, 54
    A, B = 0, 0

    light_map = ".,-~:;!=*#$@"

    light = [10., 30., 20.]
    m = sum([i ** 2 for i in light]) ** 0.5
    light = [i / m for i in light]
    
    R = 1
    r = .4

    iter = 0
    while iter <= iterations:
        iter += 1 if iterations != 0 else -1

        print("\x1b[H")

        pixel_buffer = [[" " for i in range(W)] for j in range(H)]
        z_buffer = [[0 for i in range(W)] for j in range(H)]

        A += 0.01
        B += 0.03

        for RAD in range(0, 6280, 7 * ris):
            RAD /= 1000.

            sinRAD, cosRAD = sin(RAD), cos(RAD)
            sinA, cosA = sin(A), cos(A)
            sinB, cosB = sin(B), cos(B)


            for rad in range(0, 6280, 2 * ris):
                rad /= 1000.
                sinrad, cosrad = sin(rad), cos(rad)

                x_c = R + r * cosrad 
                x_cn = r * cosrad 
                y_c = r

                x = x_c * cosRAD * cosB - (x_c * sinRAD * sinA + y_c * sinrad * cosA) * sinB
                y = x_c * sinRAD * cosA - y_c * sinrad * sinA
                z = x_c * cosRAD * sinB + (x_c * sinRAD * sinA + y_c * sinrad * cosA) * cosB

                x_n = x_cn * cosRAD * cosB - (x_cn * sinRAD * sinA + y_c * sinrad * cosA) * sinB
                y_n = x_cn * sinRAD * cosA - y_c * sinrad * sinA
                z_n = x_cn * cosRAD * sinB + (x_cn * sinRAD * sinA + y_c * sinrad * cosA) * cosB
                
                norm = [x_n, y_n, z_n]
                m = sum([i ** 2 for i in norm]) ** 0.5
                norm = [i / m for i in norm]

                z += 5.0
                
                x /= z
                y /= z

                x *= H * 1.725 * 2
                y *= H * 1.725
                
                color = - sum([n * l for n, l in zip(norm, light)]) * 11
                if color < 0.: color = 0.

                pointer_1 = int(x) + W // 2
                pointer_2 = int(y) + H // 2

                ooz = 1 / z

                if not (pointer_1 >= W or pointer_1 < 0 or pointer_2 >= H or pointer_2 < 0):
                    
                    if z_buffer[pointer_2][pointer_1] < ooz:
                        pixel_buffer[pointer_2][pointer_1] = light_map[round(color)]
                        z_buffer[pointer_2][pointer_1] = ooz

        for ind, linea in enumerate(pixel_buffer):
            output = "".join(linea)
            print(f"{ind}. {output}")


if __name__ == "__main__":
    main_loop(iterations=0, ris = int(input("Inserisci il livello di dettaglio (1 = alta risoluzione, 10 = bassa risoluzione): ")))
    

        

