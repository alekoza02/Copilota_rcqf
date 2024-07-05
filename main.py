import os, cProfile, configparser, yappi
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame.locals import *
import pygame

def main(config: configparser):
    
    from _modulo_UI import UI, Logica
    from _modulo_plots import Painter
    from _modulo_3D_grafica import TreDi

    ui = UI(config)
    logica = Logica()

    logica.scena = int(config.get('Default', 'scena_iniziale'))
    
    # Zona inizializzazione plot
    main_plot = Painter()
    main_plot.link_ui(ui)
    main_plot.full_import_plot_data(ui.scena["plots"])

    # Zone inizializzazione tracer
    tredi = TreDi()
    tredi.TEMPORARY_GENERATION()
    tredi.link_ui(ui)
    
    while ui.running:

        ui.start_cycle(logica)

        eventi_in_corso = pygame.event.get()

        ui.event_manage_ui(eventi_in_corso, logica)
        [tab.disegna_tab(logica) for index, tab in ui.scena["main"].tabs.items()]

        match logica.scena:
            
            case 0: 
                ui.event_manage_plots(eventi_in_corso, logica, main_plot)
                [tab.disegna_tab(logica) for index, tab in ui.scena["plots"].tabs.items()]
        
                ui.scena["plots"].bottoni["normalizza"].visibile = True if len([plot for plot in main_plot.plots if plot.acceso]) == 2 else False
            
                main_plot.disegna(logica, ui.scena["plots"].data_widgets_plots)
                ui.scena["plots"].schermo["viewport"].aggiorna_schermo()
        
            case 1: 
                ui.event_manage_tracer(eventi_in_corso, logica, tredi)
                [tab.disegna_tab(logica) for index, tab in ui.scena["tracer"].tabs.items()]
                
                tredi.disegna(logica, ui.scena["tracer"].data_widgets_tracer)
                ui.scena["tracer"].schermo["viewport"].aggiorna_schermo()
                
        # controllo di uscita dal programma ed eventuale aggiornamento dello schermo
        ui.mouse_icon(logica)   # lanciato due volte per evitare flickering a bassi FPS
        ui.aggiornamento_e_uscita_check()
                        

if __name__ == "__main__":
    
    config = configparser.ConfigParser()
    config.read('./DATA/settings.ini')
    
    _profiler = eval(config.get('Default', 'profiler'))
    
    if _profiler:
        # profiler = cProfile.Profile()
        # profiler.enable()    
        yappi.start()

    import time
    start = time.time()
    main(config)
    print(f"Finito in {time.time() - start:.1f}s")
    
    if _profiler:
        # profiler.disable()
        # profiler.dump_stats('PROFILATORE/_prof.prof')
        yappi.stop()
        func_stats = yappi.get_func_stats()
        func_stats.save('PROFILATORE/_prof_yappi.prof', type='pstat')