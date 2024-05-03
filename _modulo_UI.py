import numpy as np
import pygame
import ctypes
import psutil
import wmi
import os
import configparser

class Logica:
    def __init__(self) -> None:
        '''
        Inizializzazione di variabili che mi danno infomrazioni sull'UI / comandi da eseguire
        '''
        self.dragging = False
        self.original_start_pos = (0,0)
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

    def __init__(self, config: configparser.ConfigParser) -> None:
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
        self.BG: tuple[int] = eval(config.get(config.get("Default", "tema"), 'colore_bg_UI'))
        
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
        self.config = config
        parametri_scena_repeat: list = [self.MAIN, self.lista_font, self.moltiplicatore_x, self.shift_ori, self.config]
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

    @staticmethod
    def salva_screenshot(destinazione, nome, formato, schermo):
        try:
            existing_files = os.listdir(destinazione)
            highest_number = 0
            for filename in existing_files:
                if filename.startswith(nome) and filename.endswith(formato):
                    try:
                        file_number = int(filename[len(nome):-len(formato)])
                        if file_number > highest_number:
                            highest_number = file_number
                    except ValueError:
                        pass
            new_number = highest_number + 1
            new_filename = f'{nome}{new_number}{formato}'
            destination_file_modello = os.path.join(destinazione, new_filename)
            pygame.image.save(schermo, destination_file_modello)
        except FileNotFoundError:
            pass

    
    def event_manage(self, eventi: pygame.event, logica: Logica, plot):
        al_sc = self.scena["main"]
        
        # Stato di tutti i tasti
        keys = pygame.key.get_pressed()

        # CONTROLLO CARATTERI SPECIALI
        logica.ctrl = keys[pygame.K_LCTRL]
        logica.shift = keys[pygame.K_LSHIFT]
        logica.backspace = keys[pygame.K_BACKSPACE]
        logica.left = keys[pygame.K_LEFT]
        logica.right = keys[pygame.K_RIGHT]

        # scena main UI
        for event in eventi:
            # MOUSE
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    
                    # gestisce eventi bottone e entrata schiacciata
                    [elemento.selezionato_bot(event) for indice, elemento in al_sc.bottoni.items()]
                    [elemento.selezionato_ent(event) for indice, elemento in al_sc.entrate.items()]
                    [mult_box.selezionato_mul(event) for indice, mult_box in al_sc.multi_box.items()]
                    [scrolla.selezionato_scr(event, logica) for indice, scrolla in al_sc.scrolls.items()]
                    
                    '-----------------------------------------------------------------------------------------------------'
                    # Inizio sezione push events
                    if al_sc.bottoni["carica"].toggled:
                        al_sc.bottoni["carica"].push()
                        try:
                            plot.full_import_plot_data(al_sc.entrate["caricamento"].text)
                            al_sc.scrolls["grafici"].aggiorna_externo("reload", logica)
                        except FileNotFoundError as e:
                            print(e)


                    if al_sc.bottoni["usa_poly"].toggled:
                        self.scena["main"].entrate["grado_inter"].visibile = True# self.scena["main"].label_text["params"].text = "Interpolazione Polinomiale:\n- Accendi un grafico\n- Computa l'interpolazione\n- Abilita la visualizzazione dell'interpolazione"
                    elif al_sc.bottoni["usa_gaussi"].toggled:
                        self.scena["main"].entrate["grado_inter"].visibile = False# self.scena["main"].label_text["params"].text = "Interpolazione Gaussiana:\n- Accendi un grafico\n- Computa l'interpolazione\n- Abilita la visualizzazione dell'interpolazione"
                    elif al_sc.bottoni["usa_sigmoi"].toggled: 
                        self.scena["main"].entrate["grado_inter"].visibile = False# self.scena["main"].label_text["params"].text = "Interpolazione Sigmoide:\n- Accendi un grafico\n- Computa l'interpolazione\n- Abilita la visualizzazione dell'interpolazione"
                    else:
                        self.scena["main"].entrate["grado_inter"].visibile = False
                        self.scena["main"].label_text["params"].text = "Seleziona un tipo di interpolazione.\nSuccessivamente schiaccia il bottone 'Compute Interpolation'"
                    

                    if al_sc.bottoni["comp_inter"].toggled:
                        al_sc.bottoni["comp_inter"].push()
                        if al_sc.bottoni["usa_poly"].toggled:
                            self.scena["main"].label_text["params"].text = plot.check_latex(plot.linear_interpolation())
                        elif al_sc.bottoni["usa_gaussi"].toggled:
                            self.scena["main"].label_text["params"].text = plot.check_latex(plot.customfoo_interpolation("gaussian"))
                        elif al_sc.bottoni["usa_sigmoi"].toggled:
                            self.scena["main"].label_text["params"].text = plot.check_latex(plot.customfoo_interpolation("sigmoid"))

                    if al_sc.bottoni["salva"].toggled:
                        al_sc.bottoni["salva"].push()
                        self.salva_screenshot(al_sc.entrate["salvataggio_path"].text, al_sc.entrate["salvataggio_nome"].text, ".png", self.scena["main"].schermo["viewport"].schermo)

                    # updates the active plot to the nearest to the click
                    plot.nearest_coords(self, logica)

                    # Fine sezione push events
                    '-----------------------------------------------------------------------------------------------------'

                    # raccolta di tutti i testi già presenti nelle entrate
                    test_entr_attiva: list[str] = [indice for indice, elemento in al_sc.entrate.items() if elemento.toggle]

                    # logica per cui se ci sono entrate nella scena -> aggiorna il testo, indice e il testo generico modificabile
                    if len(test_entr_attiva) > 0:
                        al_sc.entrata_attiva = al_sc.entrate[test_entr_attiva[0]]
                    else: al_sc.entrata_attiva = None

                if event.button == 3:
                    logica.dragging = True
                    logica.original_start_pos = logica.mouse_pos
                    logica.dragging_end_pos = logica.mouse_pos
                if event.button == 4:
                    logica.scroll_up += 1
                if event.button == 5:
                    logica.scroll_down += 1

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3: 
                    logica.dragging = False
                    logica.dragging_end_pos = logica.mouse_pos
                    plot.values_zoom(logica)

            if event.type == pygame.MOUSEMOTION:
                if logica.dragging:
                    logica.dragging_start_pos = logica.dragging_end_pos
                    logica.dragging_end_pos = logica.mouse_pos
                    logica.dragging_dx = logica.dragging_end_pos[0] - logica.dragging_start_pos[0]
                    logica.dragging_dy = - logica.dragging_end_pos[1] + logica.dragging_start_pos[1] # sistema di riferimento invertito

            # TASTIERA
            # controlli generici -> No inserimento
            
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_r:
                    plot.reset_zoom(logica)

                if event.key == pygame.K_UP:
                    self.scena["main"].scrolls["grafici"].aggiorna_externo("up", logica)
                    
                if event.key == pygame.K_DOWN:
                    self.scena["main"].scrolls["grafici"].aggiorna_externo("down", logica)

                if event.key == pygame.K_RETURN:
                    try:
                        if al_sc.entrate["caricamento"].toggle:
                            plot.full_import_plot_data(al_sc.entrate["caricamento"].text)
                            al_sc.scrolls["grafici"].aggiorna_externo("reload", logica)
                    except FileNotFoundError as e:
                        print(e)


            # input -> tastiera con caratteri e backspace
            if al_sc.entrata_attiva != None:

                if " " in al_sc.entrata_attiva.text: ricercatore = " " 
                else: ricercatore = "\\"

                if event.type == pygame.TEXTINPUT:           
                    al_sc.entrata_attiva.text = al_sc.entrata_attiva.text[:al_sc.entrata_attiva.puntatore] + event.text + al_sc.entrata_attiva.text[al_sc.entrata_attiva.puntatore:]
                    al_sc.entrata_attiva.puntatore += len(event.text)
                    al_sc.entrata_attiva.dt_animazione = 0

                if event.type == pygame.KEYDOWN:
                    
                    tx = al_sc.entrata_attiva.text
                            
                    if event.key == pygame.K_BACKSPACE:
                        if logica.ctrl:

                            nuovo_puntatore = tx[:al_sc.entrata_attiva.puntatore].rstrip().rfind(ricercatore)+1
                            text2eli = tx[nuovo_puntatore : al_sc.entrata_attiva.puntatore]
                            al_sc.entrata_attiva.puntatore = nuovo_puntatore
                            al_sc.entrata_attiva.text = tx.replace(text2eli, "") 

                        else:
                            if al_sc.entrata_attiva.puntatore != 0:
                                al_sc.entrata_attiva.text = al_sc.entrata_attiva.text[:al_sc.entrata_attiva.puntatore-1] + al_sc.entrata_attiva.text[al_sc.entrata_attiva.puntatore:]
                            if al_sc.entrata_attiva.puntatore > 0:
                                al_sc.entrata_attiva.puntatore -= 1

                    if event.key == pygame.K_LEFT:
                        if al_sc.entrata_attiva.puntatore > 0:
                            if logica.ctrl:
                                al_sc.entrata_attiva.puntatore = tx[:al_sc.entrata_attiva.puntatore].rstrip().rfind(ricercatore)+1
                            else: 
                                al_sc.entrata_attiva.puntatore -= 1

                    if event.key == pygame.K_RIGHT:
                        if al_sc.entrata_attiva.puntatore < len(al_sc.entrata_attiva.text):
                            if logica.ctrl:

                                # trovo l'indice di dove inizia la frase
                                start = tx.find(tx[al_sc.entrata_attiva.puntatore:].lstrip(), al_sc.entrata_attiva.puntatore, len(tx))
                                # se non la trovo mi blocco dove sono partito
                                if start == -1: start = al_sc.entrata_attiva.puntatore

                                # se la trovo, cerco la parola successiva
                                found = tx.find(ricercatore, start, len(tx))
                                # se non la trovo guardo mi posizione nell'ultimo carattere diverso da uno spazio
                                if found == -1: found = len(tx.rstrip())

                                al_sc.entrata_attiva.puntatore = found
                                
                            else:
                                al_sc.entrata_attiva.puntatore += 1

                    al_sc.entrata_attiva.dt_animazione = 0 

        if logica.backspace:
            logica.acc_backspace += 1
            if logica.acc_backspace > 20:
                if al_sc.entrata_attiva.puntatore != 0:
                    al_sc.entrata_attiva.text = al_sc.entrata_attiva.text[:al_sc.entrata_attiva.puntatore-1] + al_sc.entrata_attiva.text[al_sc.entrata_attiva.puntatore:]
                if al_sc.entrata_attiva.puntatore > 0:
                    al_sc.entrata_attiva.puntatore -= 1
        else: 
            logica.acc_backspace = 0

        if logica.left:
            logica.acc_left += 1
            if logica.acc_left > 20:
                if logica.ctrl:
                    al_sc.entrata_attiva.puntatore = al_sc.entrata_attiva.text[:al_sc.entrata_attiva.puntatore].rstrip().rfind(ricercatore)+1
                elif al_sc.entrata_attiva.puntatore > 0: al_sc.entrata_attiva.puntatore -= 1
                al_sc.entrata_attiva.dt_animazione = 0 
        else: 
            logica.acc_left = 0
        
        if logica.right:
            logica.acc_right += 1
            if logica.acc_right > 20:
                if logica.ctrl:
                    tx = al_sc.entrata_attiva.text
                    # trovo l'indice di dove inizia la frase
                    start = tx.find(tx[al_sc.entrata_attiva.puntatore:].lstrip(), al_sc.entrata_attiva.puntatore, len(tx))
                    # se non la trovo mi blocco dove sono partito
                    if start == -1: start = al_sc.entrata_attiva.puntatore

                    # se la trovo, cerco la parola successiva
                    found = tx.find(ricercatore, start, len(tx))
                    # se non la trovo guardo mi posizione nell'ultimo carattere diverso da uno spazio
                    if found == -1: found = len(tx.rstrip())

                    al_sc.entrata_attiva.puntatore = found
                     
                elif al_sc.entrata_attiva.puntatore < len(al_sc.entrata_attiva.text): al_sc.entrata_attiva.puntatore += 1
                al_sc.entrata_attiva.dt_animazione = 0 
        else: 
            logica.acc_right = 0

        # gestione collegamento ui - grafico        
        if logica.aggiorna_plot: plot.change_active_plot_UIBASED(self); logica.aggiorna_plot = False

        # resoconto dello stato di tutti i bottoni e entrate
        self.scena["main"].collect_data()


    def start_cycle(self, logica: Logica):
        # impostazione inizio giro
        self.clock.tick(self.max_fps)
        self.colora_bg()
        self.mouse_icon(logica)

        logica.dt += 1
        logica.dragging_dx = 0
        logica.dragging_dy = 0
        logica.mouse_pos = pygame.mouse.get_pos()


    def DEBUG_zoom(self, logica: Logica):
        if logica.dragging:
            poligono = [
                [logica.original_start_pos[0], logica.original_start_pos[1]], 
                [logica.mouse_pos[0], logica.original_start_pos[1]],
                [logica.mouse_pos[0], logica.mouse_pos[1]], 
                [logica.original_start_pos[0], logica.mouse_pos[1]]
            ]
            pygame.draw.polygon(self.MAIN, [0, 255, 0], poligono)

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

        self.normalizza: bool = False
        self.latex_check: bool = False
        self.toggle_2_axis: bool = False
        self.toggle_plt_bb: bool = False
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

        self.config: configparser.ConfigParser = parametri_repeat[4]

        self.ori_y: int = self.madre.get_height()

        self.entrata_attiva = None

        self.data_widgets =  WidgetData()

        self.label_text: dict[str, LabelText] = {}
        self.label_texture = {}
        self.bottoni: dict[str, Button] = {}
        self.entrate: dict[str, Entrata] = {}
        self.multi_box: dict[str, MultiBox] = {}
        self.scrolls: dict[str, ScrollConsole] = {}
        self.schermo: dict[str, Schermo] = {}
        self.ui_signs: dict[str, UI_signs] = {}

        self.parametri_repeat_elementi: list = [self.madre, self.shift, self.moltiplicatore_x, self.ori_y]
        
        self.tema = self.config.get('Default', 'tema')

        # LABEL
        # --------------------------------------------------------------------------------
        # statici
        self.label_text["memory"] = LabelText(self.parametri_repeat_elementi, [self.fonts["piccolo"], self.fonts["medio"]], w=10, h=1.8, x=90, y=98, text="Memory usage: X MB", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'memory_label_bg')), color_text=eval(self.config.get(self.tema, 'memory_label_text')))
        self.label_text["battery"] = LabelText(self.parametri_repeat_elementi, [self.fonts["piccolo"], self.fonts["medio"]], w=10, h=1.8, x=81, y=98, text="Battery: X%", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'battery_label_bg')), color_text=eval(self.config.get(self.tema, 'battery_label_text')))
        self.label_text["fps"] = LabelText(self.parametri_repeat_elementi, [self.fonts["piccolo"], self.fonts["medio"]], w=10, h=1.8, x=73, y=98, text="FPS: X", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'fps_label_bg')), color_text=eval(self.config.get(self.tema, 'fps_label_text')))
        self.label_text["cpu"] = LabelText(self.parametri_repeat_elementi, [self.fonts["piccolo"], self.fonts["medio"]], w=10, h=1.8, x=66.5, y=98, text="CPU usage: X%", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'cpu_label_bg')), color_text=eval(self.config.get(self.tema, 'cpu_label_text')))
        self.label_text["temp"] = LabelText(self.parametri_repeat_elementi, [self.fonts["piccolo"], self.fonts["medio"]], w=10, h=1.8, x=59, y=98, text="CPU temp: X°C", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'temp_label_bg')), color_text=eval(self.config.get(self.tema, 'temp_label_text')))
        self.label_text["fan"] = LabelText(self.parametri_repeat_elementi, [self.fonts["piccolo"], self.fonts["medio"]], w=10, h=1.8, x=50.5, y=98, text="Fan speed: Xrpm", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'fan_label_bg')), color_text=eval(self.config.get(self.tema, 'fan_label_text')))

        # interpolazioni
        self.label_text["params"] = LabelText(self.parametri_repeat_elementi, [self.fonts["medio"], self.fonts["piccolo"]], w=10, h=1.8, x=60, y=58, renderizza_bg=False, text="Seleziona un tipo di interpolazione.\nSuccessivamente schiaccia il bottone 'Compute Interpolation'", bg=eval(self.config.get(self.tema, 'params_label_bg')), color_text=eval(self.config.get(self.tema, 'params_label_text')))
        # --------------------------------------------------------------------------------

        # BOTTONI
        # --------------------------------------------------------------------------------
        # statici
        self.bottoni["latex_check"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=60, y=23, text="str to LaTeX", bg=eval(self.config.get(self.tema, 'latex_check_bottone_bg')), color_text=eval(self.config.get(self.tema, 'latex_check_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'latex_check_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'latex_check_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'latex_check_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'latex_check_bottone_bg2')))
        self.bottoni["toggle_2_axis"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=66.5, y=23, text="Toggle 2° axis", bg=eval(self.config.get(self.tema, 'toggle_2_axis_bottone_bg')), color_text=eval(self.config.get(self.tema, 'toggle_2_axis_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'toggle_2_axis_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'toggle_2_axis_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'toggle_2_axis_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'toggle_2_axis_bottone_bg2')))
        self.bottoni["toggle_plot_bb"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=73, y=23, text="Toggle plot BB", toggled=True, bg=eval(self.config.get(self.tema, 'toggle_plot_bb_bottone_bg')), color_text=eval(self.config.get(self.tema, 'toggle_plot_bb_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'toggle_plot_bb_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'toggle_plot_bb_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'toggle_plot_bb_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'toggle_plot_bb_bottone_bg2')))
        self.bottoni["normalizza"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=79.5, y=23, text="Normalizza", bg=eval(self.config.get(self.tema, 'normalizza_bottone_bg')), color_text=eval(self.config.get(self.tema, 'normalizza_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'normalizza_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'normalizza_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'normalizza_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'normalizza_bottone_bg2')))
        self.bottoni["carica"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3.8/1.6, h=3.8, x=82, y=14, tipologia="push", texture="UI_cerca", bg=eval(self.config.get(self.tema, 'carica_bottone_bg')), color_text=eval(self.config.get(self.tema, 'carica_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'carica_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'carica_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'carica_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'carica_bottone_bg2')))
        self.bottoni["salva"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3.8/1.6, h=3.8, x=82, y=18, tipologia="push", texture="UI_save", bg=eval(self.config.get(self.tema, 'salva_bottone_bg')), color_text=eval(self.config.get(self.tema, 'salva_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'salva_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'salva_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'salva_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'salva_bottone_bg2')))

        # dinamici
        self.bottoni["toggle_inter"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=67.5, y=36, text="Interpol", toggled=True, bg=eval(self.config.get(self.tema, 'toggle_inter_bottone_bg')), color_text=eval(self.config.get(self.tema, 'toggle_inter_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'toggle_inter_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'toggle_inter_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'toggle_inter_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'toggle_inter_bottone_bg2')))
        self.bottoni["toggle_pallini"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=67.5, y=38, text="Pallini", toggled=True, bg=eval(self.config.get(self.tema, 'toggle_pallini_bottone_bg')), color_text=eval(self.config.get(self.tema, 'toggle_pallini_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'toggle_pallini_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'toggle_pallini_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'toggle_pallini_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'toggle_pallini_bottone_bg2')))
        self.bottoni["toggle_collegamenti"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=1.8, x=67.5, y=40, text="Links", toggled=True, bg=eval(self.config.get(self.tema, 'toggle_collegamenti_bottone_bg')), color_text=eval(self.config.get(self.tema, 'toggle_collegamenti_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'toggle_collegamenti_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'toggle_collegamenti_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'toggle_collegamenti_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'toggle_collegamenti_bottone_bg2')))
        self.bottoni["acceso"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=6, h=3*1.6, x=67.5, y=42, text="Acceso", toggled=True, bg=eval(self.config.get(self.tema, 'acceso_bottone_bg')), color_text=eval(self.config.get(self.tema, 'acceso_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'acceso_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'acceso_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'acceso_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'acceso_bottone_bg2')))
        
        # interpolazioni
        self.bottoni["usa_poly"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=9, h=1.8, x=60, y=52, text="Linear interpolation", multi_box=True, bg=eval(self.config.get(self.tema, 'usa_poly_bottone_bg')), color_text=eval(self.config.get(self.tema, 'usa_poly_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'usa_poly_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'usa_poly_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'usa_poly_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'usa_poly_bottone_bg2')))
        self.bottoni["usa_gaussi"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=9, h=1.8, x=70, y=52, text="Gaussian interpolation", multi_box=True, bg=eval(self.config.get(self.tema, 'usa_gaussi_bottone_bg')), color_text=eval(self.config.get(self.tema, 'usa_gaussi_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'usa_gaussi_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'usa_gaussi_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'usa_gaussi_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'usa_gaussi_bottone_bg2')))
        self.bottoni["usa_sigmoi"] = Button(self.parametri_repeat_elementi, self.fonts["piccolo"], w=9, h=1.8, x=80, y=52, text="Sigmoid interpolation", multi_box=True, bg=eval(self.config.get(self.tema, 'usa_sigmoi_bottone_bg')), color_text=eval(self.config.get(self.tema, 'usa_sigmoi_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'usa_sigmoi_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'usa_sigmoi_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'usa_sigmoi_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'usa_sigmoi_bottone_bg2')))
        self.bottoni["comp_inter"] = Button(self.parametri_repeat_elementi, self.fonts["medio"], w=9, h=3.6, x=90, y=52, text="COMPUTE", tipologia="push", bg=eval(self.config.get(self.tema, 'comp_inter_bottone_bg')), color_text=eval(self.config.get(self.tema, 'comp_inter_bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'comp_inter_bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'comp_inter_bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'comp_inter_bottone_contorno')), bg2=eval(self.config.get(self.tema, 'comp_inter_bottone_bg2')))
        self.multi_box["interpol_mode"] = MultiBox([self.bottoni["usa_poly"],self.bottoni["usa_gaussi"],self.bottoni["usa_sigmoi"]])
        # --------------------------------------------------------------------------------


        # ENTRATE
        # --------------------------------------------------------------------------------
        # statiche
        self.entrate["titolo"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=19, h=1.8, x=65, y=5, text="", titolo="Titolo", bg=eval(self.config.get(self.tema, 'titolo_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'titolo_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'titolo_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'titolo_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'titolo_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'titolo_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'titolo_entrata_color_puntatore')))
        self.entrate["labelx"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=19, h=1.8, x=65, y=7, text="", titolo="Label X", bg=eval(self.config.get(self.tema, 'labelx_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'labelx_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'labelx_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'labelx_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'labelx_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'labelx_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'labelx_entrata_color_puntatore')))
        self.entrate["labely"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=19, h=1.8, x=65, y=9, text="", titolo="Label Y (sx)", bg=eval(self.config.get(self.tema, 'labely_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'labely_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'labely_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'labely_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'labely_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'labely_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'labely_entrata_color_puntatore')))
        self.entrate["label2y"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=19, h=1.8, x=65, y=11, text="", titolo="Label Y (dx)", bg=eval(self.config.get(self.tema, 'label2y_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'label2y_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'label2y_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'label2y_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'label2y_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'label2y_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'label2y_entrata_color_puntatore')))
        self.entrate["caricamento"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=16, h=1.8, x=65, y=15, text="PLOT_DATA\default", titolo="Input path", bg=eval(self.config.get(self.tema, 'caricamento_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'caricamento_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'caricamento_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'caricamento_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'caricamento_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'caricamento_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'caricamento_entrata_color_puntatore')))
        self.entrate["salvataggio_path"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=7, h=1.8, x=65, y=19, text="OUTPUT", titolo="Output path", bg=eval(self.config.get(self.tema, 'salvataggio_path_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'salvataggio_path_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'salvataggio_path_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'salvataggio_path_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'salvataggio_path_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'salvataggio_path_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'salvataggio_path_entrata_color_puntatore')))
        self.entrate["salvataggio_nome"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=5, h=1.8, x=76, y=19, text="default", titolo="File name", bg=eval(self.config.get(self.tema, 'salvataggio_nome_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'salvataggio_nome_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'salvataggio_nome_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'salvataggio_nome_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'salvataggio_nome_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'salvataggio_nome_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'salvataggio_nome_entrata_color_puntatore')))
        self.entrate["round_label"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1.5, h=1.8, x=90, y=9, text="2", titolo="Round to", bg=eval(self.config.get(self.tema, 'round_label_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'round_label_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'round_label_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'round_label_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'round_label_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'round_label_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'round_label_entrata_color_puntatore')))
        self.entrate["font_size"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1.5, h=1.8, x=90, y=7, text=f"{self.fonts['grande'].dim_font}", titolo="Font size", bg=eval(self.config.get(self.tema, 'font_size_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'font_size_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'font_size_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'font_size_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'font_size_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'font_size_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'font_size_entrata_color_puntatore')))
        self.entrate["color_bg"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=11, text="#151924", titolo="Colore bg", bg=eval(self.config.get(self.tema, 'color_bg_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'color_bg_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'color_bg_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'color_bg_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'color_bg_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'color_bg_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'color_bg_entrata_color_puntatore')))
        self.entrate["color_text"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=13, text="#b4b4b4", titolo="Colore UI", bg=eval(self.config.get(self.tema, 'color_text_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'color_text_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'color_text_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'color_text_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'color_text_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'color_text_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'color_text_entrata_color_puntatore')))
        self.entrate["area_w"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=15, text=".8", titolo="w plot area", bg=eval(self.config.get(self.tema, 'area_w_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'area_w_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'area_w_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'area_w_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'area_w_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'area_w_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'area_w_entrata_color_puntatore')))
        self.entrate["area_h"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=17, text=".8", titolo="h plot area", bg=eval(self.config.get(self.tema, 'area_h_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'area_h_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'area_h_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'area_h_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'area_h_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'area_h_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'area_h_entrata_color_puntatore')))
        self.entrate["x_legenda"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=19, text=".2", titolo="x legenda", bg=eval(self.config.get(self.tema, 'x_legenda_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'x_legenda_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'x_legenda_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'x_legenda_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'x_legenda_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'x_legenda_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'x_legenda_entrata_color_puntatore')))
        self.entrate["y_legenda"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=90, y=21, text=".3", titolo="y legenda", bg=eval(self.config.get(self.tema, 'y_legenda_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'y_legenda_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'y_legenda_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'y_legenda_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'y_legenda_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'y_legenda_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'y_legenda_entrata_color_puntatore')))

        # dinamiche
        self.entrate["nome_grafico"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=10, h=1.8, x=65, y=30, text="Plot 1", titolo="Nome", bg=eval(self.config.get(self.tema, 'nome_grafico_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'nome_grafico_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'nome_grafico_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'nome_grafico_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'nome_grafico_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'nome_grafico_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'nome_grafico_entrata_color_puntatore')))
        self.entrate["color_plot"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=3, h=1.8, x=65, y=32, text="#ffffff", titolo="Colore graf.", bg=eval(self.config.get(self.tema, 'color_plot_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'color_plot_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'color_plot_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'color_plot_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'color_plot_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'color_plot_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'color_plot_entrata_color_puntatore')))
        self.entrate["dim_pallini"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1, h=1.8, x=65, y=36, text="1", titolo="Dim. pallini", bg=eval(self.config.get(self.tema, 'dim_pallini_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'dim_pallini_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'dim_pallini_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'dim_pallini_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'dim_pallini_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'dim_pallini_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'dim_pallini_entrata_color_puntatore')))
        self.entrate["dim_link"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1, h=1.8, x=65, y=38, text="1", titolo="Dim. links", bg=eval(self.config.get(self.tema, 'dim_link_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'dim_link_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'dim_link_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'dim_link_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'dim_link_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'dim_link_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'dim_link_entrata_color_puntatore')))
        
        # interpolazioni
        self.entrate["grado_inter"] = Entrata(self.parametri_repeat_elementi, self.fonts["piccolo"], w=1, h=1.8, x=98, y=56, text="1", titolo="Grado Interpolazione:", visibile=False, bg=eval(self.config.get(self.tema, 'grado_inter_entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'grado_inter_entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'grado_inter_entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'grado_inter_entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'grado_inter_entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'grado_inter_entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'grado_inter_entrata_color_puntatore')))
        # --------------------------------------------------------------------------------


        # SCROLLCONSOLE
        # --------------------------------------------------------------------------------
        # dinamiche
        self.scrolls["grafici"] = ScrollConsole(self.parametri_repeat_elementi, self.fonts["piccolo"], w=18, h=16, x=77.5, y=30, titolo="Scelta grafici / data plot", bg=eval(self.config.get(self.tema, 'grafici_scroll_bg')), color_text=eval(self.config.get(self.tema, 'grafici_scroll_color_text')), colore_selezionato=eval(self.config.get(self.tema, 'grafici_scroll_colore_selezionato')), titolo_colore=eval(self.config.get(self.tema, 'grafici_scroll_titolo_colore')))

        # UI SIGNS
        # --------------------------------------------------------------------------------
        # statiche
        self.ui_signs["div_stat_din"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=26.4, x2=98, y2=26.4, spessore=2, bg=eval(self.config.get(self.tema, 'div_stat_din_UI_signs')))
        self.ui_signs["div_din_inter"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=49, x2=98, y2=49, spessore=2, bg=eval(self.config.get(self.tema, 'div_din_inter_UI_signs')))


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
        self.data_widgets.dim_font = self.entrate["font_size"].text
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
        self.data_widgets.grado_inter = self.entrate["grado_inter"].text        

        self.data_widgets.normalizza = self.bottoni["normalizza"].toggled 
        self.data_widgets.toggle_inter = self.bottoni["toggle_inter"].toggled 
        self.data_widgets.toggle_pallini = self.bottoni["toggle_pallini"].toggled 
        self.data_widgets.toggle_collegamenti = self.bottoni["toggle_collegamenti"].toggled
        self.data_widgets.acceso = self.bottoni["acceso"].toggled
        self.data_widgets.latex_check = self.bottoni["latex_check"].toggled
        self.data_widgets.toggle_2_axis = self.bottoni["toggle_2_axis"].toggled
        self.data_widgets.toggle_plt_bb = self.bottoni["toggle_plot_bb"].toggled


class LabelText:
    def __init__(self, parametri_locali_elementi: list, font_locale: list[Font], w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, color_text: tuple[int] = (200, 200, 200), text: str = "Prova") -> None:
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

        self.font_locale_d: Font = font_locale[0]
        self.font_locale_s: Font = font_locale[1]
        self.text: str = text
        self.color_text: tuple[int] = color_text


    def disegnami(self) -> None:
        if self.renderizza_bg:
            pygame.draw.rect(self.screen, self.bg, [self.x, self.y, self.w, self.h], border_top_left_radius=10, border_bottom_right_radius=10)
        
        if self.text.count("£") == 2:
        
            start_index = self.text.find("£") + 1
            end_index = self.text.find("£", start_index)
        
            contatore_righe = 0

            for riga in self.text[:start_index - 1].split("\n"):
                self.screen.blit(self.font_locale_d.font_tipo.render(f"{riga}", True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + contatore_righe * 1.5 * self.font_locale_d.font_pixel_dim[1]))
                contatore_righe += 1

            for riga in self.text[start_index - 1:end_index].split("\n"):
                self.screen.blit(self.font_locale_s.font_tipo.render(f"{riga[1:-1]}", True, self.color_text), (self.x + 2 * self.font_locale_s.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_s.font_pixel_dim[1] // 2 + contatore_righe * 1.5 * self.font_locale_s.font_pixel_dim[1]))
                contatore_righe += 1

            for riga in self.text[end_index + 1:].split("\n"):
                self.screen.blit(self.font_locale_d.font_tipo.render(f"{riga}", True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + contatore_righe * 1.5 * self.font_locale_d.font_pixel_dim[1]))
                contatore_righe += 1

        else:
            for i, riga in enumerate(self.text.split("\n")):
                self.screen.blit(self.font_locale_d.font_tipo.render(f"{riga}", True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + i * 1.5 * self.font_locale_d.font_pixel_dim[1]))



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
    def __init__(self, parametri_locali_elementi: list, font_locale: Font, w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, text: str = "Prova", tipologia: str = "toggle", toggled: bool = False, texture: None = None, multi_box: bool = False, visibile: bool = True, color_text: tuple[int] = (200, 200, 200), colore_bg_schiacciato = [210, 210, 210], contorno_toggled = [84,160,134], contorno = [160,84,134], bg2: tuple[int] = (42, 80, 67)) -> None:
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
        self.color_text: tuple[int] = color_text

        self.multi_box = multi_box
        self.tipologia = tipologia
        self.toggled = toggled
        self.colore_bg_schiacciato = [i+10 if i < 245 else 255 for i in self.bg]

        self.contorno_toggled = contorno_toggled
        self.contorno = contorno

        self.animation: bool = False
        self.durata: int = 30
        self.tracker: int = 0
        self.bg2: tuple[int] = bg2

        self.visibile: bool = visibile

        if texture is None:
            self.texture = None
        else:
            self.texture = pygame.image.load(f"TEXTURES/{texture}.png")
            self.texture = pygame.transform.scale(self.texture, (self.w, self.h))

    def disegnami(self):
        if self.visibile:
            colore_scelto = self.colore_bg_schiacciato if self.toggled else self.bg
            
            if self.animation:
                self.tracker += 1

                colore_scelto = [int(p * (self.durata - self.tracker) / self.durata + d * (self.tracker) / self.durata) for p, d in zip(self.bg2, colore_scelto)]
                
                if self.tracker > self.durata:
                    self.tracker = 0
                    self.animation = False
            
            
            colore_secondario = self.contorno_toggled if self.toggled else self.contorno
            pygame.draw.rect(self.screen, colore_secondario, [self.x-1, self.y-1, self.w+2, self.h+2], border_top_left_radius=10, border_bottom_right_radius=10)
            pygame.draw.rect(self.screen, colore_scelto, [self.x, self.y, self.w, self.h], border_top_left_radius=10, border_bottom_right_radius=10)
            
            if self.texture is None:
                self.screen.blit(self.font_locale.font_tipo.render(f"{self.text}", True, self.color_text), (self.x + self.w // 2 - len(self.text) * self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))
            else:
                self.screen.blit(self.texture, (self.x, self.y))

    def selezionato_bot(self, event):
            
        if self.bounding_box.collidepoint(event.pos) and not self.multi_box and self.visibile:
            if self.toggled:
                self.toggled = False
            else:
                self.toggled = True
                self.animation = True
                self.tracker = 0

    def push(self) -> None:
        if self.toggled and self.tipologia == "push":
            self.toggled = False


class Entrata:
    def __init__(self, parametri_locali_elementi: list, font_locale: Font, w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, text: str = "Prova", titolo = "", visibile: bool = True, color_text: tuple[int] = (200, 200, 200), bg_toggled: tuple[int] = [10, 15, 15], contorno: tuple[int] = [100, 100, 100], contorno_toggled: tuple[int] = [100, 255, 255], color_puntatore: tuple[int] = [255, 255, 255], text_toggled: tuple[int] = (84,160,134)) -> None:
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
        self.bg_toggled: tuple[int] = bg_toggled
        self.color_text: tuple[int] = color_text
        self.color_text_toggled: tuple[int] = text_toggled
        self.contorno: tuple[int] = contorno
        self.contorno_toggled: tuple[int] = contorno_toggled
        self.color_puntatore: tuple[int] = color_puntatore

        self.screen: pygame.Surface = parametri_locali_elementi[0]
        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

        self.toggle = False

        self.puntatore: int = len(self.text)
        self.dt_animazione: int = 0 

        self.visibile = visibile

        self.font_locale: Font = font_locale

    def disegnami(self, logica: Logica):    

        if self.visibile:

            colore_sfondo = self.bg_toggled if self.toggle else self.bg 
            colore_testo = self.color_text_toggled if self.toggle else self.color_text 

            # calcolo forma
            colore_secondario = self.contorno_toggled if self.toggle else self.contorno
            pygame.draw.rect(self.screen, colore_secondario, [self.x-1, self.y-1, self.w+2, self.h+2])
            pygame.draw.rect(self.screen, colore_sfondo, [self.x, self.y, self.w, self.h])

            # calcolo scritta
            self.screen.blit(self.font_locale.font_tipo.render(f"{self.text}", True, colore_testo), (self.x + self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))

            # calcolo nome
            self.screen.blit(self.font_locale.font_tipo.render(f"{self.titolo}", True, colore_testo), (self.x - len(self.titolo + " ") * self.font_locale.font_pixel_dim[0], self.y + self.h//2 - self.font_locale.font_pixel_dim[1] // 2))

            self.dt_animazione += 1 if logica.dt % 30 == 0 else 0

            if self.toggle and self.dt_animazione % 2 == 0:
                pygame.draw.rect(self.screen, self.color_puntatore, [self.x + self.font_locale.font_pixel_dim[0] * (self.puntatore + .5) + 2, self.y, 2, self.h])

    def selezionato_ent(self, event):
            
            if self.bounding_box.collidepoint(event.pos) and self.visibile:
                if self.toggle:
                    self.toggle = False
                else:
                    self.toggle = True
                    self.puntatore = len(self.text)
            else:
                self.toggle = False

    # def completamento_testo(path, entrata):
    #     if type(path) == str:
    #         possibili_file = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and file.startswith(entrata.txt)]
    #     elif type(path) == dict:
    #         possibili_file = [i for i in path if i.startswith(entrata.txt)]

    #     if event.type == pygame.TEXTINPUT and entrata.collisione:
    #         try:
    #             entrata.subtext = possibili_file[0]
    #         except IndexError:
    #             pass

    #     if keys[pygame.K_TAB] and entrata.collisione:
    #         ultimo_file = entrata.subtext
    #         if ultimo_file in possibili_file:
    #             indice = possibili_file.index(ultimo_file) + 1
    #             if indice == len(possibili_file):
    #                 indice = 0
    #         else:
    #             indice = 0
    #         try:
    #             entrata.subtext = possibili_file[indice]
    #         except IndexError:
    #             pass

    #     if keys[pygame.K_RETURN] and entrata.collisione:
    #         entrata.txt = entrata.subtext

    def __str__(self) -> str:
        return f"{self.text}"


class ScrollConsole:
    def __init__(self, parametri_locali_elementi: list, font_locale: Font, w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, titolo: str = "Default scroll", color_text: tuple[int] = (200, 200, 200), colore_selezionato: tuple[int] = [42, 80, 67], titolo_colore: tuple[int] = (150, 150, 150)) -> None:
        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.bg: tuple[int] = bg
        self.color_text: tuple[int] = color_text
        self.colore_selezionato: tuple[int] = colore_selezionato
        self.titolo_colore: tuple[int] = titolo_colore

        self.bg_alteranto1 = np.array(self.bg) + 10
        self.bg_alteranto1[self.bg_alteranto1 > 255] = 255
        self.bg_alteranto2 = np.array(self.bg) + 15
        self.bg_alteranto2[self.bg_alteranto2 > 255] = 255
        
        self.screen: pygame.Surface = parametri_locali_elementi[0]
        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

        self.font_locale: Font = font_locale

        self.titolo: str = titolo
        self.elementi: list = [f"-                                              " for _ in range(5)]
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
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.titolo}", True, self.titolo_colore), (self.x + 3 * self.font_locale.font_pixel_dim[0] // 2, self.y + self.font_locale.font_pixel_dim[1] - self.font_locale.font_pixel_dim[1] // 2))

        # calcolo scritta elementi
        for index, elemento in enumerate(self.elementi[self.first_item : self.first_item + 5]):
            colore_alternato = self.bg_alteranto1 if index % 2 == 0 else self.bg_alteranto2
            if index == self.scroll_item_selected: colore_alternato = self.colore_selezionato
            
            pygame.draw.rect(self.screen, colore_alternato, self.pos_elementi_bb[index])
            self.screen.blit(self.font_locale.font_tipo.render(f"{elemento}", True, self.color_text), self.pos_elementi[index])


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

            case "reload":
                self.scroll_item_selected = 0
                self.first_item = 0

            case _:
                pass

        logica.aggiorna_plot = True


class MultiBox:
    def __init__(self, bottoni: list[Button]) -> None:
        self.elementi = bottoni

    def calcola_bb(self):

        min_x = np.inf
        min_y = np.inf
        max_x = - np.inf
        max_y = - np.inf

        for elemento in self.elementi:
            min_x = min(min_x, elemento.bounding_box[0])
            min_y = min(min_y, elemento.bounding_box[1])

            max_x = max(max_x, elemento.bounding_box[0] + elemento.bounding_box[2])
            max_y = max(max_y, elemento.bounding_box[1] + elemento.bounding_box[3])
                    
        max_x -= min_x
        max_y -= min_y

        self.BBB = pygame.rect.Rect(min_x, min_y, max_x, max_y)
    

    def selezionato_mul(self, event):
        
        self.calcola_bb()

        if self.BBB.collidepoint(event.pos):
            for elemento in self.elementi:
                if elemento.bounding_box.collidepoint(event.pos):
                    if elemento.toggled:
                        elemento.toggled = False
                    else:
                        elemento.toggled = True
                        elemento.animation = True
                        elemento.tracker = 0
                else:
                    elemento.toggled = False

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