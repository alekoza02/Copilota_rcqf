import os, cProfile, configparser, yappi
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame.locals import *
import pygame

def main(config: configparser):
    
    # Zona inizializzazione UI
    from _modulo_UI import UI, Logica
    ui = UI(config)
    logica = Logica()
    logica.scena = int(config.get('Default', 'scena_iniziale'))
    
    # Zona inizializzazione plot
    from _modulo_plots import Painter
    main_plot = Painter()
    main_plot.link_ui(ui)
    main_plot.full_import_plot_data()

    # Zona inizializzazione plot import
    from _modulo_analizzatore import Analizzatore
    analizzatore = Analizzatore()
    analizzatore.link_ui(ui)
    
    # Zona inizializzazione tracer
    from _modulo_3D_grafica import TreDi
    tredi = TreDi()
    tredi.TEMPORARY_GENERATION()
    tredi.link_ui(ui)

    # Zona inizializzazione orbitali
    from _modulo_orbitali import Manager_orbs
    orbs = Manager_orbs(100000)
    orbs.link_ui(ui)

    while ui.running:

        ui.start_cycle(logica)

        eventi_in_corso = pygame.event.get()
        ui.event_manage_ui(eventi_in_corso, logica)

        match logica.scena:
            
            case 0: 
                ui.event_manage_plots(eventi_in_corso, logica, main_plot)
        
                main_plot.disegna(logica)
                [schermo.aggiorna_schermo() for key, schermo in ui.scena["plots"].schermo.items()]
                [tab.disegna_tab(logica) for index, tab in ui.scena["plots"].tabs.items()]
        
            case 1: 
                ui.event_manage_plot_import(eventi_in_corso, logica, analizzatore)
        
                analizzatore.disegna(logica)
                [schermo.aggiorna_schermo() for key, schermo in ui.scena["plot_import"].schermo.items()]
                [tab.disegna_tab(logica) for index, tab in ui.scena["plot_import"].tabs.items()]

            case 2: 
                ui.event_manage_tracer(eventi_in_corso, logica, tredi)
                
                tredi.disegna(logica, ui.scena["tracer"].data_widgets_tracer)
                [schermo.aggiorna_schermo() for key, schermo in ui.scena["tracer"].schermo.items()]
                [tab.disegna_tab(logica) for index, tab in ui.scena["tracer"].tabs.items()]
                
            case 3: 
                ui.event_manage_orbitals(eventi_in_corso, logica, orbs)
                
                orbs.disegna(logica)
                [schermo.aggiorna_schermo() for key, schermo in ui.scena["orbitals"].schermo.items()]
                [tab.disegna_tab(logica) for index, tab in ui.scena["orbitals"].tabs.items()]

        [tab.disegna_tab(logica) for index, tab in ui.scena["main"].tabs.items()]
                
        # controllo di uscita dal programma ed eventuale aggiornamento dello schermo
        ui.mouse_icon(logica)   # lanciato due volte per evitare flickering a bassi FPS
        ui.aggiornamento_e_uscita_check()
                        

if __name__ == "__main__":
    
    config = configparser.ConfigParser()
    config.read('./DATA/settings.ini')

    _compilatore = eval(config.get('Default', 'compila_c'))

    if _compilatore:
        import subprocess, ctypes
        # subprocess.run("gcc -fPIC -shared -o .\\LIBRERIE\\bin\\libreria.dll .\\LIBRERIE\\source\\libreria.c")
        tmp = ctypes.CDLL(".\\LIBRERIE\\bin\\libreria.dll")
        tmp.introduce()

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
        print("Profilatore salvato!")