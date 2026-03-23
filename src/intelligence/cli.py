"""Command-line entrypoint for intelligence."""

from __future__ import annotations

import argparse
import sys

from . import __version__


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

