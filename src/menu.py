"""
src/menu.py
Interactive TUI menu for Proyecto 2 - IA.
Launched automatically when src.main is run with no arguments.
"""
from __future__ import annotations

import os
import re
import sys
from typing import List, Optional, Tuple

# ── UTF-8 output & ANSI support ──────────────────────────────────────────────
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except AttributeError:
    pass
if os.name == "nt":
    os.system("")  # Enable VT100 escape codes on Windows cmd / PowerShell

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _vlen(s: str) -> int:
    """Visible length of a string (invisible ANSI codes excluded)."""
    return len(_ANSI_RE.sub("", s))


# ── ANSI palette ─────────────────────────────────────────────────────────────
R   = "\033[0m"    # reset
B   = "\033[1m"    # bold
DIM = "\033[2m"    # dim / dark
CYA = "\033[96m"   # bright cyan
GRN = "\033[92m"   # bright green
YEL = "\033[93m"   # bright yellow
RED = "\033[91m"   # bright red
BLU = "\033[94m"   # bright blue
MAG = "\033[95m"   # bright magenta
WHI = "\033[97m"   # bright white

# ── Box drawing helpers ───────────────────────────────────────────────────────
_W = 56  # visible inner width of the box


def _top(w: int = _W) -> str:
    return f"  ╔{chr(0x2550) * (w + 2)}╗"


def _bot(w: int = _W) -> str:
    return f"  ╚{chr(0x2550) * (w + 2)}╝"


def _sep(w: int = _W) -> str:
    return f"  ╠{chr(0x2550) * (w + 2)}╣"


def _row(content: str = "", w: int = _W) -> str:
    pad = max(0, w - _vlen(content))
    return f"  ║ {content}{' ' * pad} ║"


def _box(lines: List[str], w: int = _W) -> None:
    """Print lines inside a double-line border.  Use '---' for a separator."""
    print(_top(w))
    for line in lines:
        if line == "---":
            print(_sep(w))
        else:
            print(_row(line, w))
    print(_bot(w))


def _clr() -> None:
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


# ── Prompt helpers ────────────────────────────────────────────────────────────

def _ask(prompt: str, default: str) -> str:
    """Text input with default."""
    ans = input(f"  {WHI}{prompt}{R} {DIM}[{default}]{R}: ").strip()
    return ans if ans else default


def _ask_int(prompt: str, default: int, min_val: int = 1) -> int:
    """Integer input with validation."""
    while True:
        raw = _ask(prompt, str(default))
        try:
            val = int(raw)
            if val >= min_val:
                return val
            print(f"  {RED}Debe ser >= {min_val}{R}")
        except ValueError:
            print(f"  {RED}Ingresa un numero entero{R}")


def _ask_yn(prompt: str, default: bool = True) -> bool:
    """Yes/No prompt (S/N in Spanish)."""
    hint = f"{DIM}S/n{R}" if default else f"{DIM}s/N{R}"
    raw = input(f"  {WHI}{prompt}{R} [{hint}]: ").strip().lower()
    if not raw:
        return default
    return raw in ("s", "si", "y", "yes", "1")


def _choose(options: List[Tuple[str, str]], prompt: str = "Opcion", default: int = 1) -> int:
    """
    Show numbered options and return the 0-based index of the chosen option.
    options: list of (label, description) tuples.
    """
    for i, (label, desc) in enumerate(options, start=1):
        num = f"{BLU}{B}{i}{R}"
        lbl = f"{YEL}{B}{label}{R}"
        dsc = f" {DIM}{desc}{R}" if desc else ""
        print(f"    {num}  {lbl}{dsc}")
    print()
    while True:
        raw = input(f"  {WHI}{prompt}{R} {DIM}[{default}]{R}: ").strip()
        if not raw:
            return default - 1
        try:
            idx = int(raw)
            if 1 <= idx <= len(options):
                return idx - 1
            print(f"  {RED}Elige entre 1 y {len(options)}{R}")
        except ValueError:
            print(f"  {RED}Ingresa el numero de la opcion{R}")


def _pause() -> None:
    input(f"\n  {DIM}Presiona Enter para continuar...{R}")


def _header(title: str) -> None:
    """Print a prominent section header."""
    print(f"\n  {CYA}{B}  {title}{R}")
    print(f"  {DIM}{'─' * (_W + 2)}{R}\n")


def _ok(msg: str) -> None:
    print(f"\n  {GRN}{B}[OK]{R}  {msg}")


def _info(msg: str) -> None:
    print(f"  {CYA}  >{R} {msg}")


def _warn(msg: str) -> None:
    print(f"  {YEL}  !{R}  {msg}")


def _running(msg: str) -> None:
    print(f"\n  {MAG}{B}...{R}  {msg}")
    print(f"  {DIM}     (esto puede tardar unos momentos){R}\n")


# ── Main menu ─────────────────────────────────────────────────────────────────

def _show_main_menu() -> None:
    _clr()
    _box([
        "",
        f"  {WHI}{B}PROYECTO 2  {DIM}·{R}{WHI}{B}  Inteligencia Artificial  {DIM}·{R}{WHI}{B}  2026{R}",
        f"  {DIM}Algoritmos de Busqueda en Laberintos{R}",
        "",
        "---",
        "",
        f"  {BLU}{B}1{R}  {WHI}{B}Problema 1{R}  {DIM}—{R}  Generacion de laberintos",
        f"     {DIM}Visualiza la construccion: Prim vs Kruskal{R}",
        "",
        f"  {BLU}{B}2{R}  {WHI}{B}Problema 2{R}  {DIM}—{R}  Resolver laberinto",
        f"     {DIM}Aplica BFS / DFS / UCS / A* en laberinto 60x80{R}",
        "",
        f"  {BLU}{B}3{R}  {WHI}{B}Problema 3{R}  {DIM}—{R}  Comparacion de algoritmos",
        f"     {DIM}K=25 escenarios en laberinto 45x55, ranking{R}",
        "",
        f"  {BLU}{B}4{R}  {WHI}{B}Ejecutar todo{R}  {DIM}(Problemas 1, 2 y 3){R}",
        "",
        "---",
        "",
        f"  {DIM}0  Salir{R}",
        "",
    ])
    print()


# ── Problema 1 ────────────────────────────────────────────────────────────────

def _menu_problema1() -> None:
    from src.runner import run_buildviz

    _clr()
    _box([
        "",
        f"  {CYA}{B}Problema 1{R}  {DIM}—{R}  Generacion de laberintos",
        f"  {DIM}Genera y anima la construccion: Prim vs Kruskal{R}",
        "",
        "---",
        "",
        f"  Configura los parametros {DIM}(Enter = valor por defecto){R}",
        "",
    ])
    print()

    rows      = _ask_int("Filas del laberinto", default=30, min_val=5)
    cols      = _ask_int("Columnas del laberinto", default=40, min_val=5)
    seed      = _ask_int("Semilla aleatoria (seed)", default=42, min_val=0)
    max_frames = _ask_int("Frames maximos del GIF", default=120, min_val=10)
    fps       = _ask_int("FPS del GIF", default=12, min_val=1)
    out_dir   = _ask("Directorio de salida", default="reports/problema1")

    print()
    _info(f"Tamano   : {rows} x {cols}")
    _info(f"Seed     : {seed}")
    _info(f"GIF      : {max_frames} frames @ {fps} fps")
    _info(f"Salida   : {out_dir}")
    print()

    if not _ask_yn("Continuar con estos parametros?", default=True):
        return

    _running("Generando laberintos y animacion...")
    run_buildviz(
        rows=rows, cols=cols, seed=seed,
        max_frames=max_frames, fps=fps,
        out_dir=out_dir,
    )
    _ok(f"Outputs generados en: {out_dir}")
    _pause()


# ── Problema 2 ────────────────────────────────────────────────────────────────

_GENERATORS_MENU: List[Tuple[str, str]] = [
    ("Prim",    "expansion aleatoria desde una celda"),
    ("Kruskal", "union de componentes por aristas aleatorias"),
    ("Ambos",   "ejecuta con Prim y Kruskal"),
]

_ALGOS_MENU: List[Tuple[str, str]] = [
    ("A*",          "heuristica Manhattan — mas eficiente"),
    ("BFS",         "Breadth-First Search — camino optimo"),
    ("DFS",         "Depth-First Search — rapido, no optimo"),
    ("Dijkstra",    "Uniform Cost Search — optimo con costos"),
    ("Todos",       "ejecuta los 4 algoritmos"),
]

_ALGO_KEYS = ["astar", "bfs", "dfs", "ucs"]


def _menu_problema2() -> None:
    from src.runner import run_solve

    _clr()
    _box([
        "",
        f"  {CYA}{B}Problema 2{R}  {DIM}—{R}  Resolver laberinto",
        f"  {DIM}Genera un laberinto y lo resuelve. Guarda 3 outputs por ejecucion:{R}",
        f"  {DIM}  [01] laberinto  [02] animacion GIF  [03] laberinto resuelto{R}",
        "",
        "---",
        "",
    ])
    print()

    _header("Generador de laberinto")
    gen_idx = _choose(_GENERATORS_MENU, prompt="Generador", default=1)
    generators = (
        ["prim", "kruskal"] if gen_idx == 2
        else [["prim", "kruskal"][gen_idx]]
    )

    print()
    _header("Algoritmo de busqueda")
    algo_idx = _choose(_ALGOS_MENU, prompt="Algoritmo", default=1)
    algorithms = (
        _ALGO_KEYS if algo_idx == 4
        else [_ALGO_KEYS[algo_idx]]
    )

    print()
    _header("Parametros del laberinto")
    rows     = _ask_int("Filas", default=60, min_val=5)
    cols     = _ask_int("Columnas", default=80, min_val=5)
    seed     = _ask_int("Seed", default=42, min_val=0)
    no_gif   = not _ask_yn("Generar GIF animado?", default=True)
    out_base = _ask("Directorio base de salida", default="reports/problema2")

    combos = len(generators) * len(algorithms)
    print()
    _info(f"Tamano      : {rows} x {cols}  (seed={seed})")
    _info(f"Generadores : {', '.join(g.capitalize() for g in generators)}")
    _info(f"Algoritmos  : {', '.join(a.upper() for a in algorithms)}")
    _info(f"Combinaciones : {combos}")
    _info(f"GIF animado   : {'No' if no_gif else 'Si'}")
    _info(f"Salida base   : {out_base}/{{generador}}_{{algoritmo}}/")

    if combos > 1:
        print()
        _warn(f"Se ejecutaran {combos} combinaciones.")
        if no_gif:
            _info("GIFs desactivados: tiempo estimado ~1-2 min")
        else:
            _warn(f"Con GIFs activos puede tardar varios minutos ({combos * 30}s aprox.)")

    print()
    if not _ask_yn("Continuar?", default=True):
        return

    for gen in generators:
        for algo in algorithms:
            _running(f"Resolviendo con {algo.upper()} en laberinto {gen.capitalize()} {rows}x{cols}...")
            run_solve(
                generator=gen,
                search=algo,
                rows=rows,
                cols=cols,
                seed=seed,
                no_gif=no_gif,
                out_dir=f"{out_base}/{gen}_{algo}",
            )

    _ok(f"Todos los outputs generados en: {out_base}/")
    _pause()


# ── Problema 3 ────────────────────────────────────────────────────────────────

def _menu_problema3() -> None:
    from src.runner import run_compare

    _clr()
    _box([
        "",
        f"  {CYA}{B}Problema 3{R}  {DIM}—{R}  Comparacion de algoritmos de busqueda",
        f"  {DIM}Genera K laberintos y compara BFS, DFS, Dijkstra, A* en cada uno.{R}",
        f"  {DIM}Produce imagen de comparacion por escenario + ranking final.{R}",
        "",
        "---",
        "",
    ])
    print()

    _header("Generador de laberinto")
    gen_idx  = _choose(_GENERATORS_MENU, prompt="Generador", default=1)
    generators = (
        ["prim", "kruskal"] if gen_idx == 2
        else [["prim", "kruskal"][gen_idx]]
    )

    print()
    _header("Parametros")
    k        = _ask_int("Numero de escenarios K", default=25, min_val=1)
    rows     = _ask_int("Filas del laberinto", default=45, min_val=5)
    cols     = _ask_int("Columnas del laberinto", default=55, min_val=5)
    seed     = _ask_int("Seed", default=42, min_val=0)
    out_base = _ask("Directorio base de salida", default="reports/problema3")

    total_imgs = len(generators) * k * 2
    print()
    _info(f"Tamano      : {rows} x {cols}  (seed={seed})")
    _info(f"K escenarios: {k}")
    _info(f"Generadores : {', '.join(g.capitalize() for g in generators)}")
    _info(f"Imagenes    : ~{total_imgs} (2 por escenario) + {len(generators)} ranking")
    _info(f"Salida      : {out_base}/{{generador}}/")

    if k > 10:
        print()
        _warn(f"K={k}: se generaran {total_imgs} imagenes. Puede tardar varios minutos.")

    print()
    if not _ask_yn("Continuar?", default=True):
        return

    for gen in generators:
        _running(f"Comparando K={k} escenarios con generador {gen.capitalize()}...")
        run_compare(
            generator=gen,
            rows=rows,
            cols=cols,
            k=k,
            seed=seed,
            out_dir=f"{out_base}/{gen}",
        )

    _ok(f"Outputs generados en: {out_base}/")
    _pause()


# ── Ejecutar todo ─────────────────────────────────────────────────────────────

def _menu_run_all() -> None:
    from src.runner import run_buildviz, run_compare, run_solve

    _clr()
    _box([
        "",
        f"  {CYA}{B}Ejecutar todo{R}  {DIM}—{R}  Problemas 1, 2 y 3 completos",
        "",
        f"  {DIM}Esto ejecutara:{R}",
        f"    {DIM}P1:{R}  buildviz  30x40",
        f"    {DIM}P2:{R}  8 combinaciones (Prim/Kruskal x BFS/DFS/UCS/A*)  60x80",
        f"    {DIM}P3:{R}  2 comparaciones K=25  (Prim + Kruskal)  45x55",
        "",
        "---",
        "",
    ])
    print()

    seed   = _ask_int("Seed global", default=42, min_val=0)
    no_gif = not _ask_yn("Generar GIFs animados?", default=False)

    print()
    if no_gif:
        _info("GIFs desactivados. Tiempo estimado: ~5-8 min")
    else:
        _warn("Con GIFs activos el tiempo puede superar 30 minutos.")
        _warn("Se generan 8 GIFs de 60x80 — considera usar --no-gif para tests rapidos.")
    print()

    if not _ask_yn("Confirmar ejecucion completa?", default=True):
        return

    # Problema 1
    print(f"\n  {CYA}{B}[1/3] Problema 1 — Generacion de laberintos{R}")
    run_buildviz(rows=30, cols=40, seed=seed, out_dir="reports/problema1")

    # Problema 2
    print(f"\n  {CYA}{B}[2/3] Problema 2 — Resolver laberinto 60x80{R}")
    for gen in ["prim", "kruskal"]:
        for algo in ["bfs", "dfs", "ucs", "astar"]:
            _running(f"  {algo.upper()} en {gen.capitalize()} 60x80...")
            run_solve(
                generator=gen, search=algo,
                rows=60, cols=80, seed=seed,
                no_gif=no_gif,
                out_dir=f"reports/problema2/{gen}_{algo}",
            )

    # Problema 3
    print(f"\n  {CYA}{B}[3/3] Problema 3 — Comparacion K=25 escenarios{R}")
    for gen in ["prim", "kruskal"]:
        _running(f"  Comparando K=25 con {gen.capitalize()} 45x55...")
        run_compare(
            generator=gen, rows=45, cols=55, k=25, seed=seed,
            out_dir=f"reports/problema3/{gen}",
        )

    print()
    _box([
        "",
        f"  {GRN}{B}Todos los outputs generados exitosamente!{R}",
        "",
        f"  {DIM}reports/problema1/    — Problema 1{R}",
        f"  {DIM}reports/problema2/    — Problema 2 (8 combinaciones){R}",
        f"  {DIM}reports/problema3/    — Problema 3 (2 generadores){R}",
        "",
    ])
    _pause()


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_interactive_menu() -> None:
    """Entry point — shows the main menu and dispatches to sub-menus."""
    actions = {
        "1": _menu_problema1,
        "2": _menu_problema2,
        "3": _menu_problema3,
        "4": _menu_run_all,
    }

    while True:
        try:
            _show_main_menu()
            choice = input(f"  {WHI}Selecciona una opcion{R} {DIM}[1-4 / 0]{R}: ").strip()

            if choice == "0":
                _clr()
                print(f"\n  {DIM}Hasta luego!{R}\n")
                break
            elif choice in actions:
                actions[choice]()
            else:
                _clr()
                print(f"\n  {RED}Opcion '{choice}' no valida. Elige entre 0 y 4.{R}")
                _pause()

        except KeyboardInterrupt:
            print(f"\n\n  {DIM}Interrumpido.{R}\n")
            break
        except Exception as exc:
            print(f"\n  {RED}{B}Error:{R} {exc}")
            _pause()
