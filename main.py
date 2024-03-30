import cProfile
from pygame.locals import *
import pygame
import configparser
    
def main(config: configparser):
    
    _tasto_navigazione = int(config.get('Default', 'tasto_navigazione'))
    _modello_or_cloud = config.get('Default', 'modello_or_cloud')
    _modello_default = config.get('Default', 'modello_default')
    _debug_mesh_grid = eval(config.get('Default', 'debug_mesh_grid'))
    _debug_mesh_axis = eval(config.get('Default', 'debug_mesh_axis'))

    from _modulo_UI import UI, Logica
    from _modulo_MATE import Mate
    
    ui = UI()
    logica = Logica()

    while ui.running:

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

        # CONTROLLO CARATTERI SPECIALI
        logica.ctrl = keys[pygame.K_LCTRL]
        logica.shift = keys[pygame.K_LSHIFT]
                

        # UI ----------------------------------------------------------------
        
        # disegno i labels
        [label.disegnami() for indice, label in ui.scena["main"].label_text.items()]
        
        # disegno la viewport
        ui.scena["main"].schermo["viewport"].disegnami()
        
        # calcolo parametri camera
        camera, logica = ui.scena["main"].schermo["viewport"].camera_setup(camera, logica)
        
        # set messaggi debug
        logica.messaggio_debug1 = f"FPS : {ui.current_fps:.2f}"
        logica.messaggio_debug2 = f"Numero di segmenti : /"
        logica.messaggio_debug3 = f"Altezza approssimativa (cm): /"
        logica.messaggio_debug4 = f"Cam pos : {camera.pos[0]:.1f}, {camera.pos[1]:.1f}, {camera.pos[2]:.1f}"
        logica.messaggio_debug5 = f"hehehehe"
        
        ui.aggiorna_messaggi_debug(logica)
        
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
