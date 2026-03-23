"""Command-line entrypoint for intelligence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .workflows.jade_pack import run_jade_pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intelligence",
        description="Multi-category research engine for collected social content.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"intelligence {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_pack = subparsers.add_parser(
        "run-pack",
        help="Run a tiny pack-local proof flow.",
    )
    run_pack.add_argument(
        "pack",
        choices=("jade",),
        help="Project pack to run.",
    )
    run_pack.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory that will receive the generated demo outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-pack":
        if args.pack == "jade":
            run_jade_pack(args.output_dir)
            return 0

        parser.error(f"unsupported pack: {args.pack}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
