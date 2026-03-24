"""Command-line entrypoint for intelligence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .workflows.jade_pack import jade_pack_spec
from .workflows.pack_runner import run_pack_flow
from .workflows.streetwear_pack import streetwear_pack_spec

_PACK_SPECS = {
    "jade": jade_pack_spec,
    "designer_streetwear": streetwear_pack_spec,
}


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
        help="Run a pack flow against MediaCrawler export data.",
    )
    run_pack.add_argument(
        "pack",
        choices=sorted(_PACK_SPECS),
        help="Project pack to run.",
    )
    run_pack.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to a MediaCrawler export JSONL file. Falls back to repo-local fixture when omitted.",
    )
    run_pack.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory that will receive the generated outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-pack":
        input_path: Path | None = args.input
        if input_path is not None and not input_path.is_file():
            print(f"error: input file not found: {input_path}", file=sys.stderr)
            return 1

        spec = _PACK_SPECS[args.pack]
        run_pack_flow(spec, args.output_dir, input_path=input_path)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
