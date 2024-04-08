import cProfile
from pygame.locals import *
import pygame
import configparser
    
def main(config: configparser):
    
    _tasto_navigazione = int(config.get('Default', 'tasto_navigazione'))

    from _modulo_UI import UI, Logica, Entrata, Button
    from _modulo_plots import Painter
    
    ui = UI()
    logica = Logica()
    
    # Zona inizializzazione plot
    main_plot = Painter()
    main_plot.link_ui(ui.scena["main"].schermo["viewport"])
    main_plot.import_plot_data("DATA/data (1).txt")
    # main_plot.import_plot_data("DATA/data (2).txt")
    # main_plot.import_plot_data("DATA/data (3).txt")
    # main_plot.import_plot_data("DATA/data (4).txt")
    # main_plot.import_plot_data("DATA/data (5).txt")
    # main_plot.import_plot_data("DATA/data (6).txt")
    # main_plot.import_plot_data("DATA/data (7).txt")
    # main_plot.import_plot_data("DATA/data (8).txt")
    # main_plot.import_plot_data("DATA/data (9).txt")
    # main_plot.import_plot_data("DATA/data (10).txt")

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

        # scena main UI
        for event in eventi_in_corso:
            # MOUSE
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    
                    # gestisce eventi bottone e entrata schiacciata
                    [elemento.selezionato_bot(event) for indice, elemento in al_sc.bottoni.items()]
                    [elemento.selezionato_ent(event) for indice, elemento in al_sc.entrate.items()]
                    
                    # raccolta di tutti i testi già presenti nelle entrate
                    test_entr_attiva: list[Entrata, int] = [[elemento, indice] for indice, elemento in al_sc.entrate.items() if elemento.toggle][0]

                    # logica per cui se ci sono entrate nella scena -> aggiorna il testo, indice e il testo generico modificabile
                    if len(test_entr_attiva) > 0:
                        al_sc.entrata_attiva = test_entr_attiva[0]
                        al_sc.indice_entr_at = test_entr_attiva[1]
                        al_sc.puntatore_testo_attivo = al_sc.entrata_attiva.puntatore
                        al_sc.testo_aggiornato = al_sc.entrata_attiva.text
                    else:
                        al_sc.entrata_attiva = None
                    
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
            # input -> tastiera con caratteri e backspace
            if al_sc.entrata_attiva != None:

                if event.type == pygame.TEXTINPUT:            
                    al_sc.testo_aggiornato += event.text

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        al_sc.testo_aggiornato = al_sc.testo_aggiornato[:-1]

        # aggiornamento input
        if al_sc.entrata_attiva != None:
            al_sc.entrata_attiva.text = al_sc.testo_aggiornato

        # CONTROLLO CARATTERI SPECIALI
        logica.ctrl = keys[pygame.K_LCTRL]
        logica.shift = keys[pygame.K_LSHIFT]
                

        # UI ----------------------------------------------------------------
        
        # disegno i labels / bottoni / entrate
        al_sc.disegnami()

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
