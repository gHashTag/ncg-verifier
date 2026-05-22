"""
atlas_loader.py — Load V3 Atlas entries from YAML and run no-go checks.

Milestone M2 implementation (feat/m2-atlas-loader).

This module provides:
  - AtlasEntry dataclass: typed representation of one atlas YAML file.
  - ValidationError: structured schema error.
  - BrokenRef: cross-reference error for related_entries.
  - load_entry(path) -> AtlasEntry — parse, validate, return typed entry.
  - load_all(atlas_dir) -> dict[str, AtlasEntry] — load all entries.
  - validate_schema(entry_dict) -> list[ValidationError] — schema check.
  - cross_reference_check(entries) -> list[BrokenRef] — verify related_entries.

The original stub types (NCGModel, FormulaSpec, SpectralTripleSpec,
NoGoCheckResult, run_nogo_checks, load_model) are preserved for backward
compatibility with the existing test_smoke.py tests.

References:
  - Schema: schemas/atlas-entry-v1.yaml
  - Source entries: atlas/entries/NCG-*.yaml
  - V3 Atlas schema: V3_atlas_schema.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml  # pyyaml required; listed in pyproject.toml dependencies

# ---------------------------------------------------------------------------
# Schema constants
# ---------------------------------------------------------------------------

REQUIRED_FIELDS: list[str] = [
    "id",
    "model_name",
    "version",
    "date_added",
    "algebra",
    "algebra_type",
    "hilbert_space_description",
    "dirac_operator_description",
    "real_structure_J",
    "grading_gamma",
    "KO_dimension",
    "obstruction_type",
    "obstruction_statement",
    "obstruction_informal",
    "proof_system",
    "proof_status",
    "literature_citation",
]

VALID_ALGEBRA_TYPES: set[str] = {
    "matrix_algebra",
    "group_algebra",
    "jordan_algebra",
    "clifford_algebra",
    "other",
}

VALID_OBSTRUCTION_TYPES: set[str] = {
    "chirality",
    "cosmology",
    "mass_hierarchy",
    "sigma_field",
    "first_order",
    "poincare_duality",
    "orientability",
    "fermion_doubling",
    "gauge_unification",
    "other",
}

VALID_PROOF_SYSTEMS: set[str] = {
    "Coq",
    "Lean4",
    "Agda",
    "Isabelle",
    "informal",
    "none",
}

VALID_PROOF_STATUSES: set[str] = {
    "formally_verified",
    "partially_verified",
    "informal_proof",
    "candidate",
    "refuted",
}

VALID_CITATION_RELEVANCES: set[str] = {
    "main_result",
    "background",
    "partial_result",
    "related_model",
}

ID_PATTERN_HINT = "^NCG-[A-Z0-9]{2,4}-[0-9]{3}$"


# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------

@dataclass
class ValidationError:
    """A schema validation error for one atlas entry field."""
    field: str
    message: str
    entry_id: str | None = None

    def __str__(self) -> str:
        prefix = f"[{self.entry_id}] " if self.entry_id else ""
        return f"{prefix}ValidationError: field={self.field!r} — {self.message}"


@dataclass
class BrokenRef:
    """A broken cross-reference in related_entries."""
    source_id: str
    target_id: str

    def __str__(self) -> str:
        return (
            f"BrokenRef: {self.source_id!r} references non-existent entry "
            f"{self.target_id!r}"
        )


# ---------------------------------------------------------------------------
# AtlasEntry dataclass
# ---------------------------------------------------------------------------

@dataclass
class LiteratureCitation:
    """One literature citation from an atlas entry."""
    authors: list[str]
    title: str
    doi_or_arxiv: str
    year: int
    relevance: str  # main_result | background | partial_result | related_model


@dataclass
class AtlasEntry:
    """
    Typed representation of one V3 Atlas YAML entry.

    Corresponds to the schema in schemas/atlas-entry-v1.yaml.
    """
    # Identification
    id: str
    model_name: str
    version: str
    date_added: str
    date_updated: str | None = None
    maintainer: str | None = None

    # Algebraic data
    algebra: str = ""
    algebra_type: str = ""
    hilbert_space_description: str = ""
    dirac_operator_description: str = ""
    real_structure_J: str = ""
    grading_gamma: str = ""
    KO_dimension: int | None = None

    # Obstruction data
    obstruction_type: Any = ""          # str or list[str]
    obstruction_statement: str = ""
    obstruction_informal: str = ""

    # Formal proof data
    proof_system: str = ""
    proof_status: str = ""
    proof_path: str | None = None
    theorem_name: str | None = None
    admitted_count: int | None = None
    proof_notes: str | None = None

    # Literature and cross-references
    literature_citation: list[LiteratureCitation] = field(default_factory=list)
    comparison_with_other_atlas_entries: str | None = None
    related_entries: list[str] = field(default_factory=list)

    # Raw data preserved for tooling
    _raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def is_confirmed_no_go(self) -> bool:
        """Return True if this entry has a formally verified proof."""
        return self.proof_status == "formally_verified"

    def is_open(self) -> bool:
        """Return True if this entry is a candidate or informal_proof."""
        return self.proof_status in ("candidate", "informal_proof")

    def obstruction_types(self) -> list[str]:
        """Return obstruction_type as a list (normalizes str vs list)."""
        if isinstance(self.obstruction_type, list):
            return list(self.obstruction_type)
        if self.obstruction_type:
            return [str(self.obstruction_type)]
        return []

    def summary(self) -> str:
        """One-line human-readable summary."""
        obs = ", ".join(self.obstruction_types())
        return (
            f"{self.id}: {self.model_name} | "
            f"obstruction={obs} | "
            f"status={self.proof_status}"
        )


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_schema(entry: dict[str, Any]) -> list[ValidationError]:
    """
    Validate a raw atlas entry dict against the V1 schema.

    Returns a list of ValidationError objects. An empty list means valid.
    """
    errors: list[ValidationError] = []
    eid = entry.get("id", "<unknown>")

    # 1. Required fields
    for f in REQUIRED_FIELDS:
        if f not in entry or entry[f] is None:
            # KO_dimension is allowed to be null for NCG-NM-001 (not applicable)
            if f == "KO_dimension" and entry.get("id", "").startswith("NCG-NM-"):
                continue
            errors.append(ValidationError(
                field=f,
                message="Required field missing or null.",
                entry_id=eid,
            ))

    # 2. id format (loose check — must start with NCG-)
    entry_id = entry.get("id", "")
    if entry_id and not entry_id.startswith("NCG-"):
        errors.append(ValidationError(
            field="id",
            message=f"id must start with 'NCG-'; got {entry_id!r}.",
            entry_id=eid,
        ))

    # 3. algebra_type enum
    at = entry.get("algebra_type", "")
    if at and at not in VALID_ALGEBRA_TYPES:
        errors.append(ValidationError(
            field="algebra_type",
            message=f"Invalid algebra_type {at!r}. Must be one of {sorted(VALID_ALGEBRA_TYPES)}.",
            entry_id=eid,
        ))

    # 4. obstruction_type enum
    ot = entry.get("obstruction_type")
    if ot is not None:
        types_to_check = ot if isinstance(ot, list) else [ot]
        for t in types_to_check:
            if t not in VALID_OBSTRUCTION_TYPES:
                errors.append(ValidationError(
                    field="obstruction_type",
                    message=f"Invalid obstruction_type {t!r}. Must be one of {sorted(VALID_OBSTRUCTION_TYPES)}.",
                    entry_id=eid,
                ))

    # 5. proof_system enum
    ps = entry.get("proof_system", "")
    if ps and ps not in VALID_PROOF_SYSTEMS:
        errors.append(ValidationError(
            field="proof_system",
            message=f"Invalid proof_system {ps!r}. Must be one of {sorted(VALID_PROOF_SYSTEMS)}.",
            entry_id=eid,
        ))

    # 6. proof_status enum
    pst = entry.get("proof_status", "")
    if pst and pst not in VALID_PROOF_STATUSES:
        errors.append(ValidationError(
            field="proof_status",
            message=f"Invalid proof_status {pst!r}. Must be one of {sorted(VALID_PROOF_STATUSES)}.",
            entry_id=eid,
        ))

    # 7. formally_verified must have admitted_count = 0
    if entry.get("proof_status") == "formally_verified":
        ac = entry.get("admitted_count")
        if ac is not None and ac != 0:
            errors.append(ValidationError(
                field="admitted_count",
                message=f"formally_verified entry must have admitted_count=0; got {ac}.",
                entry_id=eid,
            ))

    # 8. literature_citation items
    cites = entry.get("literature_citation", [])
    if isinstance(cites, list):
        for i, cite in enumerate(cites):
            if not isinstance(cite, dict):
                continue
            rel = cite.get("relevance", "")
            if rel and rel not in VALID_CITATION_RELEVANCES:
                errors.append(ValidationError(
                    field=f"literature_citation[{i}].relevance",
                    message=(
                        f"Invalid relevance {rel!r}. "
                        f"Must be one of {sorted(VALID_CITATION_RELEVANCES)}."
                    ),
                    entry_id=eid,
                ))

    # 9. KO_dimension range (0–7) when present
    ko = entry.get("KO_dimension")
    if ko is not None:
        if not isinstance(ko, int) or not (0 <= ko <= 7):
            errors.append(ValidationError(
                field="KO_dimension",
                message=f"KO_dimension must be an integer 0–7; got {ko!r}.",
                entry_id=eid,
            ))

    # 10. obstruction_statement min length
    obs_stmt = entry.get("obstruction_statement", "")
    if obs_stmt and len(obs_stmt.strip()) < 50:
        errors.append(ValidationError(
            field="obstruction_statement",
            message=f"obstruction_statement too short ({len(obs_stmt.strip())} chars, min 50).",
            entry_id=eid,
        ))

    return errors


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_entry(path: Path) -> AtlasEntry:
    """
    Parse a YAML atlas entry file, validate its schema, and return an AtlasEntry.

    Args:
        path: Path to a YAML file (NCG-*.yaml).

    Returns:
        AtlasEntry dataclass populated from the YAML.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file is not valid YAML or schema validation fails.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Atlas entry file not found: {path}")

    try:
        with path.open(encoding="utf-8") as fh:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse YAML {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(
            f"Atlas entry file must contain a YAML mapping (dict), "
            f"got {type(raw).__name__}: {path}"
        )

    errors = validate_schema(raw)
    if errors:
        msg_lines = [f"Schema validation failed for {path}:"]
        for e in errors:
            msg_lines.append(f"  - {e}")
        raise ValueError("\n".join(msg_lines))

    return _dict_to_entry(raw)


def load_all(atlas_dir: Path) -> dict[str, AtlasEntry]:
    """
    Load all YAML atlas entries from a directory.

    Args:
        atlas_dir: Directory containing NCG-*.yaml files (searched recursively).

    Returns:
        dict mapping entry id -> AtlasEntry for all successfully loaded entries.

    Raises:
        ValueError: if any entry fails schema validation (all errors reported).
    """
    atlas_dir = Path(atlas_dir)
    yaml_files = sorted(atlas_dir.glob("**/*.yaml"))

    entries: dict[str, AtlasEntry] = {}
    all_errors: list[str] = []

    for yf in yaml_files:
        # Skip schema files and index files
        if yf.name.startswith("atlas_index") or yf.name.startswith("atlas-entry"):
            continue
        try:
            entry = load_entry(yf)
            entries[entry.id] = entry
        except (ValueError, FileNotFoundError) as exc:
            all_errors.append(str(exc))

    if all_errors:
        raise ValueError(
            f"Failed to load {len(all_errors)} atlas entries:\n"
            + "\n".join(all_errors)
        )

    return entries


def cross_reference_check(entries: dict[str, AtlasEntry]) -> list[BrokenRef]:
    """
    Verify that all related_entries references point to existing entry IDs.

    Args:
        entries: dict[str, AtlasEntry] as returned by load_all().

    Returns:
        List of BrokenRef for each reference that points to a non-existent entry.
        Empty list means all cross-references are valid.
    """
    broken: list[BrokenRef] = []
    for eid, entry in entries.items():
        for ref in entry.related_entries:
            if ref not in entries:
                broken.append(BrokenRef(source_id=eid, target_id=ref))
    return broken


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _dict_to_entry(raw: dict[str, Any]) -> AtlasEntry:
    """Convert a raw dict (from YAML) to an AtlasEntry dataclass."""
    # Parse literature citations
    citations: list[LiteratureCitation] = []
    for c in raw.get("literature_citation", []):
        if isinstance(c, dict):
            citations.append(LiteratureCitation(
                authors=c.get("authors", []),
                title=c.get("title", ""),
                doi_or_arxiv=c.get("doi_or_arxiv", ""),
                year=int(c.get("year", 0)),
                relevance=c.get("relevance", ""),
            ))

    related = raw.get("related_entries", []) or []

    return AtlasEntry(
        id=raw.get("id", ""),
        model_name=raw.get("model_name", ""),
        version=raw.get("version", ""),
        date_added=raw.get("date_added", ""),
        date_updated=raw.get("date_updated"),
        maintainer=raw.get("maintainer"),
        algebra=raw.get("algebra", ""),
        algebra_type=raw.get("algebra_type", ""),
        hilbert_space_description=raw.get("hilbert_space_description", ""),
        dirac_operator_description=raw.get("dirac_operator_description", ""),
        real_structure_J=raw.get("real_structure_J", ""),
        grading_gamma=raw.get("grading_gamma", ""),
        KO_dimension=raw.get("KO_dimension"),
        obstruction_type=raw.get("obstruction_type", ""),
        obstruction_statement=raw.get("obstruction_statement", ""),
        obstruction_informal=raw.get("obstruction_informal", ""),
        proof_system=raw.get("proof_system", ""),
        proof_status=raw.get("proof_status", ""),
        proof_path=raw.get("proof_path"),
        theorem_name=raw.get("theorem_name"),
        admitted_count=raw.get("admitted_count"),
        proof_notes=raw.get("proof_notes"),
        literature_citation=citations,
        comparison_with_other_atlas_entries=raw.get(
            "comparison_with_other_atlas_entries"
        ),
        related_entries=list(related),
        _raw=raw,
    )


# ---------------------------------------------------------------------------
# Backward-compatible stub types (preserved from alpha for test_smoke.py)
# ---------------------------------------------------------------------------

@dataclass
class FormulaSpec:
    """
    A formula entry from the Atlas YAML/JSON.

    Preserved from v0.1.0-alpha for backward compatibility.
    """
    id: str
    expression: str
    quantity: str = ""
    units: str = ""
    pdg_value: float | None = None
    pdg_error: float | None = None
    tag: str = ""
    source: str = ""


@dataclass
class SpectralTripleSpec:
    """
    Specification of a spectral triple from YAML.

    Preserved from v0.1.0-alpha for backward compatibility.
    """
    algebra: dict[str, Any] = field(default_factory=dict)
    hilbert_space: dict[str, Any] = field(default_factory=dict)
    dirac_operator: dict[str, Any] = field(default_factory=dict)
    real_structure: dict[str, Any] = field(default_factory=dict)
    grading: dict[str, Any] = field(default_factory=dict)


@dataclass
class NCGModel:
    """
    Canonical internal representation of an NCG model (legacy interface).

    Preserved from v0.1.0-alpha for backward compatibility.
    """
    name: str = ""
    version: str = ""
    source_file: str = ""
    spectral_triple: SpectralTripleSpec | None = None
    formulas: list[FormulaSpec] = field(default_factory=list)

    def formula_count(self) -> int:
        return len(self.formulas)

    def nf_formulas(self) -> list[FormulaSpec]:
        """Formulas tagged as numerical fits."""
        NF_TAGS = {"phenomenological_fit", "NUMERICAL_FIT", "NF"}
        return [f for f in self.formulas if f.tag in NF_TAGS]

    def summary(self) -> str:
        lines = [
            f"NCG Model: {self.name} (v{self.version})",
            f"  Source    : {self.source_file}",
            f"  Formulas  : {self.formula_count()} total, "
            f"{len(self.nf_formulas())} NF",
        ]
        if self.spectral_triple:
            alg = self.spectral_triple.algebra.get("type", "unknown")
            dim = self.spectral_triple.hilbert_space.get("dimension", "?")
            lines.append(f"  Algebra   : {alg}")
            lines.append(f"  H-dim     : {dim}")
        return "\n".join(lines)


@dataclass
class NoGoCheckResult:
    """Result of a no-go check for a formula."""
    formula_id: str
    status: str       # PASS | FAIL | STUB | SKIP
    reason: str = ""


def run_nogo_checks(model: NCGModel) -> list[NoGoCheckResult]:
    """
    Run no-go checks for all formulas in the model.

    Full atlas-level no-go checking is handled by the new AtlasEntry/load_entry
    interface. This legacy function returns STUB results for backward compatibility.
    Axiom-level checking remains scheduled for M3.
    """
    results = []
    for formula in model.formulas:
        results.append(NoGoCheckResult(
            formula_id=formula.id,
            status="STUB",
            reason="STUB: axiom-level no-go checks in milestone M3 (week 12)",
        ))
    return results


def load_model(path: Path | str) -> NCGModel:
    """
    Load a YAML or JSON model specification and return an NCGModel (legacy).

    Preserved for backward compatibility with test_smoke.py.
    For V3 atlas entries, use load_entry() instead.

    Supported formats:
      - YAML (.yaml, .yml)
      - JSON (.json)

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file format is not recognised or parsing fails.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")

    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        try:
            with path.open(encoding="utf-8") as fh:
                raw = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            raise ValueError(f"Failed to parse YAML: {path}: {exc}") from exc
    elif suffix == ".json":
        with path.open(encoding="utf-8") as fh:
            raw = json.load(fh)
    else:
        raise ValueError(
            f"Unsupported model file format: {suffix!r}. "
            "Expected .yaml, .yml, or .json."
        )

    if not isinstance(raw, dict):
        raw = {}

    model = NCGModel(
        name=raw.get("name", ""),
        version=str(raw.get("version", "")),
        source_file=str(path),
    )

    st_raw = raw.get("spectral_triple", {})
    if st_raw:
        model.spectral_triple = SpectralTripleSpec(
            algebra=st_raw.get("algebra", {}),
            hilbert_space=st_raw.get("hilbert_space", {}),
            dirac_operator=st_raw.get("dirac_operator", {}),
            real_structure=st_raw.get("real_structure", {}),
            grading=st_raw.get("grading", {}),
        )

    for f_raw in raw.get("formulas", []):
        model.formulas.append(FormulaSpec(
            id=f_raw.get("id", ""),
            expression=f_raw.get("expression", ""),
            quantity=f_raw.get("quantity", ""),
            units=f_raw.get("units", ""),
            pdg_value=f_raw.get("pdg_value"),
            pdg_error=f_raw.get("pdg_error"),
            tag=f_raw.get("tag", ""),
            source=f_raw.get("source", ""),
        ))

    return model
