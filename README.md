# Jugador Autónomo de HEX — Inteligencia Artificial

**Facultad de Matemática y Computación**  
**Autor:** David Sánchez Iglesias

---

## Descripción

Implementación de un jugador autónomo para el juego de estrategia **HEX** en un tablero N×N. El jugador usa el algoritmo **Minimax con poda Alfa-Beta** y dos heurísticas para evaluar posiciones: distancia de Dijkstra y conteo de puentes.

## Estructura del repositorio

```
proyecto_IA/
├── David_Sanchez_Iglesias/
│   ├── solution.py       # Jugador autónomo (SmartPlayer)
│   └── Informe.pdf       # Documentación técnica de la estrategia
├── board.py              # Implementación del tablero HexBoard
├── player.py             # Clase base Player
├── utils.py              # DFS para verificar conexión ganadora
└── main.py               # Interfaz de consola para jugar
```

## Requisitos

Python 3.8 o superior. No se requieren librerías externas; todas las dependencias (`heapq`, `random`, `time`) pertenecen a la biblioteca estándar de Python.

## Cómo ejecutar

```bash
python main.py
```

Se mostrará un menú para elegir el modo de juego:

- `1` — Humano vs Humano
- `2` — Humano vs IA
- `3` — IA vs IA

Los movimientos se introducen como `fila columna` (ej: `3 4`).

## Estrategia del jugador

El jugador (`SmartPlayer`) implementa:

- **Minimax con poda Alfa-Beta**: explora el árbol de juego podando ramas que no pueden mejorar la solución actual.
- **Heurística de Dijkstra**: estima el número mínimo de fichas que faltan para conectar los dos bordes, sembrando desde todo el borde inicial del jugador.
- **Heurística de puentes**: cuenta pares de fichas propias conectadas por dos caminos vacíos alternativos, una estructura difícil de bloquear para el rival.
- **Control de tiempo**: la búsqueda se interrumpe automáticamente antes de los 5 segundos devolviendo la mejor jugada encontrada hasta ese momento.
- **Parámetros dinámicos**: la profundidad de búsqueda (`depth`) y el número de ramas exploradas por nodo (`top_moves`) se ajustan según la fase del juego, medida como el ratio de casillas vacías respecto al total del tablero.

## Reglas del juego HEX

- Tablero hexagonal N×N. Cada turno, el jugador coloca una ficha en una casilla vacía.
- **Jugador 1 (🔴)**: conecta el borde izquierdo con el derecho (columna 0 ↔ columna N-1).
- **Jugador 2 (🔵)**: conecta el borde superior con el inferior (fila 0 ↔ fila N-1).
- Gana el primero en completar su conexión.

