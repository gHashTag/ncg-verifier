"""
anti_numerology.py — Generalized anti-numerology CI gate.

Ported and generalized from:
  trinity-s3ai/scripts/anti_numerology_gate.py
  https://github.com/gHashTag/trinity-s3ai

CHANGES FROM UPSTREAM (v0.1.0-alpha):
  1. Configurable atom list (was hardcoded; now passed via constructor or
     loaded from a config YAML/dict).
  2. Configurable minimum atom count (was hardcoded MIN_ATOM_TYPES = 2).
  3. Configurable approved tags (same seven defaults; extensible).
  4. Configurable structural whitelist (same defaults; extensible).
  5. Accepts any file suffix (not just .v) — default .v; overridable.
  6. scan_file / scan_dir return structured result objects for programmatic use.
  7. CLI entry point: `python -m ncg_verifier.anti_numerology --dir <path>`

BEHAVIOR (identical to upstream):
  - Scans files for Definition/Theorem lines that contain ≥ MIN_ATOM_TYPES
    distinct numerological atom types.
  - Checks for an approved honesty tag in the ±COMMENT_WINDOW lines
    surrounding the definition, or in a tagged section block, or file header.
  - Reports PASS / FLAG / WHITELIST / STRUCTURAL.
  - EXIT CODE: 0 if no FLAGs; 1 if any FLAG present (unless skip override).

OVERRIDE (identical to upstream):
  SKIP_NUMEROLOGY_CHECK=1 env var  OR  [skip-numerology-check] in GIT_COMMIT_MSG

APPROVED HONESTY TAGS (identical to upstream defaults):
  [phenomenological_fit]   — formula is a fit to data, not derived
  [NUMERICAL_FIT]          — numeric fit from Python/external computation
  [HONEST: ...]            — explicit honest acknowledgement
  [NCG_AXIOM]              — axiom from noncommutative geometry framework
  [PHYSICAL_AXIOM]         — axiom from physical input (PDG value etc.)
  [MATH_TODO]              — mathematical gap, to be proven later
  [LIBRARY_GAP]            — Coq library limitation, not a conceptual gap
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Default configuration (mirrors upstream anti_numerology_gate.py)
# ---------------------------------------------------------------------------

DEFAULT_NUMEROLOGY_ATOMS: list[str] = [
    r"\bphi\b",
    r"\bPI\b",
    r"\bexp\s+1\b",
    r"\bexp\b",
    r"\bsqrt\b",
    r"\bpow_pos\b",
    r"\bpowZ\b",
]

DEFAULT_MIN_ATOM_TYPES: int = 2

DEFAULT_APPROVED_TAGS: list[str] = [
    r"\[phenomenological_fit\]",
    r"\[NUMERICAL_FIT\]",
    r"HONEST\s*:",
    r"\[NCG_AXIOM\]",
    r"\[PHYSICAL_AXIOM\]",
    r"\[MATH_TODO\]",
    r"\[LIBRARY_GAP\]",
]

DEFAULT_STRUCTURAL_WHITELIST: frozenset[str] = frozenset({
    # Pure math definitions
    "phi", "pow_pos", "powZ", "e_const",
    # Common aliases for e = exp(1)
    "euler_e", "e_coq", "e_local", "e_val", "eulerE",
    # Common aliases for phi
    "phi_local", "phi_inv", "phi_inv_cube", "phi_inv_sq",
    # H4 group order and degrees (axiomatically defined, not fit to experiment)
    "H4_order", "h_H4", "d1", "d2", "d3", "d4",
    "vertices_600cell", "edges_600cell", "faces_600cell", "cells_600cell",
    # PDG experimental values (measurements, not numerology)
    "m_u_PDG", "m_d_PDG", "m_s_PDG", "m_c_PDG", "m_b_PDG", "m_t_PDG",
    "m_e_PDG", "m_mu_PDG", "m_tau_PDG",
    "delta_m21_sq_PDG", "delta_m31_sq_PDG", "sum_m_nu_PDG",
    "V_us_PDG", "V_cb_PDG", "V_ub_PDG",
    "alpha_inv_PDG", "sin2_theta_W_PDG", "sin2_theta_12_PDG",
    "sin2_theta_23_PDG", "sin2_theta_13_PDG",
    "m_H_PDG", "m_W_PDG", "m_Z_PDG",
    "sigma_exp", "m_H_exp",
    # Error bounds
    "SG_bound", "V_bound",
    # Geometric derived quantities
    "vol_S3_phi", "scalar_curvature", "ricci_sq",
    # RGE parameters
    "Lambda_H4", "m_Z",
})

DEFAULT_SKIP_FILES: frozenset[str] = frozenset({
    "CorePhi.v",
    "test_higgs.v",
    "test_interval.v",
    "test_scratch.v",
    "test_theorem.v",
})

DEFAULT_SECTION_TAG_MARKERS: list[str] = [
    r"SMOKING GUN FORMULAS",
    r"VERIFIED FORMULAS",
    r"SG-class",
    r"V-class",
    r"PREDICTIONS.*awaiting",
    r"phenomenological",
    r"феноменологическ",  # Russian "phenomenological"
    r"\[phenomenological_fit\]",
    r"\[NUMERICAL_FIT\]",
    r"HONEST\s*:",
    r"\[NCG_AXIOM\]",
    r"\[PHYSICAL_AXIOM\]",
    r"\[MATH_TODO\]",
    r"\[LIBRARY_GAP\]",
]

COMMENT_WINDOW: int = 12
FILE_HEADER_LINES: int = 30


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FormulaResult:
    """Result for a single formula/definition found during scanning."""
    file: str
    line_no: int
    def_name: str
    rhs_snippet: str
    atoms_found: list[str]
    tag_found: str | None
    status: str           # PASS | FLAG | WHITELIST | STRUCTURAL
    reason: str = ""

    def is_flag(self) -> bool:
        return self.status == "FLAG"

    def is_pass(self) -> bool:
        return self.status == "PASS"


@dataclass
class GateResult:
    """Aggregated result from scanning a directory or set of files."""
    results: list[FormulaResult] = field(default_factory=list)
    files_scanned: int = 0
    files_skipped: int = 0

    @property
    def passes(self) -> list[FormulaResult]:
        return [r for r in self.results if r.status == "PASS"]

    @property
    def flags(self) -> list[FormulaResult]:
        return [r for r in self.results if r.status == "FLAG"]

    @property
    def whitelisted(self) -> list[FormulaResult]:
        return [r for r in self.results if r.status == "WHITELIST"]

    @property
    def structural(self) -> list[FormulaResult]:
        return [r for r in self.results if r.status == "STRUCTURAL"]

    def passed(self) -> bool:
        """Return True if no FLAGs were found (gate passes)."""
        return len(self.flags) == 0

    def summary(self) -> str:
        lines = [
            "=" * 70,
            "ANTI-NUMEROLOGY GATE — Heuristic Formula Honesty Check",
            "NCG-Verifier | generalized from trinity-s3ai",
            "=" * 70,
            "",
            f"  PASS      : {len(self.passes):4d}  (multi-atom formulas with approved tag)",
            f"  FLAG      : {len(self.flags):4d}  (multi-atom formulas MISSING tag)",
            f"  WHITELIST : {len(self.whitelisted):4d}  (structural/PDG definitions, exempt)",
            f"  STRUCTURAL: {len(self.structural):4d}  (single-atom or pure-math, not checked)",
            f"  TOTAL defs: {len(self.results):4d}",
            f"  Files scanned : {self.files_scanned}",
            f"  Files skipped : {self.files_skipped}",
            "",
        ]
        if self.flags:
            lines.append("VERDICT: FAIL — Flagged formulas must be tagged before merge.")
        else:
            lines.append("VERDICT: PASS — All multi-atom numerological formulas are tagged.")
        lines.append("=" * 70)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# AntiNumerologyGate class
# ---------------------------------------------------------------------------

class AntiNumerologyGate:
    """
    Generalized anti-numerology gate for Coq (or other) source files.

    Directly ports the logic of trinity-s3ai/scripts/anti_numerology_gate.py
    with configurable parameters. Default configuration is identical to the
    upstream production gate.

    Usage:
        gate = AntiNumerologyGate()
        result = gate.scan_dir(Path("proofs/"))
        print(result.summary())
        sys.exit(0 if result.passed() else 1)

    Parameters:
        numerology_atoms: List of regex patterns that trigger the numerology check.
        min_atom_types: Minimum number of distinct atom types to trigger.
        approved_tags: List of regex patterns for approved honesty tags.
        structural_whitelist: Set of definition names exempt from the check.
        skip_files: Set of filenames to skip entirely.
        file_suffix: File extension to scan (default: ".v" for Coq).
        comment_window: Lines before/after a definition to search for tags.
    """

    def __init__(
        self,
        numerology_atoms: list[str] | None = None,
        min_atom_types: int = DEFAULT_MIN_ATOM_TYPES,
        approved_tags: list[str] | None = None,
        structural_whitelist: frozenset[str] | None = None,
        skip_files: frozenset[str] | None = None,
        section_tag_markers: list[str] | None = None,
        file_suffix: str = ".v",
        comment_window: int = COMMENT_WINDOW,
    ) -> None:
        self.numerology_atoms = numerology_atoms or DEFAULT_NUMEROLOGY_ATOMS
        self.min_atom_types = min_atom_types
        self.approved_tags = approved_tags or DEFAULT_APPROVED_TAGS
        self.structural_whitelist = structural_whitelist or DEFAULT_STRUCTURAL_WHITELIST
        self.skip_files = skip_files or DEFAULT_SKIP_FILES
        self.section_tag_markers = section_tag_markers or DEFAULT_SECTION_TAG_MARKERS
        self.file_suffix = file_suffix
        self.comment_window = comment_window

        # Pre-compile regex patterns
        self._atom_res = [re.compile(p) for p in self.numerology_atoms]
        self._tag_res = [re.compile(p, re.IGNORECASE) for p in self.approved_tags]
        self._marker_res = [
            re.compile(m, re.IGNORECASE) for m in self.section_tag_markers
        ]
        self._simple_def_re = re.compile(
            r"^\s*Definition\s+(\w+)\s*(?::\s*\w+\s*)?:=\s*(.+)"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan_file(self, path: Path | str) -> GateResult:
        """Scan a single file. Returns GateResult with results for that file."""
        path = Path(path)
        gate_result = GateResult(files_scanned=0, files_skipped=0)

        if path.name in self.skip_files:
            gate_result.files_skipped = 1
            return gate_result

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"[ERROR] Cannot read {path}: {e}", file=sys.stderr)
            return gate_result

        gate_result.files_scanned = 1
        lines = text.split("\n")
        definitions = self._extract_definitions(text)
        section_tagged = self._build_section_tag_map(lines)
        file_header_tag = self._file_has_header_tag(lines)

        for line_no, def_name, rhs in definitions:
            result = self._check_definition(
                str(path), lines, line_no, def_name, rhs,
                section_tagged, file_header_tag, text
            )
            gate_result.results.append(result)

        return gate_result

    def scan_dir(
        self, directory: Path | str, recursive: bool = False
    ) -> GateResult:
        """Scan all matching files in a directory."""
        directory = Path(directory)
        combined = GateResult()

        if not directory.is_dir():
            print(f"[WARN] Directory not found: {directory}", file=sys.stderr)
            return combined

        glob_pattern = f"**/*{self.file_suffix}" if recursive else f"*{self.file_suffix}"
        files = sorted(directory.glob(glob_pattern))

        if not files:
            print(f"[WARN] No {self.file_suffix} files found in {directory}", file=sys.stderr)
            return combined

        for f in files:
            file_result = self.scan_file(f)
            combined.results.extend(file_result.results)
            combined.files_scanned += file_result.files_scanned
            combined.files_skipped += file_result.files_skipped

        return combined

    # ------------------------------------------------------------------
    # Internal helpers (ported from upstream gate.py)
    # ------------------------------------------------------------------

    def _extract_definitions(self, text: str) -> list[tuple[int, str, str]]:
        """Return list of (line_no, def_name, rhs_snippet)."""
        lines = text.split("\n")
        results = []
        for i, line in enumerate(lines):
            m = self._simple_def_re.match(line)
            if m:
                def_name = m.group(1)
                rhs = m.group(2).strip()
                # Collect continuation lines (up to 5 more)
                j = i + 1
                while "." not in rhs and j < len(lines) and j < i + 6:
                    rhs += " " + lines[j].strip()
                    j += 1
                # Strip trailing comments and period
                rhs = re.sub(r"\(\*.*?\*\)", "", rhs).rstrip(". \t")
                results.append((i + 1, def_name, rhs))
        return results

    def _atoms_in_rhs(self, rhs: str) -> list[str]:
        """Return list of distinct atom types found in rhs."""
        return [p.pattern for p in self._atom_res if p.search(rhs)]

    def _find_tag_in_window(
        self, lines: list[str], line_no: int
    ) -> str | None:
        """Search ±comment_window lines for any approved tag."""
        start = max(0, line_no - self.comment_window - 1)
        end = min(len(lines), line_no + self.comment_window)
        snippet = "\n".join(lines[start:end])
        snippet_clean = re.sub(r"\(\*|\*\)", "", snippet)
        for tag_re in self._tag_res:
            if tag_re.search(snippet_clean):
                return tag_re.pattern
        return None

    def _build_section_tag_map(self, lines: list[str]) -> list[bool]:
        """Build per-line boolean: is this line inside a tagged section?"""
        n = len(lines)
        in_tagged = [False] * n
        section_active = False

        def _is_pure_sep(line: str) -> bool:
            stripped = line.strip()
            if not (stripped.startswith("(*") or stripped.startswith("(* ")):
                return False
            content = re.sub(r"\(\*|\*\)|\s", "", stripped)
            if len(content) < 10:
                return False
            eq_r = content.count("=") / len(content)
            dash_r = content.count("-") / len(content)
            star_r = content.count("*") / len(content)
            return eq_r > 0.6 or dash_r > 0.6 or star_r > 0.6

        def _has_marker(line: str) -> bool:
            clean = re.sub(r"\(\*|\*\)", "", line)
            return any(mr.search(clean) for mr in self._marker_res)

        i = 0
        while i < n:
            line = lines[i]
            if _has_marker(line):
                section_active = True
                in_tagged[i] = True
                i += 1
                continue
            if _is_pure_sep(line):
                found_marker = False
                found_untagged = False
                for j in range(i + 1, min(i + 8, n)):
                    if _has_marker(lines[j]):
                        found_marker = True
                        break
                    if lines[j].strip() and not _is_pure_sep(lines[j]):
                        found_untagged = True
                        break
                if found_marker:
                    section_active = True
                    in_tagged[i] = True
                elif found_untagged and section_active:
                    section_active = False
                    in_tagged[i] = False
                else:
                    in_tagged[i] = section_active
                i += 1
                continue
            in_tagged[i] = section_active
            i += 1

        return in_tagged

    def _file_has_header_tag(self, lines: list[str]) -> str | None:
        """Check for a file-level honesty tag in the first FILE_HEADER_LINES lines."""
        header = "\n".join(lines[:FILE_HEADER_LINES])
        header_clean = re.sub(r"\(\*|\*\)", "", header)
        for tag_re in self._tag_res:
            if tag_re.search(header_clean):
                return tag_re.pattern
        return None

    def _has_refutation_theorem(self, text: str, def_name: str) -> bool:
        """Check if a refutation theorem covers this definition."""
        pattern = re.compile(
            rf"(?:Theorem|Lemma)\s+\w*(?:refut|nogo|no_go|NGT|Fail|fail)\w*"
            rf".*?{re.escape(def_name)}",
            re.IGNORECASE | re.DOTALL,
        )
        return bool(pattern.search(text[:5000]))

    def _check_definition(
        self,
        filepath: str,
        lines: list[str],
        line_no: int,
        def_name: str,
        rhs: str,
        section_tagged: list[bool],
        file_header_tag: str | None,
        full_text: str,
    ) -> FormulaResult:
        """Evaluate a single definition and return a FormulaResult."""
        if def_name in self.structural_whitelist:
            return FormulaResult(
                file=filepath, line_no=line_no, def_name=def_name,
                rhs_snippet=rhs[:80], atoms_found=[], tag_found=None,
                status="WHITELIST",
                reason="Structural/PDG definition — exempt from numerology check",
            )

        atoms = self._atoms_in_rhs(rhs)
        if len(atoms) < self.min_atom_types:
            return FormulaResult(
                file=filepath, line_no=line_no, def_name=def_name,
                rhs_snippet=rhs[:80], atoms_found=atoms, tag_found=None,
                status="STRUCTURAL",
                reason=f"Only {len(atoms)} atom type(s) — below threshold {self.min_atom_types}",
            )

        tag = self._find_tag_in_window(lines, line_no)
        idx = min(line_no - 1, len(section_tagged) - 1)
        in_section = section_tagged[idx] if idx >= 0 else False
        refuted = self._has_refutation_theorem(full_text, def_name)

        if tag is not None:
            status = "PASS"
            reason = f"Tag found in ±{self.comment_window} lines: {tag}"
        elif file_header_tag is not None:
            status = "PASS"
            reason = f"File-level honesty tag in header: {file_header_tag}"
        elif in_section:
            status = "PASS"
            reason = "Inside a tagged section block"
        elif refuted:
            status = "PASS"
            reason = "Covered by Refutation/NoGo theorem in same file"
        else:
            status = "FLAG"
            reason = (
                f"Multi-atom numerology ({len(atoms)} atom types) — "
                f"no approved honesty tag in ±{self.comment_window} lines"
            )

        return FormulaResult(
            file=filepath, line_no=line_no, def_name=def_name,
            rhs_snippet=rhs[:80], atoms_found=atoms, tag_found=tag,
            status=status, reason=reason,
        )


# ---------------------------------------------------------------------------
# CLI entry point (mirrors upstream main())
# ---------------------------------------------------------------------------

def _should_skip() -> bool:
    if os.environ.get("SKIP_NUMEROLOGY_CHECK", "").strip() == "1":
        print("[WARN] SKIP_NUMEROLOGY_CHECK=1 — gate downgraded to warning",
              file=sys.stderr)
        return True
    commit_msg = (os.environ.get("GIT_COMMIT_MSG", "")
                  or os.environ.get("COMMIT_MESSAGE", ""))
    if "[skip-numerology-check]" in commit_msg:
        print("[WARN] [skip-numerology-check] in commit message — "
              "gate downgraded to warning", file=sys.stderr)
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Anti-numerology gate: detect unjustified phi/pi/e formulas "
            "in Coq (or other) source files. "
            "Generalized from trinity-s3ai/scripts/anti_numerology_gate.py."
        )
    )
    parser.add_argument(
        "--dir", type=Path, default=Path("proofs"),
        help="Directory containing source files to scan (default: proofs/)",
    )
    parser.add_argument(
        "--suffix", default=".v",
        help="File extension to scan (default: .v)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show PASS and WHITELIST details in addition to FLAGs",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat WARN-level issues (skip override active) as failures",
    )
    parser.add_argument(
        "--recursive", "-r", action="store_true",
        help="Scan directories recursively",
    )
    args = parser.parse_args(argv)

    gate = AntiNumerologyGate(file_suffix=args.suffix)
    print("NCG-Verifier anti-numerology gate")
    print(f"Scanning: {args.dir.resolve()}")
    print()

    result = gate.scan_dir(args.dir, recursive=args.recursive)

    # Print flagged formulas
    if result.flags:
        print("── FLAGGED FORMULAS (require honesty tag) " + "─" * 29)
        for r in result.flags:
            print(f"  FLAG  {r.file}:{r.line_no}")
            print(f"        Definition {r.def_name} := {r.rhs_snippet}")
            print(f"        Atoms: {r.atoms_found}")
            print(f"        {r.reason}")
            print()

    if args.verbose and result.passes:
        print("── PASSING FORMULAS ─────────────────────────────────────────────")
        for r in result.passes:
            print(f"  PASS  {r.file}:{r.line_no}  [{r.def_name}]  tag={r.tag_found}")

    print()
    print(result.summary())

    if result.passed():
        return 0

    if _should_skip() and not args.strict:
        print("[WARN] Gate overridden — exiting with 0 (warnings only)")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
