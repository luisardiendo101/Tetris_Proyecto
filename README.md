# Tetris (Tkinter)
# Tetris clásico

Implementación del clásico juego de bloques que utiliza la librería estándar de Python, Tkinter, para crear la interfaz gráfica y la pantalla donde caen y se deben encajar las piezas (tetrominós) para completar líneas, las cuales desaparecen y otorgan puntos.

# Requisitos

· Python 3.12.10
· Tkinter
· Librería random
· Librería datetime

# Cómo ejecutar
Abrir y ejecutar en python tetris.py

Se abre un menú con:
-Jugar
-Ver puntuaciones

Controles:
←  →: mover pieza
↓: bajar un paso
↑: girar (sentido horario)
Espacio: pausar / reanudar (también aparecen como botones en pantalla)
Enter: al finalizar el juego (Game Over), confirma presionando Enter y Guarda la puntuación

Puntuación y niveles:
Cada línea completa: +100 puntos.
Cada 1000 puntos, sube 1 nivel y el juego acelera (~25 ms menos por nivel, mínimo 60 ms).

Game Over:
Cuando la ultima pieza toca la pantalla superior, se ha concluido el juego, GAME OVER. Pulsa Enter para la confirmación y guardar tu nombre y puntuación.

# Base de datos (JSON)
Archivo: tetris_db.json
Estructura:```json{"meta": {"app": "tetris","version": 1},"scores": [{"nombre": "Gisell","puntos": 1000,"fecha": "2025-08-28 10:24"}]

  
## Colaboradores
· Luis Alejandro Sánchez
· Gisell López
