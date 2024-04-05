import numpy as np
import pygame
from _modulo_UI import Schermo
import configparser

class Painter:
    def __init__(self) -> None:

        config = configparser.ConfigParser()
        config.read('./DATA/settings.ini')

        self.schermo_madre: pygame.Surface
        
        self.w: int
        self.h: int

        self.ancoraggio_x: int
        self.ancoraggio_y: int
        
        self.offset_x_sx: float
        self.offset_y_up: float
        
        self.offset_x_dx: float
        self.offset_y_dw: float
        
        self.w_plot_area: float
        self.h_plot_area: float
        
        self.w_proportion: float = eval(config.get('Grafici', 'w_plot_area'))
        self.h_proportion: float = eval(config.get('Grafici', 'h_plot_area'))

        self.schermo: pygame.Surface
        self.bg_color: tuple[int] = eval(config.get('Grafici', 'bg_color'))
        self.text_color: tuple[int] = eval(config.get('Grafici', 'text_color'))
    
        self.data_path: str
    
        self.plots: list[Plot] = []
        
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
            r"\NULL": "κ",
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
            r"\NULL": "Κ",
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
            r"\Omega": "Ω"
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
    
    
    def import_plot_data(self, path: str, divisore: str = None) -> None:
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
            self.max_x = np.maximum(self.max_x, np.max(plot.x))
            self.max_y = np.maximum(self.max_y, np.max(plot.y))
            self.min_x = np.minimum(self.min_x, np.min(plot.x))
            self.min_y = np.minimum(self.min_y, np.min(plot.y))

        for plot in self.plots:
            x_adattata = self.w_plot_area * (plot.x - self.min_x) / (self.max_x - self.min_x)
            x_adattata += self.start_x
            
            y_adattata = self.h_plot_area * (plot.y - self.min_y) / (self.max_y - self.min_y)
            y_adattata = - y_adattata + self.start_y
                    
            plot.x_screen = x_adattata
            plot.y_screen = y_adattata
    
    
    def disegna_plots(self) -> None:
        
        self.schermo.fill(self.bg_color)
        
        self.adattamento_data2schermo()
        
        self.debug_info[1] = sum([len(i.x) for i in self.plots])
        
        for plot in self.plots:
            
            for x, y in zip(plot.x_screen.astype(int), plot.y_screen.astype(int)):
                pygame.draw.circle(self.schermo, [255, 255, 255], (x, y), 2)

            for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:-1], plot.y_screen.astype(int)[:-1], plot.x_screen.astype(int)[1:], plot.y_screen.astype(int)[1:]):
                pygame.draw.line(self.schermo, [255, 255, 255], (x1, y1), (x2, y2), 1)
    

    def disegna_metadata(self, text, bottone) -> None:
        
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
        testo_x = Painter.check_latex(f"\lambda [nm]")
        
        self.schermo.blit(self.font_tipo.render(testo_x, True, self.text_color), (
            self.start_x + self.w_plot_area // 2 - self.font_pixel_dim[0] * len(testo_x) / 2,
            self.start_y + 3 * (self.h - self.start_y) // 5
        ))
        
        # testo asse y
        testo_y = Painter.check_latex(f"Conteggi [-]")
        
        label_y_scr = self.font_tipo.render(testo_y, True, self.text_color)
        label_y_scr = pygame.transform.rotate(label_y_scr, 90)
    
        self.schermo.blit(label_y_scr, (
            self.start_x - 3 * self.start_x // 5 - self.font_pixel_dim[1],
            self.start_y - self.h_plot_area // 2 - self.font_pixel_dim[0] * len(testo_y) / 2,
        ))

        if self.visualize_second_ax:
            # testo asse 2 y
            testo_y = Painter.check_latex(f"Conteggi [-]")
            
            label_y_scr = self.font_tipo.render(testo_y, True, self.text_color)
            label_y_scr = pygame.transform.rotate(label_y_scr, 90)
        
            self.schermo.blit(label_y_scr, (
                self.end_x + self.start_x - 2 * self.start_x // 5,
                self.start_y - self.h_plot_area // 2 - self.font_pixel_dim[0] * len(testo_y) / 2,
            ))
    
        self.re_compute_font(36)
        
        # titolo
        titolo = Painter.check_latex("Titolo")
        titolo = Painter.check_latex(text) if bottone else text
        
        self.schermo.blit(self.font_tipo.render(titolo, True, self.text_color), (
            self.start_x + self.w_plot_area // 2 - self.font_pixel_dim[0] * len(titolo) / 2,
            self.end_y // 2 - self.font_pixel_dim[1] / 2
        ))

        "------------------------------------------------------------------------------------------------"

        self.re_compute_font(16)
        
        # legenda
        pos_x = self.w * 0.2
        pos_y = self.h * 0.3
        max_len_legenda = 0

        for indice, plot in enumerate(self.plots):
            legenda = self.font_tipo.render(f"{plot.nome}", True, plot.colore)
            max_len_legenda = max(len(f"{plot.nome}"), max_len_legenda)
            self.schermo.blit(legenda, (pos_x, pos_y + indice * 1.5 * self.font_pixel_dim[1]))
        
        pygame.draw.rect(self.schermo, self.text_color, [
            pos_x - self.font_pixel_dim[0], pos_y - self.font_pixel_dim[1],
            self.font_pixel_dim[0] * (max_len_legenda + 2), self.font_pixel_dim[1] * (len(self.plots) + 1) * 1.5
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