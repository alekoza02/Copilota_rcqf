import os, cProfile, configparser
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame.locals import *
import pygame
    
def main(config: configparser):
    
    from _modulo_UI import UI, Logica
    from _modulo_plots import Painter
    
    ui = UI(config)
    logica = Logica()
    
    # Zona inizializzazione plot
    main_plot = Painter()
    main_plot.link_ui(ui.scena["main"].schermo["viewport"])
    main_plot.full_import_plot_data(ui.scena["main"])

    # alias
    al_sc = ui.scena["main"]
    
    while ui.running:

        ui.start_cycle(logica)

        eventi_in_corso = pygame.event.get()
        ui.event_manage_ui(eventi_in_corso, logica)
        ui.event_manage_plots(eventi_in_corso, logica, main_plot)

        # UI ----------------------------------------------------------------

        # disegno i labels / bottoni / entrate
        [tab.disegna_tab(logica) for index, tab in ui.scena["main"].tabs.items()]

        ui.scena["main"].bottoni["normalizza"].visibile = True if len([plot for plot in main_plot.plots if plot.acceso]) == 2 else False

        # disegno il plot
        main_plot.disegna(logica, al_sc.data_widgets)
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
    print(f"Finito in {time.time() - start:.1f}s")
    
    if _profiler:
        profiler.disable()
        profiler.dump_stats('PROFILATORE/_prof.prof')
