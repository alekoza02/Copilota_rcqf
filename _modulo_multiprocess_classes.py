import numpy as np
import multiprocessing
from _modulo_MATE import AcceleratedFoo
from random import uniform
from time import perf_counter_ns, perf_counter
from memory_profiler import profile
import time

class Settings:
    def __init__(self, samples, bounces, sample_update, cores, res) -> None:
        self.samples = samples
        self.bounces = bounces
        self.sample_packet = sample_update
        self.cores = cores
        self.resolution_chunck = (res, res)


class Record:
    def __init__(self) -> None:
        self.test_eseguito: bool = False
        self.colpito: bool = False
        self.distanza: float = np.inf
        self.indice_oggetti_prox: int
        self.materiale = None
        self.punto_colpito: np.array[float] = np.array([np.inf, np.inf, np.inf])
        self.norma_colpito: np.array[float]
        self.norma_rifrazione: np.array[float]
        self.front_face: bool


class Raggio:
    def __init__(self, pos, dir) -> None:
        self.pos = pos
        self.dir = dir
        self.inv_dir = 1 / dir

        self.AO_redo = False
        self.AO_ray = np.array([0.,0.,0.])


    def check_front_face(self, record: Record) -> Record:
        if np.dot(self.dir, record.norma_colpito) > 0.0:
            record.front_face = False
            record.norma_rifrazione = - record.norma_colpito
        else:
            record.front_face = True
            record.norma_rifrazione = record.norma_colpito

        return record


    def calc_bounce(self, record: Record):

        self.AO_redo = False

        # calcolo rimbalzo random (roughness - AO) 
        # NOTE! Il raggio roughness_ray non ha test eseguiti in merito alla concordanza di segno con la normale, questo test viene eseguito solo per AO_ray
        # Usa AO_ray per test che richiedono il raggio uscente (es. metallo / roughness)
        # Usa roughness_ray per test che non richiedono un raggio specifico (es. vetro)

        roughness_ray = np.array([uniform(-1, 1) for i in range(3)])
        roughness_ray /= np.linalg.norm(roughness_ray)

        if np.dot(record.norma_colpito, roughness_ray) < 0:
            self.AO_ray = - roughness_ray
        else:
            self.AO_ray = roughness_ray
        
        # BLOCCO MATERIALE DIFFUSE / SPECULAR / GLOSS
        
        if not record.materiale.glass:

            # calcolo rimbalzo speculare
            specular_ray = self.dir - record.norma_colpito * np.dot(self.dir, record.norma_colpito) * 2.0;

            # test specularità (1 True, 0 False)
            is_specular = record.materiale.glossiness >= uniform(0, 1)

            # combinazione roughness / metal / glossiness
            dir = Raggio.lerp(self.AO_ray, specular_ray, (1 - record.materiale.roughness) * is_specular)
            
            if is_specular: self.AO_redo = True


        # BLOCCO MATERIALE VETRO

        elif record.materiale.glass:

            # ricordo di ricalcolare l'AO
            self.AO_redo = True
            
            # calcolo della direzione rifratta:
            # viene eseguito il check per raggio entrante ed uscente dall'oggetto. 
            # nel caso di raggio uscente viene testato inoltre l'angolo limite.
            # alla fine viene calcolata la probabilità di riflettanza dovuta alla legge di Brew.

            # controllo raggio entrante / uscente basato sulla faccia colpita (interna / esterna) 
            record = self.check_front_face(record)

            # calcolo del rapporto degli indici di rifrazione dei mezzi in base al raggio entrante / uscente (1.0 = aria)
            ratio_rifrazione = 1 / record.materiale.IOR if record.front_face else record.materiale.IOR

            # calcolo componenti trigonometriche
            coseno = np.dot(- self.dir, record.norma_rifrazione)
            seno = (1 - coseno ** 2) ** 0.5            
            
            # calcolo probabilità di riflettanza di Brew usando approx. di Schlick
            schlick_approx = (1 - record.materiale.IOR) / (1 + record.materiale.IOR)
            schlick_approx = schlick_approx * schlick_approx 
            
            # condizioni di rifrazione : 1 = riflettanza, 2 = angolo limite
            cannot_refract1 = schlick_approx + (1 - schlick_approx) * ((1 - coseno) ** 5) > uniform(0, 1) 
            cannot_refract2 = ratio_rifrazione * seno > 1

            if cannot_refract1 or cannot_refract2:

                # non può rifrarre -> riflessione basata sulla normale interna
                dir = self.dir - record.norma_rifrazione * np.dot(self.dir, record.norma_rifrazione) * 2

            else:        
                
                # può rifrarre -> calcolo della nuova direzione con componente parallela e perpendicolare alla normale
                r_out_perp = (self.dir + record.norma_rifrazione * coseno) * ratio_rifrazione
                r_out_para = - record.norma_rifrazione * (abs(1 - np.linalg.norm(r_out_perp) ** 2)) ** .5
                dir = r_out_para + r_out_perp

            # combinazione diffusa / vetro
            dir = self.lerp(dir, roughness_ray, record.materiale.roughness)


        # riempimento record
        self.pos = record.punto_colpito
        self.dir = dir
        self.inv_dir = 1 / dir


    @staticmethod
    def lerp(v1, v2, perc):
        """
        - perc = 0 -> v1
        - perc = 1 -> v2
        """
        return (1 - perc) * v1 + perc * v2



class RenderChunck:
    def __init__(self, ori_w, ori_h, w, h, x, y, index) -> None:
        
        self.ori_w: int = ori_w
        self.ori_h: int = ori_h

        self.w: int = w 
        self.h: int = h 
        self.x: int = x 
        self.y: int = y
        self.index: int = index

        self.albedo = np.zeros((self.w, self.h, 3))
        self.normal = np.zeros((self.w, self.h, 3))
        self.indici = np.zeros((self.w, self.h, 3))
        self.tempi = np.zeros((self.w, self.h))
        self.amb_oc = np.zeros((self.w, self.h))
        self.bounces = np.zeros((self.w, self.h))

        self.samples_rendered = 0
        self.reset = False


class RayTracer:
    def __init__(self) -> None:
        self.w: int
        self.h: int

        self.pixel_array: np.array[np.array[float]]
        self.C_pixel_array: np.array[np.array[float]]

        self.chuncks: list[RenderChunck]
        self.mode = 0
        self.old_mode = 0

        self.stats = "Inizia la renderizzazione per le statistiche"
        self.start_time_str = "Non ancora avviato"
        self.start_time = 0.0
        self.end_time = 0.0
        self.tempo_avvio = 7

        self.running = False


    def build(self, w, h, camera, factor_x=1, factor_y=1, samples=32, bounces=6, sample_update=4, cores=9, res=3):

        self.w = int(w * factor_x)
        self.h = int(h * factor_y)

        self.settings = Settings(1 + samples, bounces, sample_update, cores, res)

        self.pixel_array = np.zeros((self.w, self.h, 3), dtype=np.int8)
        self.C_pixel_array = np.zeros((self.w, self.h, 12), dtype=float)
        self.chuncks = []

        self.camera = camera

        self.res_x, self.res_y = self.settings.resolution_chunck

        for x in range(self.res_x):
            for y in range(self.res_y):

                dim_x = self.w // self.res_x
                dim_y = self.h // self.res_y
                
                rim_x = self.w % self.res_x
                rim_y = self.h % self.res_y
                
                width_x = self.w - dim_x * (self.res_x - 1) if x == (self.res_x - 1) and rim_x > 0 else dim_x 
                width_y = self.h - dim_y * (self.res_y - 1) if y == (self.res_y - 1) and rim_y > 0 else dim_y 

                anchor_x = self.w - width_x if x == (self.res_x - 1) else dim_x * x
                anchor_y = self.h - width_y if y == (self.res_y - 1) else dim_y * y

                self.chuncks.append(RenderChunck(self.w, self.h, width_x, width_y, anchor_x, anchor_y, len(self.chuncks)))

        
    def update_chunck(self, chunck: RenderChunck):
        self.chuncks[chunck.index] = chunck
        self.update_array()


    def update_array(self):

        max_time = 0
        max_test = 0
        for chunck in self.chuncks:
            max_time = np.maximum(max_time, np.max(chunck.tempi))
            max_test = np.maximum(max_test, np.max(chunck.bounces))

        for chunck in self.chuncks:
            if chunck.samples_rendered > 0:
                match self.mode:
                    case 0:
                        self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = 255 * chunck.indici / chunck.samples_rendered
                    case 1:
                        self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = self.tone_mapping(chunck)
                    case 2:
                        self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = 255 * chunck.normal / chunck.samples_rendered
                    case 3:
                        single_channel = np.clip(chunck.amb_oc / chunck.samples_rendered, 0, 1)
                        single_channel[single_channel == 0.0] = 1
                        single_channel = 1 - single_channel
                        multip_channel = np.repeat(single_channel[:,:,None], 3, axis=2) * 255
                        self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = multip_channel
                    case 4:
                        single_channel = np.clip(chunck.tempi / max_time, 0, 1)
                        multip_channel = np.repeat(single_channel[:,:,None], 3, axis=2) * 255
                        self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = multip_channel
                    case 5:
                        multip_channel = np.repeat(chunck.bounces[:,:,None], 3, axis=2) * 255 / max_test
                        self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = multip_channel

            if chunck.reset:
                chunck.reset = False
                self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = chunck.albedo + 30

        self.analisi_tempi()


    def update_camera(self, camera):
        self.camera = camera


    def tone_mapping(self, chunck):
        ris = np.sqrt(chunck.albedo / chunck.samples_rendered) * 255
        ris[ris > 255] = 255
        return ris


    def analisi_tempi(self):
        if self.running:
            average_samples = 0
            for index, chunck in enumerate(self.chuncks):
                average_samples += chunck.samples_rendered

            average_samples /= len(self.chuncks)
            if average_samples == 0:
                self.stats = f"Ora di inizio: {self.start_time_str}"
            else:
                self.stats = f"Ora di inizio: {self.start_time_str}\nTrascorso: {time.time() - self.start_time:.2f} secondi\nSamples renderizzati in media: {average_samples:.2f}/{self.settings.samples} ({100 * average_samples / self.settings.samples:.1f}%)\nTempo stimato alla fine: {(self.settings.samples - average_samples) * (time.time() - self.start_time) / (average_samples):.2f} secondi"
        else:
            if self.start_time_str == "Non ancora avviato":
                self.stats = f"Fai partire prima la renderizzazione"
            else:
                self.stats = f"Ora di inizio: {self.start_time_str}\nTerminato in: {self.end_time - self.start_time:.2f} secondi"


class Sphere:

    def __init__(self, pos, radius, materiale, indice) -> None:
        self.pos = pos 
        self.radius = radius
        self.radius_sqr = radius ** 2
        self.materiale = materiale
        self.indice = indice

        self.BB = np.array([self.pos - self.radius, self.pos + self.radius])


    def collision_BB_sphere(self, ray: Raggio):
        return AcceleratedFoo.test(self.BB, ray.pos, ray.dir)


    def collisione_sphere(self, ray, record: Record):
            
        record.test_eseguito = False

        if self.collision_BB_sphere(ray):

            record.test_eseguito = True

            oc = ray.pos - self.pos;
            
            b = np.dot(oc, ray.dir) * 2.0;
            c = np.dot(oc, oc) - self.radius_sqr;

            discriminante = b ** 2 - 4.0 * c;
            
            if discriminante >= 0.0:
                sqrt_discr = discriminante ** 0.5
                
                delta_min = (- b - sqrt_discr) / 2.0;
                delta_max = (- b + sqrt_discr) / 2.0;
                
                if delta_max > 0.001:
                    t = delta_max
                    if delta_min > 0.001 and delta_min < delta_max:
                        t = delta_min

                    if t < record.distanza:
                        record.colpito = True;
                        record.distanza = t;
                        record.indice_oggetti_prox = self.indice;
                        record.punto_colpito = self.punto_colpito(ray, record.distanza);
                        record.norma_colpito = self.normale_colpita(record.punto_colpito);
                        record.materiale = self.materiale;
            
        return record


    def punto_colpito(self, ray: Raggio, t):
        return ray.pos + (ray.dir * t)


    def normale_colpita(self, punto_colpito):
        v = punto_colpito - self.pos
        v /= np.linalg.norm(v)
        return v
    

    @staticmethod
    def convert_wireframe2tracer(oggetti):
        return [Sphere(oggetto.pos, oggetto.sx / 2, oggetto.materiale, indice) for indice, oggetto in enumerate(oggetti)]


class RenderingModes:
    @staticmethod
    def direction_bulk(wo, ho, x, y, w, h, camera):
        def direzione(i, j) -> float:
            # return camera.dir[:3] * (1 / np.tan(camera.fov / 2)) + (2 * (i / wo) - 1) * camera.rig[:3] + (2 * (j / ho) - 1) * (- camera.ups[:3]) / (wo/ho)
            return camera.dir[:3] * (1 / np.tan(camera.fov / 2)) + (2 * ((i + np.random.random()) / wo) - 1) * camera.rig[:3] + (2 * ((j + np.random.random()) / ho) - 1) * (- camera.ups[:3]) / (wo/ho)
               
        # vectorizes the function
        vectorized_find = np.vectorize(direzione, signature='(),()->(n)')

        indices_i, indices_j = np.indices((w, h))
        indices_i += x
        indices_j += y
        
        ris = vectorized_find(indices_i, indices_j)
        norma = np.linalg.norm(ris, axis=2)
        ris /= norma[:,:,None]
        return ris
    

    @staticmethod
    def test_AO(ray, list_object, chunck, x, y):
        # temporary switch
        temp_memo = ray.dir
        ray.dir = ray.AO_ray    
        ao_record = Record()

        for oggetto in list_object:
            ao_record = oggetto.collisione_sphere(ray, ao_record)
        chunck.amb_oc[x, y] += 1 / (np.linalg.norm(ao_record.punto_colpito - ray.pos) + 1)
        
        # re-switch
        ray.dir = temp_memo

    @staticmethod
    def test_spheres(args: tuple[RenderChunck, any]) -> RenderChunck:
        try:
            chunck: RenderChunck = args[0]
            camera = args[1]
            list_object = args[2]
            settings: Settings = args[3]

            direzioni = RenderingModes.direction_bulk(chunck.ori_w, chunck.ori_h, chunck.x, chunck.y, chunck.w, chunck.h, camera)

            for sample in range(settings.sample_packet):
                for x in range(chunck.w):
                    for y in range(chunck.h):

                        test_count = 0

                        start = perf_counter()

                        ray = Raggio(camera.pos[:3], direzioni[x, y])
                        ray_incoming_light = np.array([0.,0.,0.])
                        ray_color = np.array([1.,1.,1.])

                        for bounce in range(settings.bounces):

                            # inizializzazione record
                            pixel_analize = Record()
                    
                            # collisione con sfera
                            for oggetto in list_object:
                                pixel_analize = oggetto.collisione_sphere(ray, pixel_analize)
                                test_count += pixel_analize.test_eseguito

                            # AO save
                            if bounce == 1:
                                RenderingModes.test_AO(ray, list_object, chunck, x, y)


                            if pixel_analize.colpito:
                                # first save
                                if bounce == 0: 
                                    chunck.normal[x, y, :] += (pixel_analize.norma_colpito + 1) / 2
                                    chunck.indici[x, y, :] += pixel_analize.materiale.colore * np.dot(pixel_analize.norma_colpito, - ray.dir)
                                    
                                # nuovo giro settings
                                ray.calc_bounce(pixel_analize)

                                # materiale
                                materiale = pixel_analize.materiale
                                luce_emessa = materiale.emissione_colore * materiale.emissione_forza
                                ray_incoming_light = ray_incoming_light + luce_emessa * ray_color
                                ray_color = ray_color * materiale.colore

                            elif bounce > 1:
                                break
                            

                        chunck.bounces[x, y] += test_count
                        chunck.albedo[x, y, :] += ray_incoming_light
          
                        finish = perf_counter()
                        if not (x == 0 and y == 0):
                            chunck.tempi[x, y] += (finish - start)
            

                chunck.samples_rendered += 1


            return chunck
        
        except Exception as e:
            print(f"Attenzione, AleDebug in azione:\n{e}") 
            return chunck

    
    @staticmethod
    def reset_background(chunck: RenderChunck) -> RenderChunck:
        chunck.albedo[:, :, :] = 0
        chunck.normal[:, :, :] = 0
        chunck.indici[:, :, :] = 0
        chunck.tempi[:, :] = 0
        chunck.amb_oc[:, :] = 0
        chunck.bounces[:, :] = 0

        chunck.samples_rendered = 0
        chunck.reset = True

        return chunck


class AvvioMultiProcess:
    def __init__(self) -> None:
        self.pool = None
        self.stahp = False
        self.c_stopped = True


    def try_fast_kill(self):
        if not self.pool is None:
            self.pool.terminate()


    def launch_c_renderer(self, tredi, librerie):
        self.stahp = True
        self.try_fast_kill()
        tredi.pathtracer.running = False
        
        self.stahp = False
        x, y, _ = tredi.pathtracer.pixel_array.shape
        objects = []
        for oggetto, stato in zip(tredi.scenes["debug"].objects, tredi.UI_calls_tracer.scrolls["oggetti"].elementi_attivi):
            if stato: objects.append(oggetto)
        objects = Sphere.convert_wireframe2tracer(objects)

        tredi.pathtracer.running = True
        tredi.pathtracer.start_time_str = time.strftime('%H:%M:%S', time.localtime())
        tredi.pathtracer.start_time = time.time()

        tredi.pathtracer.stats = f"Ora di inizio: {tredi.pathtracer.start_time_str}"
        
        self.c_stopped = False

        if not self.stahp:

            # correzione passando da python a C (python esegue un passaggio in più come preview)
            tredi.pathtracer.settings.samples -= 1

            for sample_group in range(1, (tredi.pathtracer.settings.samples // tredi.pathtracer.settings.sample_packet) + 1):
                
                sample_update = sample_group * tredi.pathtracer.settings.sample_packet

                sample_eta = (sample_group - 1) * tredi.pathtracer.settings.sample_packet
                if sample_eta == 0: sample_eta = 1

                tredi.pathtracer.stats = f"Ora di inizio: {tredi.pathtracer.start_time_str}\nTrascorso: {time.time() - tredi.pathtracer.start_time:.2f} secondi\nSamples renderizzati in media: {sample_eta}/{tredi.pathtracer.settings.samples} ({100 * sample_eta / tredi.pathtracer.settings.samples:.1f}%)\nTempo stimato alla fine: {(tredi.pathtracer.settings.samples - sample_eta) * (time.time() - tredi.pathtracer.start_time) / (sample_eta):.2f} secondi"
                
                if sample_update == 1: sample_update = 0
                
                tmp = librerie.c_renderer(x, y, objects, tredi.pathtracer.camera, tredi.pathtracer.settings)
                tredi.pathtracer.C_pixel_array = tredi.pathtracer.C_pixel_array + tmp
                
                tredi.pathtracer.chuncks[0].samples_rendered = sample_group * tredi.pathtracer.settings.sample_packet

                tredi.pathtracer.chuncks[0].albedo = tredi.pathtracer.C_pixel_array[:,:,0:3]
                tredi.pathtracer.chuncks[0].indici = tredi.pathtracer.C_pixel_array[:,:,3:6]
                tredi.pathtracer.chuncks[0].normal = tredi.pathtracer.C_pixel_array[:,:,6:9]
                tredi.pathtracer.chuncks[0].tempi = tredi.pathtracer.C_pixel_array[:,:,9]
                tredi.pathtracer.chuncks[0].amb_oc = tredi.pathtracer.C_pixel_array[:,:,10]
                tredi.pathtracer.chuncks[0].bounces = tredi.pathtracer.C_pixel_array[:,:,11]

                tredi.pathtracer.update_array()

                if self.stahp:
                    self.c_stopped = True
                    return

        # correzione passando da C a python (python esegue un passaggio in più come preview)
        tredi.pathtracer.chuncks[0].samples_rendered += 1
        self.c_stopped = True

        tredi.pathtracer.running = False

        if not tredi.pathtracer.running:
            tredi.pathtracer.stats = f"Ora di inizio: {tredi.pathtracer.start_time_str}\nTerminato in: {time.time() - tredi.pathtracer.start_time:.2f} secondi"

        tredi.pathtracer.end_time = time.time()
        tredi.pathtracer.update_array()


    def reset_canvas(self, tredi):
            
        self.stahp = True
        self.try_fast_kill()

        while not self.c_stopped:
            ...
        
        for chunck in tredi.pathtracer.chuncks:
            tredi.pathtracer.update_chunck(RenderingModes.reset_background(chunck))
        tredi.pathtracer.running = False

        tredi.pathtracer.stats = f"Fai partire una renderizzazione!"

        self.c_stopped = True


    def avvio_multi_tracer(self, tredi):
        
        # compilazioni funzioni nel main
        # AcceleratedFoo.test(np.array([[0.,0.,0.], [0.,0.,0.]]), np.array([0.,0.,0.]), np.array([0.,0.,0.]))

        self.c_stopped = True
        self.stahp = False

        objects = []
        for oggetto, stato in zip(tredi.scenes["debug"].objects, tredi.UI_calls_tracer.scrolls["oggetti"].elementi_attivi):
            if stato: objects.append(oggetto)
        objects = Sphere.convert_wireframe2tracer(objects)

        tredi.pathtracer.running = True
        tredi.pathtracer.start_time_str = time.strftime('%H:%M:%S', time.localtime())
        tredi.pathtracer.start_time = time.time()

        # @profile
        def execute():
            start_execution = perf_counter()
            argomenti = [(chunck, tredi.pathtracer.camera, objects, tredi.pathtracer.settings) for chunck in tredi.pathtracer.chuncks]
            
            self.pool = multiprocessing.Pool(processes=tredi.pathtracer.settings.cores)

            for argomento in argomenti:
                self.pool.apply_async(RenderingModes.test_spheres, args=(argomento,), callback=tredi.pathtracer.update_chunck)
            
            stop_execution = perf_counter()

            self.pool.close()
            self.pool.join()

            return abs(stop_execution - start_execution)
            
        # DEBUGGER
        # argomenti = [(chunck, tredi.pathtracer.camera, objects, tredi.pathtracer.settings) for chunck in tredi.pathtracer.chuncks]
        # for sample_group in range(tredi.pathtracer.settings.samples // tredi.pathtracer.settings.sample_packet):
        #     for argomento in argomenti:
        #         ris = RenderingModes.test_spheres(argomento)
        #         tredi.pathtracer.update_chunck(ris)
        #         tredi.pathtracer.update_array()
        #     print(ris.samples_rendered)


        if not self.stahp:
            temp_swap = tredi.pathtracer.settings.sample_packet 
            tredi.pathtracer.settings.sample_packet = 1
            avvio_processi = execute()
            tredi.pathtracer.tempo_avvio = avvio_processi * tredi.pathtracer.settings.samples // tredi.pathtracer.settings.sample_packet

        if not self.stahp:
            tredi.pathtracer.settings.sample_packet = temp_swap
            for sample_group in range(tredi.pathtracer.settings.samples // tredi.pathtracer.settings.sample_packet):
                avvio_processi = execute()
                tredi.pathtracer.tempo_avvio = avvio_processi * tredi.pathtracer.settings.samples // tredi.pathtracer.settings.sample_packet
                if self.stahp:
                    return
        
        tredi.pathtracer.running = False
        tredi.pathtracer.end_time = time.time()
        tredi.pathtracer.update_array()