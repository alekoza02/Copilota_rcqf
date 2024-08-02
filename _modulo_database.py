class Dizionario:
    def __init__(self) -> None:
        
        self.tooltips = {
            "zero_y":               "Abilita la linea dello zero sul grafico.\nIl colore sarà quello dell'UI.",
            "grad_vert":            "Cambia la modalità gradiente in \n'verticale'. Attenzione, viene\ncolorata sempre la parte superiore\ndel grafico e la linea dello zero\nviene ignorata.",
            "grad_hori":            "Cambia la modalità gradiente in \n'orizzontale'. Attenzione, viene\ncolorata sempre l'area dentro al\ngrafico.",
            "latex_check":          "Abilita la sostituzione automatica\ndi determinati caratteri nei\nrelativi segni. Ex: \\lambda -> λ",
            "toggle_2_axis":        "Abilita il secondo asse y, per la\nvisualizzazione delle informazioni\nsul secondo grafico. Funziona\ncorrettamente solo con 2 grafici\naccesi alla volta e l'opzione\n'normalizza' attiva",
            "toggle_plot_bb":       "Abilita la griglia sullo sfondo\ndel grafico",
            "normalizza":           "Forza i 2 grafici ad essere della\nstessa altezza. Riporta inoltre il\nvalore del secondo grafico\nsul secondo asse.",
            "carica":               "Esegue una ricerca sulla cartella\nlocale dell'app. Tutti i grafici\nsaranno situati in 'PLOT_DATA\\...'",
            "salva":                "Salva la schermata attuale del\ngrafico in 'OUTPUT\\file_name.png'",
            "use_custom_borders":   "Abilita il range proposto come i nuovi\nlimiti del grafico",
            "toggle_inter":         "Abilita la visualizzazione\ndell'interpolazione. Vai nella sezione\nstatistics per calcolarla.",
            "toggle_errorbar":      "Abilita la visualizzazione\ndelle barre d'errore, oltre che alla\npossibilità di scegliere la colonna\ndai dati importati.",
            "toggle_pallini":       "Abilita la visualizzazione\ndi pallini in corrispondenza\ndelle coordinate sul grafico.",
            "toggle_collegamenti":  "Abilita il collegamento tra\nle varie coordinate sul grafico.",
            "gradiente":            "Abilita l'area del grafico,\ncolorata seguendo un gradiente\n(specificato nella pagina 'UI_SETTINGS').",
            "usa_poly":             "Specifica il tipo di interpolazione\nda usare: polinomiale.",
            "usa_gaussi":           "Specifica il tipo di interpolazione\nda usare: gaussiana.",
            "usa_sigmoi":           "Specifica il tipo di interpolazione\nda usare: sigmoide.",
            "comp_inter":           "Calcola l'interpolazione, in base\nalla tipologia selezionata.",
            "save_deriv":           "Salva la derivata nel file\n'nome_grafico_derivata.txt'. Attenzione,\nverrà ricaricato tutto l'elenco dei grafici\ne le relative impostazioni.",
            "tab_settings":         "Pagina con le impostazioni\ndell'UI.",
            "tab_plt":              "Pagina con le impostazioni\ndei grafici.",
            "tab_stats":            "Pagina con le impostazioni\ndell'analisi statistica.",
            "points":               "Abilita la visualizzazione\nPoint Cloud dei vertici.",
            "links":                "Abilita la visualizzazione\nWireframe.",
            "add_sphere":           "Aggiunge una sfera alla scena.",
            "remove_sphere":        "Rimuove una sfera dalla scena.",
            "mode1":                "Renderizza la scena contenente sfere.",
            "mode2":                "Resetta la tavolozza e arresta\nla renderizzazione in corso.",
            "indice":               "Mostra il canale basic shader:\n- colore base\n- illuminazione basata sulla normale",
            "albedo":               "Mostra il canale combined:\n- risultato della renderizzazione",
            "normali":              "Mostra il canale normali:\n- RGB -> XYZ\n- map range: [-1,1] -> [0, 255]",
            "ao":                   "Mostra il canale Ambient Occlusion.\nFormula usata:\nΣ (1 / (distance + 1))",
            "tempo":                "Mostra il canale Tempo medio:\n- bianco -> tempo maggiore\n- nero -> tempo minore\n- il primo elemento di ogni chunck\nnon è riportato",
            "bounces_tab":          "Mostra il canale _tab:\n- bianco -> maggior numero di buonces\n- nero -> minor numero di buonces\nTIP: se la mappa è completamente bianca,\naumentare i bounce massimi.",
            "tab_scene":            "Pagina con le impostazioni\nrelative alla scena.",
            "tab_raytracer":        "Pagina con le impostazioni\nrelative al motore di renderizzazione.",
            "3D":                   "Visualizza l'orbitale come:\n- Point Cloud 3D",
            "2D":                   "Visualizza l'orbitale come:\n- Gradient Map 2D",
            "tab_graphics":         "Pagina con la grafica\nrelativa all'orbitale.",
            "tab_settings":         "Pagina con le impostazioni\nrelative all'orbitale.",
            "plots":                "Sezione PLOTS",
            "tracer":               "Sezione RAYTRACER",
            "orbitals":             "Sezione ORBITALI",
            "plot_import":          "Sezione IMPORT PLOT",
            "salva":                "Salva il plot estratto nel path\nindicato di fianco.",
            "carica_import_image":  "Carica l'immagine di riferimento\ndal path indicato.",
            "calibrazione":         "Entra nella modalità calibrazione\nper correttamente estrarre i dati.",
            "inserimento":          "Entra nella modalità estrazione\nper cominciare ad estrarre i dati.",

            "titolo":               "Titolo del grafico.\nSupporta LaTeX",
            "labelx":               "Titolo asse X.\nSupporta LaTeX",
            "labely":               "Titolo asse Y.\nSupporta LaTeX",
            "label2y":              "Titolo del secondo asse Y.\nSupporta LaTeX",
            "font_size":            "Dimensione del testo.\nSe il testo risulta essere tagliato,\nsarà tagliato anche nell'immagine salvata.",
            "round_label":          "Arrotondamento alla n-esima cifra\ndecimale. Applicato su tutti gli\narrotondamenti nella sezione plots.",
            "subdivisions":         "Numero di linee presenti nella griglia del plot.\nAttenzione: numero settori = n - 1",
            "color_bg":             "Indica il colore del background\ndel grafico.",
            "color_text":           "Indica il colore del testo presente\nnel grafico.",
            "area_w":               "Indica la dimensione [0,1] lungo x dedicata al grafico.\nAttenzione, se il secondo asse è disabilitato\nla dimensione minima corrisponderà solo a mezza dimensione.",
            "area_h":               "Indica la dimensione [0,1] lungo y dedicata al grafico.\nAttenzione, se il secondo asse è disabilitato\nla dimensione minima corrisponderà solo a mezza dimensione.",
            "x_legenda":            "Posizione X della legenda tra [0,1].\n(angolo in alto a destra)",
            "y_legenda":            "Posizione Y della legenda tra [0,1].\n(angolo in alto a destra)",
            "caricamento":          "Path alla cartella contenente i grafici.\nDefault path: 'PLOT_DATA\\default'",
            "salvataggio_path":     "Path o nome della cartella dove salvare i grafici.",
            "salvataggio_nome":     "Nome del grafico salvato.\n(Estensione non necessaria)",
            "ui_spessore":          "Spessore degli assi.",
            "nome_grafico":         "Rinomina il grafico nella legenda e\nnell'elenco grafici.",
            "color_plot":           "Colore del grafico.",
            "dim_pallini":          "Dimensione dei pallini in pixel. (raggio)",
            "dim_link":             "Spessore dei collegamenti tra i punti.",
            "x_column":             "Indice della colonna da cui estrarre\nil valore delle X",
            "y_column":             "Indice della colonna da cui estrarre\nil valore delle Y",
            "ey_column":            "Indice della colonna da cui estrarre\nil valore delle eY",
            "path_import":          "Path dal quale caricare l'immagine.",
            "path_export":          "Path nel quale caricare il plot generato.",    
            "x1":                   "Valore X del primo punto di calibrazione.",
            "x2":                   "Valore X del secondo punto di calibrazione.",
            "y1":                   "Valore Y del terzo punto di calibrazione.",
            "y2":                   "Valore Y del quarto punto di calibrazione.",
            "x_min":                "Imposta il valore minimo delle X\nnel custom range.",
            "x_max":                "Imposta il valore massimo delle X\nnel custom range.",
            "y_min":                "Imposta il valore minimo delle Y\nnel custom range.",
            "y_max":                "Imposta il valore massimo delle Y\nnel custom range.",
            "grado_inter":          "Grado di interpolazione polinomiale. Es:\n1 = retta\n2 = parabola",
            "px_modello":           "Posizione X del modello.",
            "py_modello":           "Posizione Y del modello.",
            "pz_modello":           "Posizione Z del modello.",
            "rx_modello":           "Rollio del modello.",
            "ry_modello":           "Beccheggio Y del modello.",
            "rz_modello":           "Imbardata Z del modello.",
            "sx_modello":           "Scala X del modello.",
            "sy_modello":           "Scala Y del modello.",
            "sz_modello":           "Scala Z del modello.",
            "colore_diff":          "Colore base del modello.",
            "colore_emis":          "Colore di emissione del modello.",
            "forza_emis":           "Forza di emissione.\n>1 = Over-exposure -> clipped at 1",
            "roughness":            "Determina la liscezza del materiale.\n- 0.0 -> liscio\n- 1.0 -> ruvido\nLa combinazione di gloss 1 e roughness 0\nrisulta in metallo.",
            "glossiness":           "Determina la probabilità di riflesso speculare.\n- 0.0 -> 0%\n- 1.0 -> 100%\nLa combinazione di gloss 1 e roughness 0\nrisulta in metallo.",
            "glass":                "Determina comportamento vetroso.\n- 0 -> Non vetroso\n- 1 -> Vetroso",
            "IOR":                  "Indice di rifrazione.",
            "samples":              "Numero di samples eseguiti.\nLa scena verrà sempre prima renderizzata\nad 1 sample per avere un insight della scena.",
            "bounces":              "Numero di rimbalzi massimi di un raggio.",
            "sample_package":       "Frequenza di aggiornamento in termini di samples.\nIl rapporto di samples / package = antialiasing.",
            "resolution_x":         "Percentuale risoluzione X.\n- 100%: no perdita\n- 10%: risultato è 1/10 della risoluzione madre.",
            "resolution_y":         "Percentuale risoluzione Y.\n- 100%: no perdita\n- 10%: risultato è 1/10 della risoluzione madre.",
            "cores":                "Numero di cores della CPU.\nConsigliati non più di 9.\nControlla le tue disponibilità.",
            "res_chunck":           "In quanti chunck dividere ogni riga e colonna.\nChunck totali = n^2.",
        }

        self.simboli = {
            r"\alpha": "α",
            r"\beta": "β",
            r"\gamma": "γ",
            r"\delta": "δ",
            r"\epsilon": "ε",
            r"\zeta": "ζ",
            r"\eta": "η",
            r"\theta": "θ",
            r"\NULL": "ι",
            r"\kappa": "κ",
            r"\lambda": "λ",
            r"\mu": "μ",
            r"\nu": "ν",
            r"\NULL": "ξ",
            r"\NULL": "ο",
            r"\pi": "π",
            r"\rho": "ρ",
            r"\NULL": "ς",
            r"\sigma": "σ",
            r"\tau": "τ",
            r"\NULL": "υ",
            r"\phi": "φ",
            r"\chi": "χ",
            r"\psi": "ψ",
            r"\omega": "ω",
            r"\Alpha": "Α",
            r"\Beta": "Β",
            r"\Gamma": "Γ",
            r"\Delta": "Δ",
            r"\Epsilon": "Ε",
            r"\Zeta": "Ζ",
            r"\Eta": "Η",
            r"\Theta": "Θ",
            r"\NULL": "Ι",
            r"\Kappa": "Κ",
            r"\Lambda": "Λ",
            r"\Mu": "Μ",
            r"\NULL": "Ν",
            r"\NULL": "Ξ",
            r"\NULL": "Ο",
            r"\Pi": "Π",
            r"\Rho": "Ρ",
            r"\Sigma": "Σ",
            r"\Tau": "Τ",
            r"\NULL": "Υ",
            r"\Phi": "Φ",
            r"\Chi": "Χ",
            r"\Psi": "Ψ",
            r"\Omega": "Ω",
            r"\pm": "±",
            r"\sqrt": "√"
        }