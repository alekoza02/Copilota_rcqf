import cProfile
from pygame.locals import *
import pygame
import configparser
    
def main(config: configparser):
    
    _tasto_navigazione = int(config.get('Default', 'tasto_navigazione'))

    from _modulo_UI import UI, Logica
    from _modulo_plots import Painter
    
    ui = UI()
    logica = Logica()
    
    # Zona inizializzazione plot
    main_plot = Painter()
    main_plot.link_ui(ui.scena["main"].schermo["viewport"])
    main_plot.full_import_plot_data()

    while ui.running:

        al_sc = ui.scena["main"]

        # impostazione inizio giro
        ui.clock.tick(ui.max_fps)
        ui.colora_bg()
        ui.mouse_icon(logica)

        logica.dt += 1
        logica.dragging_dx = 0
        logica.dragging_dy = 0
        logica.mouse_pos = pygame.mouse.get_pos()

        # BLOCCO GESTIONE EVENTI -----------------------------------------------------------------------------
        # raccolta eventi
        eventi_in_corso = pygame.event.get()

        # Stato di tutti i tasti
        keys = pygame.key.get_pressed()

        # CONTROLLO CARATTERI SPECIALI
        logica.ctrl = keys[pygame.K_LCTRL]
        logica.shift = keys[pygame.K_LSHIFT]
        logica.backspace = keys[pygame.K_BACKSPACE]
        logica.left = keys[pygame.K_LEFT]
        logica.right = keys[pygame.K_RIGHT]

        # scena main UI
        for event in eventi_in_corso:
            # MOUSE
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    
                    # gestisce eventi bottone e entrata schiacciata
                    [elemento.selezionato_bot(event) for indice, elemento in al_sc.bottoni.items()]
                    [elemento.selezionato_ent(event) for indice, elemento in al_sc.entrate.items()]
                    [scrolla.selezionato_scr(event, logica) for indice, scrolla in al_sc.scrolls.items()]
                    
                    # raccolta di tutti i testi già presenti nelle entrate
                    test_entr_attiva: list[str] = [indice for indice, elemento in al_sc.entrate.items() if elemento.toggle]

                    # logica per cui se ci sono entrate nella scena -> aggiorna il testo, indice e il testo generico modificabile
                    if len(test_entr_attiva) > 0:
                        al_sc.entrata_attiva = al_sc.entrate[test_entr_attiva[0]]

                if event.button == _tasto_navigazione:
                    logica.dragging = True
                    logica.dragging_end_pos = logica.mouse_pos
                if event.button == 4:
                    logica.scroll_up += 1
                if event.button == 5:
                    logica.scroll_down += 1

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == _tasto_navigazione: 
                    logica.dragging = False
                    logica.dragging_end_pos = logica.mouse_pos

            if event.type == pygame.MOUSEMOTION:
                if logica.dragging:
                    logica.dragging_start_pos = logica.dragging_end_pos
                    logica.dragging_end_pos = logica.mouse_pos
                    logica.dragging_dx = logica.dragging_end_pos[0] - logica.dragging_start_pos[0]
                    logica.dragging_dy = - logica.dragging_end_pos[1] + logica.dragging_start_pos[1] # sistema di riferimento invertito

            # TASTIERA
            # controlli generici -> No inserimento
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    ui.scena["main"].scrolls["grafici"].aggiorna_externo("up", logica)
                    
                if event.key == pygame.K_DOWN:
                    ui.scena["main"].scrolls["grafici"].aggiorna_externo("down", logica)


            # input -> tastiera con caratteri e backspace
            if al_sc.entrata_attiva != None:

                if event.type == pygame.TEXTINPUT:           
                    al_sc.entrata_attiva.text = al_sc.entrata_attiva.text[:al_sc.entrata_attiva.puntatore] + event.text + al_sc.entrata_attiva.text[al_sc.entrata_attiva.puntatore:]
                    al_sc.entrata_attiva.puntatore += len(event.text)
                    al_sc.entrata_attiva.dt_animazione = 0

                if event.type == pygame.KEYDOWN:
                    
                    tx = al_sc.entrata_attiva.text
                            
                    if event.key == pygame.K_BACKSPACE:
                        if logica.ctrl:

                            nuovo_puntatore = tx[:al_sc.entrata_attiva.puntatore].rstrip().rfind(" ")+1
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
                                al_sc.entrata_attiva.puntatore = tx[:al_sc.entrata_attiva.puntatore].rstrip().rfind(" ")+1
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
                                found = tx.find(" ", start, len(tx))
                                # se non la trovo guardo mi posizione nell'ultimo carattere diverso da uno spazio
                                if found == -1: found = len(tx.rstrip())

                                al_sc.entrata_attiva.puntatore = found
                                
                            else:
                                al_sc.entrata_attiva.puntatore += 1

                    al_sc.entrata_attiva.dt_animazione = 0 

        if logica.backspace:
            logica.acc_backspace += 1
            if logica.acc_backspace > 20:
                tx = al_sc.entrata_attiva.text
                nuovo_puntatore = tx[:al_sc.entrata_attiva.puntatore].rstrip().rfind(" ")+1
                text2eli = tx[nuovo_puntatore : al_sc.entrata_attiva.puntatore]
                al_sc.entrata_attiva.puntatore = nuovo_puntatore
                al_sc.entrata_attiva.text = tx.replace(text2eli, "")
        else: 
            logica.acc_backspace = 0

        if logica.left:
            logica.acc_left += 1
            if logica.acc_left > 20:
                if logica.ctrl:
                    al_sc.entrata_attiva.puntatore = al_sc.entrata_attiva.text[:al_sc.entrata_attiva.puntatore].rstrip().rfind(" ")+1
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
                    found = tx.find(" ", start, len(tx))
                    # se non la trovo guardo mi posizione nell'ultimo carattere diverso da uno spazio
                    if found == -1: found = len(tx.rstrip())

                    al_sc.entrata_attiva.puntatore = found
                     
                elif al_sc.entrata_attiva.puntatore < len(al_sc.entrata_attiva.text): al_sc.entrata_attiva.puntatore += 1
                al_sc.entrata_attiva.dt_animazione = 0 
        else: 
            logica.acc_right = 0

        # UI ----------------------------------------------------------------

        # aggiornamento generico dei nomi grafici nella scroll bar
        ui.scena["main"].scrolls["grafici"].elementi = [main_plot.plots[index].nome for index in range(len(main_plot.plots))]

        # disegno i labels / bottoni / entrate
        al_sc.disegnami(logica)

        # gestione collegamento ui - grafico        
        if logica.aggiorna_plot: main_plot.change_active_plot(ui); logica.aggiorna_plot = False
        
        # resoconto dello stato di tutti i bottoni e entrate
        al_sc.collect_data()

        # disegno il plot
        main_plot.disegna_plots(al_sc.data_widgets)
        main_plot.disegna_metadata(al_sc.data_widgets)
        main_plot.aggiorna_schermo()
        
        # UI ----------------------------------------------------------------

        # controllo di uscita dal programma ed eventuale aggiornamento dello schermo
        ui.mouse_icon(logica)   # lanciato due volte per evitare flickering a bassi FPS
        ui.aggiornamento_e_uscita_check()
        
if __name__ == "__main__":
    
    config = configparser.ConfigParser()
    config.read('./DATA/settings.ini')
    
    _profiler = eval(config.get('Default', 'profiler'))
    
    if _profiler:
        profiler = cProfile.Profile()
        profiler.enable()    

    import time
    start = time.time()
    main(config)
    print(f"Finito in {time.time() - start}")
    
    if _profiler:
        profiler.disable()
        profiler.dump_stats('PROFILATORE/_prof.prof')
