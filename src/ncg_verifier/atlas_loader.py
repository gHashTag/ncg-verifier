"""
atlas_loader.py — Load V3 Atlas entries from YAML/JSON and run no-go checks.

ALPHA STATUS: This module is a STUB.
Full implementation is planned for milestone M2 (week 6) of the V1 roadmap.

In the full implementation, this module will:
  1. Parse the YAML/JSON model specification schema (see V1_architecture.md §3).
  2. Emit a canonical NCGModel dataclass with fields for each spectral triple
     component and a list of Formula objects.
  3. Validate required file references (coq_dir, lean_dir) exist on disk.
  4. Run schema validation via pydantic v2.
  5. Execute no-go checks: for each formula tagged `[phenomenological_fit]`,
     check that the corresponding no-go theorem (if any) is listed as Refuted.

The YAML schema is documented in V1_architecture.md §3 and the example
`models/trinity_s3ai.yaml` (to be added in M2).

References:
  - Architecture: V1_architecture.md §3 (Algebra Parser)
  - Roadmap: M2 (weeks 3–6)
  - Upstream: trinity-s3ai/scripts/sync_formulas.py (formula sync utility)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# STUB: pydantic validation will be added in M2
# from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Data structures (interface-level, stubs for M2)
# ---------------------------------------------------------------------------

@dataclass
class FormulaSpec:
    """
    A formula entry from the Atlas YAML/JSON.

    # STUB: full pydantic validation in M2 (week 6)
    """
    id: str
    expression: str
    quantity: str = ""
    units: str = ""
    pdg_value: Optional[float] = None
    pdg_error: Optional[float] = None
    tag: str = ""              # e.g. "phenomenological_fit"
    source: str = ""           # path to Coq source file


@dataclass
class SpectralTripleSpec:
    """
    Specification of a spectral triple from YAML.

    # STUB: full pydantic validation in M2 (week 6)
    """
    algebra: dict[str, Any] = field(default_factory=dict)
    hilbert_space: dict[str, Any] = field(default_factory=dict)
    dirac_operator: dict[str, Any] = field(default_factory=dict)
    real_structure: dict[str, Any] = field(default_factory=dict)
    grading: dict[str, Any] = field(default_factory=dict)


@dataclass
class NCGModel:
    """
    Canonical internal representation of an NCG model.

    Populated by load_model() from a YAML or JSON file.

    # STUB: full implementation in M2 (week 6)
    """
    name: str = ""
    version: str = ""
    source_file: str = ""
    spectral_triple: Optional[SpectralTripleSpec] = None
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


# ---------------------------------------------------------------------------
# No-go check stubs
# ---------------------------------------------------------------------------

@dataclass
class NoGoCheckResult:
    """Result of a no-go check for a formula. # STUB: M2"""
    formula_id: str
    status: str           # PASS | FAIL | STUB | SKIP
    reason: str = ""


def run_nogo_checks(model: NCGModel) -> list[NoGoCheckResult]:
    """
    Run no-go checks for all formulas in the model.

    STUB: full implementation in M2 (week 6).

    In the full implementation:
      - For each formula tagged Refuted or with a `*_refuted` theorem name,
        verify the Coq file contains the expected `Qed` theorem.
      - Report PASS if confirmed, FAIL if the Coq file is missing or
        the theorem compiles with `Admitted`.
      - For NF-class formulas, check that the `pdg_value`/`pdg_error` fields
        are populated (schema validation).

    # STUB: full implementation in milestone M2 (week 6)
    """
    # STUB: full implementation in milestone M2 (week 6)
    results = []
    for formula in model.formulas:
        results.append(NoGoCheckResult(
            formula_id=formula.id,
            status="STUB",
            reason="STUB: full no-go checks in milestone M2 (week 6)",
        ))
    return results


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_model(path: Path | str) -> NCGModel:
    """
    Load a YAML or JSON model specification and return an NCGModel.

    STUB: pydantic schema validation will be added in M2 (week 6).

    Supported formats:
      - YAML (.yaml, .yml) — requires pyyaml (optional dep in alpha)
      - JSON (.json)

    Raises:
        NotImplementedError: for YAML files in alpha (pyyaml import not
            guaranteed; full validation deferred to M2).
        FileNotFoundError: if the file does not exist.
        ValueError: if the file format is not recognised.

    # STUB: full implementation in milestone M2 (week 6)
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")

    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        # STUB: full pydantic-validated YAML loader in M2
        try:
            import yaml  # type: ignore[import]
            with path.open(encoding="utf-8") as fh:
                raw = yaml.safe_load(fh)
        except ImportError:
            # pyyaml not installed — return minimal stub model
            return NCGModel(
                name="(pyyaml not installed — stub)",
                version="unknown",
                source_file=str(path),
            )
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Failed to parse YAML: {path}: {exc}") from exc

    elif suffix == ".json":
        with path.open(encoding="utf-8") as fh:
            raw = json.load(fh)
    else:
        raise ValueError(
            f"Unsupported model file format: {suffix!r}. "
            "Expected .yaml, .yml, or .json."
        )

    # STUB: minimal parsing — full pydantic model in M2
    # STUB: full implementation in milestone M2 (week 6)
    model = NCGModel(
        name=raw.get("name", ""),
        version=str(raw.get("version", "")),
        source_file=str(path),
    )

    # Parse spectral triple if present
    st_raw = raw.get("spectral_triple", {})
    if st_raw:
        model.spectral_triple = SpectralTripleSpec(
            algebra=st_raw.get("algebra", {}),
            hilbert_space=st_raw.get("hilbert_space", {}),
            dirac_operator=st_raw.get("dirac_operator", {}),
            real_structure=st_raw.get("real_structure", {}),
            grading=st_raw.get("grading", {}),
        )

    # Parse formulas if present
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
