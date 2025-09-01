# tetris.py

# IMPORT ------------------------------------------------------------------------------

try:
    import tkinter as tk
except ImportError as e:
    print(f"Error de importación en línea 5: {e}")

try:
    import json, os
except ImportError as e:
    print(f"Error de importación en línea 10: {e}")

try:
    import random
except ImportError as e:
    print(f"Error de importación en línea 15: {e}")

try:
    from tkinter import Canvas, messagebox
except ImportError as e:
    print(f"Error de importación en línea 20: {e}")

try:
    from datetime import datetime
except ImportError as e:
    print(f"Error al importar en línea 25: {e}")


SCORES_FILE = "tetris_scores.json"
DB_FILE = "tetris_db.json"  

def _db_default():
    return {"meta": {"app": "tetris", "version": 1}, "scores": []}

def ensure_db():
    import os, json
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "scores" in data:
                return
        except Exception:
            pass
    #  migramos desde SCORE_FILE
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                legacy = json.load(f)
            if isinstance(legacy, list):
                data = _db_default()
              
                for item in legacy:
                    try:
                        data["scores"].append({
                            "nombre": item.get("nombre", "Anónimo"),
                            "puntos": int(item.get("puntos", 0)),
                            "fecha": item.get("fecha", "")
                        })
                    except Exception:
                        continue
                with open(DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return
        except Exception:
            pass
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(_db_default(), f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _read_db():
    ensure_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return _db_default()

def _write_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# CLASS -----------------------------------------------------------------------------------------------
class Tetris:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("T E T R I S")
        self.root.geometry("220x150")  
        self.root.resizable(False, False)

        # asegurar DB JSON
        ensure_db()

        # Frame ----------------
        frame1 = tk.Frame(self.root, padx=10, pady=10)
        frame1.pack(expand=True, fill="both")

        tk.Label(frame1, text="TETRIS", font=("Arial", 22, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        # Botones ------------------
        botonjugar = tk.Button(frame1, text="Jugar", command=self.juego)
        botonjugar.grid(row=1, column=0, columnspan=2, pady=4)

        botonhighscores = tk.Button(frame1, text="Ver puntuaciones", command=self.puntuaciones)
        botonhighscores.grid(row=2, column=0, columnspan=2, pady=4)

        # estado de la partida
        self.puntos = 0
        self.game_over = False  # <- CONTROLAR FIN DE PARTIDA

        ## variables de los overlays de los mensajes 
        self.mensaje_pausa_id = None
        self.mensaje_inicio_id = None
        self.mensaje_gameover_id = None

    # Cargar puntuaciones
    def cargar_puntuaciones(self):
        """Lee top 10 de la DB JSON."""
        data = _read_db()
        if not isinstance(data, dict) or "scores" not in data:
            return []
        lista = list(data["scores"])
        lista.sort(key=lambda d: int(d.get("puntos", 0)), reverse=True)
        return lista[:10]
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data[:10]
                return []
        except Exception:
            return []

    def guardar_puntuacion(self, nombre, puntos):
        data = _read_db()
        if "scores" not in data or not isinstance(data["scores"], list):
            data = _db_default()
        data["scores"].append({
            "nombre": nombre,
            "puntos": int(puntos),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        # Mantener como top 100 en archivo para que no crezca infinito
        data["scores"].sort(key=lambda d: int(d.get("puntos", 0)), reverse=True)
        data["scores"] = data["scores"][:100]
        _write_db(data)

    def puntuaciones(self):
        top = tk.Toplevel(self.root)
        top.title("Puntuaciones")
        top.geometry("520x520")
        listado = self.cargar_puntuaciones()
        tk.Label(top, text="Top 10", font=("Arial", 16, "bold")).pack(pady=8)
        if not listado:
            tk.Label(top, text="No hay puntuaciones todavía.").pack()
            return
        for i, item in enumerate(listado, 1):
            tk.Label(top, text=f"{i:>2}. {item['nombre']:<10}  {item['puntos']:>5}  ({item['fecha']})", anchor="w").pack(fill="x", padx=12)

    
    def _abrir_json(self):
        """Abre el archivo DB JSON en el explorador del sistema si es posible."""
        import os, sys, subprocess
        ensure_db()
        ruta = os.path.abspath(DB_FILE)
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", ruta])
            else:
                subprocess.Popen(["xdg-open", ruta])
        except Exception:
            try:
                messagebox.showinfo("Ruta del JSON", ruta)
            except Exception:
                print("DB:", ruta)

    def juego(self):
        self.root.withdraw()
        self.ventanaJuego = tk.Toplevel(self.root)
        self.ventanaJuego.title("T E T R I S")
        self.ventanaJuego.geometry("640x870")
        self.ventanaJuego.resizable(False, False)
        self.tetris = Canvas(self.ventanaJuego, width=420, height=870, bg="blue")
        self.tetris.pack(side="left")
        self.ventana = Canvas(self.ventanaJuego, width=220, height=870, bg="black")
        self.ventana.pack(side="right")

        self.marca = self.ventana.create_text(110, 220, text="PUNTUACIÓN", fill="white", font=("Arial",20))

        ## overlay del mensaje de inicio
        ancho = int(self.tetris["width"])
        alto = int(self.tetris["height"])
        self.overlay_inicio = self.tetris.create_rectangle(
            0, alto//3, ancho, 2*alto//3,
            fill="black", stipple="gray50", outline=""
        )
        sombra = self.tetris.create_text(
            ancho//2 + 2, alto//2 + 2,
            text='Iniciar Juego\n"Presiona la barra espaciadora"',
            fill="black",
            font=("Arial", 18, "bold"),
            justify="center"
        )
        texto = self.tetris.create_text(
            ancho//2, alto//2,
            text='Iniciar Juego\n"Presiona la barra espaciadora"',
            fill="white",
            font=("Arial", 18, "bold"),
            justify="center"
        )
        self.mensaje_inicio_id = (self.overlay_inicio, sombra, texto)

        # panel lateral ## ! panel blanco para la vista de la siguiente ficha
        self.panel_preview = self.ventana.create_rectangle(0, 0, 220, 190, fill="white", outline="")
        # Botones del panal latera - Pausa/Reanudar...
        boton_play = tk.Button(self.ventana, text="▶ Reanudar", font=("Helvetica", 14, "bold"), command=self.iniciar_juego, width=12)
        self.ventana.create_window(40, 750, anchor="nw", window=boton_play)

        boton_pausa = tk.Button(self.ventana, text="⏸ Pausar", font=("Helvetica", 14, "bold"), command=self.pausar_juego, width=12)
        self.ventana.create_window(40, 800, anchor="nw", window=boton_pausa) 
        self.puntos = 0
        self.game_over = False   # <- reinicia el flag al empezar una nueva partida

        # ··············· CAMBIO ········································
        # las variables del juego
        self.lado_cuadrado = 30   # lo que ocupará cada cuadrado en el canvas
        self.cols = int(self.tetris["width"]) // self.lado_cuadrado
        self.filas = int(self.tetris["height"]) // self.lado_cuadrado

        self.caida_ms = 350
        self._after_id = None  # id del after activo
        self.en_pausa = False

        self.ocupadas = set()    # lasceldas ocupadas por x.y
        self.bloques_por_celda = {}   # x,y del id del rectángulo en canvas

        ##! lista de self.formas de las piezas, respetando el orden que teniamos antes de la creación de las fichas
        # creación de las fichas
        self.formas = [
            [(0,0), (0,1), (0,2), (0,3)],             # I
            [(0,0), (1,0), (2,0), (3,0)],             # I tumbada
            [(0,0), (1,0), (0,1), (1,1)],             # O
            [(0,0), (1,0), (2,0), (1,1)],             # T
            [(1,0), (0,1), (1,1), (2,1)],             # T tumbada
            [(0,1), (1,1), (0,0), (0,2)],             # T girada
            [(0,0), (0,1), (0,2), (1,2)],             # L
            [(0,1), (1,0), (0,0), (0,2)],             # L inversa
            [(0,0), (1,0), (1,1), (1,2)],             # L reversa
            [(0,0), (1,0), (1,1), (2,1)],             # Z
            [(0,0), (0,1), (1,1), (1,2)],             # Z reversa
            [(1,0), (2,0), (0,1), (1,1)],             # S
            [(0,1), (0,2), (1,0), (1,1)],             # S reversa
        ]

        # Pieza siguiente y activa
        self.ficha_next = {
            "forma": random.choice(self.formas),
            "color": random.choice(["cyan", "purple", "orange", "green", "red", "yellow"])
        }
        self.siguienteFicha(65, 55, self.ficha_next["forma"], self.ficha_next["color"])  # pieza que se pinta en el panel blanco

        self.ficha_activa = None
        self.preparar_proxima_pieza()

        ##! movimiento de las fichas con las teclas
        self.ventanaJuego.bind("<Left>",  lambda e: self.mover(-1))
        self.ventanaJuego.bind("<Right>", lambda e: self.mover(1))
        self.ventanaJuego.bind("<Down>",  lambda e: self.mover(0, bajar=True))
        self.ventanaJuego.bind("<Up>",    lambda e: self.girar(1))
        self.ventanaJuego.bind("<space>", self._toggle_espacio)
        self.tetris.focus_set()

        # AL cerrar la ventana de la partida se vuelve al menú
        self.ventanaJuego.protocol("WM_DELETE_WINDOW", self._cerrar_todo)

    # Botón ▶️
    def iniciar_juego(self):
        if getattr(self, "game_over", False):
            return  # No iniciar si ya terminó la partida

        self.en_pausa = False  # Asegura que el juego esté "no en pausa"
        # Reinicia/crea marcador de puntos
        try:
            self.ventana.delete(self.marcador)
        except Exception:
            pass
        self.marcador = self.ventana.create_text(110, 250, text="0", fill="white", font=("Arial",20))
        # aquí va la visibilidad del nivel
        self.nivel = 1
        try:
            self.ventana.delete(self.lbl_nivel)
            self.ventana.delete(self.nivel_marcador)
        except Exception:
            pass
        self.lbl_nivel = self.ventana.create_text(110, 300, text="NIVEL", fill="white", font=("Arial",20))
        self.nivel_marcador = self.ventana.create_text(110, 330, text=str(self.nivel), fill="white", font=("Arial",20))

        if getattr(self, "mensaje_inicio_id", None):
            try:
                for _id in self.mensaje_inicio_id:
                    self.tetris.delete(_id)
            except Exception:
                pass
            self.mensaje_inicio_id = None

        if getattr(self, "mensaje_pausa_id", None):  # Elimina el overlay de pausa si existe
            for _id in self.mensaje_pausa_id:
                try:
                    self.tetris.delete(_id)
                except Exception:
                    pass
            self.mensaje_pausa_id = None

        if self._after_id is None:
            self._after_id = self.tetris.after(self.caida_ms, self.caer)

    # Botón ⏸️
    def pausar_juego(self):
        if getattr(self, "game_over", False):
            return  # No interactuar si terminó

        self.en_pausa = not self.en_pausa
        if self.en_pausa:
            if self._after_id is not None:
                try:
                    self.tetris.after_cancel(self._after_id)
                except Exception:
                    pass
                self._after_id = None

            ## overlay "PAUSA" 
            if self.mensaje_pausa_id is None:
                ancho = int(self.tetris["width"])
                alto = int(self.tetris["height"])
                overlay = self.tetris.create_rectangle(
                    0, alto//3, ancho, 2*alto//3,
                    fill="black", stipple="gray50", outline=""
                )
                sombra = self.tetris.create_text(
                    ancho//2 + 2, alto//2 + 2,
                    text="P A U S A",
                    fill="black",
                    font=("Arial", 40, "bold"),
                    justify="center")
                texto = self.tetris.create_text(
                    ancho//2, alto//2,
                    text="P A U S A",
                    fill="white",
                    font=("Arial", 40, "bold"),
                    justify="center")
                self.mensaje_pausa_id = (overlay, sombra, texto)
        else:
            if self._after_id is None:
                self._after_id = self.tetris.after(self.caida_ms, self.caer)
            if self.mensaje_pausa_id is not None:
                for _id in self.mensaje_pausa_id:
                    try:
                        self.tetris.delete(_id)
                    except Exception:
                        pass
                self.mensaje_pausa_id = None

    # la ficha que esta proxima a salir
    def preparar_proxima_pieza(self):
        forma = self.ficha_next["forma"]
        color_ficha = self.ficha_next["color"]

        # la posicion en la que inicia la ficha al comenzar el juego y sucesivamente...
        inicio_col = self.cols // 2 - 2
        x_pix = inicio_col * self.lado_cuadrado
        y_pix = 0

        ids = self.dibujarFichas(x_pix, y_pix, forma, color_ficha)
        self.ficha_activa = {"forma": forma,
                             "x": x_pix,
                             "y": y_pix,
                             "id": ids,
                             "color": color_ficha}

        # la siguiente ficha a mostrar en el panel blanco
        self.ficha_next = {
            "forma": random.choice(self.formas),
            "color": random.choice(["cyan", "purple", "orange", "green", "red", "yellow"])}
        self.siguienteFicha(65, 55, self.ficha_next["forma"], self.ficha_next["color"])

        ## ! cuando las fichas ya estan hasta el tope superior, la proxima ficha a salir generara el GAME OVER
        if not self.puede_mover(0, 0):
            # Borra la pieza recién creada para que la "última" quede tal cual estaba el tablero
            for rid in ids:
                try:
                    self.tetris.delete(rid)
                except Exception:
                    pass
            self.ficha_activa = None
            self.gameOver()
            return False

        return True

    def caer(self):
        if self.en_pausa or getattr(self, "game_over", False):
            self._after_id = None
            return

        paso = self.lado_cuadrado

        if self.puede_mover(0, 1):  # permite bajar si es posible
            for rid in self.ficha_activa["id"]:
                self.tetris.move(rid, 0, paso)
            self.ficha_activa["y"] += paso
        else:
            self.fijar_pieza()
            # si no hay próxima pieza posible, no sigas
            if not self.preparar_proxima_pieza():
                self._after_id = None
                return

        # prepara la siguiente caída solo si sigue vivo
        if not getattr(self, "game_over", False):
            self._after_id = self.tetris.after(self.caida_ms, self.caer)

    # movimiento izquierda, derecha y bajar
    def mover(self, dx_celdas, bajar=False):
        if self.en_pausa or not self.ficha_activa or getattr(self, "game_over", False):
            return
        paso = self.lado_cuadrado

        if bajar:
            if self.puede_mover(0, 1):
                for rid in self.ficha_activa["id"]:
                    self.tetris.move(rid, 0, paso)
                self.ficha_activa["y"] += paso
            else:
                self.fijar_pieza()
                if not self.preparar_proxima_pieza():
                    return
            return

        if self.puede_mover(dx_celdas, 0):
            for rid in self.ficha_activa["id"]:
                self.tetris.move(rid, dx_celdas * paso, 0)
            self.ficha_activa["x"] += dx_celdas * paso

    def girar(self, sentido=1):
        if self.en_pausa or not self.ficha_activa or getattr(self, "game_over", False):
            return

        forma = self.ficha_activa["forma"]

        rotada = [(dy, -dx) for (dx, dy) in forma]  ##! manecilla del reloj es el sentido del giro

        # normalización de la rotada
        minx = min(dx for dx, _ in rotada)
        miny = min(dy for _, dy in rotada)
        rotada = [(dx - minx, dy - miny) for dx, dy in rotada]

        # giros de ticks cuando esta la ficha junto a los bordes de la ventana u las otras fichas
        intentos = [(0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0)]
        for kx, ky in intentos:
            nx = self.ficha_activa["x"] + kx * self.lado_cuadrado
            ny = self.ficha_activa["y"] + ky * self.lado_cuadrado
            if self.puede_posicionar(rotada, nx, ny):
                self.ficha_activa["forma"] = rotada
                self.ficha_activa["x"] = nx
                self.ficha_activa["y"] = ny

                paso = self.lado_cuadrado
                for rid, (dx, dy) in zip(self.ficha_activa["id"], rotada):
                    x0 = nx + dx * paso
                    y0 = ny + dy * paso
                    x1 = x0 + paso
                    y1 = y0 + paso
                    self.tetris.coords(rid, x0, y0, x1, y1)
                return

    def puede_mover(self, dx_celdas, dy_celdas): # si permite la jugada el movimiento de la ficha
        paso = self.lado_cuadrado
        for rid in self.ficha_activa["id"]:
            x0, y0, x1, y1 = self.tetris.coords(rid)
            nx0 = x0 + dx_celdas * paso
            ny0 = y0 + dy_celdas * paso
            nx1 = x1 + dx_celdas * paso
            ny1 = y1 + dy_celdas * paso

            # limitamos el canvas
            if nx0 < 0 or nx1 > int(self.tetris["width"]) or ny1 > int(self.tetris["height"]):
                return False

            # control para la colision con el resto de las fichas en la partida
            gx = int(nx0 // paso)
            gy = int(ny0 // paso)
            if (gx, gy) in self.ocupadas:
                return False
        return True

    # verifica si podemos girar la ficha a la posición actual
    def puede_posicionar(self, forma, x_pix, y_pix):
        paso = self.lado_cuadrado
        for dx, dy in forma:
            x0 = x_pix + dx * paso
            y0 = y_pix + dy * paso
            x1 = x0 + paso
            y1 = y0 + paso

            if x0 < 0 or x1 > int(self.tetris["width"]) or y1 > int(self.tetris["height"]):
                return False

            gx = int(x0 // paso)
            gy = int(y0 // paso)
            if (gx, gy) in self.ocupadas:
                return False
        return True

    def fijar_pieza(self):
        paso = self.lado_cuadrado
        for rid in self.ficha_activa["id"]:
            x0, y0, _, _ = self.tetris.coords(rid)
            gx = int(x0 // paso)
            gy = int(y0 // paso)
            self.ocupadas.add((gx, gy))
            self.bloques_por_celda[(gx, gy)] = rid
        self.ficha_activa = None

        ##! la fila a borrar para marcar la puntuación
        filas_a_borrar = []
        for y in range(self.filas):
            if all((x, y) in self.ocupadas for x in range(self.cols)):
                filas_a_borrar.append(y)

        if filas_a_borrar:
            for y in filas_a_borrar:
                for x in range(self.cols):
                    rid = self.bloques_por_celda.pop((x, y), None)
                    if rid is not None:
                        self.tetris.delete(rid)
                    self.ocupadas.discard((x, y))

            # el movimiento de las fichas que bajan al eliiminar la fila eliminada
            nuevos_ocupados = set()
            nuevos_mapas = {}
            for (cx, cy) in list(self.ocupadas):
                drop = sum(1 for fy in filas_a_borrar if fy > cy)
                if drop > 0:
                    rid = self.bloques_por_celda.pop((cx, cy))
                    self.tetris.move(rid, 0, drop * paso)
                    nuevos_ocupados.add((cx, cy + drop))
                    nuevos_mapas[(cx, cy + drop)] = rid
                else:
                    rid = self.bloques_por_celda.pop((cx, cy))
                    nuevos_ocupados.add((cx, cy))
                    nuevos_mapas[(cx, cy)] = rid

            self.ocupadas = nuevos_ocupados
            self.bloques_por_celda = nuevos_mapas

            self.sumar_puntos(100 * len(filas_a_borrar))

    def sumar_puntos(self, cantidad):
        puntos_antes = self.puntos
        self.puntos += cantidad

        nivel_antes = max(1, (puntos_antes // 1000) + 1)
        nivel_actual = max(1, (self.puntos // 1000) + 1)

        if nivel_actual > nivel_antes:
            self.nivel = nivel_actual
            self.acelerar_juego()
            # la actualización visualmente en el panel 
            try:
                self.ventana.itemconfig(self.nivel_marcador, text=str(self.nivel))
            except Exception:
                pass

        # actualiza marcador de puntos
        self.ventana.itemconfig(self.marcador, text=str(self.puntos))

    def acelerar_juego(self):
        decremento = 25
        self.caida_ms = max(60, self.caida_ms - decremento)
        try:
            print(f"Nivel {getattr(self, 'nivel', '?')}: velocidad = {self.caida_ms} ms")
        except Exception:
            pass

    def dibujarFichas(self, x, y, ficha, color):
        self.lado_cuadrado = 30  # lo que ocupa cada cuadrado en el canvas
        ids = []  # aquí se guardan los IDs

        for dx, dy in ficha:
            self.coord_x0 = x + dx * self.lado_cuadrado
            self.coord_y0 = y + dy * self.lado_cuadrado
            self.coord_x1 = self.coord_x0 + self.lado_cuadrado
            self.coord_y1 = self.coord_y0 + self.lado_cuadrado

            _id = self.tetris.create_rectangle(
                self.coord_x0, self.coord_y0, self.coord_x1, self.coord_y1,
                fill=color, outline="black", width=2
            )
            ids.append(_id)

        return ids

    def siguienteFicha(self, x, y, ficha, color):
        self.lado_cuadrado = 30  # lo que ocupa cada cuadrado en el canvas

        # limpiar el área de vista previa ##! cada vez que se hace el llamado a esta fución se limpia el panel blanco
        self.ventana.create_rectangle(0, 0, 220, 190, fill="white", outline="")

        for dx, dy in ficha:
            self.coord_x0 = x + dx * self.lado_cuadrado
            self.coord_y0 = y + dy * self.lado_cuadrado
            self.coord_x1 = self.coord_x0 + self.lado_cuadrado
            self.coord_y1 = self.coord_y0 + self.lado_cuadrado

            self.ventana.create_rectangle(
                self.coord_x0, self.coord_y0, self.coord_x1, self.coord_y1,
                fill=color, outline="black", width=2
            )

        ##! No actualices aquí self.ficha_activa, eso debe ocurrir al "generar nueva ficha"

    def gameOver(self):
        self.game_over = True    # <- marca el fin de partida
        self.en_pausa = True     # <- bloquea controles

        ## overlay del GAME OVER, en lugar del messagebox 
        ancho = int(self.tetris["width"])
        alto = int(self.tetris["height"])
        overlay = self.tetris.create_rectangle(
            0, alto//3, ancho, 2*alto//3,
            fill="black", stipple="gray50", outline=""
        )
        sombra = self.tetris.create_text(
            ancho//2 + 2, alto//2 + 2,
            text="GAME OVER\n\nPresiona Enter para continuar",
            fill="black",
            font=("Arial", 20, "bold"),
            justify="center")
        texto = self.tetris.create_text(
            ancho//2, alto//2,
            text="GAME OVER\n\nPresiona Enter para continuar",
            fill="white",
            font=("Arial", 20, "bold"),
            justify="center")
        self.mensaje_gameover_id = (overlay, sombra, texto)

        if hasattr(self, "_after_id") and self._after_id is not None:
            try:
                self.tetris.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

        # tecla enter para guardar la jugada y cerrar la ventana del juego
        self.ventanaJuego.bind("<Return>", self._guardar_y_cerrar)

    ## confirmación del Game Over y guardado de puntuación si el usuario lo desea si no quiere solo cierra la ventana de la partida
    def _guardar_y_cerrar(self, event=None):
        if getattr(self, "mensaje_gameover_id", None):
            for _id in self.mensaje_gameover_id:
                try:
                    self.tetris.delete(_id)
                except Exception:
                    pass
            self.mensaje_gameover_id = None

        nombre = self._pedir_nombre()
        if nombre:
            self.guardar_puntuacion(nombre, self.puntos)

        self._cerrar_todo()

    # guardar la puntuación con el nombre que se pide
    def _pedir_nombre(self):
        top = tk.Toplevel(self.ventanaJuego)
        top.title("Guardar puntuación")
        top.resizable(False, False)
        top.transient(self.ventanaJuego)

        # Tamaño y centrado aproximado sobre la ventana del juego
        width, height = 360, 140
        try:
            self.ventanaJuego.update_idletasks()
            px = self.ventanaJuego.winfo_rootx()
            py = self.ventanaJuego.winfo_rooty()
            pw = self.ventanaJuego.winfo_width()
            ph = self.ventanaJuego.winfo_height()
            x = px + (pw - width) // 2
            y = py + (ph - height) // 2
            top.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            top.geometry(f"{width}x{height}")

        frm = tk.Frame(top, padx=16, pady=16)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Tu nombre:", font=("Arial", 12)).grid(row=0, column=0, sticky="e", padx=(0, 8))
        entrada = tk.Entry(frm, font=("Arial", 12), width=22)
        entrada.grid(row=0, column=1, sticky="we")
        frm.columnconfigure(1, weight=1)

        valor = {"n": None}
        def ok(*_):
            valor["n"] = entrada.get().strip() or "Anónimo"
            top.destroy()

        btn = tk.Button(frm, text="OK", command=ok, font=("Arial", 11, "bold"), width=6)
        btn.grid(row=0, column=2, padx=(8, 0))

        # confirma
        top.bind("<Return>", ok)

        top.grab_set()
        entrada.focus_set()
        top.wait_window()
        return valor["n"]

    # cerramos la ventana de la partida para asi volver al menú
    def _cerrar_todo(self):
        if hasattr(self, "_after_id") and self._after_id is not None:
            try:
                self.tetris.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

        if hasattr(self, "ventanaJuego") and self.ventanaJuego.winfo_exists():
            self.ventanaJuego.destroy()

        self.root.deiconify()

    # iniciar / pausar / reanudar
    def _toggle_espacio(self, event=None):
        if getattr(self, "game_over", False):
            return
        if self._after_id is None and not self.en_pausa:
            self.iniciar_juego()
        elif self.en_pausa:
            self.pausar_juego()
        else:
            self.pausar_juego()

# FUNCTIONS ----------------------------------------------------------------------------
def runTetris():
    root = tk.Tk()
    Tetris(root)
    root.mainloop()


# MAIN --------------------------------------------------------------------------------
if __name__ == "__main__":
    runTetris()