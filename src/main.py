"""
src/main.py
Entry point for Proyecto 2 - IA.

  • No arguments   → launches the interactive TUI menu (src/menu.py)
  • With arguments → full CLI (argparse subcommands: solve / compare / buildviz)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Support both `python -m src.main` and `python src/main.py`
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.runner import run_buildviz, run_compare, run_solve


# ── CLI sub-command handlers ──────────────────────────────────────────────────

def _cmd_solve(args: argparse.Namespace) -> None:
    run_solve(
        generator=args.generator,
        search=args.search,
        rows=args.rows,
        cols=args.cols,
        seed=args.seed,
        animate_frames=args.animate_frames,
        animate_fps=args.animate_fps,
        no_gif=args.no_gif,
        out_dir=args.out_dir,
    )


def _cmd_compare(args: argparse.Namespace) -> None:
    run_compare(
        generator=args.generator,
        rows=args.rows,
        cols=args.cols,
        k=args.k,
        seed=args.seed,
        min_manhattan=args.min_manhattan,
        out_dir=args.out_dir,
    )


def _cmd_buildviz(args: argparse.Namespace) -> None:
    run_buildviz(
        rows=args.rows,
        cols=args.cols,
        seed=args.seed,
        max_frames=args.max_frames,
        fps=args.fps,
        out_dir=args.out_dir,
    )


# ── Argument parser ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Proyecto 2 IA — Laberintos y busqueda",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- solve ---
    sp = sub.add_parser(
        "solve",
        help="Genera un laberinto, lo resuelve y guarda 3 outputs (maze / gif / solved).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sp.add_argument("--generator", choices=["prim", "kruskal"], default="prim")
    sp.add_argument("--search", choices=["bfs", "dfs", "ucs", "astar"], default="astar")
    sp.add_argument("--rows", type=int, default=60)
    sp.add_argument("--cols", type=int, default=80)
    sp.add_argument("--seed", type=int, default=42)
    sp.add_argument("--out-dir", default=None, help="Directorio de salida (auto si se omite).")
    sp.add_argument("--animate-frames", type=int, default=140)
    sp.add_argument("--animate-fps", type=int, default=12)
    sp.add_argument("--no-gif", action="store_true", default=False, help="Omite el GIF animado.")
    sp.set_defaults(func=_cmd_solve)

    # --- compare ---
    cp = sub.add_parser(
        "compare",
        help="Ejecuta K escenarios y compara BFS/DFS/UCS/A*.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cp.add_argument("--generator", choices=["prim", "kruskal"], default="prim")
    cp.add_argument("--rows", type=int, default=45)
    cp.add_argument("--cols", type=int, default=55)
    cp.add_argument("--k", type=int, default=25)
    cp.add_argument("--seed", type=int, default=42)
    cp.add_argument("--min-manhattan", type=int, default=10)
    cp.add_argument("--out-dir", default=None, help="Directorio raiz de salida (auto si se omite).")
    cp.set_defaults(func=_cmd_compare)

    # --- buildviz ---
    bv = sub.add_parser(
        "buildviz",
        help="Genera 3 outputs: Prim final / Kruskal final / GIF de construccion.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    bv.add_argument("--rows", type=int, default=30)
    bv.add_argument("--cols", type=int, default=40)
    bv.add_argument("--seed", type=int, default=42)
    bv.add_argument("--max-frames", type=int, default=120)
    bv.add_argument("--fps", type=int, default=12)
    bv.add_argument("--out-dir", default=None, help="Directorio de salida (auto si se omite).")
    bv.set_defaults(func=_cmd_buildviz)

    return parser


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) == 1:
        # No arguments → launch interactive TUI menu
        from src.menu import run_interactive_menu
        run_interactive_menu()
        return

    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
