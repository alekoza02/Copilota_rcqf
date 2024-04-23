import numpy as np
import pygame
import ctypes
import psutil
import wmi

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
        self.backspace = False
        self.left = False
        self.right = False

        self.acc_backspace = 0
        self.acc_left = 0
        self.acc_right = 0
        
        self.scroll_up = 0
        self.scroll_down = 0

        self.aggiorna_plot: bool = True
        
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
        self.max_fps: int = 60
        self.current_fps: int = 0
        self.running: int = 1

        self.cpu_sample: list[int] = [0 for i in range(100)]

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

        # aggiornamento
        self.current_fps = self.clock.get_fps()

        # PC status
        self.scena["main"].label_text["memory"].text = f"Memory usage: {psutil.Process().memory_info().rss / 1024**2:.2f} MB"
        
        self.cpu_sample.pop(0)
        self.cpu_sample.append(psutil.cpu_percent(interval=0))
        self.scena["main"].label_text["cpu"].text = f"CPU usage: {sum(self.cpu_sample) / len(self.cpu_sample):.0f}%"

        self.scena["main"].label_text["fps"].text = f"FPS: {self.current_fps:.2f}"
        
        battery = psutil.sensors_battery()
        if battery:
            if battery.power_plugged: charging = "chr"
            else: charging = "NO chr"
            self.scena["main"].label_text["battery"].text = f"Battery: {battery.percent:.1f}% {charging}"
        
        try:    
            w = wmi.WMI(namespace="root\\wmi")
            cpu_temperature_celsius = (w.MSAcpi_ThermalZoneTemperature()[0].CurrentTemperature / 10.0) - 273.15
            cpu_temperature_celsius = f"{cpu_temperature_celsius:.2f}"
        except Exception as e:
            cpu_temperature_celsius = "err"
        
        self.scena["main"].label_text["temp"].text = f"CPU temp: {cpu_temperature_celsius}°C"
        
        speed = "nan"
        self.scena["main"].label_text["fan"].text = f"Fan speed: {speed} RPM"


        # uscita
        keys = pygame.key.get_pressed()
        key_combo = [pygame.K_ESCAPE, pygame.K_SPACE]
        if all(keys[key] for key in key_combo):
            self.running = 0
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
        self.titolo: str = ""
        self.labelx: str = ""
        self.labely: str = ""
        self.label2y: str = ""
        self.round_label: str = ""
        self.color_bg: str = ""
        self.color_text: str = ""
        self.area_w: str = ""
        self.area_h: str = ""
        self.x_legenda: str = ""
        self.y_legenda: str = ""
        self.nome_grafico: str = ""
        self.color_plot: str = ""
        self.dim_pallini: str = ""
        self.dim_link: str = ""

        self.latex_check: bool = False
        self.toggle_2_axis: bool = False
        self.toggle_pallini: bool = False
        self.toggle_collegamenti: bool = False
        self.acceso: bool = False


    @staticmethod
    def are_attributes_equal(obj1, obj2):
        # Get the dictionary of attributes for each object
        attrs_obj1 = obj1.__dict__
        attrs_obj2 = obj2.__dict__

        # Check if the attributes of obj1 are equal to obj2
        for key, value in attrs_obj1.items():
            if key in attrs_obj2:
                if value != attrs_obj2[key]:
                    return False
            else:
                return False

        # Check if the attributes of obj2 are equal to obj1
        for key, value in attrs_obj2.items():
            if key in attrs_obj1:
                if value != attrs_obj1[key]:
                    return False
            else:
                return False

        return True


    @staticmethod
    def update_attributes(old_obj, new_obj):
        # Get the dictionary of attributes for each object
        attrs_old_obj = old_obj.__dict__
        attrs_new_obj = new_obj.__dict__

        # Check if the attributes of old_obj are equal to new_obj
        for key, value in attrs_new_obj.items():
            attrs_old_obj[key] = value


class DefaultScene:
    def __init__(self, parametri_repeat: list) -> None:
        # 0.625
        self.madre: pygame.Surface = parametri_repeat[0]
        self.fonts: dict[str, Font] = parametri_repeat[1]

        self.moltiplicatore_x: float = parametri_repeat[2]
        self.shift: int = parametri_repeat[3]

        self.ori_y: int = self.madre.get_height()

        self.entrata_attiva = None

        self.data_widgets =  WidgetData()

        self.label_text: dict[str, LabelText] = {}
        self.label_texture = {}
        self.bottoni: dict[str, Button] = {}
        self.entrate: dict[str, Entrata] = {}
        self.radio = {}
        self.scrolls: dict[str, ScrollConsole] = {}
        self.schermo: dict[str, Schermo] = {}
        self.ui_signs: dict[str, UI_signs] = {}

        self.parametri_repeat_elementi: list = [self.madre, self.shift, self.moltiplicatore_x, self.ori_y]
        
        # LABEL
        # --------------------------------------------------------------------------------
        # statici
        self.label_text["memory"] = LabelText(self.parametri_repeat_elementi, self.fonts["piccolo"], w=10, h=1.8, x=90, y=98, text="Memory usage: X MB", renderizza_bg=False)
        self.label_text["battery"] = LabelText(self.parametri_repeat_elementi, self.fonts["piccolo"], w=10, h=1.8, x=81, y=98, text="Battery: X%", renderizza_bg=False)
        self.label_text["fps"] = LabelText(self.parametri_repeat_elementi, self.fonts["piccolo"], w=10, h=1.8, x=73, y=98, text="FPS: X", renderizza_bg=False)
        self.label_text["cpu"] = LabelText(self.parametri_repeat_elementi, self.fonts["piccolo"], w=10, h=1.8, x=66.5, y=98, text="CPU usage: X%", renderizza_bg=False)
        self.label_text["temp"] = LabelText(self.parametri_repeat_elementi, self.fonts["piccolo"], w=10, h=1.8, x=59, y=98, text="CPU temp: X°C", renderizza_bg=False)
        self.label_text["fan"] = LabelText(self.parametri_repeat_elementi, self.fonts["piccolo"], w=10, h=1.8, x=50.5, y=98, text="Fan speed: Xrpm", renderizza_bg=False)

        # BOTTONI
        # --------------------------------------------------------------------------------
        # statici
        self.bottoni["latex_check"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=90, y=5, text="str to LaTeX")
        self.bottoni["toggle_2_axis"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=90, y=7, text="Toggle 2° axis")

        # dinamici
        self.bottoni["toggle_pallini"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=67.5, y=36, text="Pallini", toggled=True)
        self.bottoni["toggle_collegamenti"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=67.5, y=38, text="Links", toggled=True)
        self.bottoni["acceso"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=3*1.6, x=67.5, y=40, text="Acceso", toggled=False)
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
        self.entrate["nome_grafico"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=10, h=1.8, x=65, y=30, text="Plot 1", titolo="Nome")
        self.entrate["color_plot"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=65, y=32, text="#ffffff", titolo="Colore graf.")
        self.entrate["dim_pallini"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1, h=1.8, x=65, y=36, text="1", titolo="Dim. pallini")
        self.entrate["dim_link"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1, h=1.8, x=65, y=38, text="1", titolo="Dim. links")
        # --------------------------------------------------------------------------------


        # SCROLLCONSOLE
        # --------------------------------------------------------------------------------
        # dinamiche
        self.scrolls["grafici"] = ScrollConsole(self.parametri_repeat_elementi, self.fonts["piccolo"], w=18, h=16, x=77.5, y=30, titolo="Scelta grafici / data plot")


        # UI SIGNS
        # --------------------------------------------------------------------------------
        # statiche
        self.ui_signs["div_stat_din"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=26.4, x2=98, y2=26.4, spessore=2)


        self.schermo["viewport"] = Schermo(self.parametri_repeat_elementi)
        
    
    def disegnami(self, logica: Logica) -> None:
        
        # ui elements
        [label.disegnami() for indice, label in self.label_text.items()]
        [bottone.disegnami() for indice, bottone in self.bottoni.items()]
        [entrata.disegnami(logica) for indice, entrata in self.entrate.items()]
        [scrolla.disegnami(logica) for indice, scrolla in self.scrolls.items()]
        [segno.disegnami() for indice, segno in self.ui_signs.items()]


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
        self.data_widgets.acceso = self.bottoni["acceso"].toggled
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


class UI_signs:
    def __init__(self, parametri_locali_elementi: list, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, bg: tuple[int] = (40, 40, 40), spessore: int = 1) -> None:
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
        
        self.x1: float = self.moltiplicatore_x * x1 / 100 + self.offset
        self.y1: float = self.ori_y * y1 / 100
        self.x2: float = self.moltiplicatore_x * x2 / 100 + self.offset
        self.y2: float = self.ori_y * y2 / 100

        self.spessore: int = spessore

        self.bg: tuple[int] = bg

        self.screen: pygame.Surface = parametri_locali_elementi[0]


    def disegnami(self) -> None:
        pygame.draw.line(self.screen, self.bg, [self.x1, self.y1], [self.x2, self.y2], self.spessore)
        

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

        self.puntatore: int = len(self.text)
        self.dt_animazione: int = 0 

        self.font_locale: Font = font_locale

    def disegnami(self, logica: Logica):

        colore_sfondo = self.bg if not self.toggle else np.array(self.bg) - np.array([30,25,25])
        colore_testo = self.color_text if not self.toggle else np.array([42,80,67])

        # calcolo forma
        pygame.draw.rect(self.screen, colore_sfondo, [self.x, self.y, self.w, self.h])

        # calcolo scritta
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.text}", True, colore_testo), (self.x + self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))

        # calcolo nome
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.titolo}", True, colore_testo), (self.x - len(self.titolo + " ") * self.font_locale.font_pixel_dim[0], self.y + self.h//2 - self.font_locale.font_pixel_dim[1] // 2))

        self.dt_animazione += 1 if logica.dt % 30 == 0 else 0

        if self.toggle and self.dt_animazione % 2 == 0:
            pygame.draw.rect(self.screen, np.array([255,255,255]), [self.x + self.font_locale.font_pixel_dim[0] * (self.puntatore + .5) + 2, self.y, 2, self.h])

    def selezionato_ent(self, event):
            
            if self.bounding_box.collidepoint(event.pos):
                if self.toggle:
                    self.toggle = False
                else:
                    self.toggle = True
                    self.puntatore = len(self.text)
            else:
                self.toggle = False

    def __str__(self) -> str:
        return f"{self.text}"


class ScrollConsole:
    def __init__(self, parametri_locali_elementi: list, font_locale: Font, w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, titolo: str = "Default scroll") -> None:
        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.bg: tuple[int] = bg
        self.color_text: tuple[int] = (100, 100, 100)

        self.screen: pygame.Surface = parametri_locali_elementi[0]
        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

        self.font_locale: Font = font_locale

        self.titolo: str = titolo
        self.elementi: list = [f"Prova dell'inserimento del nome del grafico {i}" for i in range(5)]
        self.first_item: int = 0
        self.scroll_item_selected: int = 0

        # batched data
        self.pos_elementi_bb: list[pygame.Rect] = [pygame.Rect([
            self.x + 3 * self.font_locale.font_pixel_dim[0] // 2, 
            self.y + self.font_locale.font_pixel_dim[1] * 3.25 + index * (self.h - self.font_locale.font_pixel_dim[1] * 4) / 5, 
            len(elemento) * self.font_locale.font_pixel_dim[0], 
            self.font_locale.font_pixel_dim[1] * 1.5]) 
            for index, elemento in enumerate(self.elementi[self.first_item : self.first_item + 5])]

        self.pos_elementi: list[tuple[float]] = [(
            self.x + 4 * self.font_locale.font_pixel_dim[0] // 2, 
            self.y + self.font_locale.font_pixel_dim[1] * 3.5 + index * (self.h - self.font_locale.font_pixel_dim[1] * 4) / 5) 
            for index in range(len(self.elementi[self.first_item : self.first_item + 5]))]


    def disegnami(self, logica: Logica):

        # calcolo forma
        pygame.draw.rect(self.screen, self.bg, [self.x, self.y, self.w, self.h], border_top_left_radius=10, border_bottom_right_radius=10)

        # calcolo box titolo
        pygame.draw.rect(self.screen, np.array(self.bg) + 10, [self.x, self.y, self.font_locale.font_pixel_dim[0] * (len(self.titolo) + 4), self.font_locale.font_pixel_dim[1] * 2], border_top_left_radius=10, border_bottom_right_radius=10)
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.titolo}", True, (100, 100, 100)), (self.x + 3 * self.font_locale.font_pixel_dim[0] // 2, self.y + self.font_locale.font_pixel_dim[1] - self.font_locale.font_pixel_dim[1] // 2))

        bg_alteranto1 = np.array(self.bg) + 20
        bg_alteranto2 = np.array(self.bg) + 30

        # calcolo scritta elementi
        for index, elemento in enumerate(self.elementi[self.first_item : self.first_item + 5]):
            colore_alternato = bg_alteranto1 if index % 2 == 0 else bg_alteranto2
            if index == self.scroll_item_selected: colore_alternato = [42,80,67] # TODO solve colorazione
            
            pygame.draw.rect(self.screen, colore_alternato, self.pos_elementi_bb[index])
            self.screen.blit(self.font_locale.font_tipo.render(f"{elemento}", True, (100, 100, 100)), self.pos_elementi[index])


    def selezionato_scr(self, event, logica: Logica):
        
        for index, test_pos in enumerate(self.pos_elementi_bb):
            if test_pos.collidepoint(logica.mouse_pos):
                self.scroll_item_selected = index
                logica.aggiorna_plot = True

    def aggiorna_externo(self, index: str, logica: Logica):

        match index:
            case "up":
                if self.scroll_item_selected > 0: 
                    self.scroll_item_selected -= 1 
                elif self.first_item > 0:
                    self.first_item -= 1

            case "down":
                if self.scroll_item_selected < 4: 
                    self.scroll_item_selected += 1 
                elif self.first_item < len(self.elementi) - 5:
                    self.first_item += 1

            case _:
                pass

        logica.aggiorna_plot = True


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