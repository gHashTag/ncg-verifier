"""
cli.py — Command-line entry point for ncg-verifier.

Usage:
    ncg-verifier --help
    ncg-verifier anti-numerology --dir proofs/ [--verbose] [--recursive]
    ncg-verifier version

Full pipeline commands (validate, run, ci) are planned for M2 (week 6).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ncg-verifier",
        description=(
            "NCG-Verifier: formal verification pipeline for "
            "noncommutative geometry spectral triples.\n"
            "\n"
            "v0.1.0-alpha — anti-numerology gate is fully implemented; "
            "axiom checkers and model loader are stubs (M3/M2, weeks 12/6)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version",
        version="ncg-verifier 0.1.0-alpha",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # --- anti-numerology subcommand ---
    anti_parser = subparsers.add_parser(
        "anti-numerology",
        help="Run the anti-numerology gate on a directory of source files.",
        aliases=["gate"],
    )
    anti_parser.add_argument(
        "--dir", type=Path, default=Path("proofs"),
        help="Directory to scan (default: proofs/)",
    )
    anti_parser.add_argument(
        "--suffix", default=".v",
        help="File extension to scan (default: .v)",
    )
    anti_parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show passing/whitelisted results",
    )
    anti_parser.add_argument(
        "--recursive", "-r", action="store_true",
        help="Scan subdirectories recursively",
    )
    anti_parser.add_argument(
        "--strict", action="store_true",
        help="Ignore skip overrides (always fail on FLAG)",
    )

    # --- version subcommand ---
    subparsers.add_parser("version", help="Show version and exit.")

    # --- validate subcommand (stub) ---
    val_parser = subparsers.add_parser(
        "validate",
        help="[STUB M2] Validate a model YAML/JSON schema.",
    )
    val_parser.add_argument("--model", type=Path, required=True)

    # --- run subcommand (stub) ---
    run_parser = subparsers.add_parser(
        "run",
        help="[STUB M3] Run full verification pipeline.",
    )
    run_parser.add_argument("--model", type=Path, required=True)
    run_parser.add_argument("--coq-dir", type=Path)
    run_parser.add_argument("--lean-dir", type=Path)
    run_parser.add_argument("--output", type=Path)

    args = parser.parse_args(argv)

    if args.command in ("anti-numerology", "gate"):
        # Delegate to anti_numerology.main with translated argv
        from ncg_verifier.anti_numerology import main as gate_main
        gate_argv = ["--dir", str(args.dir), "--suffix", args.suffix]
        if args.verbose:
            gate_argv.append("--verbose")
        if args.recursive:
            gate_argv.append("--recursive")
        if args.strict:
            gate_argv.append("--strict")
        return gate_main(gate_argv)

    elif args.command == "version":
        from ncg_verifier import __version__
        print(f"ncg-verifier {__version__}")
        return 0

    elif args.command == "validate":
        # STUB: full implementation in M2 (week 6)
        print(
            f"[STUB] ncg-verifier validate: schema validation not yet implemented.\n"
            f"       Model file: {args.model}\n"
            f"       Full implementation in milestone M2 (week 6).\n"
            f"       See docs/roadmap.md for timeline."
        )
        return 0

    elif args.command == "run":
        # STUB: full implementation in M3 (week 12)
        print(
            f"[STUB] ncg-verifier run: full pipeline not yet implemented.\n"
            f"       Model file  : {args.model}\n"
            f"       Coq dir     : {args.coq_dir}\n"
            f"       Lean dir    : {args.lean_dir}\n"
            f"       Output      : {args.output}\n"
            f"       Full implementation in milestone M3 (week 12).\n"
            f"       See docs/roadmap.md for timeline."
        )
        return 0

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
