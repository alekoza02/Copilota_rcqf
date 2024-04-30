import numpy as np
import pygame
from _modulo_UI import Schermo, WidgetData, Logica, UI
from _modulo_MATE import Mate
import configparser
import os

class Plot:
    def __init__(self, nome: str, x: np.ndarray[float], y: np.ndarray[float], ey: np.ndarray[float] | None) -> None:
        self.nome = nome
        
        self.x = x
        self.y = y
        self.ey = ey
        
        self.x_screen: np.ndarray[float]
        self.y_screen: np.ndarray[float]
        self.ey_screen: np.ndarray[float] | None
        
        self.colore: list = [255, 255, 255]
        
        self.scatter: bool = True
        self.function: bool = False
        self.interpolate: bool = False 

        self.dim_pall: int = 1
        self.dim_link: int = 1

        self.acceso: bool = 0

        self.maschera: np.ndarray[bool]

    

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
        self.duration: int = 60
        self.progress: float = 0.0 # goes from 0.0 to 1.0
    
    
    def re_compute_font(self, dim: int = 32) -> None:
        self.dim_font = int(dim * self.ridimensiona_carattere)
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
    
    
    def change_active_plot_UIBASED(self, ui: UI):
        # aggiorno grafico selezionato
        self.active_plot = ui.scena["main"].scrolls["grafici"].scroll_item_selected + ui.scena["main"].scrolls["grafici"].first_item

        # aggiorno le entry box con i valori del nuovo grafico
        ui.scena["main"].entrate["nome_grafico"].text = str(self.plots[self.active_plot].nome)
        ui.scena["main"].entrate["nome_grafico"].puntatore = len(str(self.plots[self.active_plot].nome)) - 1
        ui.scena["main"].entrate["color_plot"].text = f"{Mate.rgb2hex(self.plots[self.active_plot].colore)}"
        ui.scena["main"].entrate["dim_link"].text = str(self.plots[self.active_plot].dim_link)
        ui.scena["main"].entrate["dim_pallini"].text = str(self.plots[self.active_plot].dim_pall)

        ui.scena["main"].bottoni["toggle_pallini"].toggled = self.plots[self.active_plot].scatter 
        ui.scena["main"].bottoni["toggle_collegamenti"].toggled = self.plots[self.active_plot].function
        ui.scena["main"].bottoni["acceso"].toggled = self.plots[self.active_plot].acceso


    def change_active_plot_INDEXBASED(self, ui: UI, logica: Logica, index: int):
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

        ui.scena["main"].bottoni["toggle_pallini"].toggled = self.plots[self.active_plot].scatter 
        ui.scena["main"].bottoni["toggle_collegamenti"].toggled = self.plots[self.active_plot].function
        ui.scena["main"].bottoni["acceso"].toggled = self.plots[self.active_plot].acceso


    def nearest_coords(self, ui: UI, logica: Logica):
        
        # TODO fix
        if self.bounding_box.collidepoint(logica.mouse_pos) and len(self.data_points_coords) > 0:

            coordinate = self.data_points_coords[:, :2]
            mouse_pos = np.array(logica.mouse_pos) - np.array([self.ancoraggio_x, self.ancoraggio_y])

            coordinate -= mouse_pos
            distanze = np.linalg.norm(coordinate, axis=1)

            minima = np.argmin(distanze)

            if distanze[minima] < 10:
                indice_grafico_minimo = int(self.data_points_coords[minima, 2])
                self.change_active_plot_INDEXBASED(ui, logica, indice_grafico_minimo)


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
    

    def full_import_plot_data(self, path_input: str = 'PLOT_DATA/') -> None:
        
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
                
            dati = []

            for index, plot in enumerate(self.plots):
                if plot.acceso:
                    x_adattata = self.w_plot_area * (plot.x[plot.maschera] - self.min_x) / (self.max_x - self.min_x)
                    x_adattata += self.start_x
                    
                    y_adattata = self.h_plot_area * (plot.y[plot.maschera] - self.min_ey) / (self.max_ey - self.min_ey)
                    y_adattata = - y_adattata + self.start_y
                    
                    plot.x_screen = x_adattata
                    plot.y_screen = y_adattata

                    if not plot.ey is None: 
                        ey_adattata = self.h_plot_area * plot.ey[plot.maschera] / (self.max_ey - self.min_ey)
                        plot.ey_screen = ey_adattata
                        
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


    def calcolo_maschere_plots(self):
        for plot in self.plots:
            if plot.acceso:
                maschera_x = np.logical_and(plot.x >= self.min_x, plot.x <= self.max_x)
                maschera_y = np.logical_and(plot.y >= self.min_y, plot.y <= self.max_y)
                plot.maschera = np.logical_and(maschera_x, maschera_y)


    def calcolo_bb_plots(self):
        self.max_x = -np.inf
        self.max_y = -np.inf
        self.max_ey = -np.inf
        self.min_x = np.inf
        self.min_y = np.inf
        self.min_ey = np.inf

        for plot in self.plots:
            if plot.acceso:
                self.max_x = np.maximum(self.max_x, np.max(plot.x))
                self.max_y = np.maximum(self.max_y, np.max(plot.y))
                self.min_x = np.minimum(self.min_x, np.min(plot.x))
                self.min_y = np.minimum(self.min_y, np.min(plot.y))

                if not plot.ey is None:
                    error_plus = plot.y + plot.ey
                    error_minus = plot.y - plot.ey
                    
                    self.max_ey = np.maximum(self.max_ey, np.max(error_plus))
                    self.min_ey = np.minimum(self.min_ey, np.min(error_minus))
                else: 
                    self.max_ey = np.maximum(self.max_ey, self.max_y)
                    self.min_ey = np.minimum(self.min_ey, self.min_y)

    
    def update_zoom_limits(self):
        delta_x = self.max_x - self.min_x
        
        self.max_x = self.min_x + self.zoom_max_x * delta_x
        self.min_x = self.min_x + self.zoom_min_x * delta_x
        
        delta_y = self.max_ey - self.min_ey
        
        self.max_ey = self.min_ey + self.zoom_max_y * delta_y
        self.min_ey = self.min_ey + self.zoom_min_y * delta_y


    def disegna_plots(self, widget_data: WidgetData) -> None:

        if not WidgetData.are_attributes_equal(self.old_widget_data, widget_data):
            self.animation = True
            self.progress = 0
            WidgetData.update_attributes(self.old_widget_data, widget_data)

        if self.animation:
            self.progress += 1 / self.duration
            if self.progress >= 1.0: self.progress = 0; self.animation = False

        # Sezione di impostazioni grafico attuale attivo
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
                
                animation_bound = int(len(plot.x_screen)*self.progress) if self.animation else len(plot.x_screen)
                colore_animazione = [0, 255, 0] if self.active_plot == index and self.animation else plot.colore

                if plot.scatter:
                    for x, y in zip(plot.x_screen.astype(int)[:animation_bound], plot.y_screen.astype(int)[:animation_bound]):
                        pygame.draw.circle(self.schermo, colore_animazione, (x, y), plot.dim_pall)

                if plot.scatter and not plot.ey is None:
                    for x, y, ey in zip(plot.x_screen.astype(int)[:animation_bound], plot.y_screen.astype(int)[:animation_bound], plot.ey_screen.astype(int)[:animation_bound]):
                        pygame.draw.line(self.schermo, colore_animazione, (x, y), (x, y + ey), plot.dim_link)
                        pygame.draw.line(self.schermo, colore_animazione, (x, y), (x, y - ey), plot.dim_link)
                        pygame.draw.line(self.schermo, colore_animazione, (x - ey / 5, y + ey), (x + ey / 5, y + ey), plot.dim_link)
                        pygame.draw.line(self.schermo, colore_animazione, (x - ey / 5, y - ey), (x + ey / 5, y - ey), plot.dim_link)

                if plot.function:
                    for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:animation_bound-1], plot.y_screen.astype(int)[:animation_bound-1], plot.x_screen.astype(int)[1:animation_bound], plot.y_screen.astype(int)[1:animation_bound]):
                        pygame.draw.line(self.schermo, colore_animazione, (x1, y1), (x2, y2), plot.dim_link)
    

    def disegna_metadata(self, logica: Logica, widget_data: WidgetData) -> None:
        '''
        titolo -> titolo grafico
        labelx -> titolo label x
        labely -> titolo label y (sx)
        label2y -> titolo label y (dx)
        round_label -> precisione in virgola mobile dei numeri sugli scalini
        color_bg -> colore dello sfondo
        color_text -> colore di tutta l'interfaccia grafica
        area_w -> area consentita da utilizzare per la larghezza
        area_h -> area consentita da utilizzare per l'altezza
        x_legenda -> posizione x della legenda        
        y_legenda -> posizione y della legenda

        latex_check -> controllo se appplicare il LaTeX
        toggle_2_axis -> attiva o disattiva il secondo asse verticale
        '''

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
        
        # Y axis
        pygame.draw.line(self.schermo, self.text_color, 
            [3 * self.start_x // 4, self.start_y],
            [3 * self.start_x // 4, self.end_y]
        )

        if self.visualize_second_ax:
            # 2 Y axis
            pygame.draw.line(self.schermo, self.text_color, 
                [self.end_x + 1 * self.start_x // 4, self.start_y],
                [self.end_x + 1 * self.start_x // 4, (self.h - self.start_y)]
            )
        
        # scalini sugli assi e valori
        self.re_compute_font(20)
        delta_x = self.max_x - self.min_x
        delta_y = self.max_ey - self.min_ey

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
            pygame.draw.line(self.schermo, self.text_color, 
                [3 * self.start_x // 4 - self.w // 100, pos_var_y],
                [3 * self.start_x // 4 + self.w // 100, pos_var_y]
            )
            
            label_y_scr = self.font_tipo.render(f"{self.min_ey + delta_y * i / 6:.{self.approx_label}f}", True, self.text_color)
            label_y_scr = pygame.transform.rotate(label_y_scr, 90)
        
            self.schermo.blit(label_y_scr, (
                self.start_x - self.start_x // 3 - self.font_pixel_dim[1],
                pos_var_y - self.font_pixel_dim[0] * len(f"{self.min_ey + delta_y * i / 6:.{self.approx_label}f}") / 2
            ))
            
            if self.visualize_second_ax:
                # data 2 y
                pygame.draw.line(self.schermo, self.text_color, 
                    [self.end_x + 1 * self.start_x // 4 - self.w // 100, pos_var_y],
                    [self.end_x + 1 * self.start_x // 4 + self.w // 100, pos_var_y]
                )
                
                label_y_scr = self.font_tipo.render(f"{self.min_ey + delta_y * i / 6:.{self.approx_label}f}", True, self.text_color)
                label_y_scr = pygame.transform.rotate(label_y_scr, 90)
            
                self.schermo.blit(label_y_scr, (
                    self.end_x + 1 * self.start_x // 3,
                    pos_var_y - self.font_pixel_dim[0] * len(f"{self.min_ey + delta_y * i / 6:.{self.approx_label}f}") / 2
                ))
        
        "------------------------------------------------------------------------------------------------"
        self.re_compute_font(32)    
        
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
    
        self.re_compute_font(36)
        
        # titolo
        self.schermo.blit(self.font_tipo.render(titolo, True, self.text_color), (
            self.start_x + self.w_plot_area // 2 - self.font_pixel_dim[0] * len(titolo) / 2,
            self.end_y // 2 - self.font_pixel_dim[1] / 2
        ))

        "------------------------------------------------------------------------------------------------"

        self.re_compute_font(16)
        
        # legenda
        pos_x = self.start_x + self.w_plot_area * self.x_legenda
        pos_y = self.end_y + self.h_plot_area * self.y_legenda
        max_len_legenda = 0

        plot_accesi = [plot for plot in self.plots if plot.acceso]

        if len(plot_accesi) != 0:

            for indice, plot in enumerate(plot_accesi):
                legenda = self.font_tipo.render(f"{plot.nome}", True, plot.colore)
                max_len_legenda = max(len(f"{plot.nome}"), max_len_legenda)
                self.schermo.blit(legenda, (pos_x, pos_y + indice * 1.5 * self.font_pixel_dim[1]))
            
            pygame.draw.rect(self.schermo, self.text_color, [
                pos_x - self.font_pixel_dim[0], pos_y - self.font_pixel_dim[1],
                self.font_pixel_dim[0] * (max_len_legenda + 2), self.font_pixel_dim[1] * (len(plot_accesi) + 1) * 1.5
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


    def reset_zoom(self, logica: Logica | None = None):
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

    def values_zoom(self, logica: Logica):
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
                    


    def pixel_research_plot_area(self, general_coordinate):
        
        x = general_coordinate[0] - self.ancoraggio_x - self.start_x
        y = general_coordinate[1] - self.ancoraggio_y - self.end_y

        perc_x = x / self.w_plot_area 
        perc_y = 1 - y / self.h_plot_area

        return perc_x, perc_y
    

    def value_research_plot_area(self, general_coordinate):
        
        perc_x, perc_y = self.pixel_research_plot_area(general_coordinate)

        delta_x = self.max_x - self.min_x 
        delta_y = self.max_y - self.min_y 

        ris_x = self.min_x + delta_x * perc_x
        ris_y = self.min_y + delta_y * perc_y

        return ris_x, ris_y


    def aggiorna_schermo(self) -> None:
        self.schermo_madre.blit(self.schermo, (self.ancoraggio_x, self.ancoraggio_y))
    