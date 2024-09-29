from _modulo_UI import LabelText, Button, MultiBox, TabUI, Entrata, Path, ScrollConsole, UI_signs, Schermo, Logica, Scena
from _modulo_database_tooltips import Dizionario

diction = Dizionario()


def add_tooltip(oggetto, index):
        oggetto.tooltip = diction.tooltips[index]


def build_main(self):
    # LABEL
    # --------------------------------------------------------------------------------
    # statici
    self.label_text["memory"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=81, y=98, text="Memory usage: X MB", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["battery"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=72, y=98, text="Battery: X%", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["fps"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=66, y=98, text="FPS: X", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["cpu"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=59, y=98, text="CPU usage: X%", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["clock"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=92, y=98, text="00:00, 1/1/2000", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    
    # BOTTONI
    # --------------------------------------------------------------------------------
    # scelta TAB
    indice_scena = int(self.config.get('Default', 'scena_iniziale'))

    toggled = True if indice_scena == 0 else False
    self.bottoni["plots"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=2, y=2, text="PLOTS", multi_box=True, toggled=toggled, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    toggled = True if indice_scena == 1 else False
    self.bottoni["plots2D"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=8.1, y=2, text="PLOT 2D", multi_box=True, toggled=toggled, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    toggled = True if indice_scena == 2 else False
    self.bottoni["plot_import"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=14.2, y=2, text="PLOT IMPORT", multi_box=True, toggled=toggled, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    toggled = True if indice_scena == 3 else False
    self.bottoni["tracer"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=20.3, y=2, text="RAY-TRACER", multi_box=True, toggled=toggled, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    toggled = True if indice_scena == 4 else False
    self.bottoni["orbitals"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=26.4, y=2, text="ORBITALI", multi_box=True, toggled=toggled, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    
    self.multi_box["active_scene"] = MultiBox([self.bottoni["plots"],self.bottoni["plots2D"],self.bottoni["tracer"],self.bottoni["orbitals"], self.bottoni["plot_import"]])
    
    # TABS LINK
    self.tabs["sys_info"] = TabUI(name="sys_info", 
        labels=[self.label_text["memory"], self.label_text["battery"], self.label_text["fps"], self.label_text["cpu"], self.label_text["clock"]]
    )

    self.tabs["scene_manager"] = TabUI(name="scene_manager", 
        bottoni=[self.bottoni["plots"], self.bottoni["plots2D"], self.bottoni["tracer"], self.bottoni["orbitals"], self.bottoni["plot_import"]],
        multi_boxes=[self.multi_box["active_scene"]]
    )

    [add_tooltip(elemento, index) for index, elemento in self.bottoni.items()]
    [add_tooltip(elemento, index) for index, elemento in self.entrate.items()]


def build_plots(self):
    # LABEL
    # --------------------------------------------------------------------------------
    # interpolazioni
    self.label_text["params"] = LabelText(self.parametri_repeat_elementi, self.fonts, w=10, h=1.8, x=60, y=26, renderizza_bg=False, text="Seleziona un tipo di interpolazione.\nSuccessivamente schiaccia il bottone 'Compute Interpolation'", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["FID"]  = LabelText(self.parametri_repeat_elementi, self.fonts, w=10, h=1.8, x=60, y=66, renderizza_bg=False, text="", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["metadata"] = LabelText(self.parametri_repeat_elementi, self.fonts, size="piccolo", w=37, h=1.8, x=61, y=50, renderizza_bg=True, text="Prova metadata", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["salvato_con_successo"] = LabelText(self.parametri_repeat_elementi, self.fonts, w=10, h=1.8, x=67.5, y=67.5, renderizza_bg=False, text="Salvato con successo!", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=[100,255,100], autodistruggi=True)
    # --------------------------------------------------------------------------------

    # BOTTONI
    # --------------------------------------------------------------------------------
    # statici
    self.bottoni["zero_y"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=40, text="Visualizza zero", toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["grad_vert"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=37, text="Grad. Verticale", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["grad_hori"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=35, text="Grad. Orizzontale", multi_box=True, toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.multi_box["grad_mode"] = MultiBox([self.bottoni["grad_vert"], self.bottoni["grad_hori"]])

    self.bottoni["latex_check"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=42, text="str to LaTeX", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["toggle_2_axis"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=44, text="Toggle 2° axis", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["toggle_plot_bb"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=46, text="Toggle plot ax", toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["normalizza"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=48, text="Normalizza", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["salva"] = Button(self.parametri_repeat_elementi, self.fonts, w=3.8/1.6, h=3.8, x=70, y=59, tipologia="push", texture="UI_save", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["use_custom_borders"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=47.5, y=96, text="Cust. ranges", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    
    # dinamici
    self.bottoni["toggle_inter"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=89, y=44, text="Interpol", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["toggle_errorbar"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=82, y=42, text="Barre errori", toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["toggle_pallini"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=82, y=44, text="Pallini", toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["toggle_collegamenti"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=82, y=46, text="Links", toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["gradiente"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=82, y=40, text="Gradiente", toggled=False, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    
    # interpolazioni
    self.bottoni["usa_poly"] = Button(self.parametri_repeat_elementi, self.fonts, w=9, h=1.8, x=60, y=16, text="Linear interpolation", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["usa_gaussi"] = Button(self.parametri_repeat_elementi, self.fonts, w=9, h=1.8, x=70, y=16, text="Gaussian interpolation", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["usa_sigmoi"] = Button(self.parametri_repeat_elementi, self.fonts, w=9, h=1.8, x=80, y=16, text="Sigmoid interpolation", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["comp_inter"] = Button(self.parametri_repeat_elementi, self.fonts, "grande", w=9, h=3.6, x=90, y=16, text="COMPUTE", tipologia="push", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.multi_box["interpol_mode"] = MultiBox([self.bottoni["usa_poly"],self.bottoni["usa_gaussi"],self.bottoni["usa_sigmoi"]])
    self.bottoni["save_deriv"] = Button(self.parametri_repeat_elementi, self.fonts, w=9, h=1.8, x=62, y=90, text="Salva derivata", tipologia="push", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    
    # scelta TAB
    self.bottoni["tab_settings"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=70, y=6+2, text="UI settings", multi_box=True, toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["tab_plt"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=77, y=6+2, text="Plot settings", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["tab_stats"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=84, y=6+2, text="Statistics", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.multi_box["active_tab"] = MultiBox([self.bottoni["tab_settings"],self.bottoni["tab_plt"],self.bottoni["tab_stats"]])
    # --------------------------------------------------------------------------------


    # ENTRATE
    # --------------------------------------------------------------------------------
    # statiche
    self.entrate["titolo"] = Entrata("titolo", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=15, text="", titolo="Titolo", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["labelx"] = Entrata("labelx", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=19, text="", titolo="Label X", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["labely"] = Entrata("labely", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=21, text="", titolo="Label Y (sx)", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["label2y"] = Entrata("label2y", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=23, text="", titolo="Label Y (dx)", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["font_size"] = Entrata("font_size", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=32, text=f"{self.fonts['grande'].dim_font}", titolo="Font size", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["round_label_x"] = Entrata("round_label_x", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=34, text="2", titolo="X Round to", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["subdivisions_x"] = Entrata("subdivisions_x", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=38, text="5", titolo="X Subdivisions", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["round_label_y"] = Entrata("round_label_y", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=36, text="2", titolo="Y Round to", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["subdivisions_y"] = Entrata("subdivisions_y", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=40, text="5", titolo="Y Subdivisions", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["color_bg"] = Entrata("color_bg", self.parametri_repeat_elementi, self.fonts, w=3.5, h=1.8, x=86.5, y=30, text="#1e1e1e", titolo="Colore bg", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["color_text"] = Entrata("color_text", self.parametri_repeat_elementi, self.fonts, w=3.5, h=1.8, x=86.5, y=32, text="#b4b4b4", titolo="Colore UI", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["x_legenda"] = Entrata("x_legenda", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=70, y=46, text=".2", titolo="x legenda", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y_legenda"] = Entrata("y_legenda", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=70, y=48, text=".3", titolo="y legenda", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["ui_spessore"] = Entrata("ui_spessore", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=30, text="1", titolo="UI spessore", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["x_foto"] = Entrata("x_foto", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=80, y=59, text="3240", titolo="Res X foto", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y_foto"] = Entrata("y_foto", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=80, y=61, text="3240", titolo="Res Y foto", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["DPI"] = Entrata("DPI", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=87, y=59, text="300", titolo="DPI", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))

    self.paths["caricamento"] = Path("caricamento", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=55, text="PLOT_DATA\\default", titolo="Input path", bg=eval(self.config.get(self.tema, 'entrata_bg')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')))

    # dinamiche
    self.entrate["nome_grafico"] = Entrata("nome_grafico", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=15, text="Plot 1", titolo="Nome", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["color_plot"] = Entrata("color_plot", self.parametri_repeat_elementi, self.fonts, w=3.5, h=1.8, x=76, y=40, text="#dc143c", titolo="Colore graf.", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["dim_pallini"] = Entrata("dim_pallini", self.parametri_repeat_elementi, self.fonts, w=1, h=1.8, x=76, y=44, text="1", titolo="Dim. pallini", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["dim_link"] = Entrata("dim_link", self.parametri_repeat_elementi, self.fonts, w=1, h=1.8, x=76, y=46, text="1", titolo="Dim. links", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["x_column"] = Entrata("x_column", self.parametri_repeat_elementi, self.fonts, w=1, h=1.8, x=66, y=40, text="0", titolo="Ind. colonna X", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y_column"] = Entrata("y_column", self.parametri_repeat_elementi, self.fonts, w=1, h=1.8, x=66, y=42, text="1", titolo="Ind. colonna Y", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["ey_column"] = Entrata("ey_column", self.parametri_repeat_elementi, self.fonts, w=1, h=1.8, x=66, y=44, text="2", titolo="Ind. colonna eY", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    
    # ui stuff
    self.entrate["x_min"] = Entrata("x_min", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=12.5, y=96, text="", titolo="inter. X min", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["x_max"] = Entrata("x_max", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=22.5, y=96, text="", titolo="inter. X max", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y_min"] = Entrata("y_min", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=32.5, y=96, text="", titolo="inter. Y min", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y_max"] = Entrata("y_max", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=42.5, y=96, text="", titolo="inter. Y max", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    
    # interpolazioni
    self.entrate["grado_inter"] = Entrata("grado_inter", self.parametri_repeat_elementi, self.fonts, w=1, h=1.8, x=68, y=19, text="1", titolo="Grado Interpolazione:", visibile=False, bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    # --------------------------------------------------------------------------------


    # SCROLLCONSOLE
    # --------------------------------------------------------------------------------
    # dinamiche
    self.scrolls["grafici"] = ScrollConsole(self.parametri_repeat_elementi, self.fonts, w=20, h=16, x=70, y=20, titolo="Scelta grafici / data plot", bg=eval(self.config.get(self.tema, 'scroll_bg')), color_text=eval(self.config.get(self.tema, 'scroll_color_text')), colore_selezionato=eval(self.config.get(self.tema, 'scroll_colore_selezionato')), titolo_colore=eval(self.config.get(self.tema, 'scroll_titolo_colore')))

    # UI SIGNS
    # --------------------------------------------------------------------------------
    # statiche
    self.ui_signs["tab_titolo"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=12.5, x2=98, y2=12.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["titolo_settings"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=27.5, x2=98, y2=27.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["settings_import"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=52.5, x2=98, y2=52.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["import_end"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=65, x2=98, y2=65, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["columns_settings"] = UI_signs(self.parametri_repeat_elementi, x1=80, y1=30, x2=80, y2=50, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))

    self.ui_signs["tab_titolo_plot"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=12.5, x2=98, y2=12.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["titolo_settings_plot"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=38, x2=98, y2=38, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))

    self.ui_signs["tab_titolo_stats"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=12.5, x2=98, y2=12.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["titolo_FID_stats"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=62, x2=98, y2=62, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))


    segni_ancora = []
    for i in range(100):
        # if i % 10 == 0:
            spessore = 5 if i % 10 == 0 else 2
            colore = (100, 100, 100) if i % 10 == 0 else (50, 50, 50)
            self.ui_signs[f"{i=} x"] = UI_signs(self.parametri_repeat_elementi, x1=i, y1=0, x2=i, y2=100, spessore=spessore, bg=colore)
            self.ui_signs[f"{i=} y"] = UI_signs(self.parametri_repeat_elementi, x1=0, y1=i, x2=100, y2=i, spessore=spessore, bg=colore)
            segni_ancora.append(self.ui_signs[f"{i=} x"])
            segni_ancora.append(self.ui_signs[f"{i=} y"])

    # TABS LINK
    self.tabs["viewport_control"] = TabUI(name="viewport_control", 
        labels=[self.label_text["salvato_con_successo"]],
        bottoni=[self.bottoni["use_custom_borders"]],
        entrate=[self.entrate["x_min"], self.entrate["x_max"], self.entrate["y_min"], self.entrate["y_max"]],
        # ui_signs=segni_ancora
    )

    self.tabs["ui_control"] = TabUI(name="ui_control", 
        bottoni=[self.bottoni["zero_y"], self.bottoni["grad_vert"], self.bottoni["grad_hori"], self.bottoni["latex_check"], self.bottoni["toggle_2_axis"], self.bottoni["toggle_plot_bb"], self.bottoni["normalizza"], self.bottoni["salva"]],
        entrate=[self.entrate["titolo"], self.entrate["labelx"], self.entrate["labely"], self.entrate["label2y"], self.entrate["ui_spessore"], self.entrate["font_size"], self.entrate["round_label_x"], self.entrate["subdivisions_x"], self.entrate["round_label_y"], self.entrate["subdivisions_y"], self.entrate["color_bg"], self.entrate["color_text"], self.entrate["x_legenda"], self.entrate["y_legenda"], self.entrate["x_foto"], self.entrate["y_foto"], self.entrate["DPI"]],
        paths=[self.paths["caricamento"]],
        ui_signs=[self.ui_signs["tab_titolo"], self.ui_signs["titolo_settings"], self.ui_signs["settings_import"], self.ui_signs["columns_settings"], self.ui_signs["import_end"]],
        multi_boxes=[self.multi_box["grad_mode"]]
    )
    
    self.tabs["plot_control"] = TabUI(name="plot_control", renderizza=False, abilita=False,
        scroll_consoles=[self.scrolls["grafici"]],
        ui_signs=[self.ui_signs["tab_titolo_plot"], self.ui_signs["titolo_settings_plot"]],
        bottoni=[self.bottoni["toggle_errorbar"], self.bottoni["toggle_inter"], self.bottoni["toggle_pallini"], self.bottoni["toggle_collegamenti"], self.bottoni["gradiente"]],
        entrate=[self.entrate["nome_grafico"], self.entrate["x_column"], self.entrate["y_column"], self.entrate["ey_column"], self.entrate["color_plot"], self.entrate["dim_pallini"], self.entrate["dim_link"]],
        labels=[self.label_text["metadata"]]
    )
    
    self.tabs["stats_control"] = TabUI(name="stats_control", renderizza=False, abilita=False,
        labels=[self.label_text["params"], self.label_text["FID"]],
        entrate=[self.entrate["grado_inter"]],
        bottoni=[self.bottoni["usa_poly"], self.bottoni["usa_gaussi"], self.bottoni["usa_sigmoi"], self.bottoni["comp_inter"], self.bottoni["save_deriv"]],
        multi_boxes=[self.multi_box["interpol_mode"]],
        ui_signs=[self.ui_signs["tab_titolo_stats"], self.ui_signs["titolo_FID_stats"]]
    )

    self.tabs["tab_control"] = TabUI(name="tab_control", 
        bottoni=[self.bottoni["tab_settings"], self.bottoni["tab_plt"], self.bottoni["tab_stats"]],
        multi_boxes=[self.multi_box["active_tab"]]
    )


    self.schermo["viewport"] = Schermo(self.parametri_repeat_elementi)

    [add_tooltip(elemento, index) for index, elemento in self.bottoni.items()]
    [add_tooltip(elemento, index) for index, elemento in self.entrate.items()]
    [add_tooltip(elemento, index) for index, elemento in self.paths.items()]


def build_plot_2D(self):
    # LABEL
    # --------------------------------------------------------------------------------
    # interpolazioni
    self.label_text["params"] = LabelText(self.parametri_repeat_elementi, self.fonts, w=10, h=1.8, x=60, y=26, renderizza_bg=False, text="Seleziona un tipo di interpolazione.\nSuccessivamente schiaccia il bottone 'Compute Interpolation'", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["FID"]  = LabelText(self.parametri_repeat_elementi, self.fonts, w=10, h=1.8, x=60, y=66, renderizza_bg=False, text="", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["metadata"] = LabelText(self.parametri_repeat_elementi, self.fonts, size="piccolo", w=37, h=1.8, x=61, y=50, renderizza_bg=True, text="Prova metadata", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["salvato_con_successo"] = LabelText(self.parametri_repeat_elementi, self.fonts, w=10, h=1.8, x=67.5, y=67.5, renderizza_bg=False, text="Salvato con successo!", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=[100,255,100], autodistruggi=True)
    # --------------------------------------------------------------------------------

    # BOTTONI
    # --------------------------------------------------------------------------------
    # statici
    self.bottoni["latex_check"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=42, text="str to LaTeX", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["toggle_2_axis"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=44, text="Toggle 2° axis", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["toggle_plot_bb"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=82, y=46, text="Toggle plot ax", toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["salva"] = Button(self.parametri_repeat_elementi, self.fonts, w=3.8/1.6, h=3.8, x=70, y=59, tipologia="push", texture="UI_save", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["use_custom_borders"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=47.5, y=96, text="Cust. ranges", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    
    # scelta TAB
    self.bottoni["tab_settings"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=70, y=6+2, text="UI settings", multi_box=True, toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["tab_plt"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=77, y=6+2, text="Plot settings", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.multi_box["active_tab"] = MultiBox([self.bottoni["tab_settings"],self.bottoni["tab_plt"]])
    # --------------------------------------------------------------------------------


    # ENTRATE
    # --------------------------------------------------------------------------------
    # statiche
    self.entrate["titolo"] = Entrata("titolo", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=15, text="", titolo="Titolo", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["labelx"] = Entrata("labelx", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=19, text="", titolo="Label X", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["labely"] = Entrata("labely", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=21, text="", titolo="Label Y (sx)", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["label2y"] = Entrata("label2y", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=23, text="", titolo="Label Y (dx)", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["font_size"] = Entrata("font_size", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=32, text=f"{self.fonts['grande'].dim_font}", titolo="Font size", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["round_label_x"] = Entrata("round_label_x", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=34, text="2", titolo="Round to", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["subdivisions_x"] = Entrata("subdivisions_x", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=36, text="5", titolo="Subdivisions", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["color_bg"] = Entrata("color_bg", self.parametri_repeat_elementi, self.fonts, w=3.5, h=1.8, x=86.5, y=30, text="#1e1e1e", titolo="Colore bg", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["color_text"] = Entrata("color_text", self.parametri_repeat_elementi, self.fonts, w=3.5, h=1.8, x=86.5, y=32, text="#b4b4b4", titolo="Colore UI", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["ui_spessore"] = Entrata("ui_spessore", self.parametri_repeat_elementi, self.fonts, w=1.5, h=1.8, x=70, y=30, text="1", titolo="UI spessore", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["x_foto"] = Entrata("x_foto", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=80, y=59, text="3240", titolo="Res X foto", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y_foto"] = Entrata("y_foto", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=80, y=61, text="3240", titolo="Res Y foto", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["DPI"] = Entrata("DPI", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=87, y=59, text="300", titolo="DPI", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))

    self.paths["caricamento"] = Path("caricamento", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=55, text="PLOT_DATA\\default", titolo="Input path", bg=eval(self.config.get(self.tema, 'entrata_bg')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')))

    # dinamiche
    self.entrate["nome_grafico"] = Entrata("nome_grafico", self.parametri_repeat_elementi, self.fonts, w=20, h=1.8, x=70, y=15, text="Plot 1", titolo="Nome", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    
    # ui stuff
    self.entrate["x_min"] = Entrata("x_min", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=12.5, y=96, text="", titolo="inter. X min", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["x_max"] = Entrata("x_max", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=22.5, y=96, text="", titolo="inter. X max", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y_min"] = Entrata("y_min", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=32.5, y=96, text="", titolo="inter. Y min", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y_max"] = Entrata("y_max", self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=42.5, y=96, text="", titolo="inter. Y max", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    

    # SCROLLCONSOLE
    # --------------------------------------------------------------------------------
    # dinamiche
    self.scrolls["grafici"] = ScrollConsole(self.parametri_repeat_elementi, self.fonts, w=20, h=16, x=70, y=20, titolo="Scelta grafici / data plot", bg=eval(self.config.get(self.tema, 'scroll_bg')), color_text=eval(self.config.get(self.tema, 'scroll_color_text')), colore_selezionato=eval(self.config.get(self.tema, 'scroll_colore_selezionato')), titolo_colore=eval(self.config.get(self.tema, 'scroll_titolo_colore')))

    # UI SIGNS
    # --------------------------------------------------------------------------------
    # statiche
    self.ui_signs["tab_titolo"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=12.5, x2=98, y2=12.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["titolo_settings"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=27.5, x2=98, y2=27.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["settings_import"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=52.5, x2=98, y2=52.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["import_end"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=65, x2=98, y2=65, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["columns_settings"] = UI_signs(self.parametri_repeat_elementi, x1=80, y1=30, x2=80, y2=50, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))

    self.ui_signs["tab_titolo_plot"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=12.5, x2=98, y2=12.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["titolo_settings_plot"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=38, x2=98, y2=38, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))


    segni_ancora = []
    for i in range(100):
        # if i % 10 == 0:
            spessore = 5 if i % 10 == 0 else 2
            colore = (100, 100, 100) if i % 10 == 0 else (50, 50, 50)
            self.ui_signs[f"{i=} x"] = UI_signs(self.parametri_repeat_elementi, x1=i, y1=0, x2=i, y2=100, spessore=spessore, bg=colore)
            self.ui_signs[f"{i=} y"] = UI_signs(self.parametri_repeat_elementi, x1=0, y1=i, x2=100, y2=i, spessore=spessore, bg=colore)
            segni_ancora.append(self.ui_signs[f"{i=} x"])
            segni_ancora.append(self.ui_signs[f"{i=} y"])

    # TABS LINK
    self.tabs["viewport_control"] = TabUI(name="viewport_control", 
        labels=[self.label_text["salvato_con_successo"]],
        bottoni=[self.bottoni["use_custom_borders"]],
        entrate=[self.entrate["x_min"], self.entrate["x_max"], self.entrate["y_min"], self.entrate["y_max"]],
        # ui_signs=segni_ancora
    )

    self.tabs["ui_control"] = TabUI(name="ui_control", 
        bottoni=[self.bottoni["latex_check"], self.bottoni["toggle_2_axis"], self.bottoni["toggle_plot_bb"], self.bottoni["salva"]],
        entrate=[self.entrate["titolo"], self.entrate["labelx"], self.entrate["labely"], self.entrate["label2y"], self.entrate["ui_spessore"], self.entrate["font_size"], self.entrate["round_label_x"], self.entrate["subdivisions_x"], self.entrate["color_bg"], self.entrate["color_text"], self.entrate["x_foto"], self.entrate["y_foto"], self.entrate["DPI"]],
        paths=[self.paths["caricamento"]],
        ui_signs=[self.ui_signs["tab_titolo"], self.ui_signs["titolo_settings"], self.ui_signs["settings_import"], self.ui_signs["columns_settings"], self.ui_signs["import_end"]],
    )
    
    self.tabs["plot_control"] = TabUI(name="plot_control", renderizza=False, abilita=False,
        scroll_consoles=[self.scrolls["grafici"]],
        ui_signs=[self.ui_signs["tab_titolo_plot"], self.ui_signs["titolo_settings_plot"]],
        labels=[self.label_text["metadata"]]
    )

    self.tabs["tab_control"] = TabUI(name="tab_control", 
        bottoni=[self.bottoni["tab_settings"], self.bottoni["tab_plt"]],
        multi_boxes=[self.multi_box["active_tab"]]
    )


    self.schermo["viewport"] = Schermo(self.parametri_repeat_elementi)

    [add_tooltip(elemento, index) for index, elemento in self.bottoni.items()]
    [add_tooltip(elemento, index) for index, elemento in self.entrate.items()]
    [add_tooltip(elemento, index) for index, elemento in self.paths.items()]


def build_plot_import(self):

    self.label_text["progresso"] = LabelText(self.parametri_repeat_elementi, self.fonts, w=10, h=1.8, x=65, y=50, renderizza_bg=False, text="Step 0", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["salvato_con_successo"] = LabelText(self.parametri_repeat_elementi, self.fonts, w=10, h=1.8, x=67.5, y=41, renderizza_bg=False, text="Salvato con successo!", bg=eval(self.config.get(self.tema, 'label_bg')), color_text=[100,255,100], autodistruggi=True)
    
    self.bottoni["calibrazione"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=70, y=20, text="Calibrazione", multi_box=True, toggled=False, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["inserimento"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=80, y=20, text="Inserimento", toggled=False, multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.multi_box["active_mode"] = MultiBox([self.bottoni["calibrazione"], self.bottoni["inserimento"]])

    self.bottoni["path_export"] = Button(self.parametri_repeat_elementi, self.fonts, w=3.8/1.6, h=3.8, x=70, y=40, tipologia="push", texture="UI_save", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))

    self.paths["path_import"] = Path("path_import", self.parametri_repeat_elementi, self.fonts, w=15, h=1.8, x=70, y=15, tipologia="file", text="INPUT\\test_graf_import.png", titolo="Path import img.", bg=eval(self.config.get(self.tema, 'entrata_bg')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')))
    self.entrate["x1"] = Entrata("x1", self.parametri_repeat_elementi, self.fonts, w=5, h=1.8, x=70, y=25, text="", titolo="X punto 1", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["x2"] = Entrata("x2", self.parametri_repeat_elementi, self.fonts, w=5, h=1.8, x=70, y=27, text="", titolo="X punto 2", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y1"] = Entrata("y1", self.parametri_repeat_elementi, self.fonts, w=5, h=1.8, x=70, y=29, text="", titolo="Y punto 3", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["y2"] = Entrata("y2", self.parametri_repeat_elementi, self.fonts, w=5, h=1.8, x=70, y=31, text="", titolo="Y punto 4", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    
    self.schermo["viewport"] = Schermo(self.parametri_repeat_elementi)

    self.tabs["calibrazione"] = TabUI(name="calibrazione", 
        labels=[self.label_text["progresso"], self.label_text["salvato_con_successo"]],
        bottoni=[self.bottoni["path_export"], self.bottoni["calibrazione"], self.bottoni["inserimento"]],
        entrate=[self.entrate["x1"], self.entrate["x2"], self.entrate["y1"], self.entrate["y2"]],
        multi_boxes=[self.multi_box["active_mode"]],
        paths=[self.paths["path_import"]]
    )

    [add_tooltip(elemento, index) for index, elemento in self.bottoni.items()]
    [add_tooltip(elemento, index) for index, elemento in self.entrate.items()]
    [add_tooltip(elemento, index) for index, elemento in self.paths.items()]


def build_tracer(self):
    # BOTTONI
    # --------------------------------------------------------------------------------
    # editor
    self.bottoni["points"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=65, y=17, text="Points", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["links"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=65, y=20, text="Links", toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["add_sphere"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=65, y=24, text="+ sfera", tipologia="push", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["remove_sphere"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=65, y=27, text="- sfera", tipologia="push", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["reset"] = Button(self.parametri_repeat_elementi, self.fonts, w=4 / 1.6, h=4, x=60, y=58 - 15, texture="reset_logo", tipologia="push", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["Crender"] = Button(self.parametri_repeat_elementi, self.fonts, w=4 / 1.6, h=4, x=60, y=53.5 - 15, texture="C_logo", tipologia="push", bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    
    # raytracer
    self.bottoni["albedo"] = Button(self.parametri_repeat_elementi, self.fonts, w=4 / 1.6, h=4, x=60, y=24.5 - 15, texture="render_mode1", multi_box=True, toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["ao"] = Button(self.parametri_repeat_elementi, self.fonts, w=4 / 1.6, h=4, x=60, y=20 - 15, texture="render_mode4", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["bounces_tab"] = Button(self.parametri_repeat_elementi, self.fonts, w=4 / 1.6, h=4, x=60, y=29 - 15, texture="render_mode6", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.multi_box["view_mode"] = MultiBox([self.bottoni["albedo"], self.bottoni["ao"], self.bottoni["bounces_tab"]])

    # scelta TAB
    self.bottoni["tab_scene"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=70, y=6+2, text="Scena", multi_box=True, toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["tab_raytracer"] = Button(self.parametri_repeat_elementi, self.fonts, w=7, h=1.8, x=77, y=6+2, text="Render settings", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.multi_box["active_tab"] = MultiBox([self.bottoni["tab_scene"],self.bottoni["tab_raytracer"]])
    # --------------------------------------------------------------------------------


    # LABEL
    # --------------------------------------------------------------------------------
    # editor
    self.label_text["active_object"] = LabelText(self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=63, y=35, text="Oggetto selezionato:", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["materiale"] = LabelText(self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=63, y=51, text="Materiale:", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
    self.label_text["eta"] = LabelText(self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=65 - 25, text="Inizia la renderizzazione per le statistiche", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))

    # ENTRATE
    # --------------------------------------------------------------------------------
    # editor
    self.entrate["px_modello"] = Entrata("px_modello", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=39, text="", titolo="Posizione X:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["py_modello"] = Entrata("py_modello", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=41, text="", titolo="Posizione Y:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["pz_modello"] = Entrata("pz_modello", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=43, text="", titolo="Posizione Z:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    
    self.entrate["rx_modello"] = Entrata("rx_modello", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=80, y=39, text="", titolo="Rotazione X:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["ry_modello"] = Entrata("ry_modello", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=80, y=41, text="", titolo="Rotazione Y:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["rz_modello"] = Entrata("rz_modello", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=80, y=43, text="", titolo="Rotazione Z:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    
    self.entrate["sx_modello"] = Entrata("sx_modello", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=90, y=39, text="", titolo="Scala X:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["sy_modello"] = Entrata("sy_modello", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=90, y=41, text="", titolo="Scala Y:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["sz_modello"] = Entrata("sz_modello", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=90, y=43, text="", titolo="Scala Z:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    
    self.entrate["colore_diff"] = Entrata("colore_diff", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=55, text="#ffffff", titolo="colore_diff:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["colore_emis"] = Entrata("colore_emis", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=57, text="#ffffff", titolo="colore_emis:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["forza_emis"] = Entrata("forza_emis", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=59, text="5", titolo="forza_emis:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["roughness"] = Entrata("roughness", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=61, text="1", titolo="roughness:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["glossiness"] = Entrata("glossiness", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=63, text="1", titolo="glossiness:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["glass"] = Entrata("glass", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=65, text="1", titolo="glass:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["IOR"] = Entrata("IOR", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=70, y=67, text="1.5", titolo="IOR:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    
    # raytracer
    self.entrate["samples"] = Entrata("samples", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=80, y=45 - 25, text="32", titolo="Samples:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["bounces"] = Entrata("bounces", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=80, y=47 - 25, text="6", titolo="Bounces:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["resolution_x"] = Entrata("resolution_x", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=80, y=51 - 25, text="10", titolo="Res X (%):", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["resolution_y"] = Entrata("resolution_y", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=80, y=53 - 25, text="10", titolo="Res Y (%):", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    self.entrate["cores"] = Entrata("cores", self.parametri_repeat_elementi, self.fonts, w=4, h=1.8, x=80, y=55 - 25, text="16", titolo="Cores:", bg=eval(self.config.get(self.tema, 'entrata_bg')), bg_toggled=eval(self.config.get(self.tema, 'entrata_bg_toggled')), color_text=eval(self.config.get(self.tema, 'entrata_color_text')), text_toggled=eval(self.config.get(self.tema, 'entrata_color_text_toggled')), contorno=eval(self.config.get(self.tema, 'entrata_contorno')), contorno_toggled=eval(self.config.get(self.tema, 'entrata_contorno_toggled')), color_puntatore=eval(self.config.get(self.tema, 'entrata_color_puntatore')))
    
    # SCROLLCONSOLE
    # --------------------------------------------------------------------------------
    # editor
    self.scrolls["oggetti"] = ScrollConsole(self.parametri_repeat_elementi, self.fonts, w=20, h=16, x=75, y=15, titolo="Scelta oggetti scena", bg=eval(self.config.get(self.tema, 'scroll_bg')), color_text=eval(self.config.get(self.tema, 'scroll_color_text')), colore_selezionato=eval(self.config.get(self.tema, 'scroll_colore_selezionato')), titolo_colore=eval(self.config.get(self.tema, 'scroll_titolo_colore')), cambio_ordine=False, all_on=True)

    # UI SIGNS
    # --------------------------------------------------------------------------------
    # editor
    self.ui_signs["tab_titolo"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=12.5, x2=98, y2=12.5, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["titolo_props"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=33, x2=98, y2=33, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    self.ui_signs["props_settings"] = UI_signs(self.parametri_repeat_elementi, x1=61, y1=48, x2=98, y2=48, spessore=2, bg=eval(self.config.get(self.tema, 'UI_signs')))
    

    segni_ancora = []
    for i in range(100):
        # if i % 10 == 0:
            spessore = 5 if i % 10 == 0 else 2
            colore = (100, 100, 100) if i % 10 == 0 else (50, 50, 50)
            self.ui_signs[f"{i=} x"] = UI_signs(self.parametri_repeat_elementi, x1=i, y1=0, x2=i, y2=100, spessore=spessore, bg=colore)
            self.ui_signs[f"{i=} y"] = UI_signs(self.parametri_repeat_elementi, x1=0, y1=i, x2=100, y2=i, spessore=spessore, bg=colore)
            segni_ancora.append(self.ui_signs[f"{i=} x"])
            segni_ancora.append(self.ui_signs[f"{i=} y"])


    self.tabs["scena_settings"] = TabUI(name="scena_settings", 
        bottoni=[self.bottoni["points"],self.bottoni["links"], self.bottoni["add_sphere"], self.bottoni["remove_sphere"]],
        ui_signs=[self.ui_signs["tab_titolo"], self.ui_signs["titolo_props"], self.ui_signs["props_settings"]],
        scroll_consoles=[self.scrolls["oggetti"]],
        entrate=[self.entrate["px_modello"],self.entrate["py_modello"],self.entrate["pz_modello"],self.entrate["rx_modello"],self.entrate["ry_modello"],self.entrate["rz_modello"],self.entrate["sx_modello"],self.entrate["sy_modello"],self.entrate["sz_modello"], self.entrate["colore_diff"], self.entrate["colore_emis"], self.entrate["forza_emis"], self.entrate["roughness"], self.entrate["glossiness"], self.entrate["glass"], self.entrate["IOR"]],
        labels=[self.label_text["active_object"], self.label_text["materiale"]]
    )

    
    self.tabs["tracer_settings"] = TabUI(name="tracer_settings", abilita=False, renderizza=False,
        labels=[self.label_text["eta"]],
        bottoni=[self.bottoni["Crender"], self.bottoni["reset"], self.bottoni["albedo"], self.bottoni["ao"], self.bottoni["bounces_tab"]],
        multi_boxes=[self.multi_box["view_mode"]],
        entrate=[self.entrate["samples"], self.entrate["bounces"], self.entrate["resolution_x"], self.entrate["resolution_y"], self.entrate["cores"]]
    )
    
    
    self.tabs["tab_control"] = TabUI(name="tab_control", 
        bottoni=[self.bottoni["tab_scene"], self.bottoni["tab_raytracer"]],
        multi_boxes=[self.multi_box["active_tab"]]
    )

    self.schermo["viewport"] = Schermo(self.parametri_repeat_elementi)

    [add_tooltip(elemento, index) for index, elemento in self.bottoni.items()]
    [add_tooltip(elemento, index) for index, elemento in self.entrate.items()]


def build_orbitals(self):
    # BOTTONI
    # --------------------------------------------------------------------------------
    # editor
    self.bottoni["3D"] = Button(self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=69, y=17, text="3D", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["2D"] = Button(self.parametri_repeat_elementi, self.fonts, w=3, h=1.8, x=65, y=17, text="2D", multi_box=True, toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.multi_box["mode"] = MultiBox([self.bottoni["2D"], self.bottoni["3D"]])

    # scelta TAB
    self.bottoni["tab_graphics"] = Button(self.parametri_repeat_elementi, self.fonts, w=6, h=1.8, x=70, y=6+2, text="Orbitali", multi_box=True, toggled=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.bottoni["tab_settings"] = Button(self.parametri_repeat_elementi, self.fonts, w=8, h=1.8, x=77, y=6+2, text="Graphics settings", multi_box=True, bg=eval(self.config.get(self.tema, 'bottone_bg')), color_text=eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato=eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled=eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno=eval(self.config.get(self.tema, 'bottone_contorno')), bg2=eval(self.config.get(self.tema, 'bottone_bg2')))
    self.multi_box["active_tab"] = MultiBox([self.bottoni["tab_graphics"],self.bottoni["tab_settings"]])
    # --------------------------------------------------------------------------------


    self.tabs["scena_settings"] = TabUI(name="scena_settings", 
        
    )

    
    self.tabs["tracer_settings"] = TabUI(name="tracer_settings", abilita=False, renderizza=False,
        bottoni=[self.bottoni["3D"], self.bottoni["2D"]], 
        multi_boxes=[self.multi_box["mode"]]                                    
    )
    
    
    self.tabs["tab_control"] = TabUI(name="tab_control", 
        bottoni=[self.bottoni["tab_graphics"], self.bottoni["tab_settings"]],
        multi_boxes=[self.multi_box["active_tab"]]
    )

    self.schermo["viewport"] = Schermo(self.parametri_repeat_elementi)
    self.schermo["helper"] = Schermo(self.parametri_repeat_elementi, 30, 30, 65, 15, False)
    self.schermo["helper2"] = Schermo(self.parametri_repeat_elementi, 30, 30, 65, 55, False)

    [add_tooltip(elemento, index) for index, elemento in self.bottoni.items()]
    [add_tooltip(elemento, index) for index, elemento in self.entrate.items()]


Scena.build_main = build_main
Scena.build_plots = build_plots
Scena.build_plot_2D = build_plot_2D
Scena.build_plot_import = build_plot_import
Scena.build_tracer = build_tracer
Scena.build_orbitals = build_orbitals