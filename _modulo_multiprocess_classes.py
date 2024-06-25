import numpy as np
import multiprocessing
from _modulo_2D_grafica import Zoomer
from random import random, uniform, normalvariate


class Settings:
    def __init__(self, samples, bounces) -> None:
        self.samples = samples
        self.bounces = bounces
        self.sample_packet = 4


class Raggio:
    def __init__(self, pos, dir) -> None:
        self.pos = pos
        self.dir = dir


class Record:
    def __init__(self) -> None:
        self.colpito: bool = False
        self.distanza: float = np.inf
        self.indice_oggetti_prox: int
        self.materiale = None
        self.punto_colpito: np.array[np.array[float]]
        self.norma_colpito: np.array[np.array[float]]


class RenderChunck:
    def __init__(self, ori_w, ori_h, w, h, x, y, index, settings) -> None:
        
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
        self.amb_oc = np.zeros((self.w, self.h, 3))
        self.amb_oc_distances = np.zeros((self.w, self.h, settings.samples))

        self.samples_rendered = 0


class RayTracer:
    def __init__(self) -> None:
        self.w: int
        self.h: int

        self.pixel_array: np.array[np.array[float]]

        self.chuncks: list[RenderChunck]
        self.mode = 0
        self.old_mode = 0

        self.settings = Settings(1024, 6)


    def build(self, w, h, camera):

        self.w = int(w / 6)
        self.h = int(h / 6) 
        self.pixel_array = np.zeros((self.w, self.h, 3), dtype=np.int8)
        self.pixel_array_zoomed = np.zeros((w, h, 3), dtype=np.int8)
        self.chuncks = []

        self.camera = camera
        self.zoomer: Zoomer = Zoomer(w, h)

        self.res_x, self.res_y = 6, 6

        dim_x = int(self.w / (self.res_x - 1))
        dim_y = int(self.h / (self.res_y - 1))

        for x in range(self.res_x):
            for y in range(self.res_y):
                anchor_x = self.w - (dim_x * (self.res_x - 1)) if x == (self.res_x - 1) else dim_x * x
                anchor_y = self.h - (dim_y * (self.res_y - 1)) if y == (self.res_y - 1) else dim_y * y
                    
                self.chuncks.append(RenderChunck(self.w, self.h, dim_x, dim_y, anchor_x, anchor_y, len(self.chuncks), self.settings))


    def update_chunck(self, chunck: RenderChunck):
        self.chuncks[chunck.index] = chunck
        # if chunck.index % 12 == 0:
            # self.update_array()


    def update_array(self):
        for chunck in self.chuncks:
            match self.mode:
                case 0:
                    self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = chunck.indici
                case 1:
                    ris = np.sqrt(chunck.albedo / (chunck.samples_rendered + 1)) * 255
                    ris[ris > 255] = 255
                    self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = ris
                case 2:
                    self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = chunck.normal
                case 3:
                    single_channel = np.clip(np.sum(1 / (chunck.amb_oc_distances[:, :, :chunck.samples_rendered] + 1), axis=2) / (chunck.samples_rendered + 1), 0, 1)
                    single_channel = 1 - single_channel
                    chunck.amb_oc = np.repeat(single_channel[:,:,None], 3, axis=2) * 255
                    self.pixel_array[chunck.x:chunck.x+chunck.w, chunck.y:chunck.y+chunck.h, :] = chunck.amb_oc

        self.pixel_array_zoomed = self.zoomer.adatta_input2output(self.pixel_array.astype(np.int8))
    

    def update_camera(self, camera):
        self.camera = camera


class Sphere:

    def __init__(self, pos, radius, materiale, indice) -> None:
        self.pos = pos 
        self.radius = radius
        self.materiale = materiale
        self.indice = indice


    def collisione_sphere(self, ray, record: Record):
        oc = ray.pos - self.pos;
        
        a = 1.0;
        b = np.dot(oc, ray.dir) * 2.0;
        c = np.dot(oc, oc) - (self.radius) ** 2;

        discriminante = b ** 2 - 4.0 * a * c;
        
        if discriminante >= 0.0:
            sqrt_discr = discriminante ** 0.5
            
            delta_min = (- b - sqrt_discr) / (2.0*a);
            delta_max = (- b + sqrt_discr) / (2.0*a);
            
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
    def gradient_chunck(args: tuple[RenderChunck, any]) -> RenderChunck:
        chunck: RenderChunck = args[0]
        for x in range(chunck.w):
            for y in range(chunck.h):
                chunck.albedo[x, y, :] = np.array([255 * (chunck.x + x)/chunck.ori_w, 255 * (chunck.y + y)/chunck.ori_h, 255]).astype(int)
        return chunck


    @staticmethod
    def direction_chunck(args: tuple[RenderChunck, any]) -> RenderChunck:
        chunck: RenderChunck = args[0]
        camera = args[1]

        direzioni = RenderingModes.direction_bulk(chunck.ori_w, chunck.ori_h, chunck.x, chunck.y, chunck.w, chunck.h, camera)
        direzioni[direzioni < 0] = 0
        direzioni *= 255
        chunck.value = direzioni
        return chunck
    

    @staticmethod
    def test_spheres(args: tuple[RenderChunck, any]) -> RenderChunck:
        # try:
            chunck: RenderChunck = args[0]
            camera = args[1]
            list_object = args[2]
            settings: Settings = args[3]

            direzioni = RenderingModes.direction_bulk(chunck.ori_w, chunck.ori_h, chunck.x, chunck.y, chunck.w, chunck.h, camera)

            for sample in range(settings.sample_packet):
                for x in range(chunck.w):
                    for y in range(chunck.h):

                        ray = Raggio(camera.pos[:3], direzioni[x, y])
                        ray_incoming_light = np.array([0.,0.,0.])
                        ray_color = np.array([1.,1.,1.])

                        for bounce in range(settings.bounces):

                            # inizializzazione record
                            pixel_analize = Record()
                
                            # collisione con sfera
                            for oggetto in list_object:
                                pixel_analize = oggetto.collisione_sphere(ray, pixel_analize)
                    
                            if pixel_analize.colpito:
                                # first save
                                if bounce == 0: 
                                    chunck.normal[x, y, :] = (pixel_analize.norma_colpito + 1) * (255/2)
                                    chunck.indici[x, y, :] = pixel_analize.materiale.colore * 255
                                
                                # AO save
                                if bounce == 1:
                                    chunck.amb_oc_distances[x, y, chunck.samples_rendered] = np.linalg.norm(pixel_analize.punto_colpito - ray.pos)
                            
                                # materiale
                                materiale = pixel_analize.materiale
                                luce_emessa = materiale.emissione_colore * materiale.emissione_forza
                                ray_incoming_light = ray_incoming_light + luce_emessa * ray_color
                                ray_color = ray_color * materiale.colore

                                # nuovo giro settings
                                ray.pos = pixel_analize.punto_colpito
                                ray.dir = np.array([uniform(-1, 1) for i in range(3)])
                                ray.dir /= np.linalg.norm(ray.dir)

                                if np.dot(pixel_analize.norma_colpito, ray.dir) < 0:
                                    # print(f"\nResoconto:\n{pixel_analize.norma_colpito =}, {ray.dir =}\n{np.dot(pixel_analize.norma_colpito, ray.dir) =}\n{- ray.dir =}\n--------------------------------------")
                                    ray.dir = - ray.dir

                            else:
                                break
                        
                        chunck.albedo[x, y, :] += ray_incoming_light

                chunck.samples_rendered += 1
                    
            return chunck
        
        # except Exception as e:
        #     print(f"Attenzione, AleDebug in azione:\n{e}") 
        #     return chunck

    
    @staticmethod
    def reset_background(args: tuple[RenderChunck, any]) -> RenderChunck:
        chunck: RenderChunck = args[0]
        chunck.albedo[:, :, :] = 30
        return chunck


class AvvioMultiProcess:
    def __init__(self) -> None:
        pass

    @staticmethod
    def avvio_multi_tracer(tredi, render_string: str, numprocess = 12):

        
        # DEBUGGER
        # for sample_group in range(tredi.pathtracer.settings.samples // tredi.pathtracer.settings.sample_packet):
        #     for argomento in argomenti:
        #         ris = RenderingModes.test_spheres(argomento)
        #         tredi.pathtracer.update_chunck(ris)
        #         tredi.pathtracer.update_array()
        #     print(ris.samples_rendered)

        objects = Sphere.convert_wireframe2tracer(tredi.scenes["debug"].objects)


        def execute():
            pool = multiprocessing.Pool(processes=numprocess)
            argomenti = [(chunck, tredi.pathtracer.camera, objects, tredi.pathtracer.settings) for chunck in tredi.pathtracer.chuncks]
            
            for argomento in argomenti:
                match render_string:
                    case "gradiente":
                        pool.apply_async(RenderingModes.gradient_chunck, args=(argomento,), callback=tredi.pathtracer.update_chunck)
                    case "direction":
                        pool.apply_async(RenderingModes.direction_chunck, args=(argomento,), callback=tredi.pathtracer.update_chunck)
                    case "sfere":
                        pool.apply_async(RenderingModes.test_spheres, args=(argomento,), callback=tredi.pathtracer.update_chunck)
                    case "reset":
                        pool.apply_async(RenderingModes.reset_background, args=(argomento,), callback=tredi.pathtracer.update_chunck)
                    case _:
                        pass
            
            pool.close()
            pool.join()
            tredi.pathtracer.update_array()


        temp_swap = tredi.pathtracer.settings.sample_packet 
        tredi.pathtracer.settings.sample_packet = 1
        execute()

        tredi.pathtracer.settings.sample_packet = temp_swap
        for sample_group in range(tredi.pathtracer.settings.samples // tredi.pathtracer.settings.sample_packet):
            execute()