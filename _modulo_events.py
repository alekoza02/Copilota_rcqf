from _modulo_UI import UI, Logica, Path
from _modulo_MATE import Mate
from PIL import Image
import pygame
import threading

def event_manage_ui(self, eventi: pygame.event, logica: Logica):

    # Stato di tutti i tasti
    keys = pygame.key.get_pressed()

    # CONTROLLO CARATTERI SPECIALI
    logica.ctrl = keys[pygame.K_LCTRL]
    logica.shift = keys[pygame.K_LSHIFT]
    logica.backspace = keys[pygame.K_BACKSPACE]
    logica.left = keys[pygame.K_LEFT]
    logica.right = keys[pygame.K_RIGHT]
    logica.tab = keys[pygame.K_TAB]


    # reset variabili
    logica.click_sinistro = False
    logica.click_destro = False

    # scena main UI
    for event in eventi:

        # if event.type == pygame.DROPFILE:
        #     # Handle the file that was dropped
        #     dropped_file_path = event.file
        #     print(f"File dropped: {dropped_file_path}")

        # MOUSE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                [tab.aggiorna_tab(event, logica) for index, tab in self.scena["main"].tabs.items()]
                if self.scena["main"].bottoni["plots"].toggled: logica.scena = 0
                if self.scena["main"].bottoni["plot_import"].toggled: logica.scena = 1
                if self.scena["main"].bottoni["tracer"].toggled: logica.scena = 2
                if self.scena["main"].bottoni["orbitals"].toggled: logica.scena = 3

                logica.click_sinistro = True

            if event.button == 3:

                logica.click_destro = True
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

        if event.type == pygame.MOUSEMOTION:
            if logica.dragging:
                logica.dragging_start_pos = logica.dragging_end_pos
                logica.dragging_end_pos = logica.mouse_pos
                logica.dragging_dx = logica.dragging_end_pos[0] - logica.dragging_start_pos[0]
                logica.dragging_dy = - logica.dragging_end_pos[1] + logica.dragging_start_pos[1] # sistema di riferimento invertito

        
        # input -> tastiera con caratteri e backspace
        if self.entrata_attiva != None:

            if " " in self.entrata_attiva.text: ricercatore = " " 
            elif "\\" in self.entrata_attiva.text: ricercatore = "\\"
            elif "/" in self.entrata_attiva.text: ricercatore = "/"
            else: ricercatore = None

            if event.type == pygame.TEXTINPUT:           
                self.entrata_attiva.text = self.entrata_attiva.text[:self.entrata_attiva.puntatore] + event.text + self.entrata_attiva.text[self.entrata_attiva.puntatore:]
                self.entrata_attiva.puntatore += len(event.text)
                self.entrata_attiva.dt_animazione = 0

            if event.type == pygame.KEYDOWN:
                
                tx = self.entrata_attiva.text
                        
                if event.key == pygame.K_BACKSPACE:
                    if logica.ctrl:
                        if ricercatore is None:
                            self.entrata_attiva.puntatore = 0
                            self.entrata_attiva.text = "" 
                        else:
                            nuovo_puntatore = tx[:self.entrata_attiva.puntatore].rstrip().rfind(ricercatore)+1
                            text2eli = tx[nuovo_puntatore : self.entrata_attiva.puntatore]
                            self.entrata_attiva.puntatore = nuovo_puntatore
                            self.entrata_attiva.text = tx.replace(text2eli, "") 

                    else:
                        if self.entrata_attiva.puntatore != 0:
                            self.entrata_attiva.text = self.entrata_attiva.text[:self.entrata_attiva.puntatore-1] + self.entrata_attiva.text[self.entrata_attiva.puntatore:]
                        if self.entrata_attiva.puntatore > 0:
                            self.entrata_attiva.puntatore -= 1

                if event.key == pygame.K_LEFT:
                    if self.entrata_attiva.puntatore > 0:
                        if logica.ctrl:
                            if ricercatore is None:
                                self.entrata_attiva.puntatore = 0
                            else:
                                self.entrata_attiva.puntatore = tx[:self.entrata_attiva.puntatore].rstrip().rfind(ricercatore)+1
                        else: 
                            self.entrata_attiva.puntatore -= 1

                if event.key == pygame.K_RIGHT:
                    if self.entrata_attiva.puntatore < len(self.entrata_attiva.text):
                        if logica.ctrl:

                            if ricercatore is None:
                                self.entrata_attiva.puntatore = len(self.entrata_attiva.text)
                            else:

                                # trovo l'indice di dove inizia la frase
                                start = tx.find(tx[self.entrata_attiva.puntatore:].lstrip(), self.entrata_attiva.puntatore, len(tx))
                                # se non la trovo mi blocco dove sono partito
                                if start == -1: start = self.entrata_attiva.puntatore

                                # se la trovo, cerco la parola successiva
                                found = tx.find(ricercatore, start, len(tx))
                                # se non la trovo guardo mi posizione nell'ultimo carattere diverso da uno spazio
                                if found == -1: found = len(tx.rstrip())

                                self.entrata_attiva.puntatore = found
                                
                        else:
                            self.entrata_attiva.puntatore += 1

                self.entrata_attiva.dt_animazione = 0 

    if logica.backspace:
        logica.acc_backspace += 1
        if logica.acc_backspace > 20:
            if self.entrata_attiva.puntatore != 0:
                self.entrata_attiva.text = self.entrata_attiva.text[:self.entrata_attiva.puntatore-1] + self.entrata_attiva.text[self.entrata_attiva.puntatore:]
            if self.entrata_attiva.puntatore > 0:
                self.entrata_attiva.puntatore -= 1
    else: 
        logica.acc_backspace = 0

    if logica.left:
        logica.acc_left += 1
        if logica.acc_left > 20:
            if logica.ctrl:
                self.entrata_attiva.puntatore = self.entrata_attiva.text[:self.entrata_attiva.puntatore].rstrip().rfind(ricercatore)+1
            elif self.entrata_attiva.puntatore > 0: self.entrata_attiva.puntatore -= 1
            self.entrata_attiva.dt_animazione = 0 
    else: 
        logica.acc_left = 0
    
    if logica.right:
        logica.acc_right += 1
        if logica.acc_right > 20:
            if logica.ctrl:
                tx = self.entrata_attiva.text
                # trovo l'indice di dove inizia la frase
                start = tx.find(tx[self.entrata_attiva.puntatore:].lstrip(), self.entrata_attiva.puntatore, len(tx))
                # se non la trovo mi blocco dove sono partito
                if start == -1: start = self.entrata_attiva.puntatore

                # se la trovo, cerco la parola successiva
                found = tx.find(ricercatore, start, len(tx))
                # se non la trovo guardo mi posizione nell'ultimo carattere diverso da uno spazio
                if found == -1: found = len(tx.rstrip())

                self.entrata_attiva.puntatore = found
                    
            elif self.entrata_attiva.puntatore < len(self.entrata_attiva.text): self.entrata_attiva.puntatore += 1
            self.entrata_attiva.dt_animazione = 0 
    else: 
        logica.acc_right = 0


def event_manage_plots(self, eventi: pygame.event, logica: Logica, plot = "Painter"):
    al_sc = self.scena["plots"]
    
    # Stato di tutti i tasti
    keys = pygame.key.get_pressed()


    # scena main UI
    for event in eventi:
        # MOUSE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                [tab.aggiorna_tab(event, logica) for index, tab in al_sc.tabs.items()]
                '-----------------------------------------------------------------------------------------------------'
                # Inizio sezione push events
                if al_sc.bottoni["usa_poly"].toggled:
                    al_sc.entrate["grado_inter"].visibile = True# al_sc.label_text["params"].text = "Interpolazione Polinomiale:\n- Accendi un grafico\n- Computa l'interpolazione\n- Abilita la visualizzazione dell'interpolazione"
                elif al_sc.bottoni["usa_gaussi"].toggled:
                    al_sc.entrate["grado_inter"].visibile = False# al_sc.label_text["params"].text = "Interpolazione Gaussiana:\n- Accendi un grafico\n- Computa l'interpolazione\n- Abilita la visualizzazione dell'interpolazione"
                elif al_sc.bottoni["usa_sigmoi"].toggled: 
                    al_sc.entrate["grado_inter"].visibile = False# al_sc.label_text["params"].text = "Interpolazione Sigmoide:\n- Accendi un grafico\n- Computa l'interpolazione\n- Abilita la visualizzazione dell'interpolazione"
                else:
                    al_sc.entrate["grado_inter"].visibile = False
                    al_sc.label_text["params"].text = "Seleziona un tipo di interpolazione.\nSuccessivamente schiaccia il bottone 'Compute Interpolation'"
                

                if al_sc.bottoni["comp_inter"].toggled:
                    al_sc.bottoni["comp_inter"].push()
                    if al_sc.bottoni["usa_poly"].toggled:
                        al_sc.label_text["params"].text = plot.check_latex(plot.linear_interpolation())
                    elif al_sc.bottoni["usa_gaussi"].toggled:
                        al_sc.label_text["params"].text = plot.check_latex(plot.customfoo_interpolation("gaussian"))
                    elif al_sc.bottoni["usa_sigmoi"].toggled:
                        al_sc.label_text["params"].text = plot.check_latex(plot.customfoo_interpolation("sigmoid"))

                if al_sc.bottoni["salva"].toggled:
                    al_sc.bottoni["salva"].push()
                    
                    path = Path.save(".")
                    
                    if path != "":
                        plot.disegna(logica, True)
                        self.salva_screenshot(path, plot.schermo)
                        al_sc.label_text["salvato_con_successo"].timer = 300

                        img = Image.open(path)
                        dpi = Mate.inp2int(al_sc.entrate["DPI"].text_invio, 300)
                        img.save(path, dpi=(dpi, dpi))


                # updates the active plot to the nearest to the click
                success = plot.nearest_coords(self, logica)

                if success:
                    al_sc.bottoni["tab_plt"].toggled = True
                    al_sc.bottoni["tab_settings"].toggled = False
                    al_sc.bottoni["tab_stats"].toggled = False
                    

                al_sc.tabs["ui_control"].abilita = False
                al_sc.tabs["ui_control"].renderizza = False
                al_sc.tabs["plot_control"].abilita = False
                al_sc.tabs["plot_control"].renderizza = False
                al_sc.tabs["stats_control"].abilita = False
                al_sc.tabs["stats_control"].renderizza = False

                if al_sc.bottoni["tab_settings"].toggled:
                    al_sc.tabs["ui_control"].abilita = True
                    al_sc.tabs["ui_control"].renderizza = True
                elif al_sc.bottoni["tab_plt"].toggled:
                    al_sc.tabs["plot_control"].abilita = True
                    al_sc.tabs["plot_control"].renderizza = True
                elif al_sc.bottoni["tab_stats"].toggled:
                    al_sc.tabs["stats_control"].abilita = True
                    al_sc.tabs["stats_control"].renderizza = True

                if al_sc.bottoni["normalizza"].toggled:
                    al_sc.bottoni["use_custom_borders"].toggled = False
                    
                al_sc.tabs["viewport_control"].abilita = not al_sc.bottoni["normalizza"].toggled
                al_sc.tabs["viewport_control"].renderizza = not al_sc.bottoni["normalizza"].toggled

                # Fine sezione push events
                '-----------------------------------------------------------------------------------------------------'

                # raccolta di tutti i testi già presenti nelle entrate
                test_entr_attiva: list[str] = [indice for indice, elemento in al_sc.entrate.items() if elemento.toggle]

                # logica per cui se ci sono entrate nella scena -> aggiorna il testo, indice e il testo generico modificabile
                if len(test_entr_attiva) > 0:
                    self.entrata_attiva = al_sc.entrate[test_entr_attiva[0]]
                else: self.entrata_attiva = None

            
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3: 
                plot.values_zoom(logica)

        # TASTIERA
        # controlli generici -> No inserimento
        
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_r:
                plot.reset_zoom(logica)
            
            if logica.tab:
                if not self.entrata_attiva is None:
                    possibili_entrate_attive = []
                    
                    for index, element in self.scena["plots"].tabs.items():
                        if element.renderizza and not element.entrate is None:
                            for entrata in element.entrate:
                                if entrata.visibile:
                                    possibili_entrate_attive.append(entrata)
                    
                    indice_attivo = possibili_entrate_attive.index(self.entrata_attiva)

                    if logica.shift:
                        if indice_attivo == 0: indice_attivo = len(possibili_entrate_attive)
                        nuova_chiave = possibili_entrate_attive[indice_attivo - 1].key    
                    else:
                        if indice_attivo == len(possibili_entrate_attive) - 1: indice_attivo = -1
                        nuova_chiave = possibili_entrate_attive[indice_attivo + 1].key
                        
                    self.entrata_attiva = al_sc.entrate[nuova_chiave]                    
                    
                    for index, i in al_sc.tabs.items(): 
                        if not i.entrate is None: [elemento.selezionato_ent(event, nuova_chiave) for elemento in i.entrate]


            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                al_sc.scrolls["grafici"].selezionato_scr(event, logica)

            if event.key == pygame.K_RETURN:
                try:
                    if al_sc.entrate["caricamento"].toggle:
                        plot.full_import_plot_data()
                        al_sc.scrolls["grafici"].aggiorna_externo("reload", logica)
                except FileNotFoundError as e:
                    print(e)

    # gestione collegamento ui - grafico        
    if logica.aggiorna_plot: plot.change_active_plot_UIBASED(self); logica.aggiorna_plot = False

    al_sc.entrate["color_plot"].color_text = Mate.hex2rgb(al_sc.entrate["color_plot"].text)
    al_sc.entrate["color_plot"].contorno = Mate.hex2rgb(al_sc.entrate["color_plot"].text)
    al_sc.entrate["color_plot"].color_text_toggled = Mate.hex2rgb(al_sc.entrate["color_plot"].text)
    al_sc.entrate["color_plot"].contorno_toggled = Mate.hex2rgb(al_sc.entrate["color_plot"].text)


def event_manage_plot_import(self, eventi: pygame.event, logica: Logica, analizzatore):
    
    al_sc = self.scena["plot_import"]


    # Stato di tutti i tasti
    keys = pygame.key.get_pressed()

    # scena main UI
    for event in eventi:
        # MOUSE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                [tab.aggiorna_tab(event, logica) for index, tab in al_sc.tabs.items()]

                '-----------------------------------------------------------------------------------------------------'
                # Inizio sezione push events
                if al_sc.bottoni["path_export"].toggled:
                    al_sc.bottoni["path_export"].push()

                    analizzatore.dump_data(Path.save(".", ".txt"))
                    al_sc.label_text["salvato_con_successo"].timer = 300
                    
                # Fine sezione push events
                '-----------------------------------------------------------------------------------------------------'

                # Inizio sezione events toggled:
                # if analizzatore.UI_calibrazione.toggled: 
                #    ...


                # raccolta di tutti i testi già presenti nelle entrate
                test_entr_attiva: list[str] = [indice for indice, elemento in al_sc.entrate.items() if elemento.toggle]

                # logica per cui se ci sono entrate nella scena -> aggiorna il testo, indice e il testo generico modificabile
                if len(test_entr_attiva) > 0:
                    self.entrata_attiva = al_sc.entrate[test_entr_attiva[0]]
                else: self.entrata_attiva = None

                if pygame.Rect(analizzatore.ancoraggio_x, analizzatore.ancoraggio_y, analizzatore.w, analizzatore.h).collidepoint(event.pos):
                    

                    if analizzatore.step_progresso_completamento == 1:

                        # controllo per aggiunta dati
                        if len(analizzatore.lista_coordinate_calibrazione) < 4:
                            analizzatore.lista_coordinate_calibrazione.append([logica.mouse_pos[0], logica.mouse_pos[1], len(analizzatore.lista_coordinate_calibrazione)])
                            analizzatore.punto_attivo = analizzatore.lista_coordinate_calibrazione[-1][2]
                    
                    elif analizzatore.step_progresso_completamento == 2:

                        # controllo per aggiunta dati
                        analizzatore.lista_coordinate_inserimento.append([logica.mouse_pos[0], logica.mouse_pos[1], len(analizzatore.lista_coordinate_inserimento)])
                        analizzatore.punto_attivo = analizzatore.lista_coordinate_inserimento[-1][2]


            if event.button == 3:
                # zona controllo punto attivo
                analizzatore.select_point(logica)

            if event.button == 4:
                logica.scroll_up += 10
            if event.button == 5:
                logica.scroll_down += 10

        # TASTIERA
        # controlli generici -> No inserimento
        
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP and not analizzatore.punto_attivo is None:
                analizzatore.move_point(x=0, y=-1)
            if event.key == pygame.K_DOWN and not analizzatore.punto_attivo is None:
                analizzatore.move_point(x=0, y=1)
            if event.key == pygame.K_LEFT and not analizzatore.punto_attivo is None:
                analizzatore.move_point(x=-1, y=0)
            if event.key == pygame.K_RIGHT and not analizzatore.punto_attivo is None:
                analizzatore.move_point(x=1, y=0)
                
            if event.key == pygame.K_RETURN:
                analizzatore.load_image()

            if event.key == pygame.K_DELETE:
                analizzatore.delete_point()

            if logica.tab:
                if not self.entrata_attiva is None:
                    possibili_entrate_attive = []
                    
                    for index, element in self.scena["plot_import"].tabs.items():
                        if element.renderizza and not element.entrate is None:
                            for entrata in element.entrate:
                                if entrata.visibile:
                                    possibili_entrate_attive.append(entrata)
                    
                    indice_attivo = possibili_entrate_attive.index(self.entrata_attiva)

                    if logica.shift:
                        if indice_attivo == 0: indice_attivo = len(possibili_entrate_attive)
                        nuova_chiave = possibili_entrate_attive[indice_attivo - 1].key    
                    else:
                        if indice_attivo == len(possibili_entrate_attive) - 1: indice_attivo = -1
                        nuova_chiave = possibili_entrate_attive[indice_attivo + 1].key
                        
                    self.entrata_attiva = al_sc.entrate[nuova_chiave]                    
                    
                    for index, i in al_sc.tabs.items(): 
                        if not i.entrate is None: [elemento.selezionato_ent(event, nuova_chiave) for elemento in i.entrate]


def event_manage_tracer(self, eventi: pygame.event, logica: Logica, tredi):
    
    al_sc = self.scena["tracer"]


    # Stato di tutti i tasti
    keys = pygame.key.get_pressed()

    # scena main UI
    for event in eventi:
        # MOUSE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                [tab.aggiorna_tab(event, logica) for index, tab in al_sc.tabs.items()]
                '-----------------------------------------------------------------------------------------------------'
                # Inizio sezione push events
                if al_sc.bottoni["reset"].toggled:
                    al_sc.bottoni["reset"].push()
                    
                    thread = threading.Thread(target=tredi.pathtracer.exit_c_renderer)
                    thread.start()
                
                
                if al_sc.bottoni["Crender"].toggled:
                    al_sc.bottoni["Crender"].push()
                    
                    tredi.pathtracer.utils.update_camera(tredi.scenes["debug"].camera)

                    tredi.build_raytracer()
                    thread = threading.Thread(target=tredi.pathtracer.launch_c_renderer, args=(tredi, ))
                    thread.start()
                    
                    thread = threading.Thread(target=tredi.pathtracer.launch_live_update, args=(logica, ))
                    thread.start()


                if al_sc.bottoni["add_sphere"].toggled:
                    al_sc.bottoni["add_sphere"].push()
                    tredi.scenes["debug"].add_sphere()
                    tredi.UI_calls_tracer.scrolls["oggetti"].elementi_attivi = [tredi.UI_calls_tracer.scrolls["oggetti"].all_on for _ in range(len(tredi.scenes["debug"].objects) + 1)] # il +1 è riferito ad un elemento in più: la camera
                    tredi.UI_calls_tracer.scrolls["oggetti"].indici = [i for i in range(len(tredi.scenes["debug"].objects) + 1)] # il +1 è riferito ad un elemento in più: la camera
                    tredi.UI_calls_tracer.scrolls["oggetti"].update_elements()
                    tredi.UI_calls_tracer.scrolls["oggetti"].aggiorna_externo("reload")

                if al_sc.bottoni["remove_sphere"].toggled:
                    al_sc.bottoni["remove_sphere"].push()
                    try:
                        tredi.scenes["debug"].remove_sphere(tredi.UI_calls_tracer.scrolls["oggetti"].first_item + tredi.UI_calls_tracer.scrolls["oggetti"].scroll_item_selected)
                        tredi.UI_calls_tracer.scrolls["oggetti"].elementi_attivi = [tredi.UI_calls_tracer.scrolls["oggetti"].all_on for _ in range(len(tredi.scenes["debug"].objects) + 1)] # il +1 è riferito ad un elemento in più: la camera
                        tredi.UI_calls_tracer.scrolls["oggetti"].indici = [i for i in range(len(tredi.scenes["debug"].objects) + 1)] # il +1 è riferito ad un elemento in più: la camera
                        tredi.UI_calls_tracer.scrolls["oggetti"].update_elements()
                        tredi.UI_calls_tracer.scrolls["oggetti"].aggiorna_externo("reload")
                    except:
                        print("Stai cercando di eliminare la camera")

                # Fine sezione push events
                '-----------------------------------------------------------------------------------------------------'

                # Inizio sezione events toggled:
                if al_sc.bottoni["albedo"].toggled: 
                    tredi.pathtracer.utils.mode = 0
                    if tredi.pathtracer.utils.old_mode != tredi.pathtracer.utils.mode:
                        tredi.pathtracer.utils.old_mode = tredi.pathtracer.utils.mode
                        tredi.pathtracer.utils.update_array(tredi.pathtracer.librerie.running) 
                
                if al_sc.bottoni["ao"].toggled: 
                    tredi.pathtracer.utils.mode = 1
                    if tredi.pathtracer.utils.old_mode != tredi.pathtracer.utils.mode:
                        tredi.pathtracer.utils.old_mode = tredi.pathtracer.utils.mode
                        tredi.pathtracer.utils.update_array(tredi.pathtracer.librerie.running)
                
                if al_sc.bottoni["bounces_tab"].toggled: 
                    tredi.pathtracer.utils.mode = 2
                    if tredi.pathtracer.utils.old_mode != tredi.pathtracer.utils.mode:
                        tredi.pathtracer.utils.old_mode = tredi.pathtracer.utils.mode
                        tredi.pathtracer.utils.update_array(tredi.pathtracer.librerie.running)


                # raccolta di tutti i testi già presenti nelle entrate
                test_entr_attiva: list[str] = [indice for indice, elemento in al_sc.entrate.items() if elemento.toggle]

                # logica per cui se ci sono entrate nella scena -> aggiorna il testo, indice e il testo generico modificabile
                if len(test_entr_attiva) > 0:
                    self.entrata_attiva = al_sc.entrate[test_entr_attiva[0]]
                else: self.entrata_attiva = None


                al_sc.tabs["scena_settings"].abilita = False
                al_sc.tabs["scena_settings"].renderizza = False
                al_sc.tabs["tracer_settings"].abilita = False
                al_sc.tabs["tracer_settings"].renderizza = False
                
                if al_sc.bottoni["tab_scene"].toggled:
                    al_sc.tabs["scena_settings"].abilita = True
                    al_sc.tabs["scena_settings"].renderizza = True
                elif al_sc.bottoni["tab_raytracer"].toggled:
                    al_sc.tabs["tracer_settings"].abilita = True
                    al_sc.tabs["tracer_settings"].renderizza = True
                
            if event.button == 4:
                logica.scroll_up += 10
            if event.button == 5:
                logica.scroll_down += 10

        # TASTIERA
        # controlli generici -> No inserimento
        
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.entrata_attiva = None
                for key, entrata in al_sc.entrate.items():
                    entrata.toggle = False
                al_sc.scrolls["oggetti"].selezionato_scr(event, logica)

            if logica.tab:
                if not self.entrata_attiva is None:
                    possibili_entrate_attive = []
                    
                    for index, element in self.scena["tracer"].tabs.items():
                        if element.renderizza and not element.entrate is None:
                            for entrata in element.entrate:
                                if entrata.visibile:
                                    possibili_entrate_attive.append(entrata)
                    
                    indice_attivo = possibili_entrate_attive.index(self.entrata_attiva)

                    if logica.shift:
                        if indice_attivo == 0: indice_attivo = len(possibili_entrate_attive)
                        nuova_chiave = possibili_entrate_attive[indice_attivo - 1].key    
                    else:
                        if indice_attivo == len(possibili_entrate_attive) - 1: indice_attivo = -1
                        nuova_chiave = possibili_entrate_attive[indice_attivo + 1].key
                        
                    self.entrata_attiva = al_sc.entrate[nuova_chiave]                    
                    
                    for index, i in al_sc.tabs.items(): 
                        if not i.entrate is None: [elemento.selezionato_ent(event, nuova_chiave) for elemento in i.entrate]

    # resoconto dello stato di tutti i bottoni e entrate
    tredi.change_UI_stuff(self, logica)
    

def event_manage_orbitals(self, eventi: pygame.event, logica: Logica, orbs):
    
    al_sc = self.scena["orbitals"]


    # Stato di tutti i tasti
    keys = pygame.key.get_pressed()

    # scena main UI
    for event in eventi:
        # MOUSE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                [tab.aggiorna_tab(event, logica) for index, tab in al_sc.tabs.items()]
                '-----------------------------------------------------------------------------------------------------'
                # Inizio sezione push events
                # if al_sc.bottoni["nome_bottone"].toggled:
                #     al_sc.bottoni["nome_bottone"].push()
                # Fine sezione push events
                '-----------------------------------------------------------------------------------------------------'

                # Inizio sezione events toggled:
                if al_sc.bottoni["3D"].toggled: 
                    orbs.mode = "3D"
                if al_sc.bottoni["2D"].toggled: 
                    orbs.mode = "2D"

                # raccolta di tutti i testi già presenti nelle entrate
                test_entr_attiva: list[str] = [indice for indice, elemento in al_sc.entrate.items() if elemento.toggle]

                # logica per cui se ci sono entrate nella scena -> aggiorna il testo, indice e il testo generico modificabile
                if len(test_entr_attiva) > 0:
                    self.entrata_attiva = al_sc.entrate[test_entr_attiva[0]]
                else: self.entrata_attiva = None

                al_sc.tabs["scena_settings"].abilita = False
                al_sc.tabs["scena_settings"].renderizza = False
                al_sc.tabs["tracer_settings"].abilita = False
                al_sc.tabs["tracer_settings"].renderizza = False
                
                if al_sc.bottoni["tab_graphics"].toggled:
                    al_sc.tabs["scena_settings"].abilita = True
                    al_sc.tabs["scena_settings"].renderizza = True

                    al_sc.schermo["helper"].toggled = True
                    al_sc.schermo["helper2"].toggled = True

                elif al_sc.bottoni["tab_settings"].toggled:
                    al_sc.tabs["tracer_settings"].abilita = True
                    al_sc.tabs["tracer_settings"].renderizza = True
                    
                    al_sc.schermo["helper"].toggled = False
                    al_sc.schermo["helper2"].toggled = False


            if event.button == 4:
                logica.scroll_up += 10
            if event.button == 5:
                logica.scroll_down += 10

        # TASTIERA
        # controlli generici -> No inserimento
        
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.entrata_attiva = None
                for key, entrata in al_sc.entrate.items():
                    entrata.toggle = False
                
            if logica.tab:
                if not self.entrata_attiva is None:
                    possibili_entrate_attive = []
                    
                    for index, element in self.scena["tracer"].tabs.items():
                        if element.renderizza and not element.entrate is None:
                            for entrata in element.entrate:
                                if entrata.visibile:
                                    possibili_entrate_attive.append(entrata)
                    
                    indice_attivo = possibili_entrate_attive.index(self.entrata_attiva)

                    if logica.shift:
                        if indice_attivo == 0: indice_attivo = len(possibili_entrate_attive)
                        nuova_chiave = possibili_entrate_attive[indice_attivo - 1].key    
                    else:
                        if indice_attivo == len(possibili_entrate_attive) - 1: indice_attivo = -1
                        nuova_chiave = possibili_entrate_attive[indice_attivo + 1].key
                        
                    self.entrata_attiva = al_sc.entrate[nuova_chiave]                    
                    
                    for index, i in al_sc.tabs.items(): 
                        if not i.entrate is None: [elemento.selezionato_ent(event, nuova_chiave) for elemento in i.entrate]


UI.event_manage_ui = event_manage_ui
UI.event_manage_plots = event_manage_plots
UI.event_manage_plot_import = event_manage_plot_import
UI.event_manage_tracer = event_manage_tracer
UI.event_manage_orbitals = event_manage_orbitals
