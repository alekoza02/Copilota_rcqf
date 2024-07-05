from numba import njit
import numpy as np
import pygame
import configparser
from _modulo_UI import Schermo, WidgetDataTracer, Logica, UI
from _modulo_MATE import Mate, AcceleratedFoo, RandomAle
from _modulo_multiprocess_classes import RayTracer

class TreDi:
    def __init__(self) -> None:
        config = configparser.ConfigParser()
        config.read('./DATA/settings.ini')

        self.debugging = eval(config.get('Default', 'debugging'))

        self.schermo_madre: pygame.Surface
        
        self.w: int
        self.h: int

        self.ancoraggio_x: int
        self.ancoraggio_y: int

        self.x_legenda: float
        self.y_legenda: float

        self.schermo: pygame.Surface
        self.bg_color: tuple[int] = Mate.hex2rgb("#1e1e1e")
        self.text_color: tuple[int]
    
        self.dim_font_base = 32
        self.dim_font = 32 
        self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
        self.font_pixel_dim = self.font_tipo.size("a")

        self.bounding_box = pygame.rect.Rect([0, 0, 1, 1])

        self.scenes: dict[str, Geo_Scene] = {}
        self.mode: int

        self.change_elemento_attivo: bool = False

        self.pathtracer: RayTracer


    def link_ui(self, ui: UI) -> None: 
        """Collegamento UI con il painter. Raccoglie informazioni circa le dimensioni dello schermo e si calcola l'ancoraggio

        Parameters
        ----------
        info_schermo : Schermo
            Dato la classe Schermo, posso capire le informazioni che mi servono
        """
        info_schermo: Schermo = ui.scena["tracer"].schermo["viewport"]
        self.schermo_madre = info_schermo.madre
        
        self.w = info_schermo.w
        self.h = info_schermo.h

        self.ridimensiona_carattere = 1 if info_schermo.shift_x == 0 else 0.7

        self.ancoraggio_x = info_schermo.ancoraggio_x
        self.ancoraggio_y = info_schermo.ancoraggio_y 
        
        self.schermo = info_schermo.schermo

        self.UI_calls_tracer = ui.scena["tracer"]

        elementi = self.scenes["debug"].objects

        self.UI_calls_tracer.scrolls["oggetti"].elementi = elementi 
        self.UI_calls_tracer.scrolls["oggetti"].elementi_attivi = [self.UI_calls_tracer.scrolls["oggetti"].all_on for _ in range(len(elementi) + 1)] # il +1 è riferito ad un elemento in più: la camera
        self.UI_calls_tracer.scrolls["oggetti"].indici = [i for i in range(len(elementi) + 1)] # il +1 è riferito ad un elemento in più: la camera
        self.UI_calls_tracer.scrolls["oggetti"].update_elements()

        self.build_raytracer()


    def build_raytracer(self):
        self.pathtracer = RayTracer()
        self.pathtracer.build(
            self.w, self.h, self.scenes["debug"].camera, 
            Mate.inp2flo(self.UI_calls_tracer.entrate["resolution_x"].text, 1.0) / 100, 
            Mate.inp2flo(self.UI_calls_tracer.entrate["resolution_y"].text, 1.0) / 100, 
            Mate.inp2int(self.UI_calls_tracer.entrate["samples"].text, 32), 
            Mate.inp2int(self.UI_calls_tracer.entrate["bounces"].text, 6), 
            Mate.inp2int(self.UI_calls_tracer.entrate["sample_package"].text, 4), 
            Mate.inp2int(self.UI_calls_tracer.entrate["cores"].text, 9), 
            Mate.inp2int(self.UI_calls_tracer.entrate["res_chunck"].text, 3)
        )


    def change_UI_stuff(self, ui: UI) -> None:

        if len(self.scenes["debug"].elenco_raw) != 0:
            self.scenes["debug"].elemento_attivo = self.scenes["debug"].elenco_raw[ui.scena["tracer"].data_widgets_tracer.oggetto_attivo]
        
        ui.scena["tracer"].label_text["active_object"].text = f"Oggetto attivo: {self.scenes['debug'].elemento_attivo.name}"

        if type(self.scenes["debug"].elemento_attivo) == Object:
            if not ui.scena["tracer"].entrate["px_modello"].toggle: ui.scena["tracer"].entrate["px_modello"].text = f"{self.scenes['debug'].elemento_attivo.x:.3f}"
            if not ui.scena["tracer"].entrate["py_modello"].toggle: ui.scena["tracer"].entrate["py_modello"].text = f"{self.scenes['debug'].elemento_attivo.y:.3f}"
            if not ui.scena["tracer"].entrate["pz_modello"].toggle: ui.scena["tracer"].entrate["pz_modello"].text = f"{self.scenes['debug'].elemento_attivo.z:.3f}"
            if not ui.scena["tracer"].entrate["rx_modello"].toggle: ui.scena["tracer"].entrate["rx_modello"].text = f"{self.scenes['debug'].elemento_attivo.r:.3f}"
            if not ui.scena["tracer"].entrate["ry_modello"].toggle: ui.scena["tracer"].entrate["ry_modello"].text = f"{self.scenes['debug'].elemento_attivo.b:.3f}"
            if not ui.scena["tracer"].entrate["rz_modello"].toggle: ui.scena["tracer"].entrate["rz_modello"].text = f"{self.scenes['debug'].elemento_attivo.i:.3f}"
            if not ui.scena["tracer"].entrate["sx_modello"].toggle: ui.scena["tracer"].entrate["sx_modello"].text = f"{self.scenes['debug'].elemento_attivo.sx:.3f}"
            if not ui.scena["tracer"].entrate["sy_modello"].toggle: ui.scena["tracer"].entrate["sy_modello"].text = f"{self.scenes['debug'].elemento_attivo.sy:.3f}"
            if not ui.scena["tracer"].entrate["sz_modello"].toggle: ui.scena["tracer"].entrate["sz_modello"].text = f"{self.scenes['debug'].elemento_attivo.sz:.3f}"
            ui.scena["tracer"].entrate["sx_modello"].visibile = True
            ui.scena["tracer"].entrate["sy_modello"].visibile = True
            ui.scena["tracer"].entrate["sz_modello"].visibile = True

            if not ui.scena["tracer"].entrate["colore_diff"].toggle: ui.scena["tracer"].entrate["colore_diff"].text = f"{Mate.rgb2hex(self.scenes['debug'].elemento_attivo.materiale.colore)}"
            if not ui.scena["tracer"].entrate["colore_emis"].toggle: ui.scena["tracer"].entrate["colore_emis"].text = f"{Mate.rgb2hex(self.scenes['debug'].elemento_attivo.materiale.emissione_colore)}"
            if not ui.scena["tracer"].entrate["forza_emis"].toggle: ui.scena["tracer"].entrate["forza_emis"].text = f"{self.scenes['debug'].elemento_attivo.materiale.emissione_forza:.3f}"
            if not ui.scena["tracer"].entrate["roughness"].toggle: ui.scena["tracer"].entrate["roughness"].text = f"{self.scenes['debug'].elemento_attivo.materiale.roughness:.3f}"
            if not ui.scena["tracer"].entrate["glossiness"].toggle: ui.scena["tracer"].entrate["glossiness"].text = f"{self.scenes['debug'].elemento_attivo.materiale.glossiness:.3f}"
            if not ui.scena["tracer"].entrate["glass"].toggle: ui.scena["tracer"].entrate["glass"].text = f"{self.scenes['debug'].elemento_attivo.materiale.glass:.0f}"
            if not ui.scena["tracer"].entrate["IOR"].toggle: ui.scena["tracer"].entrate["IOR"].text = f"{self.scenes['debug'].elemento_attivo.materiale.IOR:.3f}"
            ui.scena["tracer"].entrate["colore_diff"].visibile = True
            ui.scena["tracer"].entrate["colore_emis"].visibile = True
            ui.scena["tracer"].entrate["forza_emis"].visibile = True
            ui.scena["tracer"].entrate["roughness"].visibile = True
            ui.scena["tracer"].entrate["glossiness"].visibile = True
            ui.scena["tracer"].entrate["glass"].visibile = True
            ui.scena["tracer"].entrate["IOR"].visibile = True


        elif type(self.scenes["debug"].elemento_attivo) == Camera:
            if not ui.scena["tracer"].entrate["px_modello"].toggle: ui.scena["tracer"].entrate["px_modello"].text = f"{self.scenes['debug'].elemento_attivo.pos[0]:.3f}"
            if not ui.scena["tracer"].entrate["py_modello"].toggle: ui.scena["tracer"].entrate["py_modello"].text = f"{self.scenes['debug'].elemento_attivo.pos[1]:.3f}"
            if not ui.scena["tracer"].entrate["pz_modello"].toggle: ui.scena["tracer"].entrate["pz_modello"].text = f"{self.scenes['debug'].elemento_attivo.pos[2]:.3f}"
            if not ui.scena["tracer"].entrate["rx_modello"].toggle: ui.scena["tracer"].entrate["rx_modello"].text = f"{self.scenes['debug'].elemento_attivo.becche:.3f}"
            if not ui.scena["tracer"].entrate["ry_modello"].toggle: ui.scena["tracer"].entrate["ry_modello"].text = f"{self.scenes['debug'].elemento_attivo.rollio:.3f}"
            if not ui.scena["tracer"].entrate["rz_modello"].toggle: ui.scena["tracer"].entrate["rz_modello"].text = f"{self.scenes['debug'].elemento_attivo.imbard:.3f}"
            ui.scena["tracer"].entrate["sx_modello"].visibile = False
            ui.scena["tracer"].entrate["sy_modello"].visibile = False
            ui.scena["tracer"].entrate["sz_modello"].visibile = False

            ui.scena["tracer"].entrate["colore_diff"].visibile = False
            ui.scena["tracer"].entrate["colore_emis"].visibile = False
            ui.scena["tracer"].entrate["forza_emis"].visibile = False
            ui.scena["tracer"].entrate["roughness"].visibile = False
            ui.scena["tracer"].entrate["metal"].visibile = False
            ui.scena["tracer"].entrate["glass"].visibile = False
            ui.scena["tracer"].entrate["IOR"].visibile = False

        ui.scena["tracer"].scrolls["oggetti"].elementi = []
        self.scenes["debug"].elenco_raw = {}
        
        for index, oggetto in enumerate(self.scenes["debug"].objects):
            ui.scena["tracer"].scrolls["oggetti"].elementi.append(oggetto.name)
            self.scenes["debug"].elenco_raw[index] = oggetto

        ui.scena["tracer"].scrolls["oggetti"].elementi.append(self.scenes["debug"].camera.name)
        self.scenes["debug"].elenco_raw[len(self.scenes["debug"].elenco_raw)] = self.scenes["debug"].camera
        ui.scena["tracer"].scrolls["oggetti"].update_elements()
            
            
    def disegna(self, logica: Logica, widget_data: WidgetDataTracer):
        self.schermo.fill(self.bg_color)

        scena = self.scenes["debug"]

        if widget_data.tab == "scena_settings":
            if type(self.scenes["debug"].elemento_attivo) == Object:
                scena.elemento_attivo.b = Mate.inp2flo(widget_data.rx)
                scena.elemento_attivo.r = Mate.inp2flo(widget_data.ry)
                scena.elemento_attivo.i = Mate.inp2flo(widget_data.rz)
                scena.elemento_attivo.x = Mate.inp2flo(widget_data.px)
                scena.elemento_attivo.y = Mate.inp2flo(widget_data.py)
                scena.elemento_attivo.z = Mate.inp2flo(widget_data.pz)
                scena.elemento_attivo.sx = Mate.inp2flo(widget_data.sx, 1)
                scena.elemento_attivo.sy = Mate.inp2flo(widget_data.sy, 1)
                scena.elemento_attivo.sz = Mate.inp2flo(widget_data.sz, 1)
            
                scena.elemento_attivo.materiale.colore = np.array(Mate.hex2rgb(self.UI_calls_tracer.entrate["colore_diff"].text))  / 255
                scena.elemento_attivo.materiale.emissione_colore = np.array(Mate.hex2rgb(self.UI_calls_tracer.entrate["colore_emis"].text)) / 255
                scena.elemento_attivo.materiale.emissione_forza = Mate.inp2flo(self.UI_calls_tracer.entrate["forza_emis"].text)
                scena.elemento_attivo.materiale.roughness = Mate.inp2flo(self.UI_calls_tracer.entrate["roughness"].text)
                scena.elemento_attivo.materiale.glossiness = Mate.inp2flo(self.UI_calls_tracer.entrate["glossiness"].text)
                scena.elemento_attivo.materiale.glass = Mate.inp2int(self.UI_calls_tracer.entrate["glass"].text)
                scena.elemento_attivo.materiale.IOR = Mate.inp2flo(self.UI_calls_tracer.entrate["IOR"].text)
            
            elif type(self.scenes["debug"].elemento_attivo) == Camera:
                scena.elemento_attivo.becche = Mate.inp2flo(widget_data.rx)
                scena.elemento_attivo.rollio = Mate.inp2flo(widget_data.ry)
                scena.elemento_attivo.imbard = Mate.inp2flo(widget_data.rz)
                scena.elemento_attivo.pos[0] = Mate.inp2flo(widget_data.px)
                scena.elemento_attivo.pos[1] = Mate.inp2flo(widget_data.py)
                scena.elemento_attivo.pos[2] = Mate.inp2flo(widget_data.pz)

            scena.camera.aggiorna_attributi(logica)
            scena.camera.rotazione_camera()

            for i, obj in enumerate(scena.objects): 
                if self.UI_calls_tracer.scrolls["oggetti"].elementi_attivi[i]:

                    obj.applica_rotazioni()
                    obj.applica_traslazioni()

                    obj.transformed_vertices @= Mate.camera_world(scena.camera) 
                    obj.transformed_vertices @= Mate.screen_world() 
                    
                    obj.transformed_vertices @= Mate.frustrum(self.w, self.h, self.scenes["debug"].camera.fov) 
                    obj.transformed_vertices = Mate.proiezione(obj.transformed_vertices) 

                    obj.transformed_vertices @= Mate.centra_schermo(self.w, self.h) 

                    triangles = obj.transformed_vertices[obj.links]
                    
                    if widget_data.pallini:
                        for p in obj.transformed_vertices[:, :2]:
                            pygame.draw.circle(self.schermo, obj.materiale.colore * 255, [p[0], p[1]], 4)    
                    

                    if widget_data.links:
                        for triangle in triangles:
                            if not AcceleratedFoo.any_fast(triangle, self.w * 1.5, self.h * 1.5):
                                pygame.draw.polygon(self.schermo, obj.materiale.colore * 255, [triangle[0, :2], triangle[1, :2], triangle[2, :2]], 1)


        if widget_data.tab == "tracer_settings":
            self.UI_calls_tracer.label_text["eta"].text = self.pathtracer.stats
            surface = pygame.surfarray.make_surface(self.pathtracer.pixel_array_zoomed)
            self.schermo.blit(surface, (0,0))
        

    def TEMPORARY_GENERATION(self):
        self.scenes["debug"] = Geo_Scene()
        # self.scenes["debug"].default_scene()
        self.scenes["debug"].import_model()


class Geo_Scene:
    def __init__(self) -> None:
        self.objects: list[Object] = []
        self.camera: Camera = Camera()
        self.camera.pos = np.array([2.245, -60.454, 1.752, 1])
        self.camera.becche = 1.534
        self.camera.rollio = 0.000
        self.camera.imbard = 0.060

        self.elenco_raw: dict[str, Camera | Object] = {}
        self.elemento_attivo: Camera | Object = None


    def default_scene(self):

        # cubo nell'origine
        v = np.array([[-2,-2,-2,1],[-2,-2,2,1],[-2,2,-2,1],[-2,2,2,1],[2,-2,-2,1],[2,-2,2,1],[2,2,-2,1],[2,2,2,1]])
        l = np.array([[0,1,2],[1,2,3],[0,2,4],[4,2,6],[4,5,6],[5,6,7],[5,1,3],[5,3,7],[2,3,6],[3,6,7],[0,1,4],[1,4,5]])

        self.objects.append(Object("cubo", v, l))
        self.objects.append(Object("cubo", v, l, x=4, y=4, z=4))
        self.objects.append(Object("cubo", v, l, x=4, y=4, z=-4))
        self.objects.append(Object("cubo", v, l, x=4, y=-4, z=4))
        self.objects.append(Object("cubo", v, l, x=4, y=-4, z=-4))
        self.objects.append(Object("cubo", v, l, x=-4, y=4, z=4))
        self.objects.append(Object("cubo", v, l, x=-4, y=4, z=-4))
        self.objects.append(Object("cubo", v, l, x=-4, y=-4, z=4))
        self.objects.append(Object("cubo", v, l, x=-4, y=-4, z=-4))

        self.elemento_attivo: Camera | Object = self.objects[0]

    
    def import_model(self):

        self.i = Importer()
        # i.modello("TRACER_DATA/m_hyperion.obj")
        # i.modello("TRACER_DATA/m_ban.obj")
        self.i.modello("TRACER_DATA/m_sph.obj")

        self.i.verteces = Mate.add_homogenous(self.i.verteces)

        self.objects.append(Object("Sfera_piccola", self.i.verteces, self.i.links, z=-8.5, x=-5, y=-5, sx=6, sy=6, sz=6, materiale=Materiale(colore=np.array([1., 1., 1.]))))
        self.objects.append(Object("Sfera_media", self.i.verteces, self.i.links, z=-7.5, y=-10, x=6, sx=8, sy=8, sz=8, materiale=Materiale(colore=np.array([1., 1., 1.]))))
        self.objects.append(Object("Sfera_grande", self.i.verteces, self.i.links, z=-5, x=3, sx=13, sy=13, sz=13, materiale=Materiale(colore=np.array([1., 1., 1.]))))
        self.objects.append(Object("Sfera_pavimento", self.i.verteces, self.i.links, z=-1010, sx=2000, sy=2000, sz=2000, materiale=Materiale(colore=np.array([1., 1., 1.]))))
        self.objects.append(Object("Sfera_cielo", self.i.verteces, self.i.links, z=1010, sx=2000, sy=2000, sz=2000, materiale=Materiale(colore=np.array([1., 1., 1.]))))
        self.objects.append(Object("Sfera_parete_sx", self.i.verteces, self.i.links, x=-1010, sx=2000, sy=2000, sz=2000, materiale=Materiale(colore=np.array([1., .5, 0.]))))
        self.objects.append(Object("Sfera_parete_dx", self.i.verteces, self.i.links, x=1010, sx=2000, sy=2000, sz=2000, materiale=Materiale(colore=np.array([0., 1., 1.]))))
        self.objects.append(Object("Sfera_parete_fondo", self.i.verteces, self.i.links, y=1010, sx=2000, sy=2000, sz=2000, materiale=Materiale(colore=np.array([1., 1., 1.]))))
        self.objects.append(Object("Luce", self.i.verteces, self.i.links, z=18, sx=20, sy=20, sz=20, materiale=Materiale(emissione_forza=5)))
        self.elemento_attivo: Object = self.objects[0]
        
        # self.objects.append(Object("Sfera_piccola", i.verteces, i.links, sx=2, sy=2, sz=2))
        # self.elemento_attivo: Camera | Object = self.objects[0]


    def add_sphere(self):
        self.objects.append(Object(f"Nuova sfera {len(self.objects)}", self.i.verteces, self.i.links, materiale=Materiale()))
    
    
    def remove_sphere(self, index):
        self.objects.pop(index)


class Materiale:
    def __init__(self, colore = np.array([1,1,1]), emissione_forza = 0, emissione_colore = np.array([1,1,1])) -> None:
        self.colore = colore
        self.emissione_forza = emissione_forza
        self.emissione_colore = emissione_colore
        self.roughness = 1
        self.glossiness = 1
        self.glass = 1
        self.IOR = 1.5

    def __str__(self) -> str:
        return f"{self.colore}"


class Object:
    def __init__(self, nome, vertici, links, materiale: Materiale, x = 0.0, y = 0.0, z = 0.0, r = 0.0, b = 0.0, i = 0.0, sx = 1.0, sy = 1.0, sz = 1.0, wireframe = True) -> None:
        self.name = nome
        self.vertices: np.ndarray[np.ndarray[float]] = vertici
        self.transformed_vertices: np.ndarray[np.ndarray[int]] = vertici
        self.links: np.ndarray[int] = links

        self.x: float = x
        self.y: float = y
        self.z: float = z
        
        self.b: float = b
        self.r: float = r
        self.i: float = i

        self.sx: float = sx
        self.sy: float = sy
        self.sz: float = sz

        self.wireframe = wireframe

        self.materiale = materiale

    @property
    def pos(self):
        return np.array([self.x, self.y, self.z])

    def applica_rotazioni(self) -> None:
        '''
        Applicazioni rotazioni eulero XYZ
        '''
        self.transformed_vertices = self.vertices @ Mate.rotx(self.b)    
        self.transformed_vertices = self.transformed_vertices @ Mate.roty(self.r)   
        self.transformed_vertices = self.transformed_vertices @ Mate.rotz(self.i)  

    def applica_traslazioni(self) -> None:
        '''
        Applicazioni traslazioni
        '''
        self.transformed_vertices = self.transformed_vertices @ Mate.scalotrasla(self)

    def __str__(self):
        return f"{self.name}"


class Triangle:
    def __init__(self) -> None:
        pass

    @staticmethod
    @njit()
    def rasterization(w: int, h: int, triangles: np.ndarray[np.ndarray[np.ndarray[float]]], bg_color: np.ndarray[float], plot_color: np.ndarray[float], l_min: float, l_max: float) -> np.ndarray[np.ndarray[float]]:
        
        v1 = triangles[:, 0, :]
        v2 = triangles[:, 1, :]
        v3 = triangles[:, 2, :]
        
        triangles = np.ones(triangles.shape)
        triangles[:, 0, :] = v1
        triangles[:, 1, :] = v3
        triangles[:, 2, :] = v2
        
        def cross_edge(vertex1, vertex2, p):
            edge12 = vertex1 - vertex2
            edge1p = vertex1 - p
            return edge12[0] * edge1p[1] - edge12[1] * edge1p[0]
        
        buffer = np.ones((w, h, 3)) * bg_color
        # buffer = np.zeros((w, h, 3))

        for triangle in triangles:
            
            min_x = round(np.min(triangle[:,0]))
            max_x = round(np.max(triangle[:,0]))
            min_y = round(np.min(triangle[:,1]))
            max_y = round(np.max(triangle[:,1]))
            
            if max_x < 0: continue
            if max_y < 0: continue
            if min_x > w: continue
            if min_y > h: continue
                            
            if max_x > w: max_x = w
            if max_y > h: max_y = h
            if min_x < 0: min_x = 0
            if min_y < 0: min_y = 0
                        
            v_1 = triangle[0]
            v_2 = triangle[1]
            v_3 = triangle[2]
            
            area = cross_edge(v_1, v_2, v_3)
            if area == 0: continue
            
            delta_w0_col = v_2[1] - v_3[1]
            delta_w1_col = v_3[1] - v_1[1]
            delta_w2_col = v_1[1] - v_2[1]
            
            delta_w0_row = v_3[0] - v_2[0]
            delta_w1_row = v_1[0] - v_3[0]
            delta_w2_row = v_2[0] - v_1[0]
            
            p0 = np.array([min_x, min_y]) + np.array([0.5, 0.51])

            w0_row = cross_edge(v_2, v_3, p0)
            w1_row = cross_edge(v_3, v_1, p0)
            w2_row = cross_edge(v_1, v_2, p0)
            
            for y in range(min_y, max_y):
                w0 = w0_row
                w1 = w1_row
                w2 = w2_row
                for x in range(min_x, max_x):
                    
                    alpha = w0 / area
                    beta = w1 / area
                    gamma = w2 / area
                    
                    if w0 >= 0 and w1 >= 0 and w2 >= 0:
                
                        progresso = 1 - (y - l_min) / (l_max - l_min) 

                        buffer[x, y, 0] = progresso * (plot_color[0] - bg_color[0]) + bg_color[0]
                        buffer[x, y, 1] = progresso * (plot_color[1] - bg_color[1]) + bg_color[1]
                        buffer[x, y, 2] = progresso * (plot_color[2] - bg_color[2]) + bg_color[2]
                
                    w0 += delta_w0_col 
                    w1 += delta_w1_col
                    w2 += delta_w2_col
                
                w0_row += delta_w0_row 
                w1_row += delta_w1_row
                w2_row += delta_w2_row
                    
        return buffer
    


class Camera:
    def __init__(self) -> None:
        
        # REMEMBER -> PYGAME VISUALIZZA I PUNTI DA IN ALTO A SINISTRA
        
        # O ---------->
        # |
        # |
        # V

        # sistema di riferimento:
        # right -> asse x
        # front -> asse y
        # up    -> asse z

        # default:
        # pos = asse z positivo
        # focus = punto di orbita per le rotazioni
        # front = verso asse z negativo
        # right = verso asse x positivo
        # up = verso asse y positivo

        self.name: str = "Camera"
        self.fov: float = np.pi / 6

        self.pos: np.ndarray[float] = np.array([0.,0.,1.,1])
        self.focus: np.ndarray[float] = np.array([0.,0.,0.,1])

        self.rig_o: np.ndarray[float] = np.array([1.,0.,0.,1])
        self.ups_o: np.ndarray[float] = np.array([0.,1.,0.,1])
        self.dir_o: np.ndarray[float] = np.array([0.,0.,-1.,1])

        self.rig: np.ndarray[float] = np.array([1.,0.,0.,1])
        self.ups: np.ndarray[float] = np.array([0.,1.,0.,1])
        self.dir: np.ndarray[float] = np.array([0.,0.,-1.,1])

        # inclinazioni (sistema di riferimento locale): 
        # rollio -> attorno ad asse y (avvitamento)
        # beccheggio -> attorno ad asse x (pendenza)
        # imbardata -> attorno ad asse z (direzione NSWE)

        # imbardata è relativa all'asse Z globale [0,0,1]   (BLENDER)
        # beccheggio è relativo all'asse X locale           (BLENDER)
        # rollio è relativo all'asse Y locale               (BLENDER)

        self.rollio = 0
        self.becche = 0
        self.imbard = 0
        
        # i delta angoli sono usati per calcolare lo spostamento relativo per poter orbitare attorno all'oggetto
        
        self.delta_becche = 0
        self.delta_rollio = 0
        self.delta_imbard = 0

        # con il default la camera dovrebbe guardare dall'alto verso il basso avendo:
        # - sulla sua destra l'asse x positivo
        # - sulla sua sopra l'asse y positivo

        # ---------------------------------------------------------------------------------------

        # valori default di partenza

        self.pos[0] = 9.2
        self.pos[1] = -11.1
        self.pos[2] = 3.0
        
        self.becche = 1.4
        self.rollio = 0
        self.imbard = 0.7
    
    
    def rotazione_camera(self) -> None:
        '''
        Applico le rotazioni in ordine Eulero XYZ ai vari vettori di orientamento della camera
        '''
        self.rig = self.rig_o @ Mate.rotx(self.becche)
        self.ups = self.ups_o @ Mate.rotx(self.becche)
        self.dir = self.dir_o @ Mate.rotx(self.becche)

        self.rig = self.rig @ Mate.roty(self.rollio)
        self.dir = self.dir @ Mate.roty(self.rollio)
        self.ups = self.ups @ Mate.roty(self.rollio)

        self.rig = self.rig @ Mate.rotz(self.imbard)
        self.ups = self.ups @ Mate.rotz(self.imbard)
        self.dir = self.dir @ Mate.rotz(self.imbard)

        self.pos -= self.focus
        self.pos = self.pos @ Mate.rotz(- self.delta_imbard)
        self.pos = self.pos @ Mate.rot_ax(self.rig, self.delta_becche)
        self.pos += self.focus

    def aggiorna_attributi(self, logica) -> None:
        '''
        Aggiorna gli attributi della camera come pos / rot / zoom.
        Con le traslazioni viene aggiornato anche il focus attorno al quale avverrà la rotazione
        '''
        
        # se il ctrl è schiacciato -> avverrà zoom
        if logica.ctrl:
            self.pos[:3] += self.dir[:3] * logica.dragging_dy / 100

        # se lo shift è schiacciato -> avverrà traslazione
        elif logica.shift:
            # ABILITA FOCUS
            # self.focus[:3] -= self.rig[:3] * logica.dragging_dx / 100
            # self.focus[:3] -= self.ups[:3] * logica.dragging_dy / 100
            self.pos[:3] -= self.rig[:3] * logica.dragging_dx / 100
            self.pos[:3] -= self.ups[:3] * logica.dragging_dy / 100

        # se non è schiacciato nulla -> avverrà rotazione
        else:
            self.becche += logica.dragging_dy / 500
            self.delta_becche = - logica.dragging_dy / 500
            
            self.rollio -= 0
            self.delta_rollio = 0
            
            self.imbard -= logica.dragging_dx / 500
            self.delta_imbard = logica.dragging_dx / 500

        # controllo dello zoom con rotella
        if logica.scroll_up:
            self.pos[:3] += self.dir[:3]
        elif logica.scroll_down:
            self.pos[:3] -= self.dir[:3]

        if logica.scroll_down > 0: logica.scroll_down -= 3
        else: logica.scroll_down = 0 
        if logica.scroll_up > 0: logica.scroll_up -= 3
        else: logica.scroll_up = 0



class Importer:
    def __init__(self, use_file = True, use_struttura = False) -> None:
        self.use_file = use_file
        self.use_struttura = use_struttura

    def modello(self, nome, texture = None, uv_check = False):
        if self.use_file:
            file_path = f'{nome}'
            texture_path = f'{texture}'

            vertici = []
            links = []
            uv_links = []
            uv = []
            
            with open(file_path, 'r') as file:
                lines = file.readlines()

            for line in lines:
                if line.startswith('v '):
                    vertex = [float(x) for x in line.split()[1:]]
                    vertici.append(vertex)
                elif line.startswith('f '):
                    link = [x.split('/') for x in line.split()[1:]]
                    links.append([int(i[0]) for i in link])
                    if uv_check: uv_links.append([int(i[1]) for i in link])
                elif line.startswith('vt ') and uv_check:
                    uv_single = [float(x) for x in line.split()[1:]]
                    uv.append(uv_single)
                    
            vertici = np.array(vertici)
            uv = np.array(uv)
            uv_links = np.array(uv_links) - 1
            links = np.array(links) - 1

            self.verteces = vertici
            self.links = links
            
            if uv_check:
                self.uv = uv
                self.uv_links = uv_links
            else:
                self.uv = np.zeros_like(vertici)
                self.uv_links = np.zeros_like(links)

            if not texture is None:
                from PIL import Image
                image = Image.open(texture_path)

                self.texture = np.array(image)
                self.texture = self.texture.transpose(1,0,2)
                self.texture = self.texture[:,::-1,:]

