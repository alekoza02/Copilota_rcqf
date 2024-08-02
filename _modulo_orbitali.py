import numpy as np
import math
from scipy.special import assoc_laguerre, sph_harm
from scipy.constants import physical_constants, pi, epsilon_0, hbar, e, m_e
from _modulo_3D_grafica import Camera, Object
from _modulo_MATE import Mate
from _modulo_UI import Schermo, Logica, UI
from _modulo_plots import Painter, Plot
import pygame

class Orbitale:
    def __init__(self, ris) -> None:
        # Define constants
        self.Z = 1  # Atomic number for hydrogen-like atom (e.g., hydrogen Z=1, helium+ Z=2)
        self.n = 4  # Principal quantum number
        self.l = 2  # Azimuthal quantum number
        self.m = 0  # Magnetic quantum number

        # Physical constants
        self.a_0 = physical_constants["Bohr radius"][0]  # Bohr radius in meters
        self.mu = m_e  # Reduced mass for hydrogen-like atom (approx. equal to electron mass)
        
        self.ris = ris

        self.range = self.a_0 * 60

        # self.coords = np.random.uniform(-1, 1, (self.ris, 3))
        radius = np.random.uniform(0, 1, self.ris) ** (1/3)
        radius[0] = 0.001
        radius *= self.range
        theta = np.random.uniform(0, pi, self.ris)
        phi = np.random.uniform(-pi, pi, self.ris)

        self.polar = Mate.stack_attributes(radius, theta, phi)
        self.cartesian = Mate.pol2car(self.polar)
        
        self.coords = Mate.add_homogenous(self.cartesian)
        self.modello = Object("Orbitale", self.coords, None)
        self.camera = Camera()
        self.camera.pos = np.array([0.,-234.,64.8,1])
        self.camera.becche = 1.32
        self.camera.rollio = 0
        self.camera.imbard = 0
        
        self.mask = np.ones(self.ris)

        self.probabilit = np.zeros(self.ris)
        self.dimensions = np.ones(self.ris)
        self.colori = np.ones((self.ris, 3))
        self.colori_int8 = (self.colori * 255).astype(np.int8)

        self.indici_controllo = np.arange(0, ris, 1)
        self.attributo_calcolato = False


    def attribute(self, att: str = "schrodinger"):
        if not self.attributo_calcolato:

            self.reset_color()
            
            match att:
                case "distanza":
                    distanze = np.linalg.norm(self.cartesian, axis=1)
                    distanze -= min(distanze)
                    distanze /= max(distanze)
                    distanze = np.abs(distanze)
                    self.colori *= (1 - distanze[:, None])
                    
                    self.dimensions = (1 - distanze) * 6
                    self.dimensions = self.dimensions.astype(int) 
                    

                case "schrodinger":
                    self.probabilit = self.hydrogenoid_wave_function(self.polar[:, 0], self.polar[:, 1], self.polar[:, 2], self.n, self.l, self.m, self.Z)

                    self.probabilit = self.probabilit.real.astype(float)
                    

                    self.probabilit = self.probabilit

                    # self.probabilit -= min(self.probabilit)
                    self.probabilit /= max(self.probabilit)
                    
                    # self.colori[:, 0] = 0
                    # self.colori[:, 1] *= self.probabilit
                    # self.colori[:, 2] *= self.probabilit
        
                    self.probability_threshold = 1/100
                    self.dimension_range = 10

                    self.colori = self.color_ramp(self.probabilit, self.probability_threshold)
                    self.dimensions = self.probabilit.copy()

                    self.dimensions[self.dimensions < self.probability_threshold] = -1
                    self.dimensions *= self.dimension_range
                    self.dimensions += 1
                    self.dimensions = self.dimensions.astype(int)  
            
            self.attributo_calcolato = True
            self.hide_points()
            self.fast_color()

            return self.attributo_calcolato


        else:

            self.hide_points()
            self.fast_color()

            return not self.attributo_calcolato


    def reset_color(self):
        self.colori = np.ones((self.ris, 3))


    def fast_color(self):
        self.colori_int8 = self.colori * 255
        self.colori_int8 = self.colori_int8.astype(int)


    @staticmethod
    def color_ramp(perc, min_threshold):

        colori = np.array([
            [0.117648, 0.117648, 0.117648],     # nero
            [0.30603, 0, 0.449578],            # viola
            [0.499173, 0.12141, 0],             # arancio
            [0.742122, 0.750615, 0.229198],     # giallo
            [1, 1, 1],                          # bianco
            [1, 1, 1],                          # bianco
        ])

        intervalli = np.array([
            min_threshold, 0.0125, 0.025, .05, .2, 1
        ]) 

        # for index, intervallo in enumerate(intervalli):
        #     if intervallo < perc:
        #         continue
        #     else:
        #         m = index
        #         break
        # else:
        #     m = index
        
        # delta_colore = (colori[m] - colori[m - 1])
        # delta_interval = intervalli[m] - intervalli[m - 1]
        # pos_interval = perc - intervalli[m - 1]

        # m_colore = pos_interval / delta_interval

        # ris = colori[m - 1] + delta_colore * m_colore

        # return ris


        perc = np.asarray(perc)
        
        # Find the interval indices for each percentage
        m = np.searchsorted(intervalli, perc, side='right')

        # Clamp values to the valid range
        m = np.clip(m, 1, len(intervalli) - 1)
        
        # Calculate the delta in colors and intervals
        delta_colore = colori[m] - colori[m - 1]
        delta_interval = intervalli[m] - intervalli[m - 1]
        pos_interval = perc - intervalli[m - 1]

        # Calculate the color ramp
        m_colore = pos_interval / delta_interval
        ris = colori[m - 1] + delta_colore * m_colore[:, None]

        return ris


    def hide_points(self):
        self.mask = np.ones(self.ris)
        
        self.polar = Mate.car2pol(self.modello.vertices[:, :3])

        rad_mask = np.logical_and(self.polar[:, 0] > 0, self.polar[:, 0] < 1) # controllo del raggio
        # tet_mask = np.logical_and(self.polar[:, 1] > .78, self.polar[:, 1] < 3.14) # controllo angolo verticale [0, pi]
        tet_mask = np.ones(self.ris)
        # phi_mask1 = np.logical_and(self.polar[:, 2] > -.785, self.polar[:, 2] < 3.14) # controllo angolo orizzonatle [-pi, pi]
        # phi_mask2 = np.logical_and(self.polar[:, 2] > -3.14, self.polar[:, 2] < -2.355) # controllo angolo orizzonatle [-pi, pi]
        # phi_mask = np.logical_or(phi_mask1, phi_mask2)
        phi_mask = np.ones(self.ris)

        self.mask = np.logical_and(rad_mask, tet_mask)
        self.mask = np.logical_and(self.mask, phi_mask)

        # self.mask = np.ones(self.ris)


    def dist_sort(self):
        # indici_revert = np.argsort(self.indici_controllo)

        # self.indici_controllo = self.indici_controllo[indici_revert]
        # self.modello.transformed_vertices = self.modello.transformed_vertices[indici_revert]
        # self.colori_int8 = self.colori_int8[indici_revert]
        # self.dimensions = self.dimensions[indici_revert]
        # self.mask = self.mask[indici_revert]
        # self.probabilit = self.probabilit[indici_revert]

        dist = self.modello.transformed_vertices[:, :3] - self.camera.pos[:3]
        dist = np.linalg.norm(dist, axis=1)
        indici = np.argsort(dist)[::-1]

        self.indici_controllo = self.indici_controllo[indici]
        self.modello.transformed_vertices = self.modello.transformed_vertices[indici]
        self.colori_int8 = self.colori_int8[indici]
        self.dimensions = self.dimensions[indici]
        self.mask = self.mask[indici]
        self.probabilit = self.probabilit[indici]


    # Radial part of the wave function
    def radial_wave_function(self, r, n, l, Z):
        rho = 2 * Z * r / (n * self.a_0)
        norm_factor = np.sqrt((2 * Z / (n * self.a_0))**3 * math.factorial(n - l - 1) / (2 * n * math.factorial(n + l)))
        laguerre_poly = assoc_laguerre(rho, n - l - 1, 2 * l + 1)
        radial_part = norm_factor * np.exp(-rho / 2) * rho**l * laguerre_poly
        return radial_part


    # Angular part of the wave function (spherical harmonics)
    @staticmethod
    def angular_wave_function(theta, phi, l, m):
        return sph_harm(m, l, phi, theta)


    # Total wave function
    def hydrogenoid_wave_function(self, r, theta, phi, n, l, m, Z):
        R = self.radial_wave_function(r, n, l, Z)
        Y = self.angular_wave_function(theta, phi, l, m)
        return (R * Y) ** 2
    

class Manager_orbs:
    def __init__(self, ris) -> None:

        self.bg_color: tuple[int] = Mate.hex2rgb("#1e1e1e")
        self.orbitale = Orbitale(ris)

        self.mode = "2D"
        self.samples = 0
        
        self.plot = Painter("minimal")
        self.plot2 = Painter("minimal")

        self.plot.settings()
        self.plot2.settings()
        

    def link_ui(self, ui: UI) -> None: 
        """Collegamento UI con il painter. Raccoglie informazioni circa le dimensioni dello schermo e si calcola l'ancoraggio

        Parameters
        ----------
        info_schermo : Schermo
            Dato la classe Schermo, posso capire le informazioni che mi servono
        """
        info_schermo: Schermo = ui.scena["orbitals"].schermo["viewport"]
        self.schermo_madre = info_schermo.madre
        
        self.w = info_schermo.w
        self.h = info_schermo.h

        self.ridimensiona_carattere = 1 if info_schermo.shift_x == 0 else 0.7

        self.ancoraggio_x = info_schermo.ancoraggio_x
        self.ancoraggio_y = info_schermo.ancoraggio_y 

        self.background = np.zeros((self.w, self.h))

        # link plot ausiliari -----------------------------------------------------------
        self.schermo = info_schermo.schermo
        
        info_schermo_helper: Schermo = ui.scena["orbitals"].schermo["helper"]
        info_schermo_helper2: Schermo = ui.scena["orbitals"].schermo["helper2"]

        self.w_helper = info_schermo_helper.w
        self.h_helper = info_schermo_helper.h
        self.w_helper2 = info_schermo_helper2.w
        self.h_helper2 = info_schermo_helper2.h

        self.ancoraggio_x_helper = info_schermo_helper.ancoraggio_x
        self.ancoraggio_y_helper = info_schermo_helper.ancoraggio_y 
        self.ancoraggio_x_helper2 = info_schermo_helper2.ancoraggio_x
        self.ancoraggio_y_helper2 = info_schermo_helper2.ancoraggio_y 

        self.schermo_helper = info_schermo_helper.schermo
        self.schermo_helper2 = info_schermo_helper2.schermo

        self.plot.link_ui(ui, "orbitals", "helper")
        self.plot2.link_ui(ui, "orbitals", "helper2")
        # link plot ausiliari -----------------------------------------------------------

        self.UI_calls_tracer = ui.scena["orbitals"]


    def grafica_funzione(self, painter: Painter, mode):
        
        if mode == "radiale":
        
            x = np.linspace(0, self.orbitale.range, 100)
            y = self.orbitale.radial_wave_function(x, self.orbitale.n, self.orbitale.l, self.orbitale.Z)
            x /= self.orbitale.a_0
            
            plot_generato = Plot("Pippo", Mate.stack_attributes(x, y))
            plot_generato.settings([0, 255, 255], True, True, True, False, "linear", 3, 1, 1)
            
            painter.plots.append(plot_generato)
            painter.settings("Componente Radiale", "Raggi di Bohr [a_0]", "Probabilità", ridimensionamento=self.ridimensiona_carattere)

        elif mode == "angolare":
        
            x = np.linspace(0, 2 * pi, 100)
            y = self.orbitale.angular_wave_function(x, 0, self.orbitale.l, self.orbitale.m)
            y = y.real.astype(float)
            
            plot_generato = Plot("Pippo", Mate.stack_attributes(x, y))
            plot_generato.settings([0, 255, 255], True, True, True, False, "linear", 3, 1, 1)
            
            painter.plots.append(plot_generato)
            painter.settings("Componente Angolare", r"\Theta [rad]", "Probabilità", ridimensionamento=self.ridimensiona_carattere)
        
        elif mode == "histogram":
        
            c, e = np.histogram(self.orbitale.probabilit, range=(self.orbitale.probability_threshold,1), bins=100)
            b = (e[1:] + e[:-1]) / 2

            plot_generato = Plot("Pippo", b, c, None)
            plot_generato.settings([0, 255, 255], True, True, True, False, "linear", 3, 1, 1)
            
            painter.plots.append(plot_generato)
            painter.settings("Histogramma di probabilità", r"Probabilità normalizzata", "Conteggi", ridimensionamento=self.ridimensiona_carattere)


    def disegna(self, logica: Logica):

        self.schermo.fill(self.bg_color)
        self.plot.disegna(logica)
        self.plot2.disegna(logica)

        if self.mode == "3D":

            self.orbitale.camera.aggiorna_attributi(logica)
            self.orbitale.camera.rotazione_camera()

            self.orbitale.modello.i += 0.001

            self.orbitale.modello.sy = 2 / self.orbitale.a_0
            self.orbitale.modello.sz = 2 / self.orbitale.a_0
            self.orbitale.modello.sx = 2 / self.orbitale.a_0 

            self.orbitale.modello.applica_rotazioni()
            self.orbitale.modello.applica_traslazioni()


            self.orbitale.modello.transformed_vertices @= Mate.camera_world(self.orbitale.camera) 
            self.orbitale.modello.transformed_vertices @= Mate.screen_world() 
            
            grafica_funzione_bool = self.orbitale.attribute("schrodinger")
            
            if grafica_funzione_bool:
                self.grafica_funzione(self.plot, "radiale")
                self.grafica_funzione(self.plot2, "angolare")

            self.orbitale.fast_color()
            # self.orbitale.dist_sort()

            self.orbitale.modello.transformed_vertices @= Mate.frustrum(self.w, self.h, self.orbitale.camera.fov) 
            self.orbitale.modello.transformed_vertices = Mate.proiezione(self.orbitale.modello.transformed_vertices) 

            self.orbitale.modello.transformed_vertices @= Mate.centra_schermo(self.w, self.h) 

            filtro_size = self.orbitale.dimensions[self.orbitale.mask] > 0

            colori_render = self.orbitale.colori_int8[self.orbitale.mask][filtro_size]
            vertici = self.orbitale.modello.transformed_vertices[:, :2][self.orbitale.mask][filtro_size]
            dimensione = self.orbitale.dimensions[self.orbitale.mask][filtro_size]

            for color, pos, size in zip(colori_render, vertici, dimensione):
                pygame.draw.circle(self.schermo, color, [pos[0], pos[1]], size) 
        
        if self.mode == "2D":

            grafica_funzione_bool = self.orbitale.attribute("schrodinger")
            
            if grafica_funzione_bool:
                self.grafica_funzione(self.plot, "radiale")
                self.grafica_funzione(self.plot2, "angolare")

   
            if self.samples < 1:

                import time; start = time.perf_counter()

                ind_x, ind_y = np.indices((self.w, self.h))
                ind_x, ind_y = np.ravel(ind_x), np.ravel(ind_y)
                y = np.zeros((self.w * self.h))

                ind_x_calc, ind_y_calc =  - 1 + 2 * ind_x / self.w, - 1 + 2 * ind_y / self.h
                
                pol = Mate.car2pol(Mate.stack_attributes(ind_x_calc, y, ind_y_calc))
                pol[:, 0] *= self.orbitale.range

                self.background[ind_x, ind_y] = Orbitale.hydrogenoid_wave_function(self.orbitale, pol[:, 0], pol[:, 1], pol[:, 2], self.orbitale.n, self.orbitale.l, self.orbitale.m, self.orbitale.Z).real.astype(float)
                self.background = np.nan_to_num(self.background)

                self.colori = self.background.copy()
                self.colori -= np.min(self.colori)
                self.colori /= np.max(self.colori)
                self.colori = self.orbitale.color_ramp(np.ravel(self.colori), 0).reshape(self.w, self.h, 3) * 255

                self.colori = self.colori.astype(np.uint8)

                self.samples += 1
                

            colors_surface = pygame.surfarray.make_surface(self.colori)  
            self.schermo.blit(colors_surface, (0, 0))
