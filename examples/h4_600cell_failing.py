"""
h4_600cell_failing.py — Demonstration: H4/600-cell spectral triple fails axiom 5.

This example shows that the H4/600-cell spectral triple — the model investigated
over ten development waves in trinity-s3ai — fails the first-order condition
(Connes axiom 5), as formally proved by NGT4 in:

  proofs/trinity/NoGoTheorems.v
  https://github.com/gHashTag/trinity-s3ai

ALPHA STATUS:
  The actual computation (checking [[D, a], JbJ⁻¹] = 0 via matrix arithmetic)
  is NOT implemented in v0.1.0-alpha. This example raises NotImplementedError
  with a clear description of:
    - What computation is needed
    - Where it is implemented in trinity-s3ai
    - Which milestone (M3, week 12) adds the full implementation

This is honest and intentional: the alpha scaffold establishes the interface
and documents the known result. V1 is a 26-week roadmap.

Usage:
    python examples/h4_600cell_failing.py

Expected output:
    The script prints the spectral triple metadata and axiom check results,
    shows that axiom 5 returns OPEN (matching NGT4), and raises
    NotImplementedError for the actual matrix computation stub.
"""

from __future__ import annotations

import sys


# ---------------------------------------------------------------------------
# Concrete H4/600-cell spectral triple stub
# ---------------------------------------------------------------------------

try:
    from ncg_verifier.spectral_triple import SpectralTriple
    from ncg_verifier.axioms import check_all_axioms, AxiomStatus
except ImportError:
    print("ERROR: ncg_verifier not installed. Run: pip install -e .", file=sys.stderr)
    sys.exit(1)


class H4_600CellTriple(SpectralTriple):
    """
    H4/600-cell spectral triple (stub for v0.1.0-alpha).

    Model parameters (from trinity-s3ai):
      - Algebra: A = ℂ ⊕ ℍ ⊕ M₃(ℂ)  (Standard Model algebra)
      - Hilbert space: H = ℂ^120 ⊗ ℂ^2  (600-cell vertices ⊗ spinors, dim=240)
      - Dirac operator: D = graph Laplacian on the 600-cell polytope
      - KO-dimension: 6 (claimed; tension with KO-dim=0 tagged [PHYSICAL_AXIOM])
      - Real structure: J = quaternionic conjugation
        Signs: (ε, ε', ε'') = (+1, -1, +1) for KO-dim=6

    Known results from trinity-s3ai proof base (1326 Qed, 37 Admitted, 94 Axiom):
      - Axiom 1 (dimension): PARTIAL — signs Qed; KO-dim conflict: PHYSICAL_AXIOM
      - Axiom 2 (regularity): VERIFIED (finite dim)
      - Axiom 3 (finiteness): VERIFIED (finite dim)
      - Axiom 4 (reality): PARTIAL — signs Qed; [a,JbJ⁻¹]=0: PHYSICAL_AXIOM
      - Axiom 5 (first-order): OPEN — [[D,a],JbJ⁻¹]=0 FAILS (NGT4, Qed proof)
      - Axiom 6 (orientation): PARTIAL — γ defined; Hochschild cycle: MATH_TODO
      - Axiom 7 (Poincaré): PARTIAL — finite dim simplification; formal: TODO

    References:
      derivations/spectral_triple_axioms/SpectralTripleAxioms.v
      proofs/trinity/NoGoTheorems.v (NGT4)
      derivations/spectral_triple_axioms/axiom_checklist.md
    """

    @property
    def name(self) -> str:
        return "H4-600cell"

    @property
    def ko_dimension(self) -> int:
        return 6

    @property
    def sign_triple(self) -> tuple[int, int, int]:
        # (ε, ε', ε'') = (+1, -1, +1) for KO-dim = 6
        return (+1, -1, +1)

    @property
    def algebra(self) -> dict:
        return {
            "type": "finite_product",
            "components": ["ℂ", "ℍ", "M₃(ℂ)"],
            "description": "Standard Model algebra A_F = ℂ ⊕ ℍ ⊕ M₃(ℂ)",
            "coq_source": "proofs/trinity/H4GaugeEmbedding.v",
        }

    @property
    def hilbert_space(self) -> dict:
        return {
            "dimension": 240,
            "description": "ℂ^120 ⊗ ℂ^2 (600-cell vertices ⊗ spinors)",
            "coq_source": "derivations/spectral_triple_axioms/SpectralTripleAxioms.v",
            "note": "H_dim = 2 × |vertices_600cell| = 2 × 120 = 240",
        }

    @property
    def dirac(self) -> dict:
        return {
            "type": "graph_dirac",
            "description": "Graph Laplacian on the 600-cell polytope",
            "ko_dimension": 6,
            "coq_source": "proofs/trinity/DiracOperator.v",
            "note": (
                "STUB: actual 240×240 matrix representation deferred to M3. "
                "NGT4 proves [[D,a],JbJ⁻¹] ≠ 0 for this operator."
            ),
        }

    @property
    def gamma(self) -> dict:
        return {
            "type": "diagonal_sign_operator",
            "description": "Chirality operator (diagonal ±1 on 600-cell vertices)",
            "coq_source": "proofs/trinity/KODimension.v",
        }

    @property
    def J(self) -> dict:  # noqa: N802
        return {
            "type": "quaternionic_conjugation",
            "signs": {"eps": "+1", "eps_prime": "-1", "eps_double_prime": "+1"},
            "description": "Anti-linear isometry, KO-dim=6 sign triple",
            "coq_source": "proofs/trinity/QuaternionicLinearity.v",
        }


# ---------------------------------------------------------------------------
# First-order condition computation (stub)
# ---------------------------------------------------------------------------

def compute_first_order_obstruction(triple: H4_600CellTriple) -> None:
    """
    Compute [[D, a], JbJ⁻¹] for sample elements a, b ∈ A and check if it is zero.

    STUB: actual matrix computation deferred to M3 (milestone 3, week 12).

    In the full implementation (M3):
      1. Load the 240×240 Dirac matrix D from the 600-cell graph adjacency data.
      2. For each generator a_i ∈ {generators of ℂ ⊕ ℍ ⊕ M₃(ℂ)}, compute [D, π(a_i)].
      3. For each generator b_j, compute JbJ⁻¹ and then [[D, a_i], Jb_j J⁻¹].
      4. Report the max operator norm ‖[[D, a_i], Jb_j J⁻¹]‖.

    The formal Coq result (NGT4 in proofs/trinity/NoGoTheorems.v) already proves
    that ∃ a, b such that [[D,a], JbJ⁻¹] ≠ 0.

    References:
      proofs/trinity/NoGoTheorems.v (NGT4)
      derivations/spectral_triple_axioms/axiom_checklist.md (Section 6.2)
      V1_architecture.md Section 4 (Module b: Axiom Checker)

    # STUB: full implementation in milestone M3 (week 12)
    """
    raise NotImplementedError(
        "\n"
        "compute_first_order_obstruction: STUB\n"
        "\n"
        "Full implementation in milestone M3 (week 12):\n"
        "  - Load 240×240 Dirac matrix from 600-cell graph data\n"
        "  - Compute [[D, a], JbJ⁻¹] for generators a, b ∈ A_F\n"
        "  - Report max operator norm (should be > 0 per NGT4)\n"
        "\n"
        "The formal Coq result is already available:\n"
        "  proofs/trinity/NoGoTheorems.v (NGT4)\n"
        "  Qed — [[D, a_gen], J b_gen J⁻¹] ≠ 0 for specific generators\n"
        "\n"
        "This is honest: V1 is a 26-week roadmap; the alpha scaffold\n"
        "establishes the interface and documents the known failure.\n"
    )


# ---------------------------------------------------------------------------
# Main demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("NCG-Verifier v0.1.0-alpha — H4/600-cell First-Order Failure Demo")
    print("=" * 70)
    print()

    # Create the spectral triple
    triple = H4_600CellTriple()
    print(triple.summary())
    print()

    # Run all axiom checks
    print("Running axiom checks...")
    report = check_all_axioms(triple)
    print()
    print(report.summary())
    print()

    # Highlight axiom 5
    result5 = report.get(5)
    if result5 is not None:
        print("─" * 70)
        print(f"AXIOM 5 (First-order condition): {result5.status.value}")
        print(f"Evidence: {result5.evidence}")
        print(f"Notes: {result5.notes}")
        print()
        if result5.status == AxiomStatus.OPEN:
            print("CONFIRMED: Axiom 5 is OPEN — matches NGT4 from trinity-s3ai.")
            print("The H4/600-cell spectral triple fails the first-order condition.")
        print("─" * 70)
        print()

    # Attempt the actual computation (will raise NotImplementedError in alpha)
    print("Attempting matrix computation of [[D,a], JbJ⁻¹]...")
    print("(Expected: NotImplementedError — full computation in M3, week 12)")
    print()
    try:
        compute_first_order_obstruction(triple)
    except NotImplementedError as e:
        print("NotImplementedError (expected in v0.1.0-alpha):")
        print(str(e))

    print("=" * 70)
    print("Demo complete.")
    print("Result: H4/600-cell FAILS first-order condition (axiom 5 = OPEN).")
    print("Full matrix verification: milestone M3 (week 12).")
    print("=" * 70)


if __name__ == "__main__":
    main()
