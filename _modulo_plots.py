import numpy as np
import pygame
from _modulo_UI import Schermo, WidgetData, Logica, UI
from _modulo_MATE import Mate
import configparser
from copy import deepcopy
import os

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

        self.x_legenda: float
        self.y_legenda: float

        self.schermo: pygame.Surface
        self.bg_color: tuple[int] = [255, 255, 255]
        self.text_color: tuple[int]
    
        self.data_path: str
    
        self.plots: list[Plot] = []
        self.active_plot: int = 0
        
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
    
    
    def change_active_plot(self, ui: UI):

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


    def import_plot_data(self, path: str, divisore: str = None) -> None:
        
        # TODO -> Import automatico diversi formati

        self.data_path = path
        self.divisore = divisore
        
        # estrazione data
        with open(self.data_path, 'r') as file:
            data = [line for line in file]
    
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
    
        # CONVERSIONE ARRAY DI FLOATS
        data = np.array(data).astype(float)
        
        x = data[:, 0]
        y = data[:, 1]
        ey = data[:, 2] if data.shape[1] == 3 else None 
        
        nome = path.split("/")[-1]
        
        self.plots.append(Plot(nome, x, y, ey))
        self.debug_info[2].append(nome)
        
    
    def full_import_plot_data(self) -> None:

        files = os.listdir("PLOT_DATA/")

        for f in files:
            path = os.path.join("PLOT_DATA/", f)
            if os.path.isfile(path):    
                self.import_plot_data(path)



    def adattamento_data2schermo(self) -> None:
        '''
        Analizza tutti i plot e li ridimensiona in base ai nuovi dati / cambio di finestra
        '''
        # ora funziona per un singolo grafico, ci sarà da implementare:
        # - lettura errori
        # - lettura multi-plots
        
        self.max_x = -np.inf
        self.max_y = -np.inf
        self.min_x = np.inf
        self.min_y = np.inf
        
        for plot in self.plots:
            if plot.acceso:
                self.max_x = np.maximum(self.max_x, np.max(plot.x))
                self.max_y = np.maximum(self.max_y, np.max(plot.y))
                self.min_x = np.minimum(self.min_x, np.min(plot.x))
                self.min_y = np.minimum(self.min_y, np.min(plot.y))

        for plot in self.plots:
            if plot.acceso:
                x_adattata = self.w_plot_area * (plot.x - self.min_x) / (self.max_x - self.min_x)
                x_adattata += self.start_x
                
                y_adattata = self.h_plot_area * (plot.y - self.min_y) / (self.max_y - self.min_y)
                y_adattata = - y_adattata + self.start_y
                        
                plot.x_screen = x_adattata
                plot.y_screen = y_adattata
    
    
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
        
        for plot in self.plots:

            if plot.acceso:
                
                animation_bound = int(len(plot.x_screen)*self.progress) if self.animation else len(plot.x_screen)
                
                if plot.scatter:

                    for x, y in zip(plot.x_screen.astype(int)[:animation_bound], plot.y_screen.astype(int)[:animation_bound]):
                        pygame.draw.circle(self.schermo, plot.colore, (x, y), plot.dim_pall)

                if plot.function:
                    for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:animation_bound-1], plot.y_screen.astype(int)[:animation_bound-1], plot.x_screen.astype(int)[1:animation_bound], plot.y_screen.astype(int)[1:animation_bound]):
                        pygame.draw.line(self.schermo, plot.colore, (x1, y1), (x2, y2), plot.dim_link)
    

    def disegna_metadata(self, widget_data: WidgetData) -> None:
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
        delta_y = self.max_y - self.min_y

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
            
            label_y_scr = self.font_tipo.render(f"{self.min_y + delta_y * i / 6:.{self.approx_label}f}", True, self.text_color)
            label_y_scr = pygame.transform.rotate(label_y_scr, 90)
        
            self.schermo.blit(label_y_scr, (
                self.start_x - self.start_x // 3 - self.font_pixel_dim[1],
                pos_var_y - self.font_pixel_dim[0] * len(f"{self.min_y + delta_y * i / 6:.{self.approx_label}f}") / 2
            ))
            
            if self.visualize_second_ax:
                # data 2 y
                pygame.draw.line(self.schermo, self.text_color, 
                    [self.end_x + 1 * self.start_x // 4 - self.w // 100, pos_var_y],
                    [self.end_x + 1 * self.start_x // 4 + self.w // 100, pos_var_y]
                )
                
                label_y_scr = self.font_tipo.render(f"{self.min_y + delta_y * i / 6:.{self.approx_label}f}", True, self.text_color)
                label_y_scr = pygame.transform.rotate(label_y_scr, 90)
            
                self.schermo.blit(label_y_scr, (
                    self.end_x + 1 * self.start_x // 3,
                    pos_var_y - self.font_pixel_dim[0] * len(f"{self.min_y + delta_y * i / 6:.{self.approx_label}f}") / 2
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

    
    def aggiorna_schermo(self) -> None:
        self.schermo_madre.blit(self.schermo, (self.ancoraggio_x, self.ancoraggio_y))
    

class Plot:
    def __init__(self, nome: str, x: np.ndarray[float], y: np.ndarray[float], ey: np.ndarray[float] | None) -> None:
        self.nome = nome
        
        self.x = x
        self.y = y
        self.ey = ey
        
        self.x_screen: np.ndarray[float]
        self.y_screen: np.ndarray[float]
        
        self.colore: list = [255, 255, 255]
        
        self.scatter: bool = True
        self.function: bool = False
        self.interpolate: bool = False 

        self.dim_pall: int = 1
        self.dim_link: int = 1

        self.acceso: bool = False