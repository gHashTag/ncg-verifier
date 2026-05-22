"""
tests/test_atlas_loader.py — Tests for the M2 atlas YAML loader.

Covers:
  1. Loading all 10 V3 seed entries succeeds and schema validates.
  2. Each entry's required fields are present and non-empty.
  3. Exactly 4 entries have proof_status=formally_verified (CONFIRMED_NO_GO),
     and exactly 6 entries are open (candidate or informal_proof).
  4. Cross-references between entries are not broken.
  5. Bad YAML raises ValueError with a useful message.
  6. validate_schema() catches specific field errors.
  7. AtlasEntry helper methods (is_confirmed_no_go, is_open, obstruction_types).
  8. load_all() with the real atlas/entries/ directory.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

# Locate the atlas/entries directory relative to this test file.
# tests/ is one level below the repo root; atlas/entries is at repo root.
REPO_ROOT = Path(__file__).parent.parent
ATLAS_DIR = REPO_ROOT / "atlas" / "entries"


# ============================================================================
# 1. Load all 10 entries — basic success
# ============================================================================

class TestLoadAll:
    """Load all 10 real V3 seed entries from atlas/entries/."""

    def test_atlas_dir_exists(self):
        """atlas/entries/ directory must exist."""
        assert ATLAS_DIR.exists(), f"atlas/entries/ not found at {ATLAS_DIR}"

    def test_exactly_10_yaml_files(self):
        """There must be exactly 10 YAML files in atlas/entries/."""
        yaml_files = list(ATLAS_DIR.glob("NCG-*.yaml"))
        assert len(yaml_files) == 10, (
            f"Expected 10 YAML entry files, found {len(yaml_files)}: "
            + str([f.name for f in yaml_files])
        )

    def test_load_all_returns_10_entries(self):
        """load_all() returns exactly 10 entries."""
        from ncg_verifier.atlas_loader import load_all
        entries = load_all(ATLAS_DIR)
        assert len(entries) == 10, (
            f"Expected 10 entries, got {len(entries)}: {list(entries.keys())}"
        )

    def test_load_all_keys_are_entry_ids(self):
        """load_all() dict keys are the NCG-* entry IDs."""
        from ncg_verifier.atlas_loader import load_all
        entries = load_all(ATLAS_DIR)
        for key in entries:
            assert key.startswith("NCG-"), f"Key {key!r} does not start with NCG-"
            assert key == entries[key].id, (
                f"Key {key!r} does not match entry id {entries[key].id!r}"
            )

    def test_all_expected_ids_present(self):
        """All 10 expected entry IDs are present after load_all."""
        from ncg_verifier.atlas_loader import load_all
        entries = load_all(ATLAS_DIR)
        expected_ids = {
            "NCG-A4-001",
            "NCG-A4-002",
            "NCG-A4-003",
            "NCG-A4-004",
            "NCG-D5-001",
            "NCG-C2-001",
            "NCG-PS-001",
            "NCG-NM-001",
            "NCG-FD-001",
            "NCG-DI-001",
        }
        assert set(entries.keys()) == expected_ids, (
            f"Unexpected IDs. Got: {sorted(entries.keys())}"
        )


# ============================================================================
# 2. Required fields present in each entry
# ============================================================================

class TestRequiredFields:
    """Each entry's required fields must be present and non-empty."""

    @pytest.fixture(scope="class")
    def entries(self):
        from ncg_verifier.atlas_loader import load_all
        return load_all(ATLAS_DIR)

    REQUIRED_NONEMPTY = [
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
        "obstruction_statement",
        "obstruction_informal",
        "proof_system",
        "proof_status",
    ]

    @pytest.mark.parametrize("field_name", REQUIRED_NONEMPTY)
    def test_field_nonempty_all_entries(self, entries, field_name):
        """Every entry must have a non-empty value for each required field."""
        for eid, entry in entries.items():
            val = getattr(entry, field_name, None)
            assert val is not None and val != "", (
                f"Entry {eid}: field {field_name!r} is empty or None"
            )

    def test_obstruction_type_nonempty(self, entries):
        """Every entry must have at least one obstruction_type."""
        for eid, entry in entries.items():
            types = entry.obstruction_types()
            assert len(types) >= 1, (
                f"Entry {eid}: obstruction_types() returned empty list"
            )

    def test_literature_citations_nonempty(self, entries):
        """Every entry must have at least one literature citation."""
        for eid, entry in entries.items():
            assert len(entry.literature_citation) >= 1, (
                f"Entry {eid}: literature_citation is empty"
            )

    def test_ko_dimension_valid_or_none(self, entries):
        """KO_dimension must be 0–7 or None (NCG-NM-001 is allowed None)."""
        for eid, entry in entries.items():
            if entry.KO_dimension is not None:
                assert 0 <= entry.KO_dimension <= 7, (
                    f"Entry {eid}: KO_dimension={entry.KO_dimension} out of range"
                )


# ============================================================================
# 3. Proof status distribution: 4 CONFIRMED_NO_GO, 6 OPEN
# ============================================================================

class TestProofStatusDistribution:
    """Verify the 4/6 CONFIRMED/OPEN split from V3 site."""

    @pytest.fixture(scope="class")
    def entries(self):
        from ncg_verifier.atlas_loader import load_all
        return load_all(ATLAS_DIR)

    def test_four_formally_verified(self, entries):
        """Exactly 4 entries must have proof_status=formally_verified."""
        confirmed = [e for e in entries.values() if e.is_confirmed_no_go()]
        assert len(confirmed) == 4, (
            f"Expected 4 formally_verified entries, got {len(confirmed)}: "
            + str([e.id for e in confirmed])
        )

    def test_six_open_or_informal(self, entries):
        """Exactly 6 entries must be candidate or informal_proof (OPEN)."""
        open_entries = [e for e in entries.values() if e.is_open()]
        assert len(open_entries) == 6, (
            f"Expected 6 open entries, got {len(open_entries)}: "
            + str([e.id for e in open_entries])
        )

    def test_confirmed_are_a4_series(self, entries):
        """The 4 formally verified entries must be NCG-A4-001 through NCG-A4-004."""
        confirmed_ids = {e.id for e in entries.values() if e.is_confirmed_no_go()}
        expected = {"NCG-A4-001", "NCG-A4-002", "NCG-A4-003", "NCG-A4-004"}
        assert confirmed_ids == expected, (
            f"Formally verified IDs: {confirmed_ids}"
        )

    def test_open_are_non_a4(self, entries):
        """The 6 open entries are the non-A4 series."""
        open_ids = {e.id for e in entries.values() if e.is_open()}
        expected = {
            "NCG-D5-001",
            "NCG-C2-001",
            "NCG-PS-001",
            "NCG-NM-001",
            "NCG-FD-001",
            "NCG-DI-001",
        }
        assert open_ids == expected, f"Open IDs: {open_ids}"

    def test_confirmed_entries_have_admitted_count_zero(self, entries):
        """All formally_verified entries must have admitted_count=0."""
        for eid, entry in entries.items():
            if entry.is_confirmed_no_go():
                assert entry.admitted_count == 0, (
                    f"Entry {eid}: formally_verified but admitted_count="
                    f"{entry.admitted_count}"
                )

    def test_confirmed_entries_have_theorem_name(self, entries):
        """All formally_verified entries must have a theorem_name."""
        for eid, entry in entries.items():
            if entry.is_confirmed_no_go():
                assert entry.theorem_name, (
                    f"Entry {eid}: formally_verified but no theorem_name"
                )

    def test_confirmed_entries_have_proof_path(self, entries):
        """All formally_verified entries must have a proof_path."""
        for eid, entry in entries.items():
            if entry.is_confirmed_no_go():
                assert entry.proof_path, (
                    f"Entry {eid}: formally_verified but no proof_path"
                )


# ============================================================================
# 4. Cross-reference check
# ============================================================================

class TestCrossReferences:
    """All related_entries references must resolve to existing entry IDs."""

    @pytest.fixture(scope="class")
    def entries(self):
        from ncg_verifier.atlas_loader import load_all
        return load_all(ATLAS_DIR)

    def test_no_broken_cross_references(self, entries):
        """cross_reference_check() must return an empty list."""
        from ncg_verifier.atlas_loader import cross_reference_check
        broken = cross_reference_check(entries)
        assert broken == [], (
            f"Broken cross-references found:\n"
            + "\n".join(str(b) for b in broken)
        )

    def test_a4_001_related_entries(self, entries):
        """NCG-A4-001 must list NCG-A4-002, 003, 004 as related."""
        entry = entries["NCG-A4-001"]
        assert "NCG-A4-002" in entry.related_entries
        assert "NCG-A4-003" in entry.related_entries
        assert "NCG-A4-004" in entry.related_entries

    def test_a4_003_related_to_d5_001(self, entries):
        """NCG-A4-003 (chirality) must reference NCG-D5-001 (also chirality)."""
        entry = entries["NCG-A4-003"]
        assert "NCG-D5-001" in entry.related_entries

    def test_c2_001_related_to_fd_001(self, entries):
        """NCG-C2-001 must reference NCG-FD-001 (both fermion doubling)."""
        entry = entries["NCG-C2-001"]
        assert "NCG-FD-001" in entry.related_entries


# ============================================================================
# 5. Bad YAML raises ValueError with a useful message
# ============================================================================

class TestBadInputRaises:
    """Schema errors and missing files must raise appropriate exceptions."""

    def test_missing_file_raises_file_not_found(self, tmp_path):
        """load_entry() raises FileNotFoundError for a non-existent file."""
        from ncg_verifier.atlas_loader import load_entry
        with pytest.raises(FileNotFoundError, match="not found"):
            load_entry(tmp_path / "NCG-XX-999.yaml")

    def test_bad_yaml_raises_value_error(self, tmp_path):
        """load_entry() raises ValueError for malformed YAML."""
        from ncg_verifier.atlas_loader import load_entry
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("{invalid: [yaml: content", encoding="utf-8")
        with pytest.raises(ValueError, match="Failed to parse YAML"):
            load_entry(bad_yaml)

    def test_missing_required_field_raises_value_error(self, tmp_path):
        """An entry missing 'id' raises ValueError with a useful message."""
        from ncg_verifier.atlas_loader import load_entry
        incomplete = {
            # id is missing
            "model_name": "Test model",
            "version": "0.1.0",
            "date_added": "2025-07-01",
            "algebra": "ℂ",
            "algebra_type": "group_algebra",
            "hilbert_space_description": "H = ℓ²(G)",
            "dirac_operator_description": "D = adjacency",
            "real_structure_J": "J² = +1",
            "grading_gamma": "none",
            "KO_dimension": 6,
            "obstruction_type": "chirality",
            "obstruction_statement": "A" * 60,
            "obstruction_informal": "B" * 30,
            "proof_system": "none",
            "proof_status": "candidate",
            "literature_citation": [],
        }
        entry_file = tmp_path / "NCG-XX-001.yaml"
        entry_file.write_text(yaml.dump(incomplete), encoding="utf-8")
        with pytest.raises(ValueError, match="validation failed|Required field"):
            load_entry(entry_file)

    def test_invalid_proof_system_raises_value_error(self, tmp_path):
        """An entry with an invalid proof_system raises ValueError."""
        from ncg_verifier.atlas_loader import load_entry
        entry_data = {
            "id": "NCG-XX-001",
            "model_name": "Test model",
            "version": "0.1.0",
            "date_added": "2025-07-01",
            "algebra": "ℂ",
            "algebra_type": "group_algebra",
            "hilbert_space_description": "H = ℓ²(G)",
            "dirac_operator_description": "D = adjacency",
            "real_structure_J": "J² = +1",
            "grading_gamma": "none",
            "KO_dimension": 6,
            "obstruction_type": "chirality",
            "obstruction_statement": "A" * 60,
            "obstruction_informal": "B" * 30,
            "proof_system": "MAPLE",  # invalid
            "proof_status": "candidate",
            "literature_citation": [],
        }
        entry_file = tmp_path / "NCG-XX-001.yaml"
        entry_file.write_text(yaml.dump(entry_data), encoding="utf-8")
        with pytest.raises(ValueError, match="MAPLE|proof_system"):
            load_entry(entry_file)

    def test_invalid_algebra_type_raises_value_error(self, tmp_path):
        """An entry with an invalid algebra_type raises ValueError."""
        from ncg_verifier.atlas_loader import load_entry
        entry_data = {
            "id": "NCG-XX-001",
            "model_name": "Test model",
            "version": "0.1.0",
            "date_added": "2025-07-01",
            "algebra": "ℂ",
            "algebra_type": "banana_algebra",  # invalid
            "hilbert_space_description": "H",
            "dirac_operator_description": "D",
            "real_structure_J": "J",
            "grading_gamma": "γ",
            "KO_dimension": 6,
            "obstruction_type": "chirality",
            "obstruction_statement": "A" * 60,
            "obstruction_informal": "B" * 30,
            "proof_system": "none",
            "proof_status": "candidate",
            "literature_citation": [],
        }
        entry_file = tmp_path / "NCG-XX-001.yaml"
        entry_file.write_text(yaml.dump(entry_data), encoding="utf-8")
        with pytest.raises(ValueError, match="banana_algebra|algebra_type"):
            load_entry(entry_file)

    def test_error_message_names_the_field(self, tmp_path):
        """ValueError message must name the offending field."""
        from ncg_verifier.atlas_loader import load_entry
        entry_data = {
            "id": "NCG-XX-001",
            "model_name": "Test",
            "version": "0.1.0",
            "date_added": "2025-07-01",
            "algebra": "ℂ",
            "algebra_type": "group_algebra",
            "hilbert_space_description": "H",
            "dirac_operator_description": "D",
            "real_structure_J": "J",
            "grading_gamma": "γ",
            "KO_dimension": 6,
            "obstruction_type": "not_a_real_type",  # bad
            "obstruction_statement": "A" * 60,
            "obstruction_informal": "B" * 30,
            "proof_system": "none",
            "proof_status": "candidate",
            "literature_citation": [],
        }
        entry_file = tmp_path / "NCG-XX-001.yaml"
        entry_file.write_text(yaml.dump(entry_data), encoding="utf-8")
        with pytest.raises(ValueError) as exc_info:
            load_entry(entry_file)
        # The error message should be descriptive
        assert len(str(exc_info.value)) > 20


# ============================================================================
# 6. validate_schema() standalone tests
# ============================================================================

class TestValidateSchema:
    """Unit tests for validate_schema() in isolation."""

    def _minimal_valid_dict(self) -> dict:
        return {
            "id": "NCG-A4-001",
            "model_name": "Test model",
            "version": "1.0.0",
            "date_added": "2025-07-01",
            "algebra": "ℂ[2I]",
            "algebra_type": "group_algebra",
            "hilbert_space_description": "ℓ²(2I), dim = 120",
            "dirac_operator_description": "Adjacency Dirac",
            "real_structure_J": "J² = +1",
            "grading_gamma": "parity",
            "KO_dimension": 6,
            "obstruction_type": "cosmology",
            "obstruction_statement": "A" * 60,
            "obstruction_informal": "Informal statement here.",
            "proof_system": "Coq",
            "proof_status": "formally_verified",
            "admitted_count": 0,
            "literature_citation": [],
        }

    def test_valid_entry_no_errors(self):
        """A valid minimal entry produces no errors."""
        from ncg_verifier.atlas_loader import validate_schema
        errors = validate_schema(self._minimal_valid_dict())
        assert errors == [], f"Unexpected errors: {errors}"

    def test_missing_required_field(self):
        """Missing 'id' field produces a ValidationError."""
        from ncg_verifier.atlas_loader import validate_schema
        d = self._minimal_valid_dict()
        del d["id"]
        errors = validate_schema(d)
        assert any(e.field == "id" for e in errors), (
            f"Expected error on 'id', got: {errors}"
        )

    def test_bad_algebra_type(self):
        """Invalid algebra_type produces a ValidationError."""
        from ncg_verifier.atlas_loader import validate_schema
        d = self._minimal_valid_dict()
        d["algebra_type"] = "quantum_algebra"
        errors = validate_schema(d)
        assert any(e.field == "algebra_type" for e in errors)

    def test_bad_proof_system(self):
        """Invalid proof_system produces a ValidationError."""
        from ncg_verifier.atlas_loader import validate_schema
        d = self._minimal_valid_dict()
        d["proof_system"] = "Isabelle2024"
        errors = validate_schema(d)
        assert any(e.field == "proof_system" for e in errors)

    def test_bad_proof_status(self):
        """Invalid proof_status produces a ValidationError."""
        from ncg_verifier.atlas_loader import validate_schema
        d = self._minimal_valid_dict()
        d["proof_status"] = "unverified"
        errors = validate_schema(d)
        assert any(e.field == "proof_status" for e in errors)

    def test_formally_verified_with_admitted_count_nonzero(self):
        """formally_verified with admitted_count != 0 is an error."""
        from ncg_verifier.atlas_loader import validate_schema
        d = self._minimal_valid_dict()
        d["admitted_count"] = 3
        errors = validate_schema(d)
        assert any(e.field == "admitted_count" for e in errors)

    def test_list_obstruction_type_valid(self):
        """A list of valid obstruction types produces no errors."""
        from ncg_verifier.atlas_loader import validate_schema
        d = self._minimal_valid_dict()
        d["obstruction_type"] = ["gauge_unification", "first_order"]
        d["proof_system"] = "none"
        d["proof_status"] = "candidate"
        d.pop("admitted_count", None)
        errors = validate_schema(d)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_list_obstruction_type_invalid(self):
        """A list containing an invalid type produces a ValidationError."""
        from ncg_verifier.atlas_loader import validate_schema
        d = self._minimal_valid_dict()
        d["obstruction_type"] = ["chirality", "not_a_type"]
        errors = validate_schema(d)
        assert any(e.field == "obstruction_type" for e in errors)


# ============================================================================
# 7. AtlasEntry helper methods
# ============================================================================

class TestAtlasEntryHelpers:
    """Unit tests for AtlasEntry helper methods."""

    def test_is_confirmed_no_go_true(self):
        """is_confirmed_no_go() returns True for formally_verified."""
        from ncg_verifier.atlas_loader import AtlasEntry
        e = AtlasEntry(
            id="NCG-A4-001",
            model_name="Test",
            version="1.0.0",
            date_added="2025-07-01",
            proof_status="formally_verified",
        )
        assert e.is_confirmed_no_go() is True

    def test_is_confirmed_no_go_false(self):
        """is_confirmed_no_go() returns False for candidate."""
        from ncg_verifier.atlas_loader import AtlasEntry
        e = AtlasEntry(
            id="NCG-D5-001",
            model_name="Test",
            version="0.1.0",
            date_added="2025-07-01",
            proof_status="candidate",
        )
        assert e.is_confirmed_no_go() is False

    def test_is_open_candidate(self):
        """is_open() returns True for candidate."""
        from ncg_verifier.atlas_loader import AtlasEntry
        e = AtlasEntry(
            id="NCG-D5-001",
            model_name="Test",
            version="0.1.0",
            date_added="2025-07-01",
            proof_status="candidate",
        )
        assert e.is_open() is True

    def test_is_open_informal_proof(self):
        """is_open() returns True for informal_proof."""
        from ncg_verifier.atlas_loader import AtlasEntry
        e = AtlasEntry(
            id="NCG-C2-001",
            model_name="Test",
            version="0.1.0",
            date_added="2025-07-01",
            proof_status="informal_proof",
        )
        assert e.is_open() is True

    def test_obstruction_types_string(self):
        """obstruction_types() normalizes a string to a list."""
        from ncg_verifier.atlas_loader import AtlasEntry
        e = AtlasEntry(
            id="NCG-A4-001",
            model_name="Test",
            version="1.0.0",
            date_added="2025-07-01",
            obstruction_type="cosmology",
        )
        assert e.obstruction_types() == ["cosmology"]

    def test_obstruction_types_list(self):
        """obstruction_types() returns a list as-is."""
        from ncg_verifier.atlas_loader import AtlasEntry
        e = AtlasEntry(
            id="NCG-PS-001",
            model_name="Test",
            version="0.1.0",
            date_added="2025-07-01",
            obstruction_type=["gauge_unification", "first_order"],
        )
        assert e.obstruction_types() == ["gauge_unification", "first_order"]

    def test_summary_contains_id(self):
        """summary() output contains the entry ID."""
        from ncg_verifier.atlas_loader import AtlasEntry
        e = AtlasEntry(
            id="NCG-A4-001",
            model_name="H4/600-cell",
            version="1.0.0",
            date_added="2025-07-01",
            obstruction_type="cosmology",
            proof_status="formally_verified",
        )
        s = e.summary()
        assert "NCG-A4-001" in s
        assert "cosmology" in s
        assert "formally_verified" in s


# ============================================================================
# 8. load_all with real atlas directory (integration)
# ============================================================================

class TestLoadAllIntegration:
    """Integration tests against the real atlas/entries/ directory."""

    @pytest.fixture(scope="class")
    def entries(self):
        from ncg_verifier.atlas_loader import load_all
        return load_all(ATLAS_DIR)

    def test_all_summaries_non_empty(self, entries):
        """summary() is non-empty for every loaded entry."""
        for eid, entry in entries.items():
            s = entry.summary()
            assert isinstance(s, str) and len(s) > 0, (
                f"Entry {eid}: summary() returned empty or non-string"
            )

    def test_ps_001_has_list_obstruction_type(self, entries):
        """NCG-PS-001 must have a list obstruction_type (gauge_unification + first_order)."""
        entry = entries["NCG-PS-001"]
        types = entry.obstruction_types()
        assert "gauge_unification" in types
        assert "first_order" in types

    def test_nm_001_ko_dimension_is_none(self, entries):
        """NCG-NM-001 must have KO_dimension=None (Jordan geometry)."""
        entry = entries["NCG-NM-001"]
        assert entry.KO_dimension is None

    def test_a4_series_have_coq_proof_system(self, entries):
        """All 4 A4-series entries must have proof_system=Coq."""
        for eid in ["NCG-A4-001", "NCG-A4-002", "NCG-A4-003", "NCG-A4-004"]:
            assert entries[eid].proof_system == "Coq", (
                f"Entry {eid}: proof_system={entries[eid].proof_system!r}"
            )

    def test_no_schema_errors_any_entry(self, entries):
        """validate_schema() returns no errors for any loaded entry."""
        from ncg_verifier.atlas_loader import validate_schema
        for eid, entry in entries.items():
            errors = validate_schema(entry._raw)
            assert errors == [], (
                f"Entry {eid} has schema errors: "
                + "; ".join(str(e) for e in errors)
            )
