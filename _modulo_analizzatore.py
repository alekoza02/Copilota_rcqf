import numpy as np
import pygame
import os

from _modulo_UI import UI, Logica, Schermo
from _modulo_MATE import Mate

class Analizzatore:
    def __init__(self) -> None:

        self.primo_x: int = None 
        self.secondo_x: int = None 
        self.primo_y: int = None 
        self.secondo_y: int = None 

        self.punto_attivo: int = None

        self.reference = None

        self.lista_coordinate_calibrazione: list[tuple[float]] = []
        self.lista_coordinate_inserimento: list[tuple[float]] = []
        self.coppia_xx: list[float] = [None, None]
        self.coppia_yy: list[float] = [None, None]

        self.lista_coordinate_finali: list[tuple[float]] = []

        self.font = pygame.font.Font("TEXTURES/f_full_font.ttf", 20)

        self.x_conversione: float
        self.y_conversione: float

        self.step_progresso_completamento: int = 0
        # 0 -> idle
        # 1 -> calibrazione
        # 2 -> acquisizione dati
        # 3 -> salvataggio


    def load_image(self):
        try:
            self.reference = pygame.image.load(self.UI_import_path.text).convert()
        except FileNotFoundError:
            self.reference = None


    def link_ui(self, ui: UI):
        """Collegamento UI con il painter. Raccoglie informazioni circa le dimensioni dello schermo e si calcola l'ancoraggio

        Parameters
        ----------
        info_schermo : Schermo
            Dato la classe Schermo, posso capire le informazioni che mi servono
        """
        info_schermo: Schermo = ui.scena["plot_import"].schermo["viewport"]
        self.schermo_madre = info_schermo.madre
        
        self.w = info_schermo.w
        self.h = info_schermo.h

        self.ridimensiona_carattere = 1 if info_schermo.shift_x == 0 else 0.7

        self.ancoraggio_x = info_schermo.ancoraggio_x
        self.ancoraggio_y = info_schermo.ancoraggio_y 
        
        self.schermo = info_schermo.schermo
        
        self.UI_calls_plot_import = ui.scena["plot_import"]

        self.UI_console_output = self.UI_calls_plot_import.label_text["progresso"]
        self.UI_calibrazione = self.UI_calls_plot_import.bottoni["calibrazione"]
        self.UI_inserimento = self.UI_calls_plot_import.bottoni["inserimento"]

        self.UI_import_path = self.UI_calls_plot_import.paths["path_import"]
        
        self.UI_x1 = self.UI_calls_plot_import.entrate["x1"]
        self.UI_x2 = self.UI_calls_plot_import.entrate["x2"]
        self.UI_y1 = self.UI_calls_plot_import.entrate["y1"]
        self.UI_y2 = self.UI_calls_plot_import.entrate["y2"]


    def dump_data(self, path):
        try:
            with open(path, 'w') as file:
                for coords in self.lista_coordinate_finali:
                    file.write(f"{coords[0]}\t{coords[1]}\n")
    
        except Exception as e:
            print(f"Salvataggio plot ha generato: {e}")


    def update_progress(self):

        self.step_progresso_completamento = 0

        if self.UI_calibrazione.toggled or len(self.lista_coordinate_calibrazione) > 0:
            self.step_progresso_completamento = 1
        
        if self.UI_inserimento.toggled:
            self.step_progresso_completamento = 2


    def update_calibration(self):
        
        self.coppia_xx[0] = Mate.inp2flo(self.UI_x1.text, None)
        self.coppia_xx[1] = Mate.inp2flo(self.UI_x2.text, None)
        self.coppia_yy[0] = Mate.inp2flo(self.UI_y1.text, None)
        self.coppia_yy[1] = Mate.inp2flo(self.UI_y2.text, None)

        if not self.coppia_xx[0] is None and not self.coppia_xx[1] is None and not self.coppia_yy[0] is None and not self.coppia_yy[1] is None:
            cali_coords_numpy = np.array(self.lista_coordinate_calibrazione).astype(float)
            inse_coords_numpy = np.array(self.lista_coordinate_inserimento).astype(float)

            fattore_x, fattore_y = 1, 1

            if len(cali_coords_numpy) > 3:
                fattore_x = (cali_coords_numpy[1, 0] - cali_coords_numpy[0, 0]) / (self.coppia_xx[1] - self.coppia_xx[0]) 
                fattore_y = (cali_coords_numpy[3, 1] - cali_coords_numpy[2, 1]) / (self.coppia_yy[1] - self.coppia_yy[0])  

            if len(inse_coords_numpy) > 0:
                
                self.lista_coordinate_finali = []

                for coords in inse_coords_numpy:

                    x = self.coppia_xx[0] + (coords[0] - cali_coords_numpy[0, 0]) / fattore_x
                    y = self.coppia_yy[1] + (coords[1] - cali_coords_numpy[3, 1]) / fattore_y

                    self.lista_coordinate_finali.append((x, y))


    def select_point(self, logica: Logica):
        array = self.lista_coordinate_calibrazione if self.UI_calibrazione.toggled else self.lista_coordinate_inserimento
        
        if len(array) > 0:

            numpy_coords = np.array(array)
            
            coordinate = numpy_coords[:, :2]
            mouse_pos = np.array(logica.mouse_pos)

            coordinate -= mouse_pos
            distanze = np.linalg.norm(coordinate, axis=1)

            minima = np.argmin(distanze)

            if distanze[minima] < 50:
                self.punto_attivo = int(numpy_coords[minima, 2])
                return 
            else:
                return

        self.punto_attivo = None

    
    def delete_point(self):
        if not self.punto_attivo is None:
            try:
                array = self.lista_coordinate_calibrazione if self.UI_calibrazione.toggled else self.lista_coordinate_inserimento 
                array.pop(self.punto_attivo)
                array = np.array(array) 
                array[self.punto_attivo:, 2] -= 1
                array = list(array)
            except IndexError:
                ...

            self.punto_attivo = None


    def move_point(self, x=0, y=0):
        array = self.lista_coordinate_calibrazione if self.UI_calibrazione.toggled else self.lista_coordinate_inserimento
        modify = np.array(array[self.punto_attivo])
        modify[0] += x
        modify[1] += y
        array[self.punto_attivo] = modify


    def disegna(self, logica: Logica):

        if logica.dragging and not self.punto_attivo is None:
            self.move_point(logica.dragging_dx, - logica.dragging_dy)


        self.update_progress()
        self.update_calibration()

        # informations
        if self.step_progresso_completamento == 0 and len(self.lista_coordinate_calibrazione) == 0:
            self.UI_console_output.text = f"Inizia calibrando l'immagine, future istruzioni seguiranno."
        elif self.step_progresso_completamento == 1 and len(self.lista_coordinate_calibrazione) < 4:
            self.UI_console_output.text = f"In attesa di punti aggiuntivi, punti attuali calibrati: {len(self.lista_coordinate_calibrazione)}"
        elif self.step_progresso_completamento == 2:
            self.UI_console_output.text = f"Calibrazione completata.\nprocedere all'individuazione delle coordinate."

        # texture blit
        if self.reference is None:
            self.schermo.fill([30, 30, 30])
            self.schermo.blit(self.font.render(f"Carica un'immagine", True, [255, 100, 100]), (100, 100))   
        else:
            self.schermo.blit(pygame.transform.scale(self.reference, (self.w, self.h)), (0,0))
        
        # realtà aumentata
        cali_coords_numpy = np.array(self.lista_coordinate_calibrazione).astype(float)
        inse_coords_numpy = np.array(self.lista_coordinate_inserimento).astype(float)

        if len(cali_coords_numpy) > 0:

            cali_coords_numpy[:, 0] -= self.ancoraggio_x
            cali_coords_numpy[:, 1] -= self.ancoraggio_y

            for coords in cali_coords_numpy:
                colore = [100, 255, 100] if coords[2] == self.punto_attivo and self.step_progresso_completamento == 1 else [255, 100, 100]
                pygame.draw.circle(self.schermo, colore, coords[:2], 10)     
        
        if len(inse_coords_numpy) > 0:

            inse_coords_numpy[:, 0] -= self.ancoraggio_x
            inse_coords_numpy[:, 1] -= self.ancoraggio_y

            for coords in inse_coords_numpy:
                colore = [100, 255, 100] if coords[2] == self.punto_attivo and self.step_progresso_completamento != 1 else [100, 255, 255]
                pygame.draw.circle(self.schermo, colore, coords[:2], 10)        
        
        if self.step_progresso_completamento == 2:
            for coords, text in zip(inse_coords_numpy, self.lista_coordinate_finali):
                colore = [100, 255, 100] if coords[2] == self.punto_attivo else [100, 255, 255]
                self.schermo.blit(self.font.render(f"({text[0]:.2f}, {text[1]:.2f})", True, colore), (coords[0], coords[1] - 30))   