# PRY2-IA - Proyecto 2 - IA

### Integrantes

- Javier España #23361
- Ángel Esquit #23221
- Roberto Barreda #23354

## Estructura principal

- src/maze/: representacion del laberinto y generadores
- src/search/: algoritmos de busqueda
- src/experiments/: comparativa entre algoritmos
- src/visualization/: graficado de soluciones
- src/main.py: CLI principal
- tests/: pruebas unitarias
- reports/: salidas (csv, png, resumen)

## Instalacion

1. Crear entorno virtual:
   - PowerShell: `python -m venv .venv`
2. Activar entorno:
   - PowerShell: `.\.venv\Scripts\Activate.ps1`
3. Instalar dependencias:
   - `pip install -r requirements.txt`

## Uso rapido

### Problema 1: comparar construccion de laberintos (animacion)

`python -m src.main buildviz --rows 30 --cols 40 --seed 42 --output reports/generation_compare.gif`

Salida esperada:
- GIF con la evolucion de construccion en paralelo para Prim y Kruskal.

### Problema 2: resolver un laberinto 60x80

`python -m src.main solve --generator prim --search astar --rows 60 --cols 80 --seed 42 --output reports/solve_60x80.png --animate-output reports/solve_60x80.gif`

Salida esperada:
- Estadisticas en consola: longitud del camino, nodos explorados, tiempo.
- Imagen de la solucion en `reports/solve_60x80.png`.
- La imagen incluye region explorada por el algoritmo y camino final.
- GIF opcional en `reports/solve_60x80.gif` mostrando exploracion y camino final.

### Problema 3: comparar algoritmos en K escenarios

`python -m src.main compare --generator kruskal --rows 45 --cols 55 --k 25 --seed 42 --output-csv reports/comparison_45x55.csv`

Salida esperada:
- CSV por escenario y algoritmo con nodos explorados, tiempo, longitud y ranking.
- Resumen de ranking promedio en `reports/ranking_summary.txt`.