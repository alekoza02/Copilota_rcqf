import numpy as np
from random import uniform
import time
from _modulo_wrapper_librerie import LibrerieC

class RenderChunck:
    def __init__(self, w, h) -> None:
        
        self.w: int = w 
        self.h: int = h 

        self.albedo = np.zeros((self.w, self.h, 3))
        self.amb_oc = np.zeros((self.w, self.h))
        self.bounces = np.zeros((self.w, self.h))

        self.samples_rendered = 0
        

class RayTracer_utils:
    def __init__(self) -> None:
        self.w: int
        self.h: int

        self.pixel_array: np.array[np.array[float]]
        self.C_pixel_array: np.array[np.array[float]]

        self.chunck: RenderChunck
        
        # modalità di visualizzazione:
        # 0 -> albedo   (x3 floats)
        # 0 -> AO       (1x float)
        # 0 -> test     (1x float)
        # old_mode evita di eseguire l'update troppo spesso
        self.mode = 0
        self.old_mode = 0

        self.stats = "Inizia la renderizzazione per le statistiche"
        self.start_time_str = "Non ancora avviato"
        self.start_time = 0.0
        self.end_time = 0.0
        


    def build(self, w, h, camera, factor_x=1, factor_y=1, samples=32, bounces=6, cores=9):

        # genera un nuovo raytracer con le nuove impostazioni

        self.w = int(w * factor_x)
        self.h = int(h * factor_y)

        self.samples = samples
        self.bounces = bounces
        self.cores = cores

        self.pixel_array = np.zeros((self.w, self.h, 3), dtype=np.int8)
        self.C_pixel_array = np.zeros((self.w, self.h, 5), dtype=float)

        self.camera = camera

        self.chunck = RenderChunck(self.w, self.h)


    def update_array(self, running: bool, reset: bool = False):

        try:
            min_test = np.min(self.chunck.bounces[self.chunck.bounces > 1])
            self.chunck.bounces[self.chunck.bounces <= 1] = min_test
        except ValueError:
            min_test = np.min(self.chunck.bounces)

        max_test = np.max(self.chunck.bounces - min_test)


        if reset == 0:
            match self.mode:
                
                case 0:
                    ris = self.chunck.albedo * 255 / self.samples
                    ris[ris > 255] = 255
                    self.pixel_array = ris
                
                case 1:
                    single_channel = np.clip(self.chunck.amb_oc / self.samples, 0, 1)
                    single_channel[single_channel == 0.0] = 1
                    single_channel = 1 - single_channel
                    multip_channel = np.repeat(single_channel[:,:,None], 3, axis=2) * 255
                    self.pixel_array = multip_channel
                
                case 2:
                    tmp = self.chunck.bounces - min_test
                    multip_channel = np.repeat(tmp[:,:,None], 3, axis=2) * 255 / max_test
                    self.pixel_array = multip_channel

        else:
            self.chunck.albedo[:, :, :] = 0
            self.pixel_array = self.chunck.albedo + 30

        self.analisi_tempi(running)


    def update_camera(self, camera):
        self.camera = camera


    def analisi_tempi(self, running: bool):
        try:
            if running:
                self.stats = f"Ora di inizio: {self.start_time_str}\nTrascorso: {time.time() - self.start_time:.2f} secondi\n"
                # Samples renderizzati in media: {average_samples:.2f}/{self.samples} ({100 * average_samples / self.samples:.1f}%)\nTempo stimato alla fine: {(self.samples - average_samples) * (time.time() - self.start_time) / (average_samples):.2f} secondi\nFPS medio: {average_samples / (time.time() - self.start_time):.2f}
            else:
                if self.start_time_str == "Non ancora avviato":
                    self.stats = f"Fai partire prima la renderizzazione"
                else:
                    average_samples = self.chunck.samples_rendered
                    self.stats = f"Ora di inizio: {self.start_time_str}\nTerminato in: {self.end_time - self.start_time:.2f} secondi\nFPS medio durante la renderizzazione: {average_samples / (self.end_time - self.start_time):.2f}"
        except ZeroDivisionError:
            self.stats = f"Troppo veloce per fare statistica, consideralo istant :D"


class Sphere:

    def __init__(self, pos, radius, materiale, indice) -> None:
        self.pos = pos 
        self.radius = radius
        self.radius_sqr = radius ** 2
        self.materiale = materiale
        self.indice = indice

        self.BB = np.array([self.pos - self.radius, self.pos + self.radius])


    @staticmethod
    def convert_wireframe2tracer(oggetti):
        return [Sphere(oggetto.pos, oggetto.sx / 2, oggetto.materiale, indice) for indice, oggetto in enumerate(oggetti)]


class Modello_Raytracer:
    
    def __init__(self, verteces, links, materiale, indice) -> None:
        self.verteces = verteces
        self.links = links
        self.materiale = materiale
        self.indice = indice

        self.triangoli = self.verteces[self.links]

    
    @staticmethod
    def convert_wireframe2tracer(oggetti):
        return [Modello_Raytracer(oggetto.transformed_vertices[:, :3], oggetto.links, oggetto.materiale, indice) for indice, oggetto in enumerate(oggetti)]



class RayTracer:
    def __init__(self) -> None:
        
        self.librerie = LibrerieC()
        self.utils = RayTracer_utils()


    def launch_c_renderer(self, tredi):
        
        x, y, _ = self.utils.pixel_array.shape

        # creo le sfere da passare al motore in C
        spheres = []
        for oggetto, stato in zip(tredi.scenes["debug"].objects, tredi.UI_calls_tracer.scrolls["oggetti"].elementi_attivi):
            if stato: spheres.append(oggetto)
        spheres = Sphere.convert_wireframe2tracer(spheres)

        # creo i modelli da passare al motore in C
        modello = Modello_Raytracer.convert_wireframe2tracer([tredi.scenes["debug"].dev_modello])


        # avvio il motore (statistiche)
        self.utils.start_time_str = time.strftime('%H:%M:%S', time.localtime())
        self.utils.start_time = time.time()

        self.librerie.C_init_canvas(x, y)
        self.librerie.C_reset_canvas(x, y)

        self.utils.stats = f"Ora di inizio: {self.utils.start_time_str}"
        

        self.utils.stats = f"Ora di inizio: {self.utils.start_time_str}"
        # \nTrascorso: {time.time() - self.utils.start_time:.2f} secondi\nSamples renderizzati in media: {sample_eta}/{self.utils.samples} ({100 * sample_eta / self.utils.samples:.1f}%)\nTempo stimato alla fine: {(self.utils.samples - sample_eta) * (time.time() - self.utils.start_time) / (sample_eta):.2f} secondi\nFPS medio: {sample_eta / (time.time() - self.utils.start_time + 1e-6):.2f}
        
        settings = [self.utils.samples, self.utils.bounces, self.utils.cores]

        self.utils.C_pixel_array = self.librerie.c_renderer(x, y, spheres, modello, self.utils.camera, settings)

        self.utils.chunck.samples_rendered = self.utils.samples

        self.librerie.C_exit()


    def launch_live_update(self, logica):

        self.fine_live_update = False
        
        while not self.librerie.uscito_con_successo:
            
            try:

                # TODO: modificabile frequenza di aggiornamento
                if logica.trascorso % 1 == 0:

                    self.utils.C_pixel_array = self.librerie.extract_C_array(self.utils.w, self.utils.h)

                    # aggiorno canvas
                    self.utils.chunck.albedo = self.utils.C_pixel_array[:,:,0:3]
                    self.utils.chunck.amb_oc = self.utils.C_pixel_array[:,:,3]
                    self.utils.chunck.bounces = self.utils.C_pixel_array[:,:,4]

                    self.utils.update_array(self.librerie.running, self.fine_live_update)

            except:
                ...

        while self.librerie.running:
            
            try:

                # TODO: modificabile frequenza di aggiornamento
                if logica.trascorso % 1 == 0:

                    self.utils.C_pixel_array = self.librerie.extract_C_array(self.utils.w, self.utils.h)

                    # aggiorno canvas
                    self.utils.chunck.albedo = self.utils.C_pixel_array[:,:,0:3]
                    self.utils.chunck.amb_oc = self.utils.C_pixel_array[:,:,3]
                    self.utils.chunck.bounces = self.utils.C_pixel_array[:,:,4]

                    self.utils.update_array(self.librerie.running, self.fine_live_update)

            except:
                ...

        self.fine_live_update = True
        self.utils.end_time = time.time()
        self.librerie.C_free_canvas()

        # output statistiche
        self.utils.stats = f"Ora di inizio: {self.utils.start_time_str}\nTerminato in: {self.utils.end_time - self.utils.start_time:.2f} secondi\nFPS medio durante la renderizzazione: {self.utils.samples / (self.utils.end_time - self.utils.start_time):.2f}"


    def exit_c_renderer(self):
        
        self.librerie.C_exit()

        # resetta i canali di output
        self.utils.chunck.albedo[:, :, :] = 0
        self.utils.chunck.amb_oc[:, :] = 0
        self.utils.chunck.bounces[:, :] = 0

        while not self.fine_live_update:
            ... 

        self.utils.update_array(self.librerie.running, self.fine_live_update)

        # resetta le statistiche
        self.utils.chunck.samples_rendered = 0

        # resetta la frase di aiuto
        self.utils.stats = f"Fai partire una renderizzazione!"

