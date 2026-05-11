# Proyecto 2: Algoritmos de Búsqueda en Laberintos

**Inteligencia Artificial 2026**

### Integrantes
- Javier España #23361
- Ángel Esquit #23221
- Roberto Barreda #23354

---

## Descripción

Generación aleatoria de laberintos con **Prim** y **Kruskal**, resolución con **BFS, DFS, UCS (Dijkstra) y A\***, y comparación de desempeño en K=25 escenarios.

Cada ejecución produce **3 outputs numerados** por variación:
| Archivo | Contenido |
|---|---|
| `01_maze.png` | Laberinto limpio (sin solución) |
| `02_solve.gif` | Animación del proceso de resolución |
| `03_solved.png` | Laberinto resuelto con región explorada y camino |

---

## Instalación

```powershell
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Uso — Menú interactivo

Ejecutar sin argumentos lanza el **menú interactivo**:

```powershell
python -m src.main
```