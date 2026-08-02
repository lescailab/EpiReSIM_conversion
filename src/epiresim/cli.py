"""Command-line interface for EpiReSIM."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .api import run
from .exceptions import EpiReSIMError
from .reference import (
    build_reference_from_vcf,
    export_mat_reference,
    import_mat_reference,
    inspect_reference_bundle,
    validate_reference_bundle,
)
from .types import SimulationConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="epiresim",
        description="Simulate case-control SNP data with epistatic models.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    simulate = subparsers.add_parser("simulate", help="run an EpiReSIM simulation")
    simulate.add_argument("reference", type=Path, help="native bundle or MATLAB v5 reference")
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

    reference = subparsers.add_parser(
        "reference", help="build, inspect, validate, or convert reference data"
    )
    reference_commands = reference.add_subparsers(dest="reference_command", required=True)

    build = reference_commands.add_parser(
        "build", help="build a native reference bundle from VCF or VCF.GZ"
    )
    build.add_argument("vcf", type=Path, help="input VCF or VCF.GZ")
    build.add_argument("--output", type=Path, required=True, help="output .epiref directory")
    build.add_argument(
        "--genome-build", required=True, help="reference assembly, for example GRCh38"
    )
    build.add_argument("--chromosome", help="chromosome to retain")
    build.add_argument("--sample-file", type=Path, help="optional sample IDs, one per line")
    build.add_argument(
        "--sample-metadata", type=Path, help="optional tab-separated sample metadata"
    )
    build.add_argument("--population", help="population value to select from sample metadata")
    build.add_argument("--sample-column", default="sample", help="sample ID metadata column")
    build.add_argument(
        "--population-column", default="population", help="population metadata column"
    )
    build.add_argument("--min-maf", type=float, default=0.0, help="minimum donor-panel MAF")
    build.add_argument(
        "--include-filtered", action="store_true", help="include records not marked PASS or '.'"
    )
    build.add_argument("--source-name", help="source panel name for the manifest")
    build.add_argument("--source-url", help="source URL for the manifest")
    build.add_argument("--source-release", help="source release for the manifest")

    import_mat = reference_commands.add_parser(
        "import-mat", help="convert a legacy MATLAB reference to a native bundle"
    )
    import_mat.add_argument("mat", type=Path, help="input MATLAB v5 reference")
    import_mat.add_argument("--output", type=Path, required=True, help="output .epiref directory")
    import_mat.add_argument("--genome-build", default="unknown", help="known reference assembly")

    export_mat = reference_commands.add_parser(
        "export-mat", help="export a native bundle in the legacy MATLAB schema"
    )
    export_mat.add_argument("reference", type=Path, help="input native reference bundle")
    export_mat.add_argument("--output", type=Path, required=True, help="output MATLAB v5 file")

    inspect = reference_commands.add_parser("inspect", help="print reference metadata as JSON")
    inspect.add_argument("reference", type=Path, help="input native reference bundle")

    validate = reference_commands.add_parser("validate", help="validate a native reference bundle")
    validate.add_argument("reference", type=Path, help="input native reference bundle")
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
        if args.command == "reference":
            if args.reference_command == "build":
                path = build_reference_from_vcf(
                    args.vcf,
                    args.output,
                    genome_build=args.genome_build,
                    chromosome=args.chromosome,
                    sample_file=args.sample_file,
                    sample_metadata=args.sample_metadata,
                    population=args.population,
                    sample_column=args.sample_column,
                    population_column=args.population_column,
                    min_maf=args.min_maf,
                    include_filtered=args.include_filtered,
                    source_name=args.source_name,
                    source_url=args.source_url,
                    source_release=args.source_release,
                )
                print(f"Built native reference bundle: {path}")
            elif args.reference_command == "import-mat":
                path = import_mat_reference(
                    args.mat, args.output, genome_build=args.genome_build
                )
                print(f"Imported native reference bundle: {path}")
            elif args.reference_command == "export-mat":
                path = export_mat_reference(args.reference, args.output)
                print(f"Exported MATLAB reference: {path}")
            elif args.reference_command == "inspect":
                print(
                    json.dumps(
                        inspect_reference_bundle(args.reference), indent=2, sort_keys=True
                    )
                )
            else:
                validate_reference_bundle(args.reference)
                print(f"Reference bundle is valid: {args.reference}")
            return 0
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
