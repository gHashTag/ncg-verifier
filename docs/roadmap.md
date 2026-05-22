# NCG-Verifier: Development Roadmap (V1, 26-Week Plan)

This roadmap is a condensed version of the full V1 roadmap from the trinity-s3ai planning documents.

## Milestones

| Milestone | Weeks | Primary artifact | Status |
|-----------|-------|-----------------|--------|
| M1: Modular refactoring | 1–4 | Package scaffold + anti-numerology gate | **In progress (v0.1.0-alpha)** |
| M2: Algebra parser | 3–6 | `NCGModel` + YAML schema + `validate` CLI | Stub |
| M3: Axiom checker | 5–10 | Coq axiom templates + `check_all_axioms` | Stub |
| M4: Classification engine | 8–14 | R/S/NF/Refuted classifier | Stub |
| M5: Cross-prover validator | 12–20 | Lean 4 port extension + Docker | Planned |
| M6: External user + JOSS | 18–26 | JOSS submission + Zenodo archive | Planned |

## Current Status (v0.1.0-alpha = M1)

**Implemented:**
- Package scaffold (`pyproject.toml`, `src/ncg_verifier/`, CI workflow)
- `SpectralTriple` abstract base class with all five components (A, H, D, γ, J)
- `AntiNumerologyGate` — full port of `trinity-s3ai/scripts/anti_numerology_gate.py`
  with configurable atoms, tags, whitelist, and file suffix
- `AxiomResult` / `AxiomReport` types
- `check_first_order()` returning OPEN (always correct for discrete models — matches NGT4)
- `NCGModel` / `FormulaSpec` interface stubs

**Stubs (clearly marked with `# STUB: M<N> (week <W>)`):**
- Axiom checkers 1–4 and 6–7: return STUB status
- Coq compiler integration (`coqc` subprocess wrapper)
- YAML schema validation (`pydantic`)
- Full atlas loader
- Classification engine (R/S/NF/Refuted)
- Numerical validator (`coq-interval` proof generation)
- Cross-prover validator (Lean 4 / `lake build`)
- Report generator (Markdown + JSON)

## Key Design Decisions

**Why is axiom 5 always OPEN?**
The first-order condition `[[D, a], JbJ⁻¹] = 0` is the primary structural
obstruction for discrete NCG models. NGT4 in `proofs/trinity/NoGoTheorems.v`
(trinity-s3ai) gives a Qed proof that it fails for H4/600-cell. Until a
positive Coq proof is supplied for a specific model, the checker correctly
reports OPEN rather than making unsupported claims.

**Why Python + Coq rather than Coq-only?**
See V1 Architecture Specification §12.

**Why hatchling over setuptools?**
Modern PEP 517 build system; simpler `pyproject.toml`; no `setup.py` needed.
