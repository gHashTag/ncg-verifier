# NCG-Verifier

**A formal verification pipeline for noncommutative geometry spectral triples, with anti-numerology gate.**

> **Alpha status:** This is `v0.1.0-alpha` — a scaffold implementing the package interface and
> the anti-numerology gate (ported from [trinity-s3ai](https://github.com/gHashTag/trinity-s3ai)).
> The axiom checkers, classification engine, and numerical validator are **stubs** with clearly
> marked `# STUB` comments. Full implementation follows the 26-week roadmap in `docs/roadmap.md`
> (milestones M1–M6). **Do not use the alpha for production axiom verification.**

[![Tests](https://github.com/gHashTag/ncg-verifier/actions/workflows/test.yml/badge.svg)](https://github.com/gHashTag/ncg-verifier/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

---

## Summary

NCG-Verifier is an open-source Python and Coq pipeline for the systematic formal verification of
noncommutative geometry (NCG) models of the Standard Model of particle physics. The tool enforces
a discipline of mathematical honesty by:

1. **Anti-numerology gate** — CI-level scanner that blocks untagged combinations of φ, π, and e
   in Coq source files (generalized from `scripts/anti_numerology_gate.py` in trinity-s3ai).
2. **Axiom checker** — Verifies compliance with Connes' seven axioms for a real spectral triple
   (A, H, D; J, γ). *(Stub in v0.1.0-alpha; full implementation in M3, week 12.)*
3. **Formula classifier** — Tags formulas as Rigorous (R), Structural (S), NumericalFit (NF),
   or Refuted using the four-class taxonomy from the trinity-s3ai A1 audit.
   *(Stub in v0.1.0-alpha; full implementation in M4, week 14.)*
4. **Atlas loader** — Loads V3 Atlas entries from YAML/JSON and runs no-go checks.
   *(Stub in v0.1.0-alpha; full implementation in M2, week 6.)*

The tool grew out of the infrastructure developed in the
[trinity-s3ai project](https://github.com/gHashTag/trinity-s3ai), where the H4/600-cell spectral
triple was investigated over ten development waves and 1326 Qed theorems were accumulated alongside
a rigorous audit that proved four formal no-go theorems (NGT1–NGT4).

---

## Statement of Need

The NCG literature faces a reproducibility problem:

- **Numerology proliferation.** Combinations of φ, π, and e can approximate any real number to
  arbitrary precision; without a formal tool, the literature cannot reliably distinguish genuine
  derivations from numerical coincidences.
- **Axiom compliance opacity.** Connes' seven axioms are rarely verified explicitly for proposed
  models. Even in well-documented projects like trinity-s3ai, axioms 5 (first-order condition),
  6 (orientation), and 7 (Poincaré duality) remain open after substantial formalization effort.
- **Absence of cross-validation.** No established toolchain exists for validating that a theorem
  proved in Coq holds in Lean 4, despite Lean 4 Mathlib containing richer infrastructure for
  differential geometry and Lie algebras.

NCG-Verifier addresses all three through a unified pipeline running in CI with auditable reports.

---

## Installation

```bash
pip install ncg-verifier          # from PyPI (upcoming)
pip install -e .                  # from source (development)
```

Requires Python ≥ 3.11. Optional dependencies: `pydantic>=2.0` for schema validation,
`coqc` for axiom checking (M3+), `lake` for Lean 4 cross-prover (M5+).

---

## Quick Start

```python
from ncg_verifier import NCGVerifier, __version__
print(__version__)  # 0.1.0-alpha

# Anti-numerology gate (fully implemented)
from ncg_verifier.anti_numerology import AntiNumerologyGate
gate = AntiNumerologyGate()
result = gate.scan_file("proofs/my_model.v")
print(result.summary())

# Spectral triple interface (interface only in alpha)
from ncg_verifier.spectral_triple import SpectralTriple
# See examples/h4_600cell_failing.py for usage
```

CLI:
```bash
ncg-verifier --help
ncg-verifier anti-numerology --dir proofs/
```

---

## Architecture

```
src/ncg_verifier/
├── __init__.py            — package version, top-level imports
├── spectral_triple.py     — abstract base class: (A, H, D, γ, J)
├── axioms.py              — Connes' axiom checkers [STUB: M3, week 12]
├── anti_numerology.py     — anti-numerology gate (generalized from trinity-s3ai)
├── atlas_loader.py        — YAML/JSON model loader [STUB: M2, week 6]
└── cli.py                 — CLI entry point
```

The pipeline is described in full in
[`docs/joss_paper.md`](docs/joss_paper.md) and the
[V1 Architecture Specification](https://github.com/gHashTag/trinity-s3ai).

---

## The H4/600-Cell First-Order Failure

The canonical example motivating this tool: the H4/600-cell spectral triple — a model based on
the 600-cell polytope with algebra ℂ ⊕ ℍ ⊕ M₃(ℂ) — **fails axiom 5 (first-order condition)**
as proved by NGT4 in `proofs/trinity/NoGoTheorems.v` of trinity-s3ai. This failure is the primary
structural obstruction for any discrete NCG model and is the reason axiom 5 is always reported
as `OPEN` in this tool.

See `examples/h4_600cell_failing.py` for a runnable demonstration.

---

## Roadmap

| Milestone | Weeks | Status |
|-----------|-------|--------|
| M1: Modular refactoring | 1–4 | **In progress (this alpha)** |
| M2: Algebra parser | 3–6 | Stub |
| M3: Axiom checker | 5–10 | Stub |
| M4: Classification engine | 8–14 | Stub |
| M5: Cross-prover validator | 12–20 | Planned |
| M6: External user + JOSS | 18–26 | Planned |

Full roadmap: [`docs/roadmap.md`](docs/roadmap.md)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). This project follows the
[Contributor Covenant](CODE_OF_CONDUCT.md) code of conduct.

---

## License

MIT. See [LICENSE](LICENSE).

---

## Citation

If you use NCG-Verifier in research, please cite the JOSS paper (in preparation):

```bibtex
@software{ncg_verifier_2026,
  title   = {{NCG-Verifier}: A Formal Verification Pipeline for Noncommutative
             Geometry Models of the Standard Model},
  author  = {{trinity-s3ai contributors}},
  year    = {2026},
  url     = {https://github.com/gHashTag/ncg-verifier},
  version = {0.1.0-alpha}
}
```

Upstream infrastructure: [trinity-s3ai](https://github.com/gHashTag/trinity-s3ai).

---

## References

- Connes, A. (1996). Gravity coupled with matter and the foundation of non-commutative geometry.
  *Commun. Math. Phys.* 182, 155–176. https://arxiv.org/abs/hep-th/9603053
- Chamseddine, A.H., Connes, A. (2007). Why the Standard Model.
  *J. Geom. Phys.* 58(1), 38–47. https://arxiv.org/abs/0706.3688
- Chamseddine, A.H., Connes, A., van Suijlekom, W.D. (2013). Beyond the spectral standard model.
  *JHEP* 2013, 132. https://arxiv.org/abs/1304.8050
