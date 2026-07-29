"""Command-line interface for EpiReSIM."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .api import run
from .exceptions import EpiReSIMError
from .types import SimulationConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="epiresim",
        description="Simulate case-control SNP data with epistatic models.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    simulate = subparsers.add_parser("simulate", help="run an EpiReSIM simulation")
    simulate.add_argument("reference", type=Path, help="MATLAB v5 reference dataset")
    simulate.add_argument("--cases", type=int, required=True, help="number of case samples")
    simulate.add_argument(
        "--controls", type=int, required=True, help="number of control samples"
    )
    simulate.add_argument("--snps", type=int, required=True, help="number of SNP columns")
    simulate.add_argument(
        "--maf",
        type=float,
        nargs="+",
        required=True,
        metavar="VALUE",
        help="target MAF for each causal locus",
    )
    simulate.add_argument(
        "--prevalence", type=float, required=True, help="target model prevalence"
    )
    simulate.add_argument(
        "--heritability",
        type=float,
        default=None,
        help="optional target broad-sense heritability",
    )
    simulate.add_argument(
        "--order", type=int, required=True, choices=range(2, 6), help="interaction order"
    )
    simulate.add_argument(
        "--replicates", type=int, required=True, help="number of datasets to generate"
    )
    simulate.add_argument("--prefix", required=True, help="output filename prefix")
    simulate.add_argument(
        "--format",
        dest="formats",
        action="append",
        required=True,
        choices=("mat", "txt"),
        help="output format; repeat to request both",
    )
    simulate.add_argument("--seed", type=int, default=None, help="local random seed")
    simulate.add_argument(
        "--output-dir", type=Path, default=Path("."), help="output directory"
    )
    simulate.add_argument(
        "--mode",
        choices=("compatibility", "strict"),
        default="compatibility",
        help="solver and sampling behavior (default: compatibility)",
    )
    simulate.add_argument(
        "--max-sampling-attempts",
        type=int,
        default=1_000_000,
        help=argparse.SUPPRESS,
    )
    return parser


def _config_from_args(args: argparse.Namespace) -> SimulationConfig:
    return SimulationConfig(
        reference_path=args.reference,
        case_count=args.cases,
        control_count=args.controls,
        snp_count=args.snps,
        mafs=tuple(args.maf),
        prevalence=args.prevalence,
        heritability=args.heritability,
        order=args.order,
        replicates=args.replicates,
        output_prefix=args.prefix,
        output_formats=tuple(args.formats),
        seed=args.seed,
        output_dir=args.output_dir,
        mode=args.mode,
        max_sampling_attempts=args.max_sampling_attempts,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(_config_from_args(args))
    except (EpiReSIMError, OSError) as error:
        parser.exit(2, f"epiresim: error: {error}\n")
    print(
        f"Generated {len(result.matrices)} dataset(s); "
        f"prevalence={result.model.prevalence:.6f}; "
        f"heritability={result.model.heritability:.6f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
