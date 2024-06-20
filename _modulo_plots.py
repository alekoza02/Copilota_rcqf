import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import trapz
import pygame
from _modulo_UI import Schermo, WidgetDataPlots, Logica, UI, Scena
from _modulo_MATE import Mate
import configparser
import os
from copy import deepcopy

class Plot:
    def __init__(self, nome: str, x: np.ndarray[float], y: np.ndarray[float], ey: np.ndarray[float] | None) -> None:
        """Generazione di un grafico

        Parameters
        ----------
        nome : str
            Nome con cui verrà visualizzato il grafico
        x : np.ndarray[float]
            Array dei valori X
        y : np.ndarray[float]
            Array dei valori Y
        ey : np.ndarray[float] | None
            Array dei valori degli errori sulle Y
        """
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
        self.gradiente: bool = False
        
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

        self.debugging = eval(config.get('Default', 'debugging'))

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
        
        self.bounding_box = pygame.rect.Rect([0, 0, 1, 1])

        self.x_legenda: float
        self.y_legenda: float

        self.schermo: pygame.Surface
        self.bg_color: tuple[int] = [255, 255, 255]
        self.text_color: tuple[int]
    
        self.data_path: str
    
        self.plots: list[Plot] = []
        self.data_points_coords: np.array[float]
        self.active_plot: int = 0

        self.use_custom_borders: bool = False
        self.x_min: float = 0.0
        self.x_max: float = 0.0
        self.y_min: float = 0.0
        self.y_max: float = 0.0

        self.zoom_min_x: float = 0.0
        self.zoom_max_x: float = 1.0
        self.zoom_min_y: float = 0.0
        self.zoom_max_y: float = 1.0
        self.zoom_mode: bool = False
        
        self.normalizza: bool = False
        self.min_y_l: list[float] = [0.0, 0.0]
        self.max_y_l: list[float] = [1.0, 1.0]

        self.min_y: float = 0
        self.min_x: float = 0
        self.max_y: float = 0
        self.max_x: float = 0

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

        self.old_widget_data: WidgetDataPlots = WidgetDataPlots()

        self.animation: bool = True
        self.duration: int = 20
        self.progress: float = 0.0 # goes from 0.0 to 1.0
    
    
    def re_compute_font(self, factor: float = 1) -> None:
        """
        Ricalcolo della dimensione del font in base a quanto mi serve.

        Parameters
        ----------
        factor : float, optional
            Fattore di scala rispetto alla dimensione precedente. Con questo approccio, il cambio di dimensione dello schermo non è più un problema, by default 1
        """
        self.dim_font = int(self.dim_font_base * factor)
        self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
        self.font_pixel_dim = self.font_tipo.size("a")
    

    def re_compute_size(self, secondo_asse: bool = False) -> None:
        """Ricalcola la dimensione dell'UI dei grafici in base alla presenza del secondo asse Y

        Parameters
        ----------
        secondo_asse : bool, optional
            Se presente la posizione di tutti gli elementi UI dovranno essere spostati di conseguenza, by default False
        """
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
        self.bounding_box[0] += self.ancoraggio_x
        self.bounding_box[1] += self.ancoraggio_y


    @staticmethod
    def check_latex(input_str: str) -> str:
        """Data una stringa, controlla la presenza di caratteri speciali riportati nella variabile 'dizionario'. Se sono presenti li sostituisce con il carattere ASCII corrispondente

        Parameters
        ----------
        input_str : str
            Stringa da analizzare

        Returns
        -------
        str
            Stringa analizzata
        """

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

    
    def link_ui(self, ui: UI) -> None: 
        """Collegamento UI con il painter. Raccoglie informazioni circa le dimensioni dello schermo e si calcola l'ancoraggio

        Parameters
        ----------
        info_schermo : Schermo
            Dato la classe Schermo, posso capire le informazioni che mi servono
        """

        info_schermo = ui.scena["plots"].schermo["viewport"]

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
        """Cambio del grafico attivo in focus basato sull'iterazione dell'ui. Richiede l'UI per funzionare

        Parameters
        ----------
        ui : UI
            Classe UI contenente le informazioni per scegliere il nuovo grafico e caricare le relative informazioni
        """
        # aggiorno grafico selezionato
        self.riordina_plots(ui.scena["plots"].scrolls["grafici"].indici)
        self.attiva_plots(ui.scena["plots"].scrolls["grafici"].elementi_attivi)
        self.active_plot = ui.scena["plots"].scrolls["grafici"].scroll_item_selected + ui.scena["plots"].scrolls["grafici"].first_item

        # aggiorno le entry box con i valori del nuovo grafico
        ui.scena["plots"].entrate["nome_grafico"].text = str(self.plots[self.active_plot].nome)
        ui.scena["plots"].entrate["nome_grafico"].puntatore = len(str(self.plots[self.active_plot].nome)) - 1
        ui.scena["plots"].entrate["color_plot"].text = f"{Mate.rgb2hex(self.plots[self.active_plot].colore)}"
        ui.scena["plots"].entrate["dim_link"].text = str(self.plots[self.active_plot].dim_link)
        ui.scena["plots"].entrate["dim_pallini"].text = str(self.plots[self.active_plot].dim_pall)

        ui.scena["plots"].bottoni["toggle_inter"].toggled = self.plots[self.active_plot].interpolate 
        ui.scena["plots"].bottoni["toggle_pallini"].toggled = self.plots[self.active_plot].scatter 
        ui.scena["plots"].bottoni["toggle_collegamenti"].toggled = self.plots[self.active_plot].function
        ui.scena["plots"].bottoni["gradiente"].toggled = self.plots[self.active_plot].gradiente


    def change_active_plot_INDEXBASED(self, ui: UI, index: int) -> None:
        """Cambio del grafico attivo in focus basato sull'indice del grafico da scegliere. Richiede l'UI per funzionare

        Parameters
        ----------
        ui : UI
            Classe UI contenente le informazioni per caricare le info del nuovo grafico
        index : int
            Indice del grafico nuovo da caricare
        """

        self.riordina_plots(ui.scena["plots"].scrolls["grafici"].indici)
        self.attiva_plots(ui.scena["plots"].scrolls["grafici"].elementi_attivi)

        # aggiorno grafico selezionato
        first_item = index - 4
        if first_item < 0: first_item = 0

        selected_item = index - first_item

        ui.scena["plots"].scrolls["grafici"].scroll_item_selected = selected_item
        ui.scena["plots"].scrolls["grafici"].first_item = first_item
        self.active_plot = index

        # aggiorno le entry box con i valori del nuovo grafico
        ui.scena["plots"].entrate["nome_grafico"].text = str(self.plots[self.active_plot].nome)
        ui.scena["plots"].entrate["nome_grafico"].puntatore = len(str(self.plots[self.active_plot].nome)) - 1
        ui.scena["plots"].entrate["color_plot"].text = f"{Mate.rgb2hex(self.plots[self.active_plot].colore)}"
        ui.scena["plots"].entrate["dim_link"].text = str(self.plots[self.active_plot].dim_link)
        ui.scena["plots"].entrate["dim_pallini"].text = str(self.plots[self.active_plot].dim_pall)

        ui.scena["plots"].bottoni["toggle_inter"].toggled = self.plots[self.active_plot].interpolate 
        ui.scena["plots"].bottoni["toggle_pallini"].toggled = self.plots[self.active_plot].scatter 
        ui.scena["plots"].bottoni["toggle_collegamenti"].toggled = self.plots[self.active_plot].function
        ui.scena["plots"].bottoni["gradiente"].toggled = self.plots[self.active_plot].gradiente


    def nearest_coords(self, ui: UI, logica: Logica) -> None:
        """Date le informazioni dell'ui e gli input utente, capisce quale sia il grafico più vicino ad un click dell'utente

        Parameters
        ----------
        ui : UI
            Parametro da passare alla funzione 'self.change_active_plot_INDEXBASED'
        logica : Logica
            Parametro per verificare la posizione dell'evento (click del mouse) 
        """
        if self.bounding_box.collidepoint(logica.mouse_pos) and len(self.data_points_coords) > 0:

            coordinate = self.data_points_coords[:, :2]
            mouse_pos = np.array(logica.mouse_pos) - np.array([self.ancoraggio_x, self.ancoraggio_y])

            coordinate -= mouse_pos
            distanze = np.linalg.norm(coordinate, axis=1)

            minima = np.argmin(distanze)

            if distanze[minima] < 50:
                indice_grafico_minimo = int(self.data_points_coords[minima, 2])
                self.change_active_plot_INDEXBASED(ui, indice_grafico_minimo)
                return True
        return False


    def import_plot_data(self, path: str, divisore: str = None) -> None:
        """Importa un tipo di file e genera un plot con le X, Y e gli errori sulle Y (raccoglie rispettivamente le prime 3 colonne)

        Parameters
        ----------
        path : str
            Path al singolo file
        divisore : str, optional
            Divisore delle colonne all'interno del file. Se non specificato, lo cerca di ricavare in autonomia, by default None
        """
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
    

    def full_import_plot_data(self, link_scena: Scena, path_input: str = 'PLOT_DATA/default') -> None:
        """Dato un path importa tutti i file con estensioni accettate (txt, ASCII, dat, csv) e ci genera un plot.

        Parameters
        ----------
        path_input : str, optional
            Path alla cartella con i grafici, by default 'PLOT_DATA/default'
        """
        files = os.listdir(path_input)

        self.plots = []
        self.debug_info[2] = []

        for f in files:
            path = os.path.join(path_input, f)
            if os.path.isfile(path):    
                self.import_plot_data(path)

        self.original_plot_order = self.plots
        link_scena.scrolls["grafici"].elementi = [self.plots[index].nome for index in range(len(self.plots))]
        link_scena.scrolls["grafici"].elementi_attivi = [False for _ in range(len(self.plots))]
        link_scena.scrolls["grafici"].indici = [i for i in range(len(self.plots))]
        link_scena.scrolls["grafici"].update_elements()


    def riordina_plots(self, indici: list[int]):
        new_order = []
        for i in indici:
            new_order.append(self.original_plot_order[i])
        self.plots = new_order


    def attiva_plots(self, indici: list[bool]):
        for plot, accensione in zip(self.plots, indici):
            plot.acceso = accensione
        

    def adattamento_data2schermo(self) -> None:
        """
        Funzione principale che gestisce la ridimensione dei dati alle coordinate dello schermo. Si serve di altre 2 sotto-funzioni:
        - calcolo_maschere_plots
        - calcolo_bb_plots
        - update_zoom_limits
        """
        try:
            if not self.use_custom_borders:
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
            
            else:
                self.reset_zoom()
                self.min_x = self.x_min # questi sono i valori importati dalla entry box 
                self.max_x = self.x_max # questi sono i valori importati dalla entry box
                self.min_y = self.y_min # questi sono i valori importati dalla entry box
                self.max_y = self.y_max # questi sono i valori importati dalla entry box
                self.calcolo_maschere_plots()

            dati = []
            conteggio_assi_diversi = 0

            for index, plot in enumerate(self.plots):

                if plot.acceso and self.normalizza and len([plot for plot in self.plots if plot.acceso]) == 2:
                    
                    # se siamo nella condizione in cui vengono normalizzati i grafici -> Vengono ricalcolati tutti i valori e i bound
                    self.min_y_l[conteggio_assi_diversi] = min(plot.y[plot.maschera])
                    self.max_y_l[conteggio_assi_diversi] = max(plot.y[plot.maschera])

                    if not plot.ey is None:
                        error_plus = plot.y + plot.ey
                        error_minus = plot.y - plot.ey
                        
                        self.max_y_l[conteggio_assi_diversi] = np.maximum(self.max_y_l[conteggio_assi_diversi], np.max(error_plus))
                        self.min_y_l[conteggio_assi_diversi] = np.minimum(self.min_y_l[conteggio_assi_diversi], np.min(error_minus))
                    
                    if not plot.y_interp_lin is None and plot.interpolate:
                        self.max_y_l[conteggio_assi_diversi] = np.maximum(self.max_y_l[conteggio_assi_diversi], np.max(plot.y_interp_lin[plot.interpol_maschera]))
                        self.min_y_l[conteggio_assi_diversi] = np.minimum(self.min_y_l[conteggio_assi_diversi], np.min(plot.y_interp_lin[plot.interpol_maschera]))

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
        """
        Questa funzione serve a ritagliare correttamente i limiti di visualizzazione delle interpolazioni.
        I plot possiedono 'self.y_interp_lin' che è un array di sole y. Per poter gestire correttamente gli zoom, devo creare una maschera di y che compariranno nello schermo e no.
        Con questo sistema posso abilitare le interpolazioni senza dovermi preoccupare di range, dal momento che le 'self.y_interp_lin' e le 'self.y' hanno lunghezza uguale
        """
        for plot in self.plots:
            if plot.acceso:
                maschera_x = np.logical_and(plot.x >= self.min_x, plot.x <= self.max_x)
                maschera_y = np.logical_and(plot.y >= self.min_y, plot.y <= self.max_y)
                plot.maschera = np.logical_and(maschera_x, maschera_y)


    def calcolo_bb_plots(self) -> None:
        """
        Calcolo della bounding box che contiene al minimo tutti i grafici accesi
        """
        max_x = -np.inf
        max_y = -np.inf
        min_x = np.inf
        min_y = np.inf

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
        """
        Con questa funzione, se sono attivi degli zoom, verranno applicati alla bounding box calcolata nella funzione prima e si ridurrà la finestra di analisi
        """
        delta_x = self.max_x - self.min_x
        
        self.max_x = self.min_x + self.zoom_max_x * delta_x
        self.min_x = self.min_x + self.zoom_min_x * delta_x
        
        delta_y = self.max_y - self.min_y
        
        self.max_y = self.min_y + self.zoom_max_y * delta_y
        self.min_y = self.min_y + self.zoom_min_y * delta_y


    def disegna_plots(self, widget_data: WidgetDataPlots) -> None:
        """
        Disegna tutti i grafici caricati e abilitati al disegno.

        Parameters
        ----------
        widget_data : WidgetData
            Necessita dei widget data per poter aggiornare gli attributi dei singoli grafici
        """
        if not WidgetDataPlots.are_attributes_equal(self.old_widget_data, widget_data):
            self.animation = True
            self.progress = 0
            WidgetDataPlots.update_attributes(self.old_widget_data, widget_data)

        if self.animation:
            self.progress += 1 / self.duration
            if self.progress >= 1.0: self.progress = 0; self.animation = False

        self.normalizza = widget_data.normalizza

        # Sezione di impostazioni grafico attuale attivo
        self.plots[self.active_plot].acceso = widget_data.acceso 
        self.plots[self.active_plot].interpolate = widget_data.toggle_inter 
        self.plots[self.active_plot].grado_inter = Mate.inp2int(widget_data.grado_inter, 1) 
        self.plots[self.active_plot].function = widget_data.toggle_collegamenti 
        self.plots[self.active_plot].scatter = widget_data.toggle_pallini 
        self.plots[self.active_plot].gradiente = widget_data.gradiente 
        self.plots[self.active_plot].colore = Mate.hex2rgb(widget_data.color_plot) 

        self.plots[self.active_plot].dim_link = Mate.inp2int(widget_data.dim_link)
        self.plots[self.active_plot].dim_pall = Mate.inp2int(widget_data.dim_pallini)

        self.plots[self.active_plot].nome = widget_data.nome_grafico

        self.adattamento_data2schermo()
        
        self.debug_info[1] = sum([len(i.x) for i in self.plots])
        
        for index, plot in enumerate(self.plots):

            if plot.acceso:
                    
                    animation_bound, colore_animazione = self.animation_update(plot, index)
                    
                    try:
                        if plot.gradiente:
                            # Z BASED 
                            for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:animation_bound-1], plot.y_screen.astype(int)[:animation_bound-1], plot.x_screen.astype(int)[1:animation_bound], plot.y_screen.astype(int)[1:animation_bound]):
                                m = (y2 - y1) / (x2 - x1)
                                for i in range(0, x2 - x1):
                                    y_interpolated = int(y1 + m * i)
                                    colore = (self.start_y - y_interpolated) / self.start_y
                                    colore_finale = np.array(self.bg_color) + (np.array(plot.colore) - np.array(self.bg_color)) * colore
                                    pygame.draw.line(self.schermo, colore_finale, (x1 + i, self.start_y), (x1 + i, y_interpolated), 1)
                    except (TypeError, ValueError) as e:
                        if self.debugging: print(f"Warning: {e} in gradiente")


                    try:
                        if plot.scatter:
                            for x, y in zip(plot.x_screen.astype(int)[:animation_bound], plot.y_screen.astype(int)[:animation_bound]):
                                pygame.draw.circle(self.schermo, colore_animazione, (x, y), plot.dim_pall)
                    except (TypeError, ValueError) as e:
                        if self.debugging: print(f"Warning: {e} in scatter")


                    try:
                        if plot.scatter and not plot.ey is None:
                            for x, y, ey in zip(plot.x_screen.astype(int)[:animation_bound], plot.y_screen.astype(int)[:animation_bound], plot.ey_screen.astype(int)[:animation_bound]):
                                pygame.draw.line(self.schermo, colore_animazione, (x, y), (x, y + ey), plot.dim_link)
                                pygame.draw.line(self.schermo, colore_animazione, (x, y), (x, y - ey), plot.dim_link)
                                pygame.draw.line(self.schermo, colore_animazione, (x - ey / 5, y + ey), (x + ey / 5, y + ey), plot.dim_link)
                                pygame.draw.line(self.schermo, colore_animazione, (x - ey / 5, y - ey), (x + ey / 5, y - ey), plot.dim_link)
                    except (TypeError, ValueError) as e:
                        if self.debugging: print(f"Warning: {e} in errors")


                    try:
                        if plot.interpolate and not plot.y_interp_lin is None:
                            for x1, y1, x2, y2 in zip(plot.xi_screen.astype(int)[:animation_bound-1], plot.yi_screen.astype(int)[:animation_bound-1], plot.xi_screen.astype(int)[1:animation_bound], plot.yi_screen.astype(int)[1:animation_bound]):
                                pygame.draw.line(self.schermo, [255, 0, 0], (x1, y1), (x2, y2), plot.dim_link)
                    except (TypeError, ValueError) as e:
                        if self.debugging: print(f"Warning: {e} in interpolate")

                    
                    try:
                        if plot.function:
                            for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:animation_bound-1], plot.y_screen.astype(int)[:animation_bound-1], plot.x_screen.astype(int)[1:animation_bound], plot.y_screen.astype(int)[1:animation_bound]):
                                pygame.draw.line(self.schermo, colore_animazione, (x1, y1), (x2, y2), plot.dim_link)
                    except (TypeError, ValueError) as e:
                        if self.debugging: print(f"Warning: {e} in function")


                # elif plot.gradiente:

                    # # Horizontal colorgrade
                    # np.array([[[0., 0.], [100., 200.], [600., 300.]]])
                
                    # x_var1 = plot.x_screen.astype(int)[:len(plot.x_screen)-1] - self.start_x
                    # x_var2 = plot.x_screen.astype(int)[1:len(plot.x_screen)] - self.start_x
                    # y_var1 = plot.y_screen.astype(int)[:len(plot.x_screen)-1] - self.end_y
                    # y_var2 = plot.y_screen.astype(int)[1:len(plot.x_screen)] - self.end_y

                    # limite_y_min = np.min(plot.y_screen) - self.end_y
                    # limite_y_max = np.max(plot.y_screen) - self.end_y

                    # v0 = np.stack((x_var1, y_var1), axis=1)
                    # v1 = np.stack((x_var2, y_var2), axis=1)
                    # v2 = np.stack((x_var2, np.ones_like(x_var2) * (self.start_y - self.end_y) - limite_y_min), axis=1)
                    # v3 = np.stack((x_var1, np.ones_like(x_var2) * (self.start_y - self.end_y) - limite_y_min), axis=1)

                    # triangles = np.concatenate((np.stack((v2, v1, v0), axis=1), np.stack((v3, v2, v0), axis=1)))

                    # if update_gradient:
                    #     self.colors_array = Triangle.rasterization(int(self.w_plot_area), int(self.h_plot_area), triangles, np.array(self.bg_color), np.array(plot.colore), limite_y_min, limite_y_max)
                    
                    # colors_surface = pygame.surfarray.make_surface(self.colors_array)  
                    # self.schermo.blit(colors_surface, (self.start_x, self.end_y))
                
                    # ATTEMPTED ALPHA CHANNEL
                    # mask = np.any(colors_array != (0, 0, 0), axis=-1).astype(np.uint8) * 255

                    # # Convert the mask into an alpha channel for the surface
                    # alpha_surface = pygame.Surface(colors_surface.get_size(), pygame.SRCALPHA)
                    # alpha_surface.fill((255, 255, 255, 0))  # Fill with transparent
                    # alpha_surface.blit(colors_surface, (0, 0))  # Blit the new_surface onto alpha_surface
                    
                    # # Apply the mask to the alpha channel
                    # mask_surface = pygame.Surface(colors_surface.get_size(), pygame.SRCALPHA)
                    # pygame.surfarray.pixels_alpha(mask_surface)[:, :] = mask  # Apply mask to alpha channel
                    
                    # # Blit the alpha_surface (with mask) onto the screen
                    # self.schermo.blit(alpha_surface, (self.start_x, self.end_y), special_flags=pygame.BLEND_RGBA_MULT)


    def animation_update(self, plot: Plot, index: int, noanim: bool = False) -> tuple[int, list[int]]:
        """Aggiorna lo stato dell'animazione e switcha tra acceso e spento

        Parameters
        ----------
        plot : Plot
            Questo sarà il grafico ac ui verranno applicate le modifiche di animazione
        index : int
            Indice del grafico che è sotto attivo cambiamento da parte dell'utente. Verrà colorato di [0, 255, 0]
        noanim : bool, optional
            Richiesta di NON - animazione, by default False

        Returns
        -------
        tuple[int, list[int]]
            Restituisce l'indice corrispondente alla % di animazione completa e il colore del grafico
        """
        animation_bound = int(len(plot.x_screen)*self.progress) if self.animation else len(plot.x_screen)
        if noanim: animation_bound = len(plot.x_screen)
        colore_animazione = [0, 255, 0] if self.active_plot == index and self.animation else plot.colore

        return animation_bound, colore_animazione


    def disegna(self, logica: Logica, widget_data: WidgetDataPlots) -> None:
        """Funzione principale richiamata dall'utente che inizia il processo di disegno dell'UI dei grafici e i grafici stessi

        Parameters
        ----------
        logica : Logica
            Classe contenente varie informazioni riguardo agli input dell'utente (mos pos, CTRL, SHIFT, click, drag, ecc.)
        widget_data : WidgetData
            Classe contenente gli attributi dell'UI che potrebbero servire a cambiare le proprietà dei grafici
        """

        self.schermo.fill(self.bg_color)

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

        self.use_custom_borders = widget_data.use_custom_borders
        
        self.x_min = Mate.inp2flo(widget_data.x_min)
        self.x_max = Mate.inp2flo(widget_data.x_max)
        self.y_min = Mate.inp2flo(widget_data.y_min)
        self.y_max = Mate.inp2flo(widget_data.y_max)

        self.subdivisions = Mate.inp2int(widget_data.subdivisions)
        if self.subdivisions < 2: self.subdivisions = 2

        self.ui_spessore = Mate.inp2int(widget_data.ui_spessore)
        if self.ui_spessore < 1: self.ui_spessore = 1

        # recalculation of window
        self.re_compute_size(widget_data.toggle_2_axis)

        "-------------------------------------------------------------"

        # X axis
        pygame.draw.line(self.schermo, self.text_color, 
            [self.start_x, self.start_y + 1 * (self.h - self.start_y) // 4],
            [self.end_x, self.start_y + 1 * (self.h - self.start_y) // 4],
            self.ui_spessore
        )

        # colore assi
        if self.normalizza and len([plot for plot in self.plots if plot.acceso]) == 2:
            colori_assi = [plot.colore for plot in self.plots if plot.acceso]
        else: colori_assi = [self.text_color, self.text_color]
        
        # Y axis
        pygame.draw.line(self.schermo, colori_assi[0], 
            [3 * self.start_x // 4, self.start_y],
            [3 * self.start_x // 4, self.end_y],
            self.ui_spessore
        )

        if self.visualize_second_ax:
            # 2 Y axis
            pygame.draw.line(self.schermo, colori_assi[1], 
                [self.end_x + 1 * self.start_x // 4, self.start_y],
                [self.end_x + 1 * self.start_x // 4, (self.h - self.start_y)],
                self.ui_spessore
            )
        
        # scalini sugli assi e valori
        self.re_compute_font(0.625)
        minimo_locale_label = self.min_y if not self.normalizza else self.min_y_l[0]
        massimo_locale_label = self.max_y if not self.normalizza else self.max_y_l[0]
        
        delta_x = self.max_x - self.min_x
        delta_y = massimo_locale_label - minimo_locale_label
        delta_y2 = self.max_y_l[1] - self.min_y_l[1]

        for i in range(self.subdivisions):
            
            # data x
            pos_var_x = (self.start_x + self.w_plot_area * i/ (self.subdivisions - 1))
            pos_var_y = (self.start_y - self.h_plot_area * i/ (self.subdivisions - 1))
            
            pygame.draw.line(self.schermo, self.text_color, 
                [pos_var_x, self.start_y + 1 * (self.h - self.start_y) // 4 - self.w // 100],
                [pos_var_x, self.start_y + 1 * (self.h - self.start_y) // 4 + self.w // 100],
                self.ui_spessore
            )
            
            self.schermo.blit(self.font_tipo.render(f"{self.min_x + delta_x * i / (self.subdivisions - 1):.{self.approx_label}f}", True, self.text_color), (
                pos_var_x - self.font_pixel_dim[0] * len(f"{self.min_x + delta_x * i / (self.subdivisions - 1):.{self.approx_label}f}") / 2,
                self.start_y + (self.h - self.start_y) // 3
            ))

            
            # data y
            pygame.draw.line(self.schermo, colori_assi[0], 
                [3 * self.start_x // 4 - self.w // 100, pos_var_y],
                [3 * self.start_x // 4 + self.w // 100, pos_var_y],
                self.ui_spessore
            )
            
            label_y_scr = self.font_tipo.render(f"{minimo_locale_label + delta_y * i / (self.subdivisions - 1):.{self.approx_label}f}", True, colori_assi[0])
            label_y_scr = pygame.transform.rotate(label_y_scr, 90)
        

            self.schermo.blit(label_y_scr, (
                self.start_x - self.start_x // 3 - self.font_pixel_dim[1],
                pos_var_y - self.font_pixel_dim[0] * len(f"{minimo_locale_label + delta_y * i / (self.subdivisions - 1):.{self.approx_label}f}") / 2
            ))
            
            if self.visualize_second_ax:
                # data 2 y
                pygame.draw.line(self.schermo, colori_assi[1], 
                    [self.end_x + 1 * self.start_x // 4 - self.w // 100, pos_var_y],
                    [self.end_x + 1 * self.start_x // 4 + self.w // 100, pos_var_y],
                    self.ui_spessore
                )
                
                label_y_scr = self.font_tipo.render(f"{self.min_y_l[1] + delta_y2 * i / (self.subdivisions - 1):.{self.approx_label}f}", True, colori_assi[1])
                label_y_scr = pygame.transform.rotate(label_y_scr, 90)
            
                self.schermo.blit(label_y_scr, (
                    self.end_x + 1 * self.start_x // 3,
                    pos_var_y - self.font_pixel_dim[0] * len(f"{self.min_y_l[1] + delta_y2 * i / (self.subdivisions - 1):.{self.approx_label}f}") / 2
                ))
            
            # griglia
            if widget_data.toggle_plt_bb:
                pygame.draw.line(self.schermo, [50, 50, 50], 
                    [pos_var_x, self.start_y],
                    [pos_var_x, self.end_y],
                    1
                )

                pygame.draw.line(self.schermo, [50, 50, 50], 
                    [self.start_x, pos_var_y],
                    [self.end_x, pos_var_y],
                    1
                )
            
        self.disegna_plots(widget_data)

        # plots bounding box
        # if widget_data.toggle_plt_bb:
        #     pygame.draw.rect(self.schermo, self.text_color, [
        #         self.start_x, self.end_y,
        #         self.w_plot_area, self.h_plot_area
        #     ], self.ui_spessore)

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
            ], self.ui_spessore)

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
            ], self.ui_spessore)

        self.compute_integral_FWHM(widget_data)


    def compute_integral_FWHM(self, widget_data: WidgetDataPlots):
        """Computes the integral, derivative and FWHM

        Parameters
        ----------
        widget_data : WidgetData
            Class to pass flags and attrributes from the scene
        """
        pl_at = self.plots[self.active_plot]

        if pl_at.acceso:
            
            x_all = pl_at.x[pl_at.maschera]
            y_all = pl_at.y[pl_at.maschera]
            
            if len(x_all) > 2:

                x_min = x_all[0]
                x_max = x_all[-1]

                integral = trapz(y_all, x_all)
                derivata = np.gradient(y_all, x_all)

                FWHM_h = np.max(y_all) / 2
                FWHM_w = y_all > FWHM_h

                first_true_index = np.argmax(FWHM_w)
                last_true_index = len(FWHM_w) - 1 - np.argmax(FWHM_w[::-1])

                FWHM = x_all[last_true_index] - x_all[first_true_index]

                if type(integral) == np.ndarray: integral = integral[0]

                nome = pl_at.nome.split(".")

                widget_data.FID = f"Informazioni sul grafico attivo ora [{self.plots[self.active_plot].nome}]\n\nIntegrale nell'intervallo: {integral:.{self.approx_label}f}\nFWHM del massimo nell'intervallo: {FWHM:.{self.approx_label}f}\n\nRange: {x_min} - {x_max}\n\nSalva la derivata come {nome[0]}_derivata.txt"

                if widget_data.salva_der:
                    widget_data.flag_update_save_derivative = True

                    # Writing results to a text file
                    with open(f"{widget_data.input_path}/{nome[0]}_derivata.{nome[1]}", "w") as file:
                        # Writing the derivative
                        for i in range(len(x_all)):
                            file.write(f"{x_all[i]}\t{derivata[i]}\n")


    def reset_zoom(self, logica: Logica | None = None) -> None:
        """Questa funzione può essere invocata da diverse parti del codice. Se è invocata dall'utente, richiede informazioni sull'input (va ad verificare che la richiesta di reset dello zoom sia stato fatto con il mouse all'interno del grafico)


        Parameters
        ----------
        logica : Logica | None, optional
            Classe contenente varie informazioni riguardo agli input dell'utente (mos pos, CTRL, SHIFT, click, drag, ecc.), by default None
        """

        self.zoom_mode = False

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
        """Questa funzione genera i valori di minimo e massimo (X e Y) entro i quali verrà applicato il nuovo zoom. Questa scelta verrà fatta se è in corso un trascinamento.
        In base allo SHIFT schiacciato o meno verrà applicato uno zoom 
        
        Parameters
        ----------
        logica : Logica
            Classe contenente varie informazioni riguardo agli input dell'utente (mos pos, CTRL, SHIFT, click, drag, ecc.)
        """

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
        """Given a coordinate in pixels of the whole screen, this functions finds the corresponding value in the plot screen space [pixels]

        Parameters
        ----------
        general_coordinate : tuple[float]
            X, Y coordinates of the mouse position in the screen

        Returns
        -------
        tuple[float]
            X, Y coordiantes of the mouse position in the plot screen space in pixels
        """
        x = general_coordinate[0] - self.ancoraggio_x - self.start_x
        y = general_coordinate[1] - self.ancoraggio_y - self.end_y

        perc_x = x / self.w_plot_area 
        perc_y = 1 - y / self.h_plot_area

        return perc_x, perc_y
    

    def value_research_plot_area(self, general_coordinate: tuple[float]) -> tuple[float, float]:
        """Given a coordinate in pixels of the whole screen, this functions finds (in terms of plots attributes) the corresponding value

        Parameters
        ----------
        general_coordinate : tuple[float]
            X, Y coordinates of the mouse position in the screen

        Returns
        -------
        tuple[float, float]
            X, Y plot value in that point
        """
        perc_x, perc_y = self.pixel_research_plot_area(general_coordinate)

        delta_x = self.max_x - self.min_x 
        delta_y = self.max_y - self.min_y 

        ris_x = self.min_x + delta_x * perc_x
        ris_y = self.min_y + delta_y * perc_y

        return ris_x, ris_y


    def linear_interpolation(self) -> str:
        """Esegue un'interpolazione polinomiale del grafico attivo in quel momento. Restituisce un output stringa contenente tutti i dati relativi all'esito

        Returns
        -------
        str
            OUTPUT dell'interpolazione
        """
        try:    
            base_data = self.plots[self.active_plot]

            grado = base_data.grado_inter

            if base_data.maschera is None: return "Prego, Accendere un grafico per cominciare"
            
            x = base_data.x[base_data.maschera]
            y = base_data.y[base_data.maschera]
            ey = base_data.ey[base_data.maschera] if not base_data.ey is None else None

            if len(x) < grado + 2: return f"Punti insufficienti.\nGrado: {grado}\nPunti minimi richiesti: {grado + 2}\nPunti presenti nel grafico: {len(x)}"

            if grado == 1:

                '\n{correlation_type}: {correlation_intera:.{self.approx_label}f}\n{correlation_type} ridotto: {correlation_ridotta:.{self.approx_label}f}'

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
                else:
                    # INIZIO LOGICA INTERPOLAZIONE PESATA ----------------------------------------------------------
                    coeff, covar = np.polyfit(x, y, deg = 1, w = 1/ey, cov= True)
                    m, q = coeff
                    m_e, q_e = np.sqrt(np.diag(covar))
                
                base_data.interpolation_type = "Retta ai minimi quadrati"
                params_str = f"Interpolazione lineare del grafico {base_data.nome}:\nm: {m:.{self.approx_label}f} \pm {m_e:.{self.approx_label}f}\nq: {q:.{self.approx_label}f} \pm {q_e:.{self.approx_label}f}\n"

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

            if ey is None:        
                correlation = 1 - np.sum( ( y - (y_i[base_data.maschera]) )**2 ) /np.sum( ( y - (np.sum(y)/len(y)) )**2 )
                correlation_type = "R quadro"
                params_str += f"{correlation_type}: {correlation}"
            else:
                correlation_intera = np.sum(((y - (y_i[base_data.maschera]))/ey)**2)
                correlation_ridotta = np.sum(((y - (y_i[base_data.maschera]))/ey)**2) / (len(x)-2)
                correlation_type = "\chi quadro"
                params_str += f"{correlation_type}: {correlation_intera}\n{correlation_type} ridotto: {correlation_ridotta}"

            base_data.y_interp_lin = y_i
            base_data.interpol_maschera = deepcopy(base_data.maschera)

            return params_str

        except RuntimeError as e:
            return f"Parametri ottimali non trovati, prova con un altro zoom.\n{e}"


    def customfoo_interpolation(self, curve: str = "gaussian") -> str:
        """Esegue un'interpolazione con una curva specificata del grafico attivo in quel momento. Restituisce un output stringa contenente tutti i dati relativi all'esito

        Parameters
        ----------
        curve : str, optional
            nome della curva, opzioni accettate: 'gaussian', 'sigmoid', by default "gaussian"

        Returns
        -------
        str
            OUTPUT dell'interpolazione
        """
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

                    y_i = gaussian(x, initial_guess_gauss[0], initial_guess_gauss[1], initial_guess_gauss[2])

                    correlation = 1 - np.sum( ( y - y_i )**2 ) /np.sum( ( y - (np.sum(y)/len(y)) )**2 )
                    correlation_type = "R quadro"
                    console_output += f"\n{correlation_type}: {correlation}"

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

                    y_i = sigmoide(x, initial_guess_sigmo[0], initial_guess_sigmo[1], initial_guess_sigmo[2], initial_guess_sigmo[3])
                    correlation = 1 - np.sum( ( y - y_i )**2 ) /np.sum( ( y - (np.sum(y)/len(y)) )**2 )
                    correlation_type = "R quadro"
                    console_output += f"\n{correlation_type}: {correlation}"

            return console_output

        except RuntimeError as e:
            return f"Parametri ottimali non trovati, prova con un altro zoom.\n£{e}£"