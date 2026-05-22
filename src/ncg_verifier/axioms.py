"""
axioms.py — Checkers for Connes' axioms for a real spectral triple.

ALPHA STATUS: All axiom checkers in this module are STUBS.
Full implementation is planned for milestone M3 (week 12) of the V1 roadmap.

Each checker raises NotImplementedError with a description of what the full
implementation will do, grounded in the infrastructure already present in
trinity-s3ai (https://github.com/gHashTag/trinity-s3ai).

Axiom reference: Connes (1996), hep-th/9603053, and
Gracia-Bondía, Várilly, Figueroa (2001), Elements of NCG.

The seven axioms for a real spectral triple (A, H, D; J, γ):
  1. Dimension (KO-dim) — compact resolvent and sign triple consistency
  2. Regularity — A and [D,A] ⊂ ∩ Dom(δ^k) for all k (δ = [|D|, ·])
  3. Finiteness — H_∞ := ∩ Dom(D^k) is a finitely generated projective A-module
  4. Reality (J) — [a, JbJ⁻¹] = 0 for all a, b ∈ A
  5. First-order condition — [[D, a], JbJ⁻¹] = 0 for all a, b ∈ A
  6. Orientation (γ-cycle) — Hochschild cycle c → π(c) = γ
  7. Poincaré duality — K-theory pairing non-degenerate

NOTE ON AXIOM 5:
  The first-order condition is the primary structural obstruction for any
  discrete / finite NCG model. It is proved OPEN (formally: `Axiom` with
  tag [MATH_TODO]) for the H4/600-cell model in:
    proofs/trinity/NoGoTheorems.v (NGT4)
    derivations/spectral_triple_axioms/axiom_checklist.md (Section 6.2)
  This checker will always report OPEN for discrete models until a positive
  proof is supplied — this is a feature, not a limitation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from ncg_verifier.spectral_triple import SpectralTriple


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


class AxiomStatus(str, Enum):
    """Status codes for axiom compliance checks."""
    VERIFIED = "VERIFIED"      # Fully proved (Qed, no PHYSICAL_AXIOM deps)
    PARTIAL = "PARTIAL"        # Some conditions proved, others open
    OPEN = "OPEN"              # Mathematically open (MATH_TODO)
    STUB = "STUB"              # Checker not yet implemented (alpha)
    PHYSICAL_AXIOM = "PHYSICAL_AXIOM"  # Assumed as physical input
    REFUTED = "REFUTED"        # Formally proved impossible


@dataclass
class AxiomResult:
    """Result of a single axiom check."""
    axiom_number: int
    axiom_name: str
    status: AxiomStatus
    evidence: str = ""
    coq_reference: Optional[str] = None
    notes: str = ""

    def __str__(self) -> str:
        ref = f" [{self.coq_reference}]" if self.coq_reference else ""
        return f"Axiom {self.axiom_number} ({self.axiom_name}): {self.status.value}{ref}"


@dataclass
class AxiomReport:
    """Full axiom compliance report for a spectral triple."""
    triple: Any   # SpectralTriple (avoid circular import issues)
    results: list[AxiomResult] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"Axiom compliance report for: {getattr(self.triple, 'name', str(self.triple))}"]
        for r in self.results:
            lines.append(f"  {r}")
        return "\n".join(lines)

    def get(self, axiom_number: int) -> Optional[AxiomResult]:
        for r in self.results:
            if r.axiom_number == axiom_number:
                return r
        return None


# ---------------------------------------------------------------------------
# Axiom checkers (STUBS)
# ---------------------------------------------------------------------------

# STUB NOTE: Each function below documents what the full M3 implementation
# will do. The stubs return AxiomResult with status=STUB and do NOT raise
# for the smoke tests, but the full check methods raise NotImplementedError
# to make the stub nature explicit.


def check_boundedness(triple: SpectralTriple) -> AxiomResult:
    """
    Axiom 1 (Dimension / boundedness of [D, a]).

    Full implementation (M3, week 12):
      For each generator a ∈ A, verify that [D, π(a)] extends to a bounded
      operator on H by checking that the commutator matrix (in the finite-dim
      case) has finite operator norm. Also verify the sign triple (ε, ε', ε'')
      against the KO-dimension table.

    In trinity-s3ai: PARTIAL for H4/600-cell — signs Qed in
      proofs/trinity/KODimension.v (9 theorems);
      KO-dim=6 vs KO-dim=0 tension tagged [PHYSICAL_AXIOM].

    # STUB: full implementation in milestone M3 (week 12)
    """
    # STUB: full implementation in milestone M3 (week 12)
    return AxiomResult(
        axiom_number=1,
        axiom_name="Dimension / boundedness of [D,a]",
        status=AxiomStatus.STUB,
        evidence="STUB — M3 will invoke coqc on axiom_obligations_<model>.v",
        coq_reference="proofs/trinity/KODimension.v",
        notes="STUB: full implementation in milestone M3 (week 12)",
    )


def check_regularity(triple: SpectralTriple) -> AxiomResult:
    """
    Axiom 2 (Regularity).

    Full implementation (M3, week 12):
      For a FINITE spectral triple (dim H < ∞), all operators are bounded
      and Dom(δ^k) = H for all k — this is trivially VERIFIED by the lemma
      `axiom_regularity_finite_dim` in SpectralTripleAxioms.v.
      The checker detects finite dimension from the YAML `hilbert_space.dimension`
      field and returns VERIFIED immediately, matching the Qed proof in
      derivations/spectral_triple_axioms/SpectralTripleAxioms.v.

    # STUB: full implementation in milestone M3 (week 12)
    """
    # STUB: full implementation in milestone M3 (week 12)
    return AxiomResult(
        axiom_number=2,
        axiom_name="Regularity",
        status=AxiomStatus.STUB,
        evidence="STUB — for any finite-dim triple this will return VERIFIED",
        coq_reference="derivations/spectral_triple_axioms/SpectralTripleAxioms.v",
        notes="STUB: full implementation in milestone M3 (week 12). "
              "Will auto-VERIFIED for finite-dimensional triples.",
    )


def check_finiteness(triple: SpectralTriple) -> AxiomResult:
    """
    Axiom 3 (Finiteness).

    Full implementation (M3, week 12):
      For finite-dim H, the smooth domain H_∞ = H is trivially a finitely
      generated projective A-module. Returns VERIFIED automatically for any
      model with `hilbert_space.dimension > 0`.
      Mirrors: `axiom_finiteness_trivial` in SpectralTripleAxioms.v (Qed).

    # STUB: full implementation in milestone M3 (week 12)
    """
    # STUB: full implementation in milestone M3 (week 12)
    return AxiomResult(
        axiom_number=3,
        axiom_name="Finiteness",
        status=AxiomStatus.STUB,
        evidence="STUB — for finite-dim triple will return VERIFIED automatically",
        coq_reference="derivations/spectral_triple_axioms/SpectralTripleAxioms.v",
        notes="STUB: full implementation in milestone M3 (week 12). "
              "Will auto-VERIFIED for finite-dimensional triples.",
    )


def check_reality(triple: SpectralTriple) -> AxiomResult:
    """
    Axiom 4 (Reality / J-structure).

    Full implementation (M3, week 12):
      Check J² = ε·1, JD = ε'DJ, Jγ = ε''γJ (sign conditions — Qed in
      KODimension.v and QuaternionicLinearity.v) and [a, JbJ⁻¹] = 0 for
      all a, b ∈ A (commutant condition — PHYSICAL_AXIOM in trinity-s3ai).
      The checker reads `real_structure.signs` from the YAML and generates
      the sign consistency lemmas from the `connes_signs` pattern.

    In trinity-s3ai: PARTIAL — signs Qed; [a,JbJ⁻¹]=0: PHYSICAL_AXIOM.

    # STUB: full implementation in milestone M3 (week 12)
    """
    # STUB: full implementation in milestone M3 (week 12)
    return AxiomResult(
        axiom_number=4,
        axiom_name="Reality (J-structure)",
        status=AxiomStatus.STUB,
        evidence="STUB — M3 will check J² = ε, JD = ε'DJ, Jγ = ε''γJ sign conditions",
        coq_reference="proofs/trinity/QuaternionicLinearity.v",
        notes="STUB: full implementation in milestone M3 (week 12). "
              "Sign conditions will be VERIFIED; [a,JbJ⁻¹]=0 will be PHYSICAL_AXIOM.",
    )


def check_first_order(triple: SpectralTriple) -> AxiomResult:
    """
    Axiom 5 (First-order condition).

    [[D, a], JbJ⁻¹] = 0 for all a ∈ A, b° = JbJ⁻¹ ∈ J A J⁻¹.

    This is the PRIMARY STRUCTURAL OBSTRUCTION for discrete NCG models.
    For the H4/600-cell model it is PROVED IMPOSSIBLE by NGT4 in
    proofs/trinity/NoGoTheorems.v. This checker will always return OPEN
    for discrete models until a positive Coq proof is supplied.

    From the axiom_checklist.md (Section 6.2):
      "The first-order condition requires that [D, π(a)] lies in the
      commutant of J π(A) J⁻¹ as operators on H. For the 600-cell graph
      Dirac operator, direct computation shows this fails: NGT4 gives a
      Qed proof that there exist a, b ∈ A such that the nested commutator
      is non-zero. This is an inherent obstruction for any discrete, finite
      spectral triple with a non-trivial Dirac operator."

    Full implementation (M3, week 12):
      Always emit `Axiom axiom_first_order : ... (* [MATH_TODO] *)` in the
      generated axiom_obligations_<model>.v file and mark OPEN. If the user
      provides a Coq file with a positive proof, re-classify as VERIFIED or
      PHYSICAL_AXIOM (for the Pati-Salam relaxed first-order condition).

    # STUB: logic already clear (always OPEN); M3 adds Coq evidence plumbing
    """
    # This axiom always returns OPEN — this is intentional and correct.
    # See trinity-s3ai/proofs/trinity/NoGoTheorems.v (NGT4).
    return AxiomResult(
        axiom_number=5,
        axiom_name="First-order condition",
        status=AxiomStatus.OPEN,
        evidence=(
            "[[D,a], JbJ⁻¹] = 0 is OPEN for discrete spectral triples. "
            "For H4/600-cell: PROVED IMPOSSIBLE by NGT4 "
            "(proofs/trinity/NoGoTheorems.v). "
            "No positive Coq proof supplied."
        ),
        coq_reference="proofs/trinity/NoGoTheorems.v (NGT4)",
        notes=(
            "[MATH_TODO] The first-order condition is the primary obstruction "
            "for discrete NCG models. "
            "STUB: M3 (week 12) adds Coq evidence generation; "
            "logic (always OPEN) is already correct."
        ),
    )


def check_orientation(triple: SpectralTriple) -> AxiomResult:
    """
    Axiom 6 (Orientation / γ-cycle).

    Full implementation (M3, week 12):
      Verify γ² = 1, γD = -Dγ (anticommutation), γa = aγ (commutation with A),
      and the Hochschild cycle condition c → π(c) = γ. In trinity-s3ai:
      γ is defined and γD = -Dγ is proved (Qed); Hochschild cycle: MATH_TODO.
      The checker detects the γ operator from `spectral_triple.grading` in YAML.

    In trinity-s3ai: PARTIAL — γ defined; Hochschild cycle: MATH_TODO.

    # STUB: full implementation in milestone M3 (week 12)
    """
    # STUB: full implementation in milestone M3 (week 12)
    return AxiomResult(
        axiom_number=6,
        axiom_name="Orientation (γ-cycle)",
        status=AxiomStatus.STUB,
        evidence="STUB — M3 will check γ² = 1, γD = -Dγ, and Hochschild cycle",
        coq_reference="derivations/spectral_triple_axioms/SpectralTripleAxioms.v",
        notes="STUB: full implementation in milestone M3 (week 12). "
              "γ²=1 and γD=-Dγ will be VERIFIED for finite models; "
              "Hochschild cycle will be OPEN ([MATH_TODO]).",
    )


def check_poincare_duality(triple: SpectralTriple) -> AxiomResult:
    """
    Axiom 7 (Poincaré duality).

    Full implementation (M3, week 12):
      Verify that the K-theory pairing ⟨·, ·⟩ defined by D is non-degenerate.
      For finite spectral triples this simplifies to a matrix rank condition.
      In trinity-s3ai: simplified proof in finite dim (Qed with caveats);
      formal proof: MATH_TODO.

    In trinity-s3ai: PARTIAL — simplified in finite dim; formal: TODO.

    # STUB: full implementation in milestone M3 (week 12)
    """
    # STUB: full implementation in milestone M3 (week 12)
    return AxiomResult(
        axiom_number=7,
        axiom_name="Poincaré duality",
        status=AxiomStatus.STUB,
        evidence="STUB — M3 will check K-theory pairing non-degeneracy",
        coq_reference="derivations/spectral_triple_axioms/SpectralTripleAxioms.v",
        notes="STUB: full implementation in milestone M3 (week 12). "
              "Simplified finite-dim version will be VERIFIED; "
              "formal K-theory proof will be OPEN.",
    )


# ---------------------------------------------------------------------------
# Convenience: run all axiom checks
# ---------------------------------------------------------------------------

ALL_CHECKERS = [
    check_boundedness,
    check_regularity,
    check_finiteness,
    check_reality,
    check_first_order,
    check_orientation,
    check_poincare_duality,
]


def check_all_axioms(triple: SpectralTriple) -> AxiomReport:
    """
    Run all seven Connes axiom checkers on a spectral triple and return
    a full AxiomReport.

    In v0.1.0-alpha: axioms 1–4 and 6–7 return STUB status;
    axiom 5 (first-order condition) returns OPEN — which is the correct
    answer for any discrete spectral triple without a positive Coq proof.

    Full implementation: M3 (week 12).
    """
    report = AxiomReport(triple=triple)
    for checker in ALL_CHECKERS:
        result = checker(triple)
        report.results.append(result)
    return report
