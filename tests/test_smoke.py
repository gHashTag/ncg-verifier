"""
tests/test_smoke.py — Smoke tests for ncg-verifier v0.1.0-alpha.

These tests verify that:
  1. The package imports correctly.
  2. The version string is as expected.
  3. The SpectralTriple ABC is importable and requires concrete implementations.
  4. The AxiomResult / AxiomReport types work as expected.
  5. Axiom 5 (first-order condition) always returns OPEN — matching the
     NGT4 result for H4/600-cell from trinity-s3ai.
  6. The AntiNumerologyGate can scan a synthetic .v file and FLAG untagged
     multi-atom formulas.
  7. The AntiNumerologyGate PASSES tagged formulas and whitelisted names.
  8. The atlas_loader NCGModel interface is accessible.

DESIGN PRINCIPLE:
  These tests do NOT require numpy, scipy, Coq, or Lean 4.
  They are pure interface checks and lightweight string-processing tests.
  The H4/600-cell "fails first-order" test uses a MINIMAL synthetic
  spectral triple (no real linear-algebra) to demonstrate that check_first_order
  always returns OPEN for any discrete model without a positive Coq proof.
"""

from __future__ import annotations

import tempfile
import textwrap
from pathlib import Path

# ============================================================================
# 1. Package import and version
# ============================================================================

class TestPackageImport:
    def test_import_ncg_verifier(self):
        """Package imports without errors."""
        import ncg_verifier  # noqa: F401
        assert ncg_verifier is not None

    def test_version_string(self):
        """__version__ is defined and non-empty."""
        import ncg_verifier
        assert hasattr(ncg_verifier, "__version__")
        assert isinstance(ncg_verifier.__version__, str)
        assert len(ncg_verifier.__version__) > 0

    def test_version_is_alpha(self):
        """Version is 0.1.0-alpha (alpha scaffold)."""
        import ncg_verifier
        assert ncg_verifier.__version__ == "0.1.0-alpha"

    def test_top_level_exports(self):
        """Key names are accessible from the top-level package."""
        from ncg_verifier import (
            AntiNumerologyGate,
            FormulaResult,
            GateResult,
            SpectralTriple,
        )
        assert SpectralTriple is not None
        assert AntiNumerologyGate is not None
        assert GateResult is not None
        assert FormulaResult is not None


# ============================================================================
# 2. SpectralTriple ABC
# ============================================================================

class TestSpectralTripleABC:
    def test_cannot_instantiate_abstract(self):
        """SpectralTriple is abstract — cannot instantiate directly."""
        import pytest

        from ncg_verifier.spectral_triple import SpectralTriple
        with pytest.raises(TypeError):
            SpectralTriple()  # type: ignore[abstract]

    def test_concrete_subclass_requires_all_properties(self):
        """A concrete subclass must implement all abstract properties."""
        import pytest

        from ncg_verifier.spectral_triple import SpectralTriple

        class IncompleteTriple(SpectralTriple):
            # Missing: hilbert_space, dirac, gamma, J
            @property
            def algebra(self):
                return "C ⊕ H ⊕ M3C"

        with pytest.raises(TypeError):
            IncompleteTriple()  # type: ignore[abstract]

    def test_minimal_concrete_subclass(self):
        """A minimal concrete subclass with all abstract properties works."""
        from ncg_verifier.spectral_triple import SpectralTriple

        class MinimalTriple(SpectralTriple):
            @property
            def algebra(self):
                return "ℂ"
            @property
            def hilbert_space(self):
                return 2   # dimension
            @property
            def dirac(self):
                return [[0, 1], [1, 0]]  # Pauli σ₁
            @property
            def gamma(self):
                return [[1, 0], [0, -1]]  # σ₃
            @property
            def J(self):
                return "complex_conjugation"

        t = MinimalTriple()
        assert t is not None
        assert t.algebra == "ℂ"
        assert t.hilbert_space == 2

    def test_name_default(self):
        """Default name is the class name."""
        from ncg_verifier.spectral_triple import SpectralTriple

        class MyTriple(SpectralTriple):
            @property
            def algebra(self): return "A"
            @property
            def hilbert_space(self): return 1
            @property
            def dirac(self): return [[0]]
            @property
            def gamma(self): return [[1]]
            @property
            def J(self): return "id"

        t = MyTriple()
        assert t.name == "MyTriple"

    def test_summary_method(self):
        """summary() returns a non-empty string."""
        from ncg_verifier.spectral_triple import SpectralTriple

        class MyTriple(SpectralTriple):
            @property
            def algebra(self): return "A"
            @property
            def hilbert_space(self): return 4
            @property
            def dirac(self): return "D"
            @property
            def gamma(self): return "γ"
            @property
            def J(self): return "J"

        t = MyTriple()
        s = t.summary()
        assert isinstance(s, str)
        assert "MyTriple" in s
        assert "Hilbert" in s


# ============================================================================
# 3. Axiom checkers — stub statuses and first-order OPEN behavior
# ============================================================================

class TestAxiomCheckers:
    """
    Tests for axioms.py.

    KEY TEST: check_first_order MUST return OPEN for any concrete
    spectral triple that does NOT supply a positive Coq proof.
    This mirrors NGT4 in trinity-s3ai/proofs/trinity/NoGoTheorems.v.
    """

    def _make_h4_like_triple(self):
        """
        Minimal stub spectral triple that represents a discrete/finite model
        analogous to the H4/600-cell (algebra ℂ ⊕ ℍ ⊕ M₃(ℂ), H_dim=240).
        No real linear algebra — just metadata stubs for interface testing.
        """
        from ncg_verifier.spectral_triple import SpectralTriple

        class H4LikeTriple(SpectralTriple):
            """
            Stub H4/600-cell spectral triple for smoke testing.

            This triple FAILS the first-order condition, as proved by NGT4
            in trinity-s3ai/proofs/trinity/NoGoTheorems.v.
            In this alpha, the axiom checker correctly returns OPEN for all
            discrete triples (positive Coq proof not supplied).
            """
            @property
            def name(self): return "H4-600cell (stub)"
            @property
            def ko_dimension(self): return 6
            @property
            def sign_triple(self): return (+1, -1, +1)
            @property
            def algebra(self):
                return {"type": "finite_product", "components": ["C", "H", "M3C"]}
            @property
            def hilbert_space(self):
                return {"dimension": 240, "description": "C^120 ⊗ C^2"}
            @property
            def dirac(self):
                return {"type": "graph_dirac", "ko_dimension": 6}
            @property
            def gamma(self):
                return {"type": "diagonal_sign_operator"}
            @property
            def J(self):
                return {"type": "quaternionic_conjugation",
                        "signs": {"eps": "+1", "eps_prime": "-1", "eps_double_prime": "+1"}}

        return H4LikeTriple()

    def test_import_axioms(self):
        """axioms module imports without error."""
        import ncg_verifier.axioms as ax  # noqa: F401
        assert ax is not None

    def test_axiom_status_enum(self):
        """AxiomStatus enum has expected values."""
        from ncg_verifier.axioms import AxiomStatus
        assert AxiomStatus.OPEN == "OPEN"
        assert AxiomStatus.VERIFIED == "VERIFIED"
        assert AxiomStatus.STUB == "STUB"

    def test_check_first_order_returns_open(self):
        """
        Axiom 5 (first-order condition) MUST return OPEN for any discrete
        spectral triple without a positive Coq proof.

        This is the smoke test for NGT4 (trinity-s3ai): the H4/600-cell
        spectral triple fails the first-order condition. The checker should
        return OPEN, never VERIFIED, for a stub triple.
        """
        from ncg_verifier.axioms import AxiomStatus, check_first_order

        triple = self._make_h4_like_triple()
        result = check_first_order(triple)

        assert result.axiom_number == 5
        assert result.status == AxiomStatus.OPEN, (
            f"Expected OPEN for first-order condition (matching NGT4 from trinity-s3ai), "
            f"got {result.status}"
        )
        assert "first" in result.axiom_name.lower() or "order" in result.axiom_name.lower()
        assert result.coq_reference is not None

    def test_check_first_order_references_ngt4(self):
        """The first-order result should mention NGT4 in its evidence."""
        from ncg_verifier.axioms import check_first_order

        triple = self._make_h4_like_triple()
        result = check_first_order(triple)

        # Should mention the NoGoTheorems proof
        combined = (result.evidence + result.notes + (result.coq_reference or "")).upper()
        assert "NGT4" in combined or "NOGO" in combined or "NO_GO" in combined, (
            f"Expected reference to NGT4 or no-go theorem; got evidence={result.evidence!r}"
        )

    def test_check_all_axioms_returns_seven_results(self):
        """check_all_axioms returns exactly 7 results (one per Connes axiom)."""
        from ncg_verifier.axioms import check_all_axioms

        triple = self._make_h4_like_triple()
        report = check_all_axioms(triple)

        assert len(report.results) == 7

    def test_check_all_axioms_axiom5_is_open(self):
        """In check_all_axioms, axiom 5 must be OPEN for the H4-like triple."""
        from ncg_verifier.axioms import AxiomStatus, check_all_axioms

        triple = self._make_h4_like_triple()
        report = check_all_axioms(triple)

        result5 = report.get(5)
        assert result5 is not None, "Axiom 5 result should be in the report"
        assert result5.status == AxiomStatus.OPEN, (
            f"Axiom 5 should be OPEN (matches NGT4), got {result5.status}"
        )

    def test_axiom_report_summary(self):
        """AxiomReport.summary() returns a non-empty string."""
        from ncg_verifier.axioms import check_all_axioms

        triple = self._make_h4_like_triple()
        report = check_all_axioms(triple)
        s = report.summary()
        assert isinstance(s, str)
        assert len(s) > 0
        assert "OPEN" in s    # axiom 5 is always OPEN

    def test_stub_axioms_have_notes(self):
        """All stub axiom results have non-empty notes explaining the stub."""
        from ncg_verifier.axioms import AxiomStatus, check_all_axioms

        triple = self._make_h4_like_triple()
        report = check_all_axioms(triple)

        for result in report.results:
            if result.status == AxiomStatus.STUB:
                assert "STUB" in result.notes, (
                    f"Axiom {result.axiom_number} is STUB but notes don't say so: "
                    f"{result.notes!r}"
                )
                assert "M3" in result.notes or "M2" in result.notes, (
                    f"Axiom {result.axiom_number} STUB notes should reference a milestone"
                )


# ============================================================================
# 4. Anti-numerology gate
# ============================================================================

class TestAntiNumerologyGate:
    """
    Tests for anti_numerology.py.

    Uses synthetic .v file content (in-memory tempfiles) — no real Coq required.
    """

    def _write_temp_v(self, content: str) -> Path:
        """Write content to a temporary .v file and return its path."""
        tf = tempfile.NamedTemporaryFile(suffix=".v", mode="w",
                                         delete=False, encoding="utf-8")
        tf.write(textwrap.dedent(content))
        tf.flush()
        tf.close()
        return Path(tf.name)

    def test_import_gate(self):
        """anti_numerology module imports without error."""
        from ncg_verifier.anti_numerology import AntiNumerologyGate  # noqa: F401
        assert AntiNumerologyGate is not None

    def test_gate_flags_untagged_multi_atom(self):
        """
        An untagged multi-atom definition is flagged.
        This replicates the behavior that caught numerology in trinity-s3ai.
        """
        from ncg_verifier.anti_numerology import AntiNumerologyGate

        content = """
        (* No honesty tag here *)
        Definition m_H_approx : R := 4 * phi * PI * exp 1.
        """
        path = self._write_temp_v(content)

        gate = AntiNumerologyGate()
        result = gate.scan_file(path)

        flags = result.flags
        assert len(flags) >= 1, (
            f"Expected at least 1 FLAG for untagged multi-atom formula, "
            f"got {len(flags)}: {result.summary()}"
        )
        flag = flags[0]
        assert flag.def_name == "m_H_approx"
        assert flag.status == "FLAG"

    def test_gate_passes_tagged_formula(self):
        """A formula with an approved honesty tag passes the gate."""
        from ncg_verifier.anti_numerology import AntiNumerologyGate

        content = """
        (* [phenomenological_fit] — empirical fit, not H4 derivation *)
        Definition m_H_formula : R := 4 * phi * PI * exp 1.
        """
        path = self._write_temp_v(content)

        gate = AntiNumerologyGate()
        result = gate.scan_file(path)

        assert result.passed(), (
            f"Expected PASS for tagged formula, got: {result.summary()}"
        )
        assert len(result.flags) == 0

    def test_gate_passes_whitelisted_name(self):
        """A whitelisted definition name (e.g. 'phi') is always exempt."""
        from ncg_verifier.anti_numerology import AntiNumerologyGate

        content = """
        (* No tag needed — phi is structural *)
        Definition phi : R := (1 + sqrt 5) / 2.
        """
        path = self._write_temp_v(content)

        gate = AntiNumerologyGate()
        result = gate.scan_file(path)

        assert len(result.flags) == 0, (
            f"Expected no flags for whitelisted 'phi', got: {result.flags}"
        )
        assert len(result.whitelisted) >= 1

    def test_gate_passes_single_atom(self):
        """A single-atom formula (only phi, no other atoms) does not trigger."""
        from ncg_verifier.anti_numerology import AntiNumerologyGate

        content = """
        Definition simple_phi_scale : R := 3 * phi.
        """
        path = self._write_temp_v(content)

        gate = AntiNumerologyGate()
        result = gate.scan_file(path)

        # single atom → STRUCTURAL (not checked), not FLAG
        assert len(result.flags) == 0

    def test_gate_result_passed_method(self):
        """GateResult.passed() returns True when no flags, False otherwise."""
        from ncg_verifier.anti_numerology import FormulaResult, GateResult

        # empty result → passes
        empty = GateResult()
        assert empty.passed() is True

        # result with a FLAG
        with_flag = GateResult(results=[
            FormulaResult(
                file="x.v", line_no=1, def_name="f",
                rhs_snippet="phi * PI", atoms_found=["phi", "PI"],
                tag_found=None, status="FLAG", reason="no tag",
            )
        ])
        assert with_flag.passed() is False

    def test_gate_passes_math_todo_tag(self):
        """[MATH_TODO] is an approved honesty tag."""
        from ncg_verifier.anti_numerology import AntiNumerologyGate

        content = """
        (* [MATH_TODO] derivation not yet completed *)
        Definition mystery_formula : R := phi * PI * exp 1.
        """
        path = self._write_temp_v(content)

        gate = AntiNumerologyGate()
        result = gate.scan_file(path)
        assert result.passed(), f"[MATH_TODO] should pass gate: {result.summary()}"

    def test_empty_directory_no_crash(self, tmp_path):
        """Scanning an empty directory does not crash."""
        from ncg_verifier.anti_numerology import AntiNumerologyGate

        gate = AntiNumerologyGate()
        result = gate.scan_dir(tmp_path)
        assert result.passed()
        assert result.files_scanned == 0


# ============================================================================
# 5. Atlas loader interface
# ============================================================================

class TestAtlasLoader:
    def test_import_atlas_loader(self):
        """atlas_loader module imports without error."""
        import ncg_verifier.atlas_loader as al  # noqa: F401
        assert al is not None

    def test_ncg_model_dataclass(self):
        """NCGModel can be instantiated directly."""
        from ncg_verifier.atlas_loader import NCGModel
        m = NCGModel(name="TestModel", version="1.0")
        assert m.name == "TestModel"
        assert m.formula_count() == 0

    def test_formula_spec_dataclass(self):
        """FormulaSpec can be instantiated."""
        from ncg_verifier.atlas_loader import FormulaSpec
        f = FormulaSpec(id="H01", expression="4 * phi^3 * exp(1)^2")
        assert f.id == "H01"

    def test_load_model_missing_file_raises(self, tmp_path):
        """load_model raises FileNotFoundError for missing file."""
        import pytest

        from ncg_verifier.atlas_loader import load_model
        with pytest.raises(FileNotFoundError):
            load_model(tmp_path / "nonexistent.yaml")

    def test_load_model_json(self, tmp_path):
        """load_model can parse a minimal JSON model spec."""
        from ncg_verifier.atlas_loader import load_model

        model_data = {
            "name": "TestNCGModel",
            "version": "1.0",
            "spectral_triple": {
                "algebra": {"type": "finite_product", "components": ["C", "H"]},
                "hilbert_space": {"dimension": 4},
                "dirac_operator": {},
                "real_structure": {},
                "grading": {},
            },
            "formulas": [
                {"id": "F01", "expression": "phi + PI", "tag": "phenomenological_fit"},
            ],
        }
        import json
        json_file = tmp_path / "model.json"
        json_file.write_text(json.dumps(model_data), encoding="utf-8")

        model = load_model(json_file)
        assert model.name == "TestNCGModel"
        assert model.formula_count() == 1
        assert model.formulas[0].id == "F01"

    def test_nogo_checks_stub(self):
        """run_nogo_checks returns STUB results for each formula."""
        from ncg_verifier.atlas_loader import FormulaSpec, NCGModel, run_nogo_checks

        model = NCGModel(name="TestModel", version="1.0")
        model.formulas = [
            FormulaSpec(id="F01", expression="phi * PI"),
            FormulaSpec(id="F02", expression="4 * exp 1"),
        ]

        results = run_nogo_checks(model)
        assert len(results) == 2
        for r in results:
            assert r.status == "STUB"
