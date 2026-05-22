"""
cli.py — Command-line entry point for ncg-verifier.

Usage:
    ncg-verifier --help
    ncg-verifier anti-numerology --dir proofs/ [--verbose] [--recursive]
    ncg-verifier atlas list [--atlas-dir atlas/entries/]
    ncg-verifier atlas show <id> [--atlas-dir atlas/entries/]
    ncg-verifier version

Full pipeline commands (validate, run, ci) are planned for M3 (week 12).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _find_atlas_dir(explicit: Path | None) -> Path:
    """
    Resolve the atlas entries directory.

    If explicit is given, use it. Otherwise, look for atlas/entries/ relative
    to the current working directory, then relative to this file's package root.
    """
    if explicit is not None:
        return explicit
    # Try cwd first
    cwd_candidate = Path.cwd() / "atlas" / "entries"
    if cwd_candidate.exists():
        return cwd_candidate
    # Try relative to the package (installed or source)
    pkg_root = Path(__file__).parent.parent.parent  # src/ncg_verifier -> repo root
    pkg_candidate = pkg_root / "atlas" / "entries"
    if pkg_candidate.exists():
        return pkg_candidate
    return cwd_candidate  # return even if not found; error will be raised by loader


def _cmd_atlas_list(args: argparse.Namespace) -> int:
    """Implement `ncg-verifier atlas list`."""
    from ncg_verifier.atlas_loader import load_all

    atlas_dir = _find_atlas_dir(getattr(args, "atlas_dir", None))
    if not atlas_dir.exists():
        print(
            f"Error: atlas entries directory not found: {atlas_dir}\n"
            f"Use --atlas-dir to specify the path.",
            file=sys.stderr,
        )
        return 1

    try:
        entries = load_all(atlas_dir)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error loading atlas entries: {exc}", file=sys.stderr)
        return 1

    if not entries:
        print("No entries found in atlas.")
        return 0

    # Sort by id for deterministic output
    sorted_entries = sorted(entries.values(), key=lambda e: e.id)

    print(f"NCG Atlas — {len(entries)} entries")
    print("-" * 72)
    for entry in sorted_entries:
        status_marker = "✓" if entry.is_confirmed_no_go() else "○"
        obs = ", ".join(entry.obstruction_types())
        ko = f"KO={entry.KO_dimension}" if entry.KO_dimension is not None else "KO=?"
        print(
            f"{status_marker} {entry.id:<14}  "
            f"{entry.proof_status:<20}  "
            f"{ko:<6}  "
            f"{obs}"
        )
    print("-" * 72)
    confirmed = sum(1 for e in entries.values() if e.is_confirmed_no_go())
    open_count = sum(1 for e in entries.values() if e.is_open())
    print(f"  formally_verified: {confirmed}  |  open (candidate/informal): {open_count}")
    return 0


def _cmd_atlas_show(args: argparse.Namespace) -> int:
    """Implement `ncg-verifier atlas show <id>`."""
    from ncg_verifier.atlas_loader import load_all

    atlas_dir = _find_atlas_dir(getattr(args, "atlas_dir", None))
    if not atlas_dir.exists():
        print(
            f"Error: atlas entries directory not found: {atlas_dir}\n"
            f"Use --atlas-dir to specify the path.",
            file=sys.stderr,
        )
        return 1

    try:
        entries = load_all(atlas_dir)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error loading atlas entries: {exc}", file=sys.stderr)
        return 1

    entry_id: str = args.id
    # Normalize: NCG- prefix, uppercase
    if not entry_id.startswith("NCG-"):
        entry_id = "NCG-" + entry_id.upper()
    else:
        entry_id = entry_id.upper()

    entry = entries.get(entry_id)
    if entry is None:
        print(
            f"Error: entry {entry_id!r} not found.\n"
            f"Available: {', '.join(sorted(entries.keys()))}",
            file=sys.stderr,
        )
        return 1

    # Pretty-print the entry
    print(f"\n{'=' * 72}")
    print(f"Atlas Entry: {entry.id}")
    print(f"{'=' * 72}")
    print(f"  Model          : {entry.model_name}")
    print(f"  Version        : {entry.version}")
    print(f"  Date Added     : {entry.date_added}")
    print(f"  Algebra        : {entry.algebra}")
    print(f"  Algebra Type   : {entry.algebra_type}")
    print(f"  KO-dimension   : {entry.KO_dimension}")
    print(f"  Hilbert Space  : {entry.hilbert_space_description}")
    print(f"  Dirac Operator : {entry.dirac_operator_description}")
    print(f"  Real Structure : {entry.real_structure_J}")
    print(f"  Grading γ      : {entry.grading_gamma}")
    print()
    print(f"  Obstruction Type : {', '.join(entry.obstruction_types())}")
    print(f"  Proof System     : {entry.proof_system}")
    print(f"  Proof Status     : {entry.proof_status}")
    if entry.theorem_name:
        print(f"  Theorem Name     : {entry.theorem_name}")
    if entry.proof_path:
        print(f"  Proof Path       : {entry.proof_path}")
    if entry.admitted_count is not None:
        print(f"  Admitted Count   : {entry.admitted_count}")
    print()
    print("  Obstruction (informal):")
    for line in entry.obstruction_informal.strip().splitlines():
        print(f"    {line.strip()}")
    print()
    if entry.proof_notes:
        print("  Proof Notes:")
        for line in entry.proof_notes.strip().splitlines():
            print(f"    {line.strip()}")
        print()
    if entry.literature_citation:
        print("  Citations:")
        for cite in entry.literature_citation:
            authors = ", ".join(cite.authors[:2])
            if len(cite.authors) > 2:
                authors += " et al."
            print(f"    [{cite.relevance}] {authors} ({cite.year}): {cite.title}")
            print(f"      {cite.doi_or_arxiv}")
    if entry.related_entries:
        print()
        print(f"  Related Entries: {', '.join(entry.related_entries)}")
    print(f"{'=' * 72}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ncg-verifier",
        description=(
            "NCG-Verifier: formal verification pipeline for "
            "noncommutative geometry spectral triples.\n"
            "\n"
            "v0.1.0-alpha — anti-numerology gate is fully implemented; "
            "atlas loader is M2 complete; "
            "axiom checkers are stubs (M3, week 12)."
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

    # --- atlas subcommand ---
    atlas_parser = subparsers.add_parser(
        "atlas",
        help="Query the V3 NCG No-Go Atlas (M2 implemented).",
    )
    atlas_parser.add_argument(
        "--atlas-dir", type=Path, default=None, dest="atlas_dir",
        help="Path to atlas entries directory (default: auto-detect atlas/entries/)",
    )
    atlas_subparsers = atlas_parser.add_subparsers(
        dest="atlas_command", help="Atlas subcommand"
    )

    # atlas list
    atlas_list_parser = atlas_subparsers.add_parser(
        "list",
        help="List all atlas entries.",
    )
    atlas_list_parser.add_argument(
        "--atlas-dir", type=Path, default=None, dest="atlas_dir",
        help="Path to atlas entries directory",
    )

    # atlas show <id>
    atlas_show_parser = atlas_subparsers.add_parser(
        "show",
        help="Show details of one atlas entry by ID.",
    )
    atlas_show_parser.add_argument(
        "id",
        help="Atlas entry ID, e.g. NCG-A4-001",
    )
    atlas_show_parser.add_argument(
        "--atlas-dir", type=Path, default=None, dest="atlas_dir",
        help="Path to atlas entries directory",
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
        from ncg_verifier.anti_numerology import main as gate_main
        gate_argv = ["--dir", str(args.dir), "--suffix", args.suffix]
        if args.verbose:
            gate_argv.append("--verbose")
        if args.recursive:
            gate_argv.append("--recursive")
        if args.strict:
            gate_argv.append("--strict")
        return gate_main(gate_argv)

    elif args.command == "atlas":
        if not hasattr(args, "atlas_command") or args.atlas_command is None:
            atlas_parser.print_help()
            return 0
        if args.atlas_command == "list":
            return _cmd_atlas_list(args)
        elif args.atlas_command == "show":
            return _cmd_atlas_show(args)
        else:
            atlas_parser.print_help()
            return 0

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
