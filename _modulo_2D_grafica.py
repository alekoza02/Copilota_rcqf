import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy



class Image:
    def __init__(self) -> None:

        self.image = np.random.randint(0, 255, (16, 16, 3))
        self.zoom = deepcopy(self.image)
        self.zoom_factor = 1
        self.schermo_dim = 1080


    def disegna(self):

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        ax1.imshow(self.image)
        ax2.imshow(self.zoom)
        plt.show()


    def apply_zoom(self):
        
        X, Y = np.indices(self.image.shape[:2])

        fattore = self.schermo_dim / (self.image.shape[0] / self.zoom_factor)

        X = np.repeat(np.repeat(X, fattore, axis=0), fattore, axis=1).astype(int)
        Y = np.repeat(np.repeat(Y, fattore, axis=0), fattore, axis=1).astype(int)

        X = X[:self.schermo_dim, :self.schermo_dim]
        Y = Y[:self.schermo_dim, :self.schermo_dim]

        self.zoom = self.image[X, Y, :]



if __name__ == "__main__":

    i = Image()
    
    while True:
        i.apply_zoom()
        i.disegna()
        i.zoom_factor += .1

        print(i.zoom_factor)