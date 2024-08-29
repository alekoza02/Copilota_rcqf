import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import trapezoid
import pygame
from _modulo_UI import Schermo, Logica, UI, Scena
from _modulo_MATE import Mate
from _modulo_database import Dizionario
import configparser
import os
from copy import deepcopy

diction = Dizionario()

MIN_BORDER = -10000
MAX_BORDER = 10000

ZERO_MIN_BORDER = -.001
ZERO_MAX_BORDER = .001

class Plot:
    def __init__(self, nome: str, matrix_data: np.ndarray[float], metadata: list[str] | None = None) -> None:
        """Generazione di un grafico

        Parameters
        ----------
        nome : str
            Nome con cui verrà visualizzato il grafico
        matrix_data : np.ndarray[float]
            Array data importata
        metadata : list[str]
            metadata ordinata in lista
        """
        self.nome = nome
        
        self.data = matrix_data

        self.toggle_errorbar = True

        self.x_column = 0
        self.y_column = 1
        self.ey_column = 2

        self.recompute_data(0, 1, 2)

        self.metadata: list[str] = metadata if not metadata is None else [""]
        
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
        self.interpolate: bool = False 
        self.interpolation_type: str = "" 

        self.dim_pall: int = 1
        self.dim_link: int = 1

        self.acceso: bool = 0

        self.maschera: np.ndarray[bool] | None = None
        self.interpol_maschera: np.ndarray[bool] | None = None

        self.colors_surface = None

    
    def recompute_data(self, x_index: int | None = None, y_index: int | None = None, ey_index: int | None = None):
        
        if not x_index is None and not y_index is None and not ey_index is None: 
            
            if x_index >= 0 and x_index < self.data.shape[1]:
                self.x_column = x_index
            
            if y_index >= 0 and y_index < self.data.shape[1]:
                self.y_column = y_index
            
            if ey_index >= 0 and ey_index < self.data.shape[1]:
                self.ey_column = ey_index

        self.x = np.around(self.data[:, self.x_column], decimals=8)
        self.y = np.around(self.data[:, self.y_column], decimals=8)
        
        if not self.toggle_errorbar:
            self.ey = np.zeros(len(self.x))
        else:
            self.ey = np.around(self.data[:, self.ey_column], decimals=8) if self.data.shape[1] > 2 else np.zeros(len(self.x))


    def settings(self, colore: list = [255, 255, 255], gradiente: bool = False, scatter: bool = True, function: bool = False, interpolate: bool = True , interpolation_type: str = "" , dim_pall: int = 1, dim_link: int = 1, acceso: bool = 0):
        self.colore = colore
        self.gradiente = gradiente
        
        self.scatter = scatter
        self.function = function
        self.interpolate = interpolate
        self.interpolation_type = interpolation_type

        self.dim_pall = dim_pall
        self.dim_link = dim_link

        self.acceso = acceso


class Painter:
    def __init__(self, control: str = "full") -> None:

        match control:
            case "minimal":
                self.control = False
            case "full":
                self.control = True
            case _:
                raise NameError(f"{control} is an invalid mode")

        config = configparser.ConfigParser()
        path = os.path.join('DATA', 'settings.ini')
        config.read(path)

        self.debugging = eval(config.get('Default', 'debugging'))

        self.schermo_madre: pygame.Surface
        
        self.w: int
        self.h: int

        self.w_foto: int
        self.h_foto: int

        self.DPI_factor: float

        self.utilizzo_w: int
        self.utilizzo_h: int

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
        self.schermo_fast: pygame.Surface
        self.schermo_foto: pygame.Surface
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

        self.salva_derivata: bool = False
        
        self.min_y: float = 0
        self.min_x: float = 0
        self.max_y: float = 0
        self.max_x: float = 0

        self.zero_y: float = 0

        self.dim_font_base = 32
        self.dim_font = 32 
        path = os.path.join('TEXTURES', 'f_full_font.ttf')
        self.font_tipo = pygame.font.Font(path, self.dim_font)
        self.font_pixel_dim = self.font_tipo.size("a")

        self.titolo = ""
        self.testo_x = ""
        self.testo_y = ""
        self.testo_2y = ""

        self.approx_label: int = int(config.get('Grafici', 'approx_label'))
        self.visualize_second_ax: bool = eval(config.get('Grafici', 'visualize_second_ax'))

        self.grad_mode = "vert"

        self.debug_info: list[str] = [(), "", [], ""] 
        # 0: width, height
        # 1: total points
        # 2: names
        # 3: ...

    
    def settings(self, titolo = "Titolo", testo_x = "Asse X", testo_y = "Asse Y", testo_2y = "2° Asse Y", visualize_second_ax = False, visualize_zero_ax = True, approx_label = 2, dim_font_base = 24, w_proportion = 0.7, h_proportion = 0.7, x_legenda = 0.3, y_legenda = 0.3, bg_color = Mate.hex2rgb("#1e1e1e"), text_color = Mate.hex2rgb("#b4b4b4"), use_custom_borders = False, x_min = 0.0, x_max = 1.0, y_min = 0.0, y_max = 1.0, subdivisions = 5, grad_mode = "hori", ui_spessore = 1, ridimensionamento = 1):
        self.titolo = self.check_latex(titolo)
        self.testo_x = self.check_latex(testo_x)
        self.testo_y = self.check_latex(testo_y)
        self.testo_2y = self.check_latex(testo_2y)

        self.visualize_second_ax = visualize_second_ax
        self.visualize_zero_ax = visualize_zero_ax

        self.approx_label = approx_label
        self.dim_font_base = dim_font_base * ridimensionamento
        
        self.w_proportion = w_proportion
        self.h_proportion = h_proportion

        self.x_legenda = x_legenda
        self.y_legenda = y_legenda

        self.bg_color = bg_color
        self.text_color = text_color

        self.use_custom_borders = use_custom_borders
        
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        self.subdivisions = subdivisions
        self.grad_mode = grad_mode

        self.ui_spessore = ui_spessore
    
    
    def re_compute_font(self, factor: float = 1) -> None:
        """
        Ricalcolo della dimensione del font in base a quanto mi serve.

        Parameters
        ----------
        factor : float, optional
            Fattore di scala rispetto alla dimensione precedente. Con questo approccio, il cambio di dimensione dello schermo non è più un problema, by default 1
        """
        self.dim_font = int(round(self.dim_font_base * factor * self.DPI_factor, 0))
        path = os.path.join('TEXTURES', 'f_full_font.ttf')
        self.font_tipo = pygame.font.Font(path, self.dim_font)
        self.font_pixel_dim = self.font_tipo.size("a")
    

    def re_compute_size(self) -> None:
        """Ricalcola la dimensione dell'UI dei grafici in base alla presenza del secondo asse Y"""

        if self.visualize_second_ax:

            self.w_plot_area = self.w_proportion * self.utilizzo_w
            self.h_plot_area = self.h_proportion * self.utilizzo_h
            
            self.start_x = (self.utilizzo_w - self.w_plot_area) // 2
            self.start_y = self.utilizzo_h - (self.utilizzo_h - self.h_plot_area) // 2
            
            self.end_x = self.start_x + self.w_plot_area
            self.end_y = self.start_y - self.h_plot_area

        else:

            self.w_plot_area = self.w_proportion * self.utilizzo_w
            self.h_plot_area = self.h_proportion * self.utilizzo_h
            
            self.start_x = (self.utilizzo_w - self.w_plot_area) // 2
            self.start_y = self.utilizzo_h - (self.utilizzo_h - self.h_plot_area) // 2
            
            self.w_plot_area += self.start_x // 2
            self.h_plot_area += (self.utilizzo_h - self.start_y) // 2

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

        for indice, segno in diction.simboli.items():
            if indice in input_str: input_str = input_str.replace(indice, segno)

        return input_str


    def check_esponente_pedice(self, texto, posx, posy, centered = False, vertical = False):
    
        self.re_compute_font()

        if self.UI_latex_check.toggled:

            testo_aggiornato = texto
            
            elemento_testi = []
            elemento_anchors = []
            elemento_tipo = []
            
            def check(testo_aggiornato: str, depth = 0):

                # blocco ricerca della prima occorrenza -> decido se è un apice o un pedice
                occorrenza_apice = testo_aggiornato.find("^{")
                occorrenza_pedic = testo_aggiornato.find("_{")

                if occorrenza_apice < 0:
                    test = False
                elif occorrenza_pedic < 0:
                    test = True
                elif occorrenza_apice < occorrenza_pedic:
                    test = True
                elif occorrenza_apice > occorrenza_pedic:
                    test = False

                primo_ch = "^{" if test else "_{"
                secon_ch = "_{" if test else "^{"
                testo_lista = list(testo_aggiornato)
                old_start = 0
                old_len = 0
                # fine blocco ricerca
                
                if len(testo_lista) > 0:

                    # verifico che effettivamente sia ancora presente il carattere scelto
                    if testo_aggiornato.count(primo_ch) > 0:
                        
                        # trovo l'intervallo interessato
                        start = testo_aggiornato.find(primo_ch)
                        end = testo_aggiornato.find("}", start) 

                        # test nel caso non venisse trovato l'inizio o la fine
                        if start == -1 or end == -1:
                            return None

                        lunghezza = end - start - 2

                        # popolo il record con tipologia di carattere, testo e posizione
                        tipo_ch = True if primo_ch == "^{" else False
                        
                        elemento_tipo.append(tipo_ch)
                        elemento_testi.append(testo_aggiornato[start + 2:end])
                        elemento_anchors.append(start) 
                        
                        # elimino dal testo originale la sintassi di comando e il testo dell'apice / pedice (già salvato in precedenza)
                        for i in range(lunghezza + 3):
                            testo_lista.pop(start)

                        # riaggiungo l'equivalente in spazi di dimensione del carattere base
                        ceiling = np.ceil(lunghezza / 2).astype(int)

                        for _ in range(ceiling):
                            testo_lista.insert(start, " ")
                
                        # testo pronto per lo step successivo
                        testo_aggiornato = "".join(testo_lista)
                    
                        # testo se per caso esiste un carattere speciale subito dopo la fine 
                        if testo_aggiornato.find(secon_ch) == start + ceiling:
                            old_start = start
                            old_len = ceiling

                        # se è così, testo se esiste il carattere opposto (pedice e apice messi vicini avranno X uguale)
                        if testo_aggiornato.count(secon_ch) > 0:
                            
                            # rieseguo le stesse cose, popolando però per il secondo tipo si segno
                            start = testo_aggiornato.find(secon_ch)
                            end = testo_aggiornato.find("}", start) 

                            if start == -1 or end == -1:
                                return None

                            if start == old_start + old_len:
                                
                                start_text = start
                                end_text = end

                                start_anchor = start - old_len
                                
                                lunghezza = end - start - 2

                                tipo_ch = not tipo_ch
                        
                                elemento_tipo.append(tipo_ch)
                            
                                elemento_testi.append(testo_aggiornato[start_text + 2:end_text])
                                elemento_anchors.append(start_anchor) 

                                for i in range(lunghezza + 3):
                                    testo_lista.pop(start)

                                ceiling = np.ceil(lunghezza / 2).astype(int)

                                # unico cambiamento, lo spazio allocato dipenderà dal confronto delle due lunghezze
                                delta_offset_anchor = ceiling - old_len

                                if delta_offset_anchor > 0:
                                    for _ in range(delta_offset_anchor):
                                        testo_lista.insert(start, " ")

                testo_aggiornato = "".join(testo_lista)

                # se ci sono ancora segni speciali, continua l'analisi
                if testo_aggiornato.count("^{") > 0 or testo_aggiornato.count("_{") > 0:
                    return check(testo_aggiornato, depth + 1)

                return "".join(testo_lista)
            
            texto_mod = check(testo_aggiornato)
            
            if not texto_mod is None:
                lunghezza = len(texto_mod) * self.font_pixel_dim[0] / 2
                
                rendered_label = self.font_tipo.render(texto_mod, True, self.text_color)
                if vertical:
                    rendered_label = pygame.transform.rotate(rendered_label, 90)

                if centered:
                    if not vertical:
                        posx -= lunghezza
                    elif vertical:
                        posy -= lunghezza

                self.schermo.blit(rendered_label, (posx, posy))

                larghezza_grande = self.font_pixel_dim[0]

                self.re_compute_font(0.6)

                for exp, anchor, tipo in zip(elemento_testi, elemento_anchors, elemento_tipo):
                    offset_y = 0 if tipo else self.font_pixel_dim[1]
                    # colore = [255, 100, 100] if tipo else [100, 255, 255]

                    rendered_label = self.font_tipo.render(exp, True, self.text_color)
                    if vertical:
                        rendered_label = pygame.transform.rotate(rendered_label, 90)

                    if not vertical:
                        bias_x = anchor * larghezza_grande
                        bias_y = offset_y
                    elif vertical:
                        bias_x = offset_y
                        bias_y = (len(texto_mod) - anchor) * larghezza_grande - len(exp) * self.font_pixel_dim[0]
                    
                    self.schermo.blit(rendered_label, (posx + bias_x, posy + bias_y))
                    
            return

        rendered_label = self.font_tipo.render(texto, True, self.text_color)
        if vertical:
            rendered_label = pygame.transform.rotate(rendered_label, 90)

        if centered:
            lunghezza = len(texto) * self.font_pixel_dim[0] / 2
            
            if not vertical:
                posx -= lunghezza
            elif vertical:
                posy -= lunghezza

        self.schermo.blit(rendered_label, (posx, posy))
        

    def link_ui(self, ui: UI, scene: str = "plots", schermo: str = "viewport") -> None: 
        """Collegamento UI con il painter. Raccoglie informazioni circa le dimensioni dello schermo e si calcola l'ancoraggio

        Parameters
        ----------
        info_schermo : Schermo
            Dato la classe Schermo, posso capire le informazioni che mi servono
        """

        info_schermo = ui.scena[scene].schermo[schermo]

        self.schermo_madre = info_schermo.madre
    
        self.w = info_schermo.w
        self.h = info_schermo.h
        
        self.utilizzo_w = self.w
        self.utilizzo_h = self.h

        
        self.w_plot_area = self.w_proportion * self.utilizzo_w
        self.h_plot_area = self.h_proportion * self.utilizzo_h
        
        self.start_x = (self.utilizzo_w - self.w_plot_area) // 2
        self.start_y = self.utilizzo_h - (self.utilizzo_h - self.h_plot_area) // 2
        
        self.end_x = self.start_x + self.w_plot_area
        self.end_y = self.start_y - self.h_plot_area
        
        self.debug_info[0] = (self.w, self.h)

        self.ancoraggio_x = info_schermo.ancoraggio_x
        self.ancoraggio_y = info_schermo.ancoraggio_y 
        
        self.schermo_fast = info_schermo.schermo

        self.UI_calls_plots = ui.scena["plots"]

        self.UI_titolo = self.UI_calls_plots.entrate["titolo"]
        self.UI_labelx = self.UI_calls_plots.entrate["labelx"]
        self.UI_labely = self.UI_calls_plots.entrate["labely"]
        self.UI_label2y = self.UI_calls_plots.entrate["label2y"]
        self.UI_round_label = self.UI_calls_plots.entrate["round_label"]
        self.UI_font_size = self.UI_calls_plots.entrate["font_size"]
        self.UI_color_bg = self.UI_calls_plots.entrate["color_bg"]
        self.UI_color_text = self.UI_calls_plots.entrate["color_text"]
        self.UI_area_w = self.UI_calls_plots.entrate["area_w"]
        self.UI_area_h = self.UI_calls_plots.entrate["area_h"]
        self.UI_x_legenda = self.UI_calls_plots.entrate["x_legenda"]
        self.UI_y_legenda = self.UI_calls_plots.entrate["y_legenda"]        
        self.UI_color_plot = self.UI_calls_plots.entrate["color_plot"]        
        self.UI_dim_link = self.UI_calls_plots.entrate["dim_link"]        
        self.UI_dim_pallini = self.UI_calls_plots.entrate["dim_pallini"]        
        self.UI_grado_inter = self.UI_calls_plots.entrate["grado_inter"] 
        self.UI_x_column = self.UI_calls_plots.entrate["x_column"]
        self.UI_y_column = self.UI_calls_plots.entrate["y_column"]
        self.UI_ey_column = self.UI_calls_plots.entrate["ey_column"]
        self.UI_x_min = self.UI_calls_plots.entrate["x_min"]
        self.UI_x_max = self.UI_calls_plots.entrate["x_max"]
        self.UI_y_min = self.UI_calls_plots.entrate["y_min"]
        self.UI_y_max = self.UI_calls_plots.entrate["y_max"]       
        self.UI_subdivisions = self.UI_calls_plots.entrate["subdivisions"]       
        self.UI_ui_spessore = self.UI_calls_plots.entrate["ui_spessore"]  
        self.UI_x_foto = self.UI_calls_plots.entrate["x_foto"]  
        self.UI_y_foto = self.UI_calls_plots.entrate["y_foto"]  

        self.UI_nome_grafico = self.UI_calls_plots.entrate["nome_grafico"]        
        self.UI_caricamento = self.UI_calls_plots.paths["caricamento"]

        self.UI_scroll_grafici = self.UI_calls_plots.scrolls["grafici"]
        self.UI_normalizza = self.UI_calls_plots.bottoni["normalizza"] 
        self.UI_use_custom_borders = self.UI_calls_plots.bottoni["use_custom_borders"] 
        self.UI_toggle_inter = self.UI_calls_plots.bottoni["toggle_inter"] 
        self.UI_toggle_pallini = self.UI_calls_plots.bottoni["toggle_pallini"] 
        self.UI_toggle_errorbar = self.UI_calls_plots.bottoni["toggle_errorbar"] 
        self.UI_toggle_collegamenti = self.UI_calls_plots.bottoni["toggle_collegamenti"]
        self.UI_latex_check = self.UI_calls_plots.bottoni["latex_check"]
        self.UI_toggle_2_axis = self.UI_calls_plots.bottoni["toggle_2_axis"]
        self.UI_toggle_plot_bb = self.UI_calls_plots.bottoni["toggle_plot_bb"]
        self.UI_gradiente = self.UI_calls_plots.bottoni["gradiente"]
        self.UI_gradiente_hori = self.UI_calls_plots.bottoni["grad_hori"]
        self.UI_gradiente_vert = self.UI_calls_plots.bottoni["grad_vert"]
        self.UI_zero_y = self.UI_calls_plots.bottoni["zero_y"]
        self.UI_save_deriv = self.UI_calls_plots.bottoni["save_deriv"]

        self.UI_FID = self.UI_calls_plots.label_text["FID"]
        self.UI_metadata = self.UI_calls_plots.label_text["metadata"]

        self.UI_path_import = self.UI_calls_plots.paths["caricamento"]
    

    
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

        # TODO: FIX WHEN < 5 PLOTS IN FOLDER 

        # aggiorno le entry box con i valori del nuovo grafico
        ui.scena["plots"].entrate["nome_grafico"].text = str(self.plots[self.active_plot].nome)
        ui.scena["plots"].entrate["nome_grafico"].puntatore = len(str(self.plots[self.active_plot].nome)) - 1
        ui.scena["plots"].entrate["color_plot"].text = f"{Mate.rgb2hex(self.plots[self.active_plot].colore)}"
        ui.scena["plots"].entrate["dim_link"].text = str(self.plots[self.active_plot].dim_link)
        ui.scena["plots"].entrate["dim_pallini"].text = str(self.plots[self.active_plot].dim_pall)
        ui.scena["plots"].entrate["x_column"].text = str(self.plots[self.active_plot].x_column)
        ui.scena["plots"].entrate["y_column"].text = str(self.plots[self.active_plot].y_column)
        ui.scena["plots"].entrate["ey_column"].text = str(self.plots[self.active_plot].ey_column)

        ui.scena["plots"].bottoni["toggle_inter"].toggled = self.plots[self.active_plot].interpolate 
        ui.scena["plots"].bottoni["toggle_pallini"].toggled = self.plots[self.active_plot].scatter 
        ui.scena["plots"].bottoni["toggle_errorbar"].toggled = self.plots[self.active_plot].toggle_errorbar 
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
        ui.scena["plots"].entrate["x_column"].text = str(self.plots[self.active_plot].x_column)
        ui.scena["plots"].entrate["y_column"].text = str(self.plots[self.active_plot].y_column)
        ui.scena["plots"].entrate["ey_column"].text = str(self.plots[self.active_plot].ey_column)

        ui.scena["plots"].bottoni["toggle_inter"].toggled = self.plots[self.active_plot].interpolate 
        ui.scena["plots"].bottoni["toggle_pallini"].toggled = self.plots[self.active_plot].scatter 
        ui.scena["plots"].bottoni["toggle_errorbar"].toggled = self.plots[self.active_plot].toggle_errorbar 
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
    
        # controllo tipologia float dei dati, se non è un float lo carico nel metadata
        metadata_str = ""
        counter_non_metadata = 0
        counter_domanda = True

        for coordinate in data[::-1]:
            for elemento in coordinate:
                try:
                    float(elemento)
                    if counter_domanda:
                        counter_non_metadata += 1
                        if counter_non_metadata > 3:
                            counter_non_metadata = 0
                            counter_domanda = False
                            metadata_str += f"...\n"

                except ValueError:
                    data.remove(coordinate)
                    for _ in coordinate:
                        metadata_str += f"{_}\t"
                    metadata_str += f"\n"
                    counter_domanda = True
                    break
    
        metadata_str += "Metadata / Non converted lines:\n"

        # reverse metadata
        metadata_lst = [f"{i}\n" if f"{i[-1:]}" != "\n" else f"{i}" for i in metadata_str.split("\n")][::-1]
        
        # remove "\n" and "\t\n"
        for _ in range(metadata_lst.count("\n")):
            metadata_lst.remove("\n")
        for _ in range(metadata_lst.count("\t\n")):
            metadata_lst.remove("\t\n")

        # controllo presenza dati None 
        data = [i for i in data if i]
    
        try:
            # CONVERSIONE ARRAY DI FLOATS
            if len(data[0]) != len(data[1]): data.pop(0)
            data = np.array(data).astype(float)    
            
            nome = path.split('\\')[-1]
            
            # test ordinamento x
            indici = np.argsort(data[:, 0])
            data = data[indici]

            self.plots.append(Plot(nome, data, metadata_lst))
            self.debug_info[2].append(nome)
        
        except:
            print(f"Impossibile caricare il file: {path}")
    

    def full_import_plot_data(self) -> None:
        """Dato un path importa tutti i file con estensioni accettate (txt, ASCII, dat, csv) e ci genera un plot.

        Parameters
        ----------
        path_input : str, optional
            Path alla cartella con i grafici, by default 'PLOT_DATA/default'
        """
        files = os.listdir(self.UI_caricamento.text)

        self.plots = []
        self.debug_info[2] = []

        for f in files:
            path = os.path.join(self.UI_caricamento.text, f)
            if os.path.isfile(path):    
                self.import_plot_data(path)

        self.original_plot_order = self.plots
        self.UI_scroll_grafici.elementi = [self.plots[index].nome for index in range(len(self.plots))]
        self.UI_scroll_grafici.elementi_attivi = [False for _ in range(len(self.plots))]
        self.UI_scroll_grafici.indici = [i for i in range(len(self.plots))]
        self.UI_scroll_grafici.update_elements()


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

                            if plot.toggle_errorbar:
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

                    if plot.toggle_errorbar:
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

                    if plot.toggle_errorbar: 
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

                    if plot.toggle_errorbar: 
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

            
            self.zero_y = self.h_plot_area * (0 - self.min_y) / (self.max_y - self.min_y)
            self.zero_y = - self.zero_y + self.start_y

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


    
    def disegna_gradiente(self) -> None:

        self.adattamento_data2schermo()

        if self.control:
            if self.UI_gradiente_vert.toggled:
                self.grad_mode = "vert"
            if self.UI_gradiente_hori.toggled:
                self.grad_mode = "hori"

        for index, plot in enumerate(self.plots):
            if plot.acceso:
                if plot.gradiente:
                    
                    if self.grad_mode == "vert":
                        # VERTICAL
                        for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:-1], plot.y_screen.astype(int)[:-1], plot.x_screen.astype(int)[1:], plot.y_screen.astype(int)[1:]):
                            m = (y2 - y1) / (x2 - x1)
                            for i in range(0, x2 - x1):
                                y_interpolated = int(y1 + m * i)
                                colore = (self.start_y - y_interpolated) / self.start_y
                                colore_finale = np.array(self.bg_color) + (np.array(plot.colore) - np.array(self.bg_color)) * colore
                                pygame.draw.line(self.schermo, colore_finale, (x1 + i, self.start_y), (x1 + i, y_interpolated), 1)
                    
                    elif self.grad_mode == "hori":
                        # HORIZONTAL

                        gradient = np.zeros((int(self.w_plot_area), int(self.h_plot_area), 3), dtype=np.uint8)
                        
                        # CASO 1 -> 0 In mezzo al range
                        if self.zero_y > self.end_y and self.zero_y < self.start_y:
                            
                            # coloro il gradiente UPPER
                            limite = int(self.zero_y - self.end_y)
                            for i in range(3):
                                gradient[:, :limite, i] = np.tile(np.linspace(plot.colore[i] / 2, self.bg_color[i], limite), (int(self.w_plot_area), 1)).reshape(int(self.w_plot_area), limite)
                            # coloro il gradiente LOWER
                            limite = int(self.start_y - self.zero_y)
                            for i in range(3):
                                gradient[:, -limite:, i] = np.tile(np.linspace(self.bg_color[i], plot.colore[i] / 2, limite), (1, int(self.w_plot_area))).reshape(int(self.w_plot_area), limite)
                            
                            plot.colors_surface = pygame.surfarray.make_surface(gradient)  
                            self.schermo.blit(plot.colors_surface, (self.start_x, self.end_y))
                            

                            # lancio della maschera (zero fuori dagli estremi) UPPER  
                            for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:-1], plot.y_screen.astype(int)[:-1], plot.x_screen.astype(int)[1:], plot.y_screen.astype(int)[1:]):
                                m = (y2 - y1) / (x2 - x1)
                                
                                for i in range(0, x2 - x1):
                                    y_interpolated = int(y1 + m * i)
                                    obiettivo = y_interpolated if y_interpolated < self.zero_y else self.zero_y
                                    pygame.draw.line(self.schermo, self.bg_color, (x1 + i, self.end_y), (x1 + i, obiettivo), 1)

                            # lancio della maschera (zero fuori dagli estremi) LOWER
                            for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:-1], plot.y_screen.astype(int)[:-1], plot.x_screen.astype(int)[1:], plot.y_screen.astype(int)[1:]):
                                m = (y2 - y1) / (x2 - x1)
                                
                                for i in range(0, x2 - x1):
                                    y_interpolated = int(y1 + m * i)
                                    obiettivo = y_interpolated if y_interpolated > self.zero_y else self.zero_y 
                                    pygame.draw.line(self.schermo, self.bg_color, (x1 + i, self.start_y), (x1 + i, obiettivo), 1)


                        else:
                            # CASO 2 -> Tutto sotto lo 0
                            if self.zero_y <= self.end_y: 
                                from_y = self.start_y
                                colore_start = self.bg_color
                                colore_finale = np.array(plot.colore) / 2
                            
                            # CASO 3 -> Tutto sopra lo 0
                            elif self.zero_y >= self.start_y:
                                from_y = self.end_y
                                colore_start = np.array(plot.colore) / 2
                                colore_finale = self.bg_color

                            # coloro il gradiente
                            for i in range(3):
                                gradient[:, :, i] = np.linspace(colore_start[i], colore_finale[i], int(self.h_plot_area)).reshape(1, int(self.h_plot_area))
                            plot.colors_surface = pygame.surfarray.make_surface(gradient)  
                            self.schermo.blit(plot.colors_surface, (self.start_x, self.end_y))
                            
                            # lancio della maschera (zero fuori dagli estremi)    
                            for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:-1], plot.y_screen.astype(int)[:-1], plot.x_screen.astype(int)[1:], plot.y_screen.astype(int)[1:]):
                                m = (y2 - y1) / (x2 - x1)
                                
                                for i in range(0, x2 - x1):
                                    y_interpolated = int(y1 + m * i)
                                    pygame.draw.line(self.schermo, self.bg_color, (x1 + i, from_y), (x1 + i, y_interpolated), 1)

                            # elimino le tracce di gradiente fuori dal range
                            for x in range(int(self.start_x), plot.x_screen.astype(int)[0]):
                                    pygame.draw.line(self.schermo, self.bg_color, (x, self.start_y), (x, self.end_y), 1)
                            
                            for x in range(plot.x_screen.astype(int)[-1], int(self.end_x)):
                                    pygame.draw.line(self.schermo, self.bg_color, (x, self.start_y), (x, self.end_y), 1)
                            

    def disegna_plots(self) -> None:
        """
        Disegna tutti i grafici caricati e abilitati al disegno.
        """
        
        if self.control:

            self.normalizza = self.UI_normalizza.toggled

            # Sezione di impostazioni grafico attuale attivo
            
            self.UI_ey_column.visibile = True if self.UI_toggle_errorbar.toggled else False

            self.plots[self.active_plot].toggle_errorbar = self.UI_toggle_errorbar.toggled
            self.plots[self.active_plot].recompute_data(Mate.inp2int(self.UI_x_column.text_invio, 0), Mate.inp2int(self.UI_y_column.text_invio, 1), Mate.inp2int(self.UI_ey_column.text_invio, 2)) 
            
            self.plots[self.active_plot].acceso = self.UI_scroll_grafici.elementi_attivi[self.UI_scroll_grafici.first_item + self.UI_scroll_grafici.scroll_item_selected]
            self.plots[self.active_plot].interpolate = self.UI_toggle_inter.toggled 
            self.plots[self.active_plot].grado_inter = Mate.inp2int(self.UI_grado_inter.text_invio, 1) 
            self.plots[self.active_plot].function = self.UI_toggle_collegamenti.toggled 
            self.plots[self.active_plot].scatter = self.UI_toggle_pallini.toggled 
            self.plots[self.active_plot].gradiente = self.UI_gradiente.toggled 
            self.plots[self.active_plot].colore = Mate.hex2rgb(self.UI_color_plot.text_invio) 

            self.plots[self.active_plot].dim_link = Mate.inp2int(self.UI_dim_link.text_invio)
            self.plots[self.active_plot].dim_pall = Mate.inp2int(self.UI_dim_pallini.text_invio)

            self.plots[self.active_plot].nome = self.UI_nome_grafico.text_invio

        
        self.debug_info[1] = sum([len(i.x) for i in self.plots])
        
        for index, plot in enumerate(self.plots):

            if plot.acceso:

                    try:
                        if plot.scatter:
                            for x, y in zip(plot.x_screen.astype(int), plot.y_screen.astype(int)):
                                pygame.draw.circle(self.schermo, plot.colore, (x, y), round(plot.dim_pall * self.DPI_factor))
                    except (TypeError, ValueError) as e:
                        if self.debugging: print(f"Warning: {e} in scatter")


                    try:
                        if plot.scatter and plot.toggle_errorbar:
                            for x, y, ey in zip(plot.x_screen.astype(int), plot.y_screen.astype(int), plot.ey_screen.astype(int)):
                                pygame.draw.line(self.schermo, plot.colore, (x, y), (x, y + ey), round(plot.dim_link * self.DPI_factor))
                                pygame.draw.line(self.schermo, plot.colore, (x, y), (x, y - ey), round(plot.dim_link * self.DPI_factor))
                                pygame.draw.line(self.schermo, plot.colore, (x - ey / 5, y + ey), (x + ey / 5, y + ey), round(plot.dim_link * self.DPI_factor))
                                pygame.draw.line(self.schermo, plot.colore, (x - ey / 5, y - ey), (x + ey / 5, y - ey), round(plot.dim_link * self.DPI_factor))
                    except (TypeError, ValueError) as e:
                        if self.debugging: print(f"Warning: {e} in errors")


                    try:
                        if plot.interpolate and not plot.y_interp_lin is None:
                            for x1, y1, x2, y2 in zip(plot.xi_screen.astype(int)[:-1], plot.yi_screen.astype(int)[:-1], plot.xi_screen.astype(int)[1:], plot.yi_screen.astype(int)[1:]):
                                pygame.draw.line(self.schermo, [255, 0, 0], (x1, y1), (x2, y2), round(plot.dim_link * self.DPI_factor))
                    except (TypeError, ValueError, AttributeError) as e:
                        if self.debugging: print(f"Warning: {e} in interpolate")

                    
                    try:
                        if plot.function:
                            for x1, y1, x2, y2 in zip(plot.x_screen.astype(int)[:-1], plot.y_screen.astype(int)[:-1], plot.x_screen.astype(int)[1:], plot.y_screen.astype(int)[1:]):
                                pygame.draw.line(self.schermo, plot.colore, (x1, y1), (x2, y2), round(plot.dim_link * self.DPI_factor))
                    except (TypeError, ValueError) as e:
                        if self.debugging: print(f"Warning: {e} in function")


    def animation_update(self, plot: Plot, index: int, noanim: bool = False) -> tuple[int, list[int]]:
        """
        IN DISUSO
        ----------
        Aggiorna lo stato dell'animazione e switcha tra acceso e spento

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


    def disegna(self, logica: Logica, foto: bool = False) -> None:
        """Funzione principale richiamata dall'utente che inizia il processo di disegno dell'UI dei grafici e i grafici stessi

        Parameters
        ----------
        logica : Logica
            Classe contenente varie informazioni riguardo agli input dell'utente (mos pos, CTRL, SHIFT, click, drag, ecc.)
        """

        if foto:

            self.w_foto = Mate.inp2int(self.UI_x_foto.text_invio, 1620)
            self.h_foto = Mate.inp2int(self.UI_y_foto.text_invio, 1620)

            self.schermo_foto = pygame.Surface((self.w_foto, self.h_foto))

            self.DPI = self.w_foto / self.w

            self.utilizzo_w = self.w_foto
            self.utilizzo_h = self.h_foto
            self.schermo = self.schermo_foto
            self.DPI_factor = self.DPI
        else:
            self.utilizzo_w = self.w
            self.utilizzo_h = self.h
            self.schermo = self.schermo_fast
            self.DPI_factor = 1


        self.schermo.fill(self.bg_color)

        if self.UI_path_import.execute_action:
            self.UI_path_import.execute_action = False
            try:
                self.full_import_plot_data()
                self.UI_scroll_grafici.aggiorna_externo("reload", logica)
            except FileNotFoundError as e:
                print(e)


        # recalculation of window
        self.re_compute_size()


        self.disegna_gradiente()

        # import settings
        if self.control:
            if self.UI_latex_check.toggled:
                self.titolo = Painter.check_latex(self.UI_titolo.text_invio) 
                self.testo_x = Painter.check_latex(self.UI_labelx.text_invio)
                self.testo_y = Painter.check_latex(self.UI_labely.text_invio)
                self.testo_2y = Painter.check_latex(self.UI_label2y.text_invio)
            else:
                self.titolo = self.UI_titolo.text_invio
                self.testo_x = self.UI_labelx.text_invio
                self.testo_y = self.UI_labely.text_invio
                self.testo_2y = self.UI_label2y.text_invio
            
            if self.plots[self.active_plot].acceso:
                self.UI_metadata.assegna_messaggio(self.plots[self.active_plot].metadata)

            # prova di conversione
            self.approx_label = Mate.conversione_limite(self.UI_round_label.text_invio, 2, 9)
            self.dim_font_base = Mate.conversione_limite(self.UI_font_size.text_invio, 32, 128)
            
            self.w_proportion = Mate.conversione_limite(self.UI_area_w.text_invio, 0.8, 0.9)
            self.h_proportion = Mate.conversione_limite(self.UI_area_h.text_invio, 0.8, 0.9)

            self.x_legenda = Mate.conversione_limite(self.UI_x_legenda.text_invio, 0.2, 0.9)
            self.y_legenda = Mate.conversione_limite(self.UI_y_legenda.text_invio, 0.3, 0.9)

            self.bg_color = Mate.hex2rgb(self.UI_color_bg.text_invio)
            self.text_color = Mate.hex2rgb(self.UI_color_text.text_invio)

            self.use_custom_borders = self.UI_use_custom_borders.toggled
            
            self.x_min = Mate.inp2flo(self.UI_x_min.text_invio)
            self.x_max = Mate.inp2flo(self.UI_x_max.text_invio)
            self.y_min = Mate.inp2flo(self.UI_y_min.text_invio)
            self.y_max = Mate.inp2flo(self.UI_y_max.text_invio)

            self.subdivisions = Mate.inp2int(self.UI_subdivisions.text_invio)
            if self.subdivisions < 2: self.subdivisions = 2

            self.ui_spessore = Mate.inp2int(self.UI_ui_spessore.text_invio)
            if self.ui_spessore < 1: self.ui_spessore = 1

            self.UI_normalizza.visibile = True if len([plot for plot in self.plots if plot.acceso]) == 2 else False            
            self.visualize_second_ax = self.UI_toggle_2_axis.toggled
            self.visualize_zero_ax = self.UI_zero_y.toggled

        
        "-------------------------------------------------------------"

        # X axis
        pygame.draw.line(self.schermo, self.text_color, 
            [self.start_x, self.start_y + 1 * (self.utilizzo_h - self.start_y) // 4],
            [self.end_x, self.start_y + 1 * (self.utilizzo_h - self.start_y) // 4],
            round(self.ui_spessore * self.DPI_factor)
        )

        # colore assi
        if self.normalizza and len([plot for plot in self.plots if plot.acceso]) == 2:
            colori_assi = [plot.colore for plot in self.plots if plot.acceso]
        else: colori_assi = [self.text_color, self.text_color]
        
        # Y axis
        pygame.draw.line(self.schermo, colori_assi[0], 
            [3 * self.start_x // 4, self.start_y],
            [3 * self.start_x // 4, self.end_y],
            round(self.ui_spessore * self.DPI_factor)
        )

        if self.visualize_second_ax:
            # 2 Y axis
            pygame.draw.line(self.schermo, colori_assi[1], 
                [self.end_x + 1 * self.start_x // 4, self.start_y],
                [self.end_x + 1 * self.start_x // 4, (self.utilizzo_h - self.start_y)],
                round(self.ui_spessore * self.DPI_factor)
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
                [pos_var_x, self.start_y + 1 * (self.utilizzo_h - self.start_y) // 4 - self.utilizzo_w // 100],
                [pos_var_x, self.start_y + 1 * (self.utilizzo_h - self.start_y) // 4 + self.utilizzo_w // 100],
                round(self.ui_spessore * self.DPI_factor)
            )
            
            value = self.min_x + delta_x * i / (self.subdivisions - 1)
            formatting = "e" if ((value > MAX_BORDER or value < MIN_BORDER) or (value < ZERO_MAX_BORDER and value > ZERO_MIN_BORDER)) and value != 0 else "f"
            self.schermo.blit(self.font_tipo.render(f"{value:.{self.approx_label}{formatting}}", True, self.text_color), (
                pos_var_x - self.font_pixel_dim[0] * len(f"{value:.{self.approx_label}{formatting}}") / 2,
                self.start_y + (self.utilizzo_h - self.start_y) // 3
            ))
            
            # data y
            pygame.draw.line(self.schermo, colori_assi[0], 
                [3 * self.start_x // 4 - self.utilizzo_w // 100, pos_var_y],
                [3 * self.start_x // 4 + self.utilizzo_w // 100, pos_var_y],
                round(self.ui_spessore * self.DPI_factor)
            )
            
            value = minimo_locale_label + delta_y * i / (self.subdivisions - 1)
            formatting = "e" if ((value > MAX_BORDER or value < MIN_BORDER) or (value < ZERO_MAX_BORDER and value > ZERO_MIN_BORDER)) and value != 0 else "f"
            label_y_scr = self.font_tipo.render(f"{value:.{self.approx_label}{formatting}}", True, colori_assi[0])
            label_y_scr = pygame.transform.rotate(label_y_scr, 90)
        

            self.schermo.blit(label_y_scr, (
                self.start_x - self.start_x // 3 - self.font_pixel_dim[1],
                pos_var_y - self.font_pixel_dim[0] * len(f"{value:.{self.approx_label}{formatting}}") / 2
            ))
            
            if self.visualize_second_ax:
                # data 2 y
                pygame.draw.line(self.schermo, colori_assi[1], 
                    [self.end_x + 1 * self.start_x // 4 - self.utilizzo_w // 100, pos_var_y],
                    [self.end_x + 1 * self.start_x // 4 + self.utilizzo_w // 100, pos_var_y],
                    round(self.ui_spessore * self.DPI_factor)
                )
                
                value = self.min_y_l[1] + delta_y2 * i / (self.subdivisions - 1)
                formatting = "e" if ((value > MAX_BORDER or value < MIN_BORDER) or (value < ZERO_MAX_BORDER and value > ZERO_MIN_BORDER)) and value != 0 else "f"
                label_y_scr = self.font_tipo.render(f"{value:.{self.approx_label}{formatting}}", True, colori_assi[1])
                label_y_scr = pygame.transform.rotate(label_y_scr, 90)
            
                self.schermo.blit(label_y_scr, (
                    self.end_x + 1 * self.start_x // 3,
                    pos_var_y - self.font_pixel_dim[0] * len(f"{value:.{self.approx_label}{formatting}}") / 2
                ))
            
            # griglia
            if self.UI_toggle_plot_bb.toggled:
                if True:
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

        self.disegna_plots()

        # linea dello 0 sulle Y
        if self.visualize_zero_ax:
            if self.zero_y > self.end_y and self.zero_y < self.start_y:
                pygame.draw.line(self.schermo, self.text_color, [self.start_x, self.zero_y], [self.end_x, self.zero_y], round(1 * self.DPI_factor))

        # plots bounding box
        # if self.UI_toggle_plot_bb.toggled:
        #     pygame.draw.rect(self.schermo, self.text_color, [
        #         self.start_x, self.end_y,
        #         self.w_plot_area, self.h_plot_area
        #     ], self.ui_spessore)

        "------------------------------------------------------------------------------------------------"
        bias_asse_y_sinistro = self.font_pixel_dim[1] * 1.25
        self.re_compute_font()    
    

        # testo asse x
        self.check_esponente_pedice(
                f"{self.testo_x}",
                self.start_x + self.w_plot_area // 2,
                self.start_y + 3 * (self.utilizzo_h - self.start_y) // 5,
                centered=True
            )
    
        
        # testo asse y
        self.check_esponente_pedice(
                f"{self.testo_y}",
                self.start_x - 3 * self.start_x // 5 - bias_asse_y_sinistro,
                self.start_y - self.h_plot_area // 2,
                vertical=True,
                centered=True
            )

        
        if self.visualize_second_ax:
            # testo asse 2 y
            self.check_esponente_pedice(
                f"{self.testo_2y}",
                self.end_x + self.start_x - 2 * self.start_x // 5,
                self.start_y - self.h_plot_area // 2,
                vertical=True,
                centered=True
            )

        
        self.re_compute_font(1.125)
    
        
        # titolo 
        self.check_esponente_pedice(
                f"{self.titolo}",
                self.start_x + self.w_plot_area // 2,
                self.end_y // 2 - self.font_pixel_dim[1] / 2,
                centered=True
            )
        
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
            ], round(self.ui_spessore * self.DPI_factor))

        # mouse coordinate
        coords_values = self.value_research_plot_area(logica.mouse_pos)
        value_x = coords_values[0]
        
        formatting_x = "e" if ((value_x > MAX_BORDER or value_x < MIN_BORDER) or (value_x < ZERO_MAX_BORDER and value_x > ZERO_MIN_BORDER)) and value_x != 0 else "f"
        value_y = coords_values[1]
        formatting_y = "e" if ((value_y > MAX_BORDER or value_y < MIN_BORDER) or (value_y < ZERO_MAX_BORDER and value_y > ZERO_MIN_BORDER)) and value_y != 0 else "f"
        mouse_coords = self.font_tipo.render(f"{value_x:.{self.approx_label}{formatting_x}}, {value_y:.{self.approx_label}{formatting_y}}", True, self.text_color)
        
        if not foto:
            self.schermo.blit(mouse_coords, (logica.mouse_pos[0] - self.ancoraggio_x, logica.mouse_pos[1] - self.ancoraggio_y - 1.5 * self.font_pixel_dim[1]))

        # zoom BB
        if logica.dragging and self.control:

            min_bb_x = min(logica.original_start_pos[0], logica.mouse_pos[0])
            max_bb_x = max(logica.original_start_pos[0], logica.mouse_pos[0])
            min_bb_y = min(logica.original_start_pos[1], logica.mouse_pos[1])
            max_bb_y = max(logica.original_start_pos[1], logica.mouse_pos[1])

            pygame.draw.rect(self.schermo, [0, 255, 0], [
                min_bb_x - self.ancoraggio_x,
                min_bb_y - self.ancoraggio_y, 
                max_bb_x - min_bb_x, 
                max_bb_y - min_bb_y
            ], round(self.ui_spessore * self.DPI_factor))

        if self.control:
            self.compute_integral_FWHM(logica)


    def compute_integral_FWHM(self, logica):
        """Computes the integral, derivative and FWHM"""
        pl_at = self.plots[self.active_plot]

        if pl_at.acceso:
            
            x_all = pl_at.x[pl_at.maschera]
            y_all = pl_at.y[pl_at.maschera]
            
            if len(x_all) > 2:

                x_min = x_all[0]
                x_max = x_all[-1]

                integral = trapezoid(y_all, x_all)
                derivata = np.gradient(y_all, x_all)

                FWHM_h = np.max(y_all) / 2
                FWHM_w = y_all > FWHM_h

                first_true_index = np.argmax(FWHM_w)
                last_true_index = len(FWHM_w) - 1 - np.argmax(FWHM_w[::-1])

                FWHM = x_all[last_true_index] - x_all[first_true_index]

                if type(integral) == np.ndarray: integral = integral[0]

                nome = pl_at.nome.split(".")

                self.UI_FID.assegna_messaggio(f"Informazioni sul grafico attivo ora [{self.plots[self.active_plot].nome}]\n\nIntegrale nell'intervallo: {integral:.{self.approx_label}f}\nFWHM del massimo nell'intervallo: {FWHM:.{self.approx_label}f}\n\nRange: {x_min} - {x_max}\n\nSalva la derivata come {nome[0]}_derivata.txt")

                if self.UI_save_deriv.toggled:
                    self.UI_save_deriv.push()
                    self.salva_derivata = True

                    # Writing results to a text file
                    with open(f"{self.UI_caricamento.text_invio}/{nome[0]}_derivata.{nome[1]}", "w") as file:
                        # Writing the derivative
                        for i in range(len(x_all)):
                            file.write(f"{x_all[i]}\t{derivata[i]}\n")
                    
                    self.UI_scroll_grafici.aggiorna_externo("reload", logica)
                    self.full_import_plot_data()


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
            ey = base_data.ey[base_data.maschera] if base_data.toggle_errorbar else None

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
                params_str = f"Interpolazione lineare del grafico {base_data.nome}:\nm: {m:.{self.approx_label}f} \\pm {m_e:.{self.approx_label}f}\nq: {q:.{self.approx_label}f} \\pm {q_e:.{self.approx_label}f}\n"

                errori = (m_e, q_e)

            else:
                if grado > 8: grado = 8

                coeff, covar = np.polyfit(x, y, deg = grado, cov= True) 
                errori = np.sqrt(np.diag(covar))

                coeff_name = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
                console_output = [f"{n}: {c:.{self.approx_label}f} \\pm {e:.{self.approx_label}f}\n" for n, c, e in zip(coeff_name, coeff, errori)]
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
                correlation_type = "\\chi quadro"
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
                    console_output = f"Interpolazione Guassiana del grafico {base_data.nome}:\nA: {params_gaus[0]:.{self.approx_label}f} \\pm {errori[0]:.{self.approx_label}f}\n\\mu: {params_gaus[1]:.{self.approx_label}f} \\pm {errori[1]:.{self.approx_label}f}\n\\sigma: {params_gaus[2]:.{self.approx_label}f} \\pm {errori[2]:.{self.approx_label}f}"

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
                    console_output = f"Interpolazione sigmoide del grafico {base_data.nome}:\na: {params_sigm[0]:.{self.approx_label}f} \\pm {errori[0]:.{self.approx_label}f}\nb: {params_sigm[1]:.{self.approx_label}f} \\pm {errori[1]:.{self.approx_label}f}\n\\lambda^2_0: {params_sigm[2]:.{self.approx_label}f} \\pm {errori[2]:.{self.approx_label}f}\n\\Delta\\lambda: {params_sigm[3]:.{self.approx_label}f} \\pm {errori[3]:.{self.approx_label}f}"

                    y_i = sigmoide(x, initial_guess_sigmo[0], initial_guess_sigmo[1], initial_guess_sigmo[2], initial_guess_sigmo[3])
                    correlation = 1 - np.sum( ( y - y_i )**2 ) /np.sum( ( y - (np.sum(y)/len(y)) )**2 )
                    correlation_type = "R quadro"
                    console_output += f"\n{correlation_type}: {correlation}"

            return console_output

        except RuntimeError as e:
            return f"Parametri ottimali non trovati, prova con un altro zoom.\n£{e}£"