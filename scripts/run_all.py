#!/usr/bin/env python3
"""
scripts/run_all.py
Ejecuta los tres problemas del Proyecto 2 y genera todos los outputs.

Uso:
    python scripts/run_all.py              # todo completo
    python scripts/run_all.py --no-gif    # omite GIFs de resolución (más rápido)
    python scripts/run_all.py --problema 2  # solo problema 2
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

_DIVIDER = "=" * 60


def run(cmd: List[str]) -> None:
    label = " ".join(cmd[2:])  # skip "python -m"
    print(f"\n  → {label}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"\n  ERROR: falló con código {result.returncode}")
        sys.exit(result.returncode)


def problema1(seed: int = 42) -> None:
    print(f"\n{_DIVIDER}")
    print("  PROBLEMA 1 — Generación de laberintos: Prim vs Kruskal")
    print(_DIVIDER)
    run([PYTHON, "-m", "src.main", "buildviz",
         "--rows", "30", "--cols", "40",
         "--seed", str(seed),
         "--out-dir", "reports/problema1"])


def problema2(no_gif: bool = False, seed: int = 42) -> None:
    print(f"\n{_DIVIDER}")
    print("  PROBLEMA 2 — Resolución de laberinto 60×80 (todas las combinaciones)")
    print(_DIVIDER)
    for generator in ["prim", "kruskal"]:
        for search in ["bfs", "dfs", "ucs", "astar"]:
            cmd = [
                PYTHON, "-m", "src.main", "solve",
                "--generator", generator,
                "--search", search,
                "--rows", "60", "--cols", "80",
                "--seed", str(seed),
                "--out-dir", f"reports/problema2/{generator}_{search}",
            ]
            if no_gif:
                cmd.append("--no-gif")
            run(cmd)


def problema3(seed: int = 42) -> None:
    print(f"\n{_DIVIDER}")
    print("  PROBLEMA 3 — Comparación K=25 escenarios 45×55")
    print(_DIVIDER)
    for generator in ["prim", "kruskal"]:
        run([PYTHON, "-m", "src.main", "compare",
             "--generator", generator,
             "--rows", "45", "--cols", "55",
             "--k", "25",
             "--seed", str(seed),
             "--out-dir", f"reports/problema3/{generator}"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera todos los outputs del Proyecto 2")
    parser.add_argument("--no-gif", action="store_true", help="Omite GIFs de resolución (más rápido)")
    parser.add_argument("--problema", type=int, choices=[1, 2, 3], default=None,
                        help="Ejecuta solo el problema indicado")
    parser.add_argument("--seed", type=int, default=42, help="Semilla global para reproducibilidad")
    args = parser.parse_args()

    print(f"\n{_DIVIDER}")
    print("  PROYECTO 2 — IA: Generando todos los outputs")
    print(_DIVIDER)

    if args.problema is None or args.problema == 1:
        problema1(seed=args.seed)
    if args.problema is None or args.problema == 2:
        problema2(no_gif=args.no_gif, seed=args.seed)
    if args.problema is None or args.problema == 3:
        problema3(seed=args.seed)

    print(f"\n{_DIVIDER}")
    print("  ¡Listo! Todos los outputs generados.")
    print(f"  Ver carpeta: reports/")
    print(_DIVIDER + "\n")


if __name__ == "__main__":
    main()
