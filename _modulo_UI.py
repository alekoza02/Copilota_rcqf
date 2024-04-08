import numpy as np
import pygame
import ctypes

from _modulo_MATE import Mate

class Logica:
    def __init__(self) -> None:
        '''
        Inizializzazione di variabili che mi danno infomrazioni sull'UI / comandi da eseguire
        '''
        self.dragging = False
        self.dragging_start_pos = (0,0)
        self.dragging_end_pos = (0,0)
        self.dragging_dx = 0
        self.dragging_dy = 0
        self.mouse_pos = (0,0)
        
        self.skip_salto = False
        self.dt = 0
        self.scena = 0
        
        self.ctrl = False
        self.shift = False
        
        self.scroll_up = 0
        self.scroll_down = 0
        
        self.messaggio_debug1: str = "Empty!"
        self.messaggio_debug2: str = "Empty!"
        self.messaggio_debug3: str = "Empty!"
        self.messaggio_debug4: str = "Empty!"
        self.messaggio_debug5: str = "Empty!"
        
    @property
    def lista_messaggi(self):
        return [self.messaggio_debug1, self.messaggio_debug2, self.messaggio_debug3, self.messaggio_debug4, self.messaggio_debug5]

class UI:
    '''
    Classe responsabile per la generazione dell'interfaccia grafica.
    Conterrà i vari elementi grafici:
    - Schermo
    - Scene
    - Bottoni
    - Labels
    - Entrate
    - Radio
    - Scrolls
    '''

    def __init__(self) -> None:
        '''
        Inizializzazione applicazione
        '''

        # DPI aware
        pygame.init()
        ctypes.windll.user32.SetProcessDPIAware()
        screen_info = pygame.display.Info()
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

        # custom mouse
        pygame.mouse.set_visible(False)
        self.custom_mouse_icon = pygame.image.load("TEXTURES\mouse.png")

        # impostazione dimensione schermi e rapporti
        self.w: int = int(screen_info.current_w * scale_factor)
        self.h: int = int(screen_info.current_h * scale_factor)

        self.aspect_ratio_nativo: float = 2880 / 1800
        self.moltiplicatore_x: float = self.h * self.aspect_ratio_nativo
        self.rapporto_ori: float = self.w / 2880
        self.shift_ori: float = (self.w - self.moltiplicatore_x) / 2

        # generazione finestra
        self.MAIN = pygame.display.set_mode((self.w, self.h))
        self.BG: tuple[int] = (30, 30, 30)
        
        self.clock = pygame.time.Clock()
        self.max_fps: int = 0
        self.current_fps: int = 0
        self.running: int = 1

        # generazione font
        self.lista_font: dict[Font] = {}
        self.lista_font["piccolo"] = Font("piccolo", self.rapporto_ori)
        self.lista_font["medio"] = Font("medio", self.rapporto_ori)
        self.lista_font["grande"] = Font("grande", self.rapporto_ori)
        self.lista_font["gigante"] = Font("gigante", self.rapporto_ori)

        # generazione scene
        parametri_scena_repeat: list = [self.MAIN, self.lista_font, self.moltiplicatore_x, self.shift_ori]
        self.scena: dict[str, DefaultScene] = {}
        self.scena["main"] = DefaultScene(parametri_scena_repeat)


    def cambio_opacit(self) -> None:
        '''
        Modifica l'opacità della finestra principale
        '''
        # Get the window handle using GetActiveWindow
        hwnd = ctypes.windll.user32.GetActiveWindow()

        # Set the window style to allow transparency
        win32style = ctypes.windll.user32.GetWindowLongW(hwnd, ctypes.c_int(-20))  # -20 corresponds to GWL_EXSTYLE
        ctypes.windll.user32.SetWindowLongW(hwnd, ctypes.c_int(-20), ctypes.c_long(win32style | 0x80000))  # 0x80000 corresponds to WS_EX_LAYERED

        # Set the opacity level
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(255 * 0.7), 2)  # 0x000000 corresponds to color key

    def colora_bg(self) -> None:
        '''
        Colora la finestra con il colore dello sfondo (self.BG)
        Inoltre disegna uno sfondo di colore (25, 25, 25) per gli aspect ratio diversi da 2880 x 1800
        '''
        self.MAIN.fill((25, 25, 25))
        pygame.draw.rect(self.MAIN, self.BG, [self.shift_ori, 0, self.w - 2 * self.shift_ori, self.h])

    def mouse_icon(self, logica: Logica) -> None:
        '''
        Ottiene la posizione del mouse attuale e ci disegna sopra l'icona custom 
        Assicurarsi che in UI ci sia pygame.mouse.set_visible(False)
        '''
        mouse = logica.mouse_pos
        self.MAIN.blit(self.custom_mouse_icon, mouse)

    def aggiornamento_e_uscita_check(self) -> None:
        '''
        Controlla se la combinazione di uscita è stata selezionata -> Uscita
        Altrimenti aggiornamento pagina
        '''
        # uscita
        keys = pygame.key.get_pressed()
        key_combo = [pygame.K_ESCAPE, pygame.K_SPACE]
        if all(keys[key] for key in key_combo):
            self.running = 0

        # aggiornamento
        self.current_fps = self.clock.get_fps()
        pygame.display.flip()
        
    def aggiorna_messaggi_debug(self, logica: Logica) -> None:
        messaggio_inviato = 0
        for indice, label in self.scena["main"].label_text.items():
            messaggi = logica.lista_messaggi
            if indice.startswith("debug"):
                label.assegna_messaggio(messaggi[messaggio_inviato])
                messaggio_inviato += 1

class Font:
    def __init__(self, dimensione: str = "medio", rapporto: float = 1.0) -> None:    
        
        match dimensione:
            case "piccolo":
                self.dim_font = int(16 * rapporto) 
                self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")
            case "medio":
                self.dim_font = int(24 * rapporto) 
                self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")
            case "grande":
                self.dim_font = int(32 * rapporto) 
                self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")
            case "gigante":
                self.dim_font = int(128 * rapporto) 
                self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")


class WidgetData:
    def __init__(self) -> None:
        self.titolo: str
        self.labelx: str
        self.labely: str
        self.label2y: str
        self.round_label: str
        self.color_bg: str
        self.color_text: str
        self.area_w: str
        self.area_h: str
        self.x_legenda: str
        self.y_legenda: str
        self.nome_grafico: str
        self.color_plot: str
        self.dim_pallini: str
        self.dim_link: str

        self.latex_check: bool
        self.toggle_2_axis: bool
        self.toggle_pallini: bool
        self.toggle_collegamenti: bool


class DefaultScene:
    def __init__(self, parametri_repeat: list) -> None:
        # 0.625
        self.madre: pygame.Surface = parametri_repeat[0]
        self.fonts: dict[str, Font] = parametri_repeat[1]

        self.moltiplicatore_x: float = parametri_repeat[2]
        self.shift: int = parametri_repeat[3]

        self.ori_y: int = self.madre.get_height()

        # impostazioni varie per la entry box
        self.testo_aggiornato = ""
        self.indice_entr_at = ""
        self.entrata_attiva = None
        self.puntatore_testo_attivo: int = 0

        self.data_widgets =  WidgetData()

        self.label_text: dict[str, LabelText] = {}
        self.label_texture = {}
        self.bottoni: dict[str, Button] = {}
        self.entrate: dict[str, Entrata] = {}
        self.radio = {}
        self.scrolls = {}
        self.schermo: dict[str, Schermo] = {}

        self.parametri_repeat_elementi: list = [self.madre, self.shift, self.moltiplicatore_x, self.ori_y]
        
        # BOTTONI
        # --------------------------------------------------------------------------------
        # statici
        self.bottoni["latex_check"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=90, y=5, text="str to LaTeX")
        self.bottoni["toggle_2_axis"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=90, y=7, text="Toggle 2° axis")

        # dinamici
        self.bottoni["toggle_pallini"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=67.5, y=36, text="Pallini", toggled=True)
        self.bottoni["toggle_collegamenti"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=67.5, y=38, text="Links", toggled=True)
        # --------------------------------------------------------------------------------


        # ENTRATE
        # --------------------------------------------------------------------------------
        # statiche
        self.entrate["titolo"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=19, h=1.8, x=65, y=5, text="", titolo="Titolo")
        self.entrate["labelx"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=19, h=1.8, x=65, y=7, text="", titolo="Label X")
        self.entrate["labely"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=19, h=1.8, x=65, y=9, text="", titolo="Label Y (sx)")
        self.entrate["label2y"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=19, h=1.8, x=65, y=11, text="", titolo="Label Y (dx)")
        self.entrate["round_label"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1, h=1.8, x=90, y=9, text="2", titolo="Round to")
        self.entrate["color_bg"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=11, text="#151924", titolo="Colore bg")
        self.entrate["color_text"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=13, text="#b4b4b4", titolo="Colore UI")
        self.entrate["area_w"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=15, text=".8", titolo="w plot area")
        self.entrate["area_h"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=17, text=".8", titolo="h plot area")
        self.entrate["x_legenda"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=19, text=".2", titolo="x legenda")
        self.entrate["y_legenda"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=21, text=".3", titolo="y legenda")

        # dinamiche
        self.entrate["nome_grafico"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=19, h=1.8, x=65, y=30, text="Plot 1", titolo="Nome")
        self.entrate["color_plot"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=65, y=32, text="#ffffff", titolo="Colore graf.")
        self.entrate["dim_pallini"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1, h=1.8, x=65, y=36, text="1", titolo="Dim. pallini")
        self.entrate["dim_link"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1, h=1.8, x=65, y=38, text="1", titolo="Dim. links")
        # --------------------------------------------------------------------------------


        self.schermo["viewport"] = Schermo(self.parametri_repeat_elementi)
        
    
    def disegnami(self) -> None:
        [label.disegnami() for indice, label in self.label_text.items()]
        [bottone.disegnami() for indice, bottone in self.bottoni.items()]
        [entrata.disegnami() for indice, entrata in self.entrate.items()]


    def collect_data(self) -> None:
        self.data_widgets.titolo = self.entrate["titolo"].text
        self.data_widgets.labelx = self.entrate["labelx"].text
        self.data_widgets.labely = self.entrate["labely"].text
        self.data_widgets.label2y = self.entrate["label2y"].text
        self.data_widgets.round_label = self.entrate["round_label"].text
        self.data_widgets.color_bg = self.entrate["color_bg"].text
        self.data_widgets.color_text = self.entrate["color_text"].text
        self.data_widgets.area_w = self.entrate["area_w"].text
        self.data_widgets.area_h = self.entrate["area_h"].text
        self.data_widgets.x_legenda = self.entrate["x_legenda"].text
        self.data_widgets.y_legenda = self.entrate["y_legenda"].text        
        self.data_widgets.nome_grafico = self.entrate["nome_grafico"].text        
        self.data_widgets.color_plot = self.entrate["color_plot"].text        
        self.data_widgets.dim_link = self.entrate["dim_link"].text        
        self.data_widgets.dim_pallini = self.entrate["dim_pallini"].text        

        self.data_widgets.toggle_pallini = self.bottoni["toggle_pallini"].toggled 
        self.data_widgets.toggle_collegamenti = self.bottoni["toggle_collegamenti"].toggled
        self.data_widgets.latex_check = self.bottoni["latex_check"].toggled
        self.data_widgets.toggle_2_axis = self.bottoni["toggle_2_axis"].toggled


class LabelText:
    def __init__(self, parametri_locali_elementi: list, font_locale: Font, w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, text: str = "Prova") -> None:
        '''
        parametri_locali_elementi dovrà contenere:
        - schermo madre
        - shift_x
        - x a disposizione sullo schermo
        - y a disposizione sullo schermo
        '''
        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.bg: tuple[int] = bg
        self.renderizza_bg: bool = renderizza_bg

        self.screen: pygame.Surface = parametri_locali_elementi[0]

        self.font_locale: Font = font_locale
        self.text: str = text
        self.color_text: tuple[int] = (100, 100, 100)

    def disegnami(self) -> None:
        if self.renderizza_bg:
            pygame.draw.rect(self.screen, self.bg, [self.x, self.y, self.w, self.h], border_top_left_radius=10, border_bottom_right_radius=10)
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.text}", True, self.color_text), (self.x + self.w // 2 - len(self.text) * self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))

    def assegna_messaggio(self, str: str = "Empty!") -> None:
        self.text = str


class Button():
    def __init__(self, parametri_locali_elementi: list, font_locale: Font, w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, text: str = "Prova", tipologia = "toggle", toggled = False) -> None:
        '''
        parametri_locali_elementi dovrà contenere:
        - schermo madre
        - shift_x
        - x a disposizione sullo schermo
        - y a disposizione sullo schermo
        '''
        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

        self.bg: tuple[int] = bg
        self.renderizza_bg: bool = renderizza_bg

        self.screen: pygame.Surface = parametri_locali_elementi[0]

        self.font_locale: Font = font_locale
        self.text: str = text
        self.color_text: tuple[int] = (100, 100, 100)

        self.tipologia = tipologia
        self.toggled = toggled
        self.colore_bg_schiacciato = [i+10 if i < 245 else 255 for i in self.bg]

    def disegnami(self):
        colore_scelto = self.colore_bg_schiacciato if self.toggled else self.bg
        pygame.draw.rect(self.screen, colore_scelto, [self.x, self.y, self.w, self.h], border_top_left_radius=10, border_bottom_right_radius=10)
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.text}", True, self.color_text), (self.x + self.w // 2 - len(self.text) * self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))

    def selezionato_bot(self, event):
            
        if self.bounding_box.collidepoint(event.pos):
            if self.toggled:
                self.toggled = False
            else:
                self.toggled = True

    def push(self):
        if self.toggled and self.tipologia == "push":
            self.toggled = False


class Entrata:
    def __init__(self, parametri_locali_elementi: list, font_locale: Font, w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, text: str = "Prova", titolo = "") -> None:
        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.text: str = text
        self.titolo: str = titolo
        
        self.bg: tuple[int] = bg
        self.color_text: tuple[int] = (100, 100, 100)

        self.screen: pygame.Surface = parametri_locali_elementi[0]
        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

        self.toggle = False

        self.puntatore: int = len(self.text) - 1

        self.font_locale: Font = font_locale

    def disegnami(self):

        colore_sfondo = self.bg if not self.toggle else np.array(self.bg) - np.array([30,25,25])
        colore_testo = self.color_text if not self.toggle else np.array([42,80,67])

        # calcolo forma
        pygame.draw.rect(self.screen, colore_sfondo, [self.x, self.y, self.w, self.h])

        # calcolo scritta
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.text}", True, colore_testo), (self.x + self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))

        # calcolo nome
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.titolo}", True, colore_testo), (self.x - len(self.titolo + " ") * self.font_locale.font_pixel_dim[0], self.y + self.h//2 - self.font_locale.font_pixel_dim[1] // 2))

        if self.toggle:
            pygame.draw.rect(self.screen, np.array([255,255,255]), [self.x + self.font_locale.font_pixel_dim[0] * (len(self.text) + .5) + 2, self.y, 2, self.h])

    def selezionato_ent(self, event):
            
            if self.bounding_box.collidepoint(event.pos):
                if self.toggle:
                    self.toggle = False
                else:
                    self.toggle = True
            else:
                self.toggle = False

    def __str__(self) -> str:
        return f"{self.text}"

class Schermo:
    def __init__(self, parametri_locali_elementi: list) -> None:

        self.w: int = int(parametri_locali_elementi[3] * 0.9)
        self.h: int = int(parametri_locali_elementi[3] * 0.9)
        self.ancoraggio_x: int = parametri_locali_elementi[3] * 0.05 + parametri_locali_elementi[1]
        self.ancoraggio_y: int = parametri_locali_elementi[3] * 0.05

        self.shift_x = parametri_locali_elementi[1]

        self.madre: pygame.Surface = parametri_locali_elementi[0]

        self.buffer: np.ndarray = np.zeros((self.w, self.h, 3))
        self.bg: tuple[int] = (30, 30, 30)

        self.schermo: pygame.Surface = pygame.Surface((self.w, self.h))

    def disegnami(self) -> None:
        '''
        Imposta solo lo sfondo
        ''' 
        self.schermo.fill((148 / 7, 177 / 7, 255 / 7))
        self.madre.blit(self.schermo, (self.ancoraggio_x, self.ancoraggio_y))