import numpy as np
from scipy.optimize import curve_fit
import pygame
from _modulo_UI import Schermo, WidgetData, Logica, UI
from _modulo_MATE import Mate
import configparser
import os
from copy import deepcopy

class Plot:
    def __init__(self, nome: str, x: np.ndarray[float], y: np.ndarray[float], ey: np.ndarray[float] | None) -> None:
        self.nome = nome
        
        self.x = x
        self.y = y
        self.ey = ey
        self.y_interp_lin: np.ndarray[float] | None = None
        self.grado_inter: int = 1

        self.x_screen: np.ndarray[float]
        self.y_screen: np.ndarray[float]
        self.ey_screen: np.ndarray[float] | None
        self.xi_screen: np.ndarray[float] | None
        self.yi_screen: np.ndarray[float] | None
        
        self.colore: list = [255, 255, 255]
        
        self.scatter: bool = True
        self.function: bool = False
        self.interpolate: bool = True 
        self.interpolation_type: str = "" 

        self.dim_pall: int = 1
        self.dim_link: int = 1

        self.acceso: bool = 0

        self.maschera: np.ndarray[bool] | None = None
        self.interpol_maschera: np.ndarray[bool] | None = None
    

class Painter:
    def __init__(self) -> None:

        config = configparser.ConfigParser()
        config.read('./DATA/settings.ini')

        self.schermo_madre: pygame.Surface
        
        self.w: int
        self.h: int

        self.ancoraggio_x: int
        self.ancoraggio_y: int

        self.start_x: float
        self.start_y: float
        
        self.end_x: float
        self.end_y: float
        
        self.w_plot_area: float
        self.h_plot_area: float
        
        self.w_proportion: float = eval(config.get('Grafici', 'w_plot_area'))
        self.h_proportion: float = eval(config.get('Grafici', 'h_plot_area'))
        
        self.bounding_box: pygame.rect.Rect

        self.x_legenda: float
        self.y_legenda: float

        self.schermo: pygame.Surface
        self.bg_color: tuple[int] = [255, 255, 255]
        self.text_color: tuple[int]
    
        self.data_path: str
    
        self.plots: list[Plot] = []
        self.data_points_coords: np.array[float]
        self.active_plot: int = 0

        self.zoom_min_x: float = 0.0
        self.zoom_max_x: float = 1.0
        self.zoom_min_y: float = 0.0
        self.zoom_max_y: float = 1.0
        self.zoom_mode: bool = False
        
        self.normalizza: bool = False
        self.min_y_l: list[float] = [0.0, 0.0]
        self.max_y_l: list[float] = [1.0, 1.0]

        self.dim_font_base = 32
        self.dim_font = 32 
        self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
        self.font_pixel_dim = self.font_tipo.size("a")

        self.approx_label: int = int(config.get('Grafici', 'approx_label'))
        self.visualize_second_ax: bool = eval(config.get('Grafici', 'visualize_second_ax'))

        self.debug_info: list[str] = [(), "", [], ""] 
        # 0: width, height
        # 1: total points
        # 2: names
        # 3: ...

        '---------------ANIMATION----------------'

        self.old_widget_data: WidgetData = WidgetData()

        self.animation: bool = True
        self.duration: int = 20
        self.progress: float = 0.0 # goes from 0.0 to 1.0
    
    
    def re_compute_font(self, factor: float = 1) -> None:
        self.dim_font = int(self.dim_font_base * factor)
        self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
        self.font_pixel_dim = self.font_tipo.size("a")
    

    def re_compute_size(self, secondo_asse: bool = False) -> None:
        
        self.visualize_second_ax = secondo_asse

        if secondo_asse:

            self.w_plot_area = self.w_proportion * self.w
            self.h_plot_area = self.h_proportion * self.h
            
            self.start_x = (self.w - self.w_plot_area) // 2
            self.start_y = self.h - (self.h - self.h_plot_area) // 2
            
            self.end_x = self.start_x + self.w_plot_area
            self.end_y = self.start_y - self.h_plot_area

        else:

            self.w_plot_area = self.w_proportion * self.w
            self.h_plot_area = self.h_proportion * self.h
            
            self.start_x = (self.w - self.w_plot_area) // 2
            self.start_y = self.h - (self.h - self.h_plot_area) // 2
            
            self.w_plot_area += self.start_x // 2
            self.h_plot_area += (self.h - self.start_y) // 2

            self.end_x = self.start_x + self.w_plot_area
            self.end_y = self.start_y - self.h_plot_area

        self.bounding_box = pygame.rect.Rect([self.start_x - 20, self.end_y - 20, self.w_plot_area + 40, self.h_plot_area + 40])
        # self.bounding_box = pygame.rect.Rect([0, 0, self.w, self.h])
        self.bounding_box[0] += self.ancoraggio_x
        self.bounding_box[1] += self.ancoraggio_y


    @staticmethod
    def check_latex(input_str: str) -> str:
        dizionario = {
            r"\alpha": "α",
            r"\beta": "β",
            r"\gamma": "γ",
            r"\delta": "δ",
            r"\epsilon": "ε",
            r"\zeta": "ζ",
            r"\eta": "η",
            r"\theta": "θ",
            r"\NULL": "ι",
            r"\kappa": "κ",
            r"\lambda": "λ",
            r"\mu": "μ",
            r"\nu": "ν",
            r"\NULL": "ξ",
            r"\NULL": "ο",
            r"\pi": "π",
            r"\rho": "ρ",
            r"\NULL": "ς",
            r"\sigma": "σ",
            r"\tau": "τ",
            r"\NULL": "υ",
            r"\phi": "φ",
            r"\chi": "χ",
            r"\psi": "ψ",
            r"\omega": "ω",
            r"\Alpha": "Α",
            r"\Beta": "Β",
            r"\Gamma": "Γ",
            r"\Delta": "Δ",
            r"\Epsilon": "Ε",
            r"\Zeta": "Ζ",
            r"\Eta": "Η",
            r"\Theta": "Θ",
            r"\NULL": "Ι",
            r"\Kappa": "Κ",
            r"\Lambda": "Λ",
            r"\Mu": "Μ",
            r"\NULL": "Ν",
            r"\NULL": "Ξ",
            r"\NULL": "Ο",
            r"\Pi": "Π",
            r"\Rho": "Ρ",
            r"\Sigma": "Σ",
            r"\Tau": "Τ",
            r"\NULL": "Υ",
            r"\Phi": "Φ",
            r"\Chi": "Χ",
            r"\Psi": "Ψ",
            r"\Omega": "Ω",
            r"\pm": "±",
            r"\sqrt": "√"
        }

        for indice, segno in dizionario.items():
            if indice in input_str: input_str = input_str.replace(indice, segno)

        return input_str

    
    def link_ui(self, info_schermo: Schermo) -> None: 
        self.schermo_madre = info_schermo.madre
        
        self.w = info_schermo.w
        self.h = info_schermo.h
        
        self.w_plot_area = self.w_proportion * self.w
        self.h_plot_area = self.h_proportion * self.h
        
        self.start_x = (self.w - self.w_plot_area) // 2
        self.start_y = self.h - (self.h - self.h_plot_area) // 2
        
        self.end_x = self.start_x + self.w_plot_area
        self.end_y = self.start_y - self.h_plot_area
        
        self.ridimensiona_carattere = 1 if info_schermo.shift_x == 0 else 0.7

        self.debug_info[0] = (self.w, self.h)

        self.ancoraggio_x = info_schermo.ancoraggio_x
        self.ancoraggio_y = info_schermo.ancoraggio_y 
        
        self.schermo = info_schermo.schermo
    
    
    def change_active_plot_UIBASED(self, ui: UI) -> None:
        # aggiorno grafico selezionato
        self.active_plot = ui.scena["main"].scrolls["grafici"].scroll_item_selected + ui.scena["main"].scrolls["grafici"].first_item

        # aggiorno le entry box con i valori del nuovo grafico
        ui.scena["main"].entrate["nome_grafico"].text = str(self.plots[self.active_plot].nome)
        ui.scena["main"].entrate["nome_grafico"].puntatore = len(str(self.plots[self.active_plot].nome)) - 1
        ui.scena["main"].entrate["color_plot"].text = f"{Mate.rgb2hex(self.plots[self.active_plot].colore)}"
        ui.scena["main"].entrate["dim_link"].text = str(self.plots[self.active_plot].dim_link)
        ui.scena["main"].entrate["dim_pallini"].text = str(self.plots[self.active_plot].dim_pall)

        ui.scena["main"].bottoni["toggle_inter"].toggled = self.plots[self.active_plot].interpolate 
        ui.scena["main"].bottoni["toggle_pallini"].toggled = self.plots[self.active_plot].scatter 
        ui.scena["main"].bottoni["toggle_collegamenti"].toggled = self.plots[self.active_plot].function
        ui.scena["main"].bottoni["acceso"].toggled = self.plots[self.active_plot].acceso


    def change_active_plot_INDEXBASED(self, ui: UI, index: int) -> None:
        # aggiorno grafico selezionato
        ui.scena["main"].scrolls["grafici"].scroll_item_selected = index
        
        first_item = index - 2
        if first_item < 0: first_item = 0

        ui.scena["main"].scrolls["grafici"].first_item = first_item
        self.active_plot = index

        # aggiorno le entry box con i valori del nuovo grafico
        ui.scena["main"].entrate["nome_grafico"].text = str(self.plots[self.active_plot].nome)
        ui.scena["main"].entrate["nome_grafico"].puntatore = len(str(self.plots[self.active_plot].nome)) - 1
        ui.scena["main"].entrate["color_plot"].text = f"{Mate.rgb2hex(self.plots[self.active_plot].colore)}"
        ui.scena["main"].entrate["dim_link"].text = str(self.plots[self.active_plot].dim_link)
        ui.scena["main"].entrate["dim_pallini"].text = str(self.plots[self.active_plot].dim_pall)

        ui.scena["main"].bottoni["toggle_inter"].toggled = self.plots[self.active_plot].interpolate 
        ui.scena["main"].bottoni["toggle_pallini"].toggled = self.plots[self.active_plot].scatter 
        ui.scena["main"].bottoni["toggle_collegamenti"].toggled = self.plots[self.active_plot].function
        ui.scena["main"].bottoni["acceso"].toggled = self.plots[self.active_plot].acceso


    def nearest_coords(self, ui: UI, logica: Logica) -> None:
        
        if self.bounding_box.collidepoint(logica.mouse_pos) and len(self.data_points_coords) > 0:

            coordinate = self.data_points_coords[:, :2]
            mouse_pos = np.array(logica.mouse_pos) - np.array([self.ancoraggio_x, self.ancoraggio_y])

            coordinate -= mouse_pos
            distanze = np.linalg.norm(coordinate, axis=1)

            minima = np.argmin(distanze)

            if distanze[minima] < 50:
                indice_grafico_minimo = int(self.data_points_coords[minima, 2])
                self.change_active_plot_INDEXBASED(ui, indice_grafico_minimo)


    def import_plot_data(self, path: str, divisore: str = None) -> None:
        
        self.data_path = path
        self.divisore = divisore
        
        # SUPPORTO .CSV
        if self.data_path.endswith(".csv"): self.divisore = ","

        # estrazione data
        with open(self.data_path, 'r') as file:
            data = [line for line in file]

        # SUPPORTO FORMATO HEX utf-16-le
        if data[0].startswith(r"ÿþ"): 
            import codecs
            with codecs.open(self.data_path, 'r', encoding='utf-16-le') as file:
                data = [line.strip() for line in file]

        data = [i.split(self.divisore) for i in data]

        # controllo dati indesiderati
        for coordinate in data:
            if "\n" in coordinate:
                coordinate.remove("\n")
    
        # controllo tipologia float dei dati
        for coordinate in data[::-1]:
            for elemento in coordinate:
                try:
                    float(elemento)
                except ValueError:
                    data.remove(coordinate)
                    break
    
        # controllo presenza dati None 
        data = [i for i in data if i]
    
        try:
            # CONVERSIONE ARRAY DI FLOATS
            if len(data[0]) != len(data[1]): data.pop(0)
            data = np.array(data).astype(float)    
            x = data[:, 0]
            y = data[:, 1]
            ey = data[:, 2] if data.shape[1] == 3 else None 
            
            nome = path.split('\\')[-1]
            
            # test ordinamento x
            indici = np.argsort(x)
            x = x[indici]
            y = y[indici]
            ey = ey[indici] if data.shape[1] == 3 else None 

            self.plots.append(Plot(nome, x, y, ey))
            self.debug_info[2].append(nome)
        
        except:
            print(f"Impossibile caricare il file: {path}")
    

    def full_import_plot_data(self, path_input: str = 'PLOT_DATA/default') -> None:
        
        files = os.listdir(path_input)

        self.plots = []
        self.debug_info[2] = []

        for f in files:
            path = os.path.join(path_input, f)
            if os.path.isfile(path):    
                self.import_plot_data(path)


    def adattamento_data2schermo(self) -> None:
        '''
        Analizza tutti i plot e li ridimensiona in base ai nuovi dati / cambio di finestra
        '''
        try:
            # ora funziona per un singolo grafico, ci sarà da implementare:
            # - lettura errori
            # - lettura multi-plots
            
            # calcolo i valori limite del grafico
            self.calcolo_bb_plots()
            
            # aggiorno limiti massimi di zoom x
            self.update_zoom_limits()

            # calcolo delle maschere aggiornate
            self.calcolo_maschere_plots()

            # ricalcolo i nuovi limiti dello zoom sulle y in base alla modalità
            if not self.zoom_mode:
                self.max_y = -np.inf
                self.min_y = np.inf
                
                for plot in self.plots:
                    if plot.acceso:
                        self.max_y = np.maximum(self.max_y, np.max(plot.y[plot.maschera]))
                        self.min_y = np.minimum(self.min_y, np.min(plot.y[plot.maschera]))

                        if not plot.ey is None:
                            error_plus = plot.y + plot.ey
                            error_minus = plot.y - plot.ey
                            
                            self.max_y = np.maximum(self.max_y, np.max(error_plus))
                            self.min_y = np.minimum(self.min_y, np.min(error_minus))
                        
                        if not plot.y_interp_lin is None and plot.interpolate:
                            self.max_y = np.maximum(self.max_y, np.max(plot.y_interp_lin[plot.interpol_maschera]))
                            self.min_y = np.minimum(self.min_y, np.min(plot.y_interp_lin[plot.interpol_maschera]))
                
            dati = []
            conteggio_assi_diversi = 0

            for index, plot in enumerate(self.plots):

                if plot.acceso and self.normalizza and len([plot for plot in self.plots if plot.acceso]) == 2:
                    
                    # se siamo nella condizione in cui vengono normalizzati i grafici -> Vengono ricalcolati tutti i valori e i bound
                    self.min_y_l[conteggio_assi_diversi] = min(plot.y[plot.maschera])
                    self.max_y_l[conteggio_assi_diversi] = max(plot.y[plot.maschera])

                    if not plot.y_interp_lin is None:

                        self.min_y_l[conteggio_assi_diversi] = min(self.min_y_l[conteggio_assi_diversi], min(plot.y_interp_lin[plot.interpol_maschera]))
                        self.max_y_l[conteggio_assi_diversi] = max(self.max_y_l[conteggio_assi_diversi], max(plot.y_interp_lin[plot.interpol_maschera]))

                    x_adattata = self.w_plot_area * (plot.x[plot.maschera] - self.min_x) / (self.max_x - self.min_x)
                    x_adattata += self.start_x
                    
                    y_adattata = self.h_plot_area * (plot.y[plot.maschera] - self.min_y_l[conteggio_assi_diversi]) / (self.max_y_l[conteggio_assi_diversi] - self.min_y_l[conteggio_assi_diversi])
                    y_adattata = - y_adattata + self.start_y
                    
                    plot.x_screen = x_adattata
                    plot.y_screen = y_adattata

                    if not plot.ey is None: 
                        ey_adattata = self.h_plot_area * plot.ey[plot.maschera] / (self.max_y_l[conteggio_assi_diversi] - self.min_y_l[conteggio_assi_diversi])
                        plot.ey_screen = ey_adattata
                        
                    if not plot.y_interp_lin is None and plot.interpolate: 
                        
                        xi_adattata = self.w_plot_area * (plot.x[plot.interpol_maschera] - self.min_x) / (self.max_x - self.min_x)
                        xi_adattata += self.start_x
                        plot.xi_screen = xi_adattata

                        yi_adattata = self.h_plot_area * (plot.y_interp_lin[plot.interpol_maschera] - self.min_y_l[conteggio_assi_diversi]) / (self.max_y_l[conteggio_assi_diversi] - self.min_y_l[conteggio_assi_diversi])
                        plot.yi_screen = - yi_adattata + self.start_y

                    # caricamento dati coordinate
                    for x, y in zip(plot.x_screen, plot.y_screen):
                        dati.append([x, y, index])
                    
                    conteggio_assi_diversi += 1

                elif plot.acceso:
                    x_adattata = self.w_plot_area * (plot.x[plot.maschera] - self.min_x) / (self.max_x - self.min_x)
                    x_adattata += self.start_x
                    
                    y_adattata = self.h_plot_area * (plot.y[plot.maschera] - self.min_y) / (self.max_y - self.min_y)
                    y_adattata = - y_adattata + self.start_y
                    
                    plot.x_screen = x_adattata
                    plot.y_screen = y_adattata

                    if not plot.ey is None: 
                        ey_adattata = self.h_plot_area * plot.ey[plot.maschera] / (self.max_y - self.min_y)
                        plot.ey_screen = ey_adattata
                        
                    if not plot.y_interp_lin is None and plot.interpolate: 
                        
                        xi_adattata = self.w_plot_area * (plot.x[plot.interpol_maschera] - self.min_x) / (self.max_x - self.min_x)
                        xi_adattata += self.start_x
                        plot.xi_screen = xi_adattata

                        yi_adattata = self.h_plot_area * (plot.y_interp_lin[plot.interpol_maschera] - self.min_y) / (self.max_y - self.min_y)
                        plot.yi_screen = - yi_adattata + self.start_y

                    # caricamento dati coordinate
                    for x, y in zip(plot.x_screen, plot.y_screen):
                        dati.append([x, y, index])


            self.data_points_coords = np.array(dati)
            if len(self.data_points_coords) != 0:
                self.data_points_coords = self.data_points_coords.ravel()
                self.data_points_coords = self.data_points_coords.reshape(-1, 3)

        except ValueError:
            # check per troppi pochi punti
            print("Attenzione! Zoom troppo grande, punti insufficienti! Applico zoom default")
            self.reset_zoom()


    def calcolo_maschere_plots(self) -> None:
        for plot in self.plots:
            if plot.acceso:
                maschera_x = np.logical_and(plot.x >= self.min_x, plot.x <= self.max_x)
                maschera_y = np.logical_and(plot.y >= self.min_y, plot.y <= self.max_y)
                plot.maschera = np.logical_and(maschera_x, maschera_y)


    def calcolo_bb_plots(self) -> None:
        max_x = -np.inf
        max_y = -np.inf
        max_ey = -np.inf
        min_x = np.inf
        min_y = np.inf
        min_ey = np.inf

        for plot in self.plots:
            if plot.acceso:
                max_x = np.maximum(max_x, np.max(plot.x))
                max_y = np.maximum(max_y, np.max(plot.y))
                min_x = np.minimum(min_x, np.min(plot.x))
                min_y = np.minimum(min_y, np.min(plot.y))

        self.max_x = max_x
        self.min_x = min_x
        self.max_y = max_y
        self.min_y = min_y

    
    def update_zoom_limits(self) -> None:
        delta_x = self.max_x - self.min_x
        
        self.max_x = self.min_x + self.zoom_max_x * delta_x
        self.min_x = self.min_x + self.zoom_min_x * delta_x
        
        delta_y = self.max_y - self.min_y
        
        self.max_y = self.min_y + self.zoom_max_y * delta_y
        self.min_y = self.min_y + self.zoom_min_y * delta_y


    def disegna_plots(self, widget_data: WidgetData) -> None:

        if not WidgetData.are_attributes_equal(self.old_widget_data, widget_data):
            self.animation = True
            self.progress = 0
            WidgetData.update_attributes(self.old_widget_data, widget_data)

        if self.animation:
            self.progress += 1 / self.duration
            if self.progress >= 1.0: self.progress = 0; self.animation = False

        self.normalizza = widget_data.normalizza

        # Sezione di impostazioni grafico attuale attivo
        self.plots[self.active_plot].interpolate = widget_data.toggle_inter 
        self.plots[self.active_plot].grado_inter = Mate.inp2int(widget_data.grado_inter, 1) 
        self.plots[self.active_plot].function = widget_data.toggle_collegamenti 
        self.plots[self.active_plot].scatter = widget_data.toggle_pallini 
        self.plots[self.active_plot].acceso = widget_data.acceso 
        self.plots[self.active_plot].colore = Mate.hex2rgb(widget_data.color_plot) 

        self.plots[self.active_plot].dim_link = Mate.inp2int(widget_data.dim_link)
        self.plots[self.active_plot].dim_pall = Mate.inp2int(widget_data.dim_pallini)

        self.plots[self.active_plot].nome = widget_data.nome_grafico


        self.schermo.fill(self.bg_color)
        
        self.adattamento_data2schermo()
        
        self.debug_info[1] = sum([len(i.x) for i in self.plots])
        
        for index, plot in enumerate(self.plots):

            if plot.acceso:
                
                animation_bound, colore_animazione = self.animation_update(plot, index)

                if plot.scatter:
                    for x, y in zip(plot.x_screen.astype(int)[:animation_bound], plot.y_screen.astype(int)[:animation_bound]):
                        pygame.draw.circle(self.schermo, colore_animazione, (x, y), plot.dim_pall)

                if plot.scatter and not plot.ey is None:
                    for x, y, ey in zip(plot.x_screen.astype(int)[:animation_bound], plot.y_screen.astype(int)[:animation_bound], plot.ey_screen.astype(int)[:animation_bound]):
                        pygame.draw.line(self.schermo, colore_animazione, (x, y), (x, y + ey), plot.dim_link)
                        pygame.draw.line(self.schermo, colore_animazione, (x, y), (x, y - ey), plot.dim_link)
                        pygame.draw.line(self.schermo, colore_animazione, (x - ey / 5, y + ey), (x + ey / 5, y + ey), plot.dim_link)
                        pygame.draw.line(self.schermo, colore_animazione, (x - ey / 5, y - ey), (x + ey / 5, y - ey), plot.dim_link)

                if plot.interpolate and not plot.y_interp_lin is None:
                    for x1, y1, x2, y2 in zip(plot.xi_screen.astype(int)[:animation_bound-1], plot.yi_screen.astype(int)[:animation_bound-1], plot.xi_screen.astype(int)[1:animation_bound], plot.yi_screen.astype(int)[1:animation_bound]):
                        pygame.draw.line(self.schermo, [255, 0, 0], (x1, y1), (x2, y2), plot.dim_link)
                        
                if plot.function:
                    for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:animation_bound-1], plot.y_screen.astype(int)[:animation_bound-1], plot.x_screen.astype(int)[1:animation_bound], plot.y_screen.astype(int)[1:animation_bound]):
                        pygame.draw.line(self.schermo, colore_animazione, (x1, y1), (x2, y2), plot.dim_link)


    def animation_update(self, plot: Plot, index: int, noanim: bool = False) -> tuple[int, list[int]]:
        animation_bound = int(len(plot.x_screen)*self.progress) if self.animation else len(plot.x_screen)
        if noanim: animation_bound = len(plot.x_screen)
        colore_animazione = [0, 255, 0] if self.active_plot == index and self.animation else plot.colore

        return animation_bound, colore_animazione


    def disegna_metadata(self, logica: Logica, widget_data: WidgetData) -> None:

        # import settings
        if widget_data.latex_check:
            titolo = Painter.check_latex(widget_data.titolo) 
            testo_x = Painter.check_latex(widget_data.labelx)
            testo_y = Painter.check_latex(widget_data.labely)
            testo_2y = Painter.check_latex(widget_data.label2y)
        else:
            titolo = widget_data.titolo
            testo_x = widget_data.labelx
            testo_y = widget_data.labely
            testo_2y = widget_data.label2y

        # prova di conversione
        self.approx_label = Mate.conversione_limite(widget_data.round_label, 2, 9)
        self.dim_font_base = Mate.conversione_limite(widget_data.dim_font, 32, 128)
        
        self.w_proportion = Mate.conversione_limite(widget_data.area_w, 0.8, 0.9)
        self.h_proportion = Mate.conversione_limite(widget_data.area_h, 0.8, 0.9)

        self.x_legenda = Mate.conversione_limite(widget_data.x_legenda, 0.2, 0.9)
        self.y_legenda = Mate.conversione_limite(widget_data.y_legenda, 0.3, 0.9)

        self.bg_color = Mate.hex2rgb(widget_data.color_bg)
        self.text_color = Mate.hex2rgb(widget_data.color_text)

        # recalculation of window
        self.re_compute_size(widget_data.toggle_2_axis)

        "-------------------------------------------------------------"

        # plots bounding box
        if widget_data.toggle_plt_bb:
            pygame.draw.rect(self.schermo, self.text_color, [
                self.start_x, self.end_y,
                self.w_plot_area, self.h_plot_area
            ], 1)
        
        # X axis
        pygame.draw.line(self.schermo, self.text_color, 
            [self.start_x, self.start_y + 1 * (self.h - self.start_y) // 4],
            [self.end_x, self.start_y + 1 * (self.h - self.start_y) // 4]
        )

        # colore assi
        if self.normalizza and len([plot for plot in self.plots if plot.acceso]) == 2:
            colori_assi = [plot.colore for plot in self.plots if plot.acceso]
        else: colori_assi = [self.text_color, self.text_color]
        
        # Y axis
        pygame.draw.line(self.schermo, colori_assi[0], 
            [3 * self.start_x // 4, self.start_y],
            [3 * self.start_x // 4, self.end_y]
        )

        if self.visualize_second_ax:
            # 2 Y axis
            pygame.draw.line(self.schermo, colori_assi[1], 
                [self.end_x + 1 * self.start_x // 4, self.start_y],
                [self.end_x + 1 * self.start_x // 4, (self.h - self.start_y)]
            )
        
        # scalini sugli assi e valori
        self.re_compute_font(0.625)
        minimo_locale_label = self.min_y if not self.normalizza else self.min_y_l[0]
        massimo_locale_label = self.max_y if not self.normalizza else self.max_y_l[0]
        
        delta_x = self.max_x - self.min_x
        delta_y = massimo_locale_label - minimo_locale_label
        delta_y2 = self.max_y_l[1] - self.min_y_l[1]

        for i in range(7):
            
            # data x
            pos_var_x = (self.start_x + self.w_plot_area * i/6)
            pos_var_y = (self.start_y - self.h_plot_area * i/6)
            
            pygame.draw.line(self.schermo, self.text_color, 
                [pos_var_x, self.start_y + 1 * (self.h - self.start_y) // 4 - self.w // 100],
                [pos_var_x, self.start_y + 1 * (self.h - self.start_y) // 4 + self.w // 100]
            )
            
            self.schermo.blit(self.font_tipo.render(f"{self.min_x + delta_x * i / 6:.{self.approx_label}f}", True, self.text_color), (
                pos_var_x - self.font_pixel_dim[0] * len(f"{self.min_x + delta_x * i / 6:.{self.approx_label}f}") / 2,
                self.start_y + (self.h - self.start_y) // 3
            ))

            
            # data y
            pygame.draw.line(self.schermo, colori_assi[0], 
                [3 * self.start_x // 4 - self.w // 100, pos_var_y],
                [3 * self.start_x // 4 + self.w // 100, pos_var_y]
            )
            
            label_y_scr = self.font_tipo.render(f"{minimo_locale_label + delta_y * i / 6:.{self.approx_label}f}", True, colori_assi[0])
            label_y_scr = pygame.transform.rotate(label_y_scr, 90)
        

            self.schermo.blit(label_y_scr, (
                self.start_x - self.start_x // 3 - self.font_pixel_dim[1],
                pos_var_y - self.font_pixel_dim[0] * len(f"{minimo_locale_label + delta_y * i / 6:.{self.approx_label}f}") / 2
            ))
            
            if self.visualize_second_ax:
                # data 2 y
                pygame.draw.line(self.schermo, colori_assi[1], 
                    [self.end_x + 1 * self.start_x // 4 - self.w // 100, pos_var_y],
                    [self.end_x + 1 * self.start_x // 4 + self.w // 100, pos_var_y]
                )
                
                label_y_scr = self.font_tipo.render(f"{self.min_y_l[1] + delta_y2 * i / 6:.{self.approx_label}f}", True, colori_assi[1])
                label_y_scr = pygame.transform.rotate(label_y_scr, 90)
            
                self.schermo.blit(label_y_scr, (
                    self.end_x + 1 * self.start_x // 3,
                    pos_var_y - self.font_pixel_dim[0] * len(f"{self.min_y_l[1] + delta_y2 * i / 6:.{self.approx_label}f}") / 2
                ))
        
        "------------------------------------------------------------------------------------------------"
        self.re_compute_font()    
        
        # testo asse x
        self.schermo.blit(self.font_tipo.render(testo_x, True, self.text_color), (
            self.start_x + self.w_plot_area // 2 - self.font_pixel_dim[0] * len(testo_x) / 2,
            self.start_y + 3 * (self.h - self.start_y) // 5
        ))
        
        # testo asse y
        label_y_scr = self.font_tipo.render(testo_y, True, self.text_color)
        label_y_scr = pygame.transform.rotate(label_y_scr, 90)
    
        self.schermo.blit(label_y_scr, (
            self.start_x - 3 * self.start_x // 5 - self.font_pixel_dim[1],
            self.start_y - self.h_plot_area // 2 - self.font_pixel_dim[0] * len(testo_y) / 2,
        ))

        if self.visualize_second_ax:
            # testo asse 2 y
            label_y_scr = self.font_tipo.render(testo_2y, True, self.text_color)
            label_y_scr = pygame.transform.rotate(label_y_scr, 90)
        
            self.schermo.blit(label_y_scr, (
                self.end_x + self.start_x - 2 * self.start_x // 5,
                self.start_y - self.h_plot_area // 2 - self.font_pixel_dim[0] * len(testo_2y) / 2,
            ))
    
        self.re_compute_font(1.125)
        
        # titolo
        self.schermo.blit(self.font_tipo.render(titolo, True, self.text_color), (
            self.start_x + self.w_plot_area // 2 - self.font_pixel_dim[0] * len(titolo) / 2,
            self.end_y // 2 - self.font_pixel_dim[1] / 2
        ))

        "------------------------------------------------------------------------------------------------"

        self.re_compute_font(.5)
        
        # legenda
        pos_x = self.start_x + self.w_plot_area * self.x_legenda
        pos_y = self.end_y + self.h_plot_area * self.y_legenda
        max_len_legenda = 0

        plot_accesi = [plot for plot in self.plots if plot.acceso]

        numero_interpolazioni_attive = len([plot for plot in self.plots if plot.acceso and plot.interpolate])

        if len(plot_accesi) + numero_interpolazioni_attive > 1:

            depth = 0
            for plot in plot_accesi:
                legenda = self.font_tipo.render(f"{plot.nome}", True, plot.colore)
                max_len_legenda = max(len(f"{plot.nome}"), max_len_legenda)
                self.schermo.blit(legenda, (pos_x, pos_y + depth * 1.5 * self.font_pixel_dim[1]))
                depth += 1
            
                if plot.interpolate:
                    legenda = self.font_tipo.render(f"Fit dei dati ({plot.interpolation_type})", True, [255, 0, 0])
                    max_len_legenda = max(len(f"Fit dei dati ({plot.interpolation_type})"), max_len_legenda)
                    self.schermo.blit(legenda, (pos_x, pos_y + depth * 1.5 * self.font_pixel_dim[1]))
                    depth += 1

            pygame.draw.rect(self.schermo, self.text_color, [
                pos_x - self.font_pixel_dim[0], pos_y - self.font_pixel_dim[1],
                self.font_pixel_dim[0] * (max_len_legenda + 2), self.font_pixel_dim[1] * (len(plot_accesi) + 1 + numero_interpolazioni_attive) * 1.5
            ], 1)

        # mouse coordinate
        coords_values = self.value_research_plot_area(logica.mouse_pos)
        mouse_coords = self.font_tipo.render(f"{coords_values[0]:.{self.approx_label}f}, {coords_values[1]:.{self.approx_label}f}", True, self.text_color)
        self.schermo.blit(mouse_coords, (logica.mouse_pos[0] - self.ancoraggio_x, logica.mouse_pos[1] - self.ancoraggio_y - 1.5 * self.font_pixel_dim[1]))

        # zoom BB
        if logica.dragging:

            min_bb_x = min(logica.original_start_pos[0], logica.mouse_pos[0])
            max_bb_x = max(logica.original_start_pos[0], logica.mouse_pos[0])
            min_bb_y = min(logica.original_start_pos[1], logica.mouse_pos[1])
            max_bb_y = max(logica.original_start_pos[1], logica.mouse_pos[1])

            pygame.draw.rect(self.schermo, [0, 255, 0], [
                min_bb_x - self.ancoraggio_x,
                min_bb_y - self.ancoraggio_y, 
                max_bb_x - min_bb_x, 
                max_bb_y - min_bb_y
            ], 2)


    def reset_zoom(self, logica: Logica | None = None) -> None:
        if logica is None:
            self.zoom_min_x = 0.0
            self.zoom_min_y = 0.0
            self.zoom_max_x = 1.0
            self.zoom_max_y = 1.0
        elif self.bounding_box.collidepoint(logica.mouse_pos):
            self.zoom_min_x = 0.0
            self.zoom_min_y = 0.0
            self.zoom_max_x = 1.0
            self.zoom_max_y = 1.0

    def values_zoom(self, logica: Logica) -> None:
        drag_distance = np.array(logica.dragging_end_pos) - np.array(logica.original_start_pos)
        drag_distance = np.linalg.norm(drag_distance)
        
        self.zoom_mode = logica.shift

        if drag_distance > 1:
            if self.bounding_box.collidepoint(logica.mouse_pos):
                x_ini_zoom, y_ini_zoom = self.pixel_research_plot_area(logica.original_start_pos)
                x_fin_zoom, y_fin_zoom = self.pixel_research_plot_area(logica.dragging_end_pos)
                
                delta_zoom_x = self.zoom_max_x - self.zoom_min_x

                self.zoom_max_x = max(x_fin_zoom, x_ini_zoom) * delta_zoom_x + self.zoom_min_x 
                self.zoom_min_x = min(x_fin_zoom, x_ini_zoom) * delta_zoom_x + self.zoom_min_x 

                if self.zoom_mode:
                    delta_zoom_y = self.zoom_max_y - self.zoom_min_y

                    self.zoom_max_y = max(y_fin_zoom, y_ini_zoom) * delta_zoom_y + self.zoom_min_y 
                    self.zoom_min_y = min(y_fin_zoom, y_ini_zoom) * delta_zoom_y + self.zoom_min_y 
                    


    def pixel_research_plot_area(self, general_coordinate: tuple[float]) -> tuple[float]:
        
        x = general_coordinate[0] - self.ancoraggio_x - self.start_x
        y = general_coordinate[1] - self.ancoraggio_y - self.end_y

        perc_x = x / self.w_plot_area 
        perc_y = 1 - y / self.h_plot_area

        return perc_x, perc_y
    

    def value_research_plot_area(self, general_coordinate: tuple[float]) -> tuple[float, float]:
        
        perc_x, perc_y = self.pixel_research_plot_area(general_coordinate)

        delta_x = self.max_x - self.min_x 
        delta_y = self.max_y - self.min_y 

        ris_x = self.min_x + delta_x * perc_x
        ris_y = self.min_y + delta_y * perc_y

        return ris_x, ris_y


    def aggiorna_schermo(self) -> None:
        self.schermo_madre.blit(self.schermo, (self.ancoraggio_x, self.ancoraggio_y))


    def linear_interpolation(self) -> tuple[float, float, float, float, float, str, str]:

        try:    
            base_data = self.plots[self.active_plot]

            grado = base_data.grado_inter

            if base_data.maschera is None: return "Prego, Accendere un grafico per cominciare"
            
            x = base_data.x[base_data.maschera]
            y = base_data.y[base_data.maschera]
            ey = base_data.ey[base_data.maschera] if not base_data.ey is None else None

            if len(x) < grado + 2: return f"Punti insufficienti.\nGrado: {grado}\nPunti minimi richiesti: {grado + 2}\nPunti presenti nel grafico: {len(x)}"

            if grado == 1:

                m = None
                q = None
                m_e = None
                q_e = None
                correlation = None
                correlation_type = ""

                if ey is None:
                    # INIZIO LOGICA INTERPOLAZIONE NON PESATA ----------------------------------------------------------
                    coeff, covar = np.polyfit(x, y, deg = 1, cov= True) 
                    m, q = coeff
                    m_e, q_e = np.sqrt(np.diag(covar))
                    correlation = round(1 - np.sum( ( y - (m*x+q) )**2 ) /np.sum( ( y - (np.sum(y)/len(y)) )**2 ),3)
                    correlation_type = "R quadro"
                else:
                    # INIZIO LOGICA INTERPOLAZIONE PESATA ----------------------------------------------------------
                    coeff, covar = np.polyfit(x, y, deg = 1, w = 1/ey, cov= True)
                    m, q = coeff
                    m_e, q_e = np.sqrt(np.diag(covar))
                    correlation = round(np.sum(((y - (m*x+q))/ey)**2) / (len(x)-2),3)
                    correlation_type = "\chi quadro"
                
                base_data.interpolation_type = "Retta ai minimi quadrati"
                params_str = f"Interpolazione lineare del grafico {base_data.nome}:\nm: {m:.{self.approx_label}f} \pm {m_e:.{self.approx_label}f}\nq: {q:.{self.approx_label}f} \pm {q_e:.{self.approx_label}f}\n{correlation_type}: {correlation:.{self.approx_label}f}"

                errori = (m_e, q_e)

            else:
                if grado > 8: grado = 8

                coeff, covar = np.polyfit(x, y, deg = grado, cov= True) 
                errori = np.sqrt(np.diag(covar))

                coeff_name = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
                console_output = [f"{n}: {c:.{self.approx_label}f} \pm {e:.{self.approx_label}f}\n" for n, c, e in zip(coeff_name, coeff, errori)]
                params_str = f"Interpolazione polinomiale di grado {grado} del grafico {base_data.nome}:\n"

                base_data.interpolation_type = f"Fit polinomiale di grado {grado}"

                params_str += "".join(console_output)

            # compute interpolation plot
            x = base_data.x
            y_i = np.zeros(len(x))

            for index, arg in enumerate(coeff[::-1]):
                if arg is None: return None
                y_i += x ** index * arg
            
            base_data.y_interp_lin = y_i
            base_data.interpol_maschera = deepcopy(base_data.maschera)

            return params_str

        except RuntimeError as e:
            return f"Parametri ottimali non trovati, prova con un altro zoom.\n{e}"


    def customfoo_interpolation(self, curve: str = "gaussian"):

        base_data = self.plots[self.active_plot]

        if base_data.maschera is None: return "Prego, Accendere un grafico per cominciare"
        
        x = base_data.x[base_data.maschera]
        y = base_data.y[base_data.maschera]

        try:

            match curve:
                case "gaussian":
                    def gaussian(x, amplitude, mean, stddev):
                        return amplitude * np.exp(-((x - mean) / stddev) ** 2 / 2)
                
                    if len(x) < 3: return f"Punti insufficienti.\nNumero parametri: 3\nPunti minimi richiesti: 4\nPunti presenti nel grafico: {len(x)}"

                    initial_guess_gauss = [max(y)-min(y), x[len(x)//2], (len(x) - 6) // 2]  # Initial guess for amplitude, mean, and standard deviation
                    params_gaus, covariance = curve_fit(gaussian, x, y, p0=initial_guess_gauss)

                    base_data.y_interp_lin = gaussian(base_data.x, *params_gaus)
                    base_data.interpol_maschera = deepcopy(base_data.maschera)

                    base_data.interpolation_type = "Fit Gaussiano"

                    errori = np.sqrt(np.diag(covariance))
                    console_output = f"Interpolazione Guassiana del grafico {base_data.nome}:\nA: {params_gaus[0]:.{self.approx_label}f} \pm {errori[0]:.{self.approx_label}f}\n\mu: {params_gaus[1]:.{self.approx_label}f} \pm {errori[1]:.{self.approx_label}f}\n\sigma: {params_gaus[2]:.{self.approx_label}f} \pm {errori[2]:.{self.approx_label}f}"

                case "sigmoid":
                    def sigmoide(x, a, b, lambda_0, delta_lambda):
                        return b + a / (1 + np.exp((-np.array(x) + lambda_0) / delta_lambda))

                    if len(x) < 5: return f"Punti insufficienti.\nNumero parametri: 4\nPunti minimi richiesti: 5\nPunti presenti nel grafico: {len(x)}"

                    initial_guess_sigmo = [max(y)-min(y), (max(y)-min(y)) // 2, x[len(x)//2], 1]
                    # a -> larghezza delta (segno determina orientamento scalino)
                    # b -> y_punto_medio
                    # lambda_0 -> x_punto_medio
                    # delta_lambda -> valore per il quale un ala raggiunge metà dell'altezza del flesso
                    params_sigm, covariance = curve_fit(sigmoide, x, y, p0=initial_guess_sigmo)

                    base_data.y_interp_lin = sigmoide(base_data.x, *params_sigm)
                    base_data.interpol_maschera = deepcopy(base_data.maschera)

                    base_data.interpolation_type = "Fit Sigmoide"

                    errori = np.sqrt(np.diag(covariance))
                    console_output = f"Interpolazione sigmoide del grafico {base_data.nome}:\na: {params_sigm[0]:.{self.approx_label}f} \pm {errori[0]:.{self.approx_label}f}\nb: {params_sigm[1]:.{self.approx_label}f} \pm {errori[1]:.{self.approx_label}f}\n\lambda0: {params_sigm[2]:.{self.approx_label}f} \pm {errori[2]:.{self.approx_label}f}\n\Delta\lambda: {params_sigm[3]:.{self.approx_label}f} \pm {errori[3]:.{self.approx_label}f}"

            return console_output

        except RuntimeError as e:
            return f"Parametri ottimali non trovati, prova con un altro zoom.\n£{e}£"