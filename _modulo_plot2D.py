import numpy as np
from _modulo_UI import Schermo, Logica, UI, Scena
import pygame
from _modulo_MATE import Mate
import os
from _modulo_database_tooltips import Dizionario

diction = Dizionario()

MIN_BORDER = -10000
MAX_BORDER = 10000

ZERO_MIN_BORDER = -.001
ZERO_MAX_BORDER = .001


class Plot2D:
    def __init__(self, nome, data_input, metadata) -> None:
        
        # data
        self.data = data_input

        # calcolo dimensione array
        indici = self.data[:, :2].copy()
    
        indici[:, 0] -= np.min(indici[:, 0])
        indici[:, 0] /= np.max(indici[:, 0])

        indici[:, 1] -= np.min(indici[:, 1])
        indici[:, 1] /= np.max(indici[:, 1])

        self.dim_x = len(np.unique(indici[:, 1]))
        self.dim_y = len(np.unique(indici[:, 0]))

        self.data = self.data.reshape(self.dim_x, self.dim_y, 3)

        # calcolo dell'array di coordinate
        self.data = self.data.transpose(1, 0, 2)
        self.data = self.data[:, ::-1, :]

        lim_min = 22
        lim_max = 30
        # self.data = self.data[lim_min:-lim_max, :, :]
        # self.data = self.data[:, lim_min:-lim_max, :]
        self.data = self.data[:, :, :]


        self.dim_x = self.data.shape[1]
        self.dim_y = self.data.shape[0]
        self.w_div_h = self.dim_x / self.dim_y

        


class Painter2D:

    def __init__(self) -> None:
        self.text_color = [180, 180, 180]
        
        self.w_proportion = 0.75
        self.h_proportion = 0.75

        self.debug_info = [0, 0]

        self.ui_spessore = 1
        self.approx_label = 2
        self.subdivisions = 5
        self.plot_bb = True
        self.latex_check = True
        
        self.control = True

        self.bg_color = [30, 30, 30]

        self.colore_mappa1 = [68, 1, 84]
        self.colore_mappa2 = [253, 231, 37]

        self.testo_x = "Coordinate X [\mum]"
        self.testo_y = "Coordinate Y [\mum]"
        self.testo_height_bar = "Coordinate Z [nm]"
        self.titolo = "Sesto tentativo di caricamento immagini AFM"

        self.titolo = self.check_latex(self.titolo)
        self.testo_x = self.check_latex(self.testo_x)
        self.testo_y = self.check_latex(self.testo_y)

        self.x_legenda = 0.3
        self.y_legenda = 0.3
        
        self.min_y_l: list[float] = [0.0, 0.0]
        self.max_y_l: list[float] = [1.0, 1.0]

        self.dim_font_base = 32
        self.dim_font = 32 
        path = os.path.join('TEXTURES', 'f_full_font.ttf')
        self.font_tipo = pygame.font.Font(path, self.dim_font)
        self.font_pixel_dim = self.font_tipo.size("a")

    
    def re_compute_size(self) -> None:
        """Ricalcola la dimensione dell'UI dei grafici in base alla presenza del secondo asse Y"""

        self.w_plot_area = self.w_proportion * self.utilizzo_w
        self.h_plot_area = self.h_proportion * self.utilizzo_h
        
        self.start_x = (self.utilizzo_w - self.w_plot_area) // 2
        self.start_y = self.utilizzo_h - (self.utilizzo_h - self.h_plot_area) // 2
        
        self.end_x = self.start_x + self.w_plot_area
        self.end_y = self.start_y - self.h_plot_area

        self.bounding_box = pygame.rect.Rect([self.start_x - 20, self.end_y - 20, self.w_plot_area + 40, self.h_plot_area + 40])
        self.bounding_box[0] += self.ancoraggio_x
        self.bounding_box[1] += self.ancoraggio_y


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

        if self.latex_check:

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


    def link_ui(self, ui: UI, scene: str = "plot2D", schermo: str = "viewport"):
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

        self.plot2D: Plot2D = None

        self.UI_calls_plots = ui.scena["plot2D"]

        self.UI_titolo = self.UI_calls_plots.entrate["titolo"]
        self.UI_labelx = self.UI_calls_plots.entrate["labelx"]
        self.UI_labely = self.UI_calls_plots.entrate["labely"]
        self.UI_label2y = self.UI_calls_plots.entrate["label2y"]
        self.UI_round_label = self.UI_calls_plots.entrate["round_label"]
        self.UI_font_size = self.UI_calls_plots.entrate["font_size"]
        self.UI_color_bg = self.UI_calls_plots.entrate["color_bg"]
        self.UI_color_text = self.UI_calls_plots.entrate["color_text"]
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
        self.UI_use_custom_borders = self.UI_calls_plots.bottoni["use_custom_borders"]
        self.UI_latex_check = self.UI_calls_plots.bottoni["latex_check"]
        self.UI_toggle_2_axis = self.UI_calls_plots.bottoni["toggle_2_axis"]
        self.UI_toggle_plot_bb = self.UI_calls_plots.bottoni["toggle_plot_bb"]

        self.UI_path_import = self.UI_calls_plots.paths["caricamento"]


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
    
        # try:
            # CONVERSIONE ARRAY DI FLOATS
        if len(data[0]) != len(data[1]): data.pop(0)
        data = np.array(data).astype(float)    
        
        nome = path.split('\\')[-1]
        
        self.plot2D = Plot2D(nome, data, metadata_lst)
        
        # except:
        #     print(f"Impossibile caricare il file: {path}")


    def disegna(self, logica: Logica, foto: bool = False):
        
        self.min_x = np.min(self.plot2D.data[:, :, 0])
        self.max_x = np.max(self.plot2D.data[:, :, 0])
        self.min_y = np.min(self.plot2D.data[:, :, 1])
        self.max_y = np.max(self.plot2D.data[:, :, 1])

        # import settings
        if self.control:
            if self.UI_latex_check.toggled:
                self.titolo = Painter2D.check_latex(self.UI_titolo.text_invio) 
                self.testo_x = Painter2D.check_latex(self.UI_labelx.text_invio)
                self.testo_y = Painter2D.check_latex(self.UI_labely.text_invio)
                self.testo_height_bar = Painter2D.check_latex(self.UI_label2y.text_invio)
            else:
                self.titolo = self.UI_titolo.text_invio
                self.testo_x = self.UI_labelx.text_invio
                self.testo_y = self.UI_labely.text_invio
                self.testo_height_bar = self.UI_label2y.text_invio
            
            # prova di conversione
            self.approx_label = Mate.conversione_limite(self.UI_round_label.text_invio, 2, 9)
            self.dim_font_base = Mate.conversione_limite(self.UI_font_size.text_invio, 32, 128)
            
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


        if foto:

            self.w_foto = 3240
            self.h_foto = 3240

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

        # recalculation of window
        self.re_compute_size()

        
        if self.plot2D.w_div_h < 1:
            nuova_larghezza_grafico = self.w_plot_area
            nuovo_offset_grafico_x = 0
            nuova_altezza_grafico = self.h_plot_area * self.plot2D.w_div_h
            nuovo_offset_grafico_y = (self.h_plot_area * self.plot2D.w_div_h) / 2
        
        if self.plot2D.w_div_h > 1:
            nuova_larghezza_grafico = self.w_plot_area / self.plot2D.w_div_h
            nuovo_offset_grafico_x = (self.w_plot_area - self.w_plot_area / self.plot2D.w_div_h) / 2
            nuova_altezza_grafico = self.h_plot_area
            nuovo_offset_grafico_y = 0


        # disegna la mappa a colori
        fa = self.plot2D.data[:, :, 2]
        fa_min = fa - np.min(fa)
        fa_norm = fa_min / np.max(fa_min)

        colore_base = np.zeros((*fa.shape, 3))

        colore_base[:, :, 0] = self.colore_mappa1[0]
        colore_base[:, :, 1] = self.colore_mappa1[1]
        colore_base[:, :, 2] = self.colore_mappa1[2]

        colore_differenza = np.zeros((*fa.shape, 3))

        colore_differenza[:, :, 0] = self.colore_mappa2[0] - self.colore_mappa1[0]
        colore_differenza[:, :, 1] = self.colore_mappa2[1] - self.colore_mappa1[1]
        colore_differenza[:, :, 2] = self.colore_mappa2[2] - self.colore_mappa1[2]

        array_finale = np.zeros((*fa.shape, 3))

        array_finale[:, :, 0] = colore_base[:, :, 0] + fa_norm * colore_differenza[:, :, 0]
        array_finale[:, :, 1] = colore_base[:, :, 1] + fa_norm * colore_differenza[:, :, 1]
        array_finale[:, :, 2] = colore_base[:, :, 2] + fa_norm * colore_differenza[:, :, 2]

        surface = pygame.surfarray.make_surface(array_finale)
        self.schermo.blit(pygame.transform.scale(surface, (nuova_larghezza_grafico, nuova_altezza_grafico)), (self.start_x + nuovo_offset_grafico_x, self.end_y + nuovo_offset_grafico_y))

        
        # fill la barra di altezza map colore
        map_color_array = np.zeros((int(self.w_plot_area * 0.05), int(nuova_altezza_grafico), 3))

        for i in range(3):
            map_color_array[:, :, i] = np.tile(np.linspace(self.colore_mappa2[i], self.colore_mappa1[i], map_color_array.shape[1]), (1, int(map_color_array.shape[0]))).reshape(int(map_color_array.shape[0]), map_color_array.shape[1])

        surface = pygame.surfarray.make_surface(map_color_array)
        self.schermo.blit(surface, ((self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico) + (2.25 / 2) * (self.start_x + nuovo_offset_grafico_x) // 4 - self.w_plot_area * 0.025, self.end_y + nuovo_offset_grafico_y))

        # disegna la barra di altezza map colore
        pygame.draw.rect(self.schermo, self.text_color, [
                (self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico) + (2.25 / 2) * (self.start_x + nuovo_offset_grafico_x) // 4 - self.w_plot_area * 0.025,
                self.end_y + nuovo_offset_grafico_y,
                self.w_plot_area * 0.05,
                nuova_altezza_grafico
            ], round(self.ui_spessore * self.DPI_factor))
        



        # X axis
        pygame.draw.line(self.schermo, self.text_color, 
            [self.start_x + nuovo_offset_grafico_x, self.start_y + 1 * (self.utilizzo_h - (self.start_y + nuovo_offset_grafico_y)) // 4],
            [self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico, self.start_y + 1 * (self.utilizzo_h - (self.start_y + nuovo_offset_grafico_y)) // 4],
            round(self.ui_spessore * self.DPI_factor)
        )

        # colore assi
        colori_assi = [self.text_color, self.text_color]
        
        # Y axis
        pygame.draw.line(self.schermo, colori_assi[0], 
            [3 * (self.start_x + nuovo_offset_grafico_x) // 4, self.end_y + nuovo_offset_grafico_y + nuova_altezza_grafico],
            [3 * (self.start_x + nuovo_offset_grafico_x) // 4, self.end_y + nuovo_offset_grafico_y],
            round(self.ui_spessore * self.DPI_factor)
        )

        # 2 Y axis
        pygame.draw.line(self.schermo, colori_assi[1], 
            [(self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico) + 2.25 * (self.start_x + nuovo_offset_grafico_x) // 4, self.end_y + nuovo_offset_grafico_y],
            [(self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico) + 2.25 * (self.start_x + nuovo_offset_grafico_x) // 4, (self.end_y + nuovo_offset_grafico_y + nuova_altezza_grafico)],
            round(self.ui_spessore * self.DPI_factor)
        )
    
        # scalini sugli assi e valori
        self.re_compute_font(0.625)
        
        delta_x = self.max_x - self.min_x
        delta_y = self.max_y - self.min_y
        
        delta_y2 = np.max(self.plot2D.data[:, :, 2]) - np.min(self.plot2D.data[:, :, 2])

        for i in range(self.subdivisions):
            
            # data x
            pos_var_x = (self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico * i/ (self.subdivisions - 1))
            pos_var_y = (self.end_y + nuovo_offset_grafico_y + nuova_altezza_grafico * i/ (self.subdivisions - 1))
            

            pygame.draw.line(self.schermo, self.text_color, 
                [pos_var_x, self.start_y + 1 * (self.utilizzo_h - (self.start_y + nuovo_offset_grafico_y)) // 4 - self.utilizzo_w // 100],
                [pos_var_x, self.start_y + 1 * (self.utilizzo_h - (self.start_y + nuovo_offset_grafico_y)) // 4 + self.utilizzo_w // 100],
                round(self.ui_spessore * self.DPI_factor)
            )
            
            value = self.min_x + delta_x * i / (self.subdivisions - 1)
            formatting = "e" if ((value > MAX_BORDER or value < MIN_BORDER) or (value < ZERO_MAX_BORDER and value > ZERO_MIN_BORDER)) and value != 0 else "f"
            self.schermo.blit(self.font_tipo.render(f"{value:.{self.approx_label}{formatting}}", True, self.text_color), (
                pos_var_x - self.font_pixel_dim[0] * len(f"{value:.{self.approx_label}{formatting}}") / 2,
                self.start_y + 1 * (self.utilizzo_h - (self.start_y + nuovo_offset_grafico_y)) // 4 + self.utilizzo_w // 100
            ))
            
            # data y
            pygame.draw.line(self.schermo, colori_assi[0], 
                [3 * (self.start_x + nuovo_offset_grafico_x) // 4 - self.utilizzo_w // 100, pos_var_y],
                [3 * (self.start_x + nuovo_offset_grafico_x) // 4 + self.utilizzo_w // 100, pos_var_y],
                round(self.ui_spessore * self.DPI_factor)
            )
            
            value = self.max_y - delta_y * i / (self.subdivisions - 1)
            formatting = "e" if ((value > MAX_BORDER or value < MIN_BORDER) or (value < ZERO_MAX_BORDER and value > ZERO_MIN_BORDER)) and value != 0 else "f"
            label_y_scr = self.font_tipo.render(f"{value:.{self.approx_label}{formatting}}", True, colori_assi[0])
            label_y_scr = pygame.transform.rotate(label_y_scr, 90)
        

            self.schermo.blit(label_y_scr, (
                3 * (self.start_x + nuovo_offset_grafico_x) // 4 - self.utilizzo_w // 100 - self.font_pixel_dim[1],
                pos_var_y - self.font_pixel_dim[0] * len(f"{value:.{self.approx_label}{formatting}}") / 2
            ))
            
            # data 2 y
            pygame.draw.line(self.schermo, colori_assi[1], 
                [(self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico) + 2.25 * (self.start_x + nuovo_offset_grafico_x) // 4 - self.utilizzo_w // 100, pos_var_y],
                [(self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico) + 2.25 * (self.start_x + nuovo_offset_grafico_x) // 4 + self.utilizzo_w // 100, pos_var_y],
                round(self.ui_spessore * self.DPI_factor)
            )
            
            value = self.min_y_l[1] + delta_y2 * i / (self.subdivisions - 1)
            formatting = "e" if ((value > MAX_BORDER or value < MIN_BORDER) or (value < ZERO_MAX_BORDER and value > ZERO_MIN_BORDER)) and value != 0 else "f"
            label_y_scr = self.font_tipo.render(f"{value * 1000:.{self.approx_label}{formatting}}", True, colori_assi[1])
            label_y_scr = pygame.transform.rotate(label_y_scr, 90)
        
            self.schermo.blit(label_y_scr, (
                (self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico) + 2.25 * (self.start_x + nuovo_offset_grafico_x) // 4 + self.utilizzo_w // 100,
                pos_var_y - self.font_pixel_dim[0] * len(f"{value:.{self.approx_label}{formatting}}") / 2
            ))
        
            # griglia
            if self.UI_toggle_plot_bb.toggled:
                pygame.draw.line(self.schermo, [50, 50, 50], 
                    [pos_var_x, self.end_y + nuovo_offset_grafico_y],
                    [pos_var_x, self.end_y + nuovo_offset_grafico_y + nuova_altezza_grafico],
                    1
                )

                pygame.draw.line(self.schermo, [50, 50, 50], 
                    [self.start_x + nuovo_offset_grafico_x, pos_var_y],
                    [self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico, pos_var_y],
                    1
                )

        # plots bounding box
        pygame.draw.rect(self.schermo, self.text_color, [
            self.start_x + nuovo_offset_grafico_x, self.end_y + nuovo_offset_grafico_y,
            nuova_larghezza_grafico, nuova_altezza_grafico
        ], self.ui_spessore)


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
                (self.start_x + nuovo_offset_grafico_x) - 3 * (self.start_x + nuovo_offset_grafico_x) // 5 - bias_asse_y_sinistro,
                self.end_y + nuovo_offset_grafico_y + nuova_altezza_grafico // 2,
                vertical=True,
                centered=True
            )

        
        # testo asse 2 y
        self.check_esponente_pedice(
            f"{self.testo_height_bar}",
            (self.start_x + nuovo_offset_grafico_x + nuova_larghezza_grafico) + (self.start_x + nuovo_offset_grafico_x) - 1 * (self.start_x + nuovo_offset_grafico_x) // 5,
            self.end_y + nuovo_offset_grafico_y + nuova_altezza_grafico // 2,
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
        
        # "------------------------------------------------------------------------------------------------"

        self.re_compute_font(.5)
        
        # mouse coordinate
        # coords_values = self.value_research_plot_area(logica.mouse_pos)
        # value_x = coords_values[0]
        
        # formatting_x = "e" if ((value_x > MAX_BORDER or value_x < MIN_BORDER) or (value_x < ZERO_MAX_BORDER and value_x > ZERO_MIN_BORDER)) and value_x != 0 else "f"
        # value_y = coords_values[1]
        # formatting_y = "e" if ((value_y > MAX_BORDER or value_y < MIN_BORDER) or (value_y < ZERO_MAX_BORDER and value_y > ZERO_MIN_BORDER)) and value_y != 0 else "f"
        # mouse_coords = self.font_tipo.render(f"{value_x:.{self.approx_label}{formatting_x}}, {value_y:.{self.approx_label}{formatting_y}}", True, self.text_color)
        
        # if not foto:
        #     self.schermo.blit(mouse_coords, (logica.mouse_pos[0] - self.ancoraggio_x, logica.mouse_pos[1] - self.ancoraggio_y - 1.5 * self.font_pixel_dim[1]))

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

        
        # debugger
        pygame.draw.circle(self.schermo, [255, 0, 0], [self.start_x, self.start_y], 10)
        pygame.draw.circle(self.schermo, [255, 0, 0], [self.end_x, self.start_y], 10)
        pygame.draw.circle(self.schermo, [255, 0, 0], [self.start_x, self.end_y], 10)
        pygame.draw.circle(self.schermo, [255, 0, 0], [self.end_x, self.end_y], 10)


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