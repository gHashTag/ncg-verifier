---
title: "NCG-Verifier: A Formal Verification Pipeline for Noncommutative Geometry Models of the Standard Model"
tags:
  - noncommutative geometry
  - formal verification
  - Coq
  - Lean 4
  - Standard Model
  - proof assistant
  - spectral triple
authors:
  - name: "[Lead author — trinity-s3ai contributors]"
    affiliation: 1
affiliations:
  - name: "[Institution]"
    index: 1
date: 2026
bibliography: paper.bib
---

# Summary

NCG-Verifier is an open-source Python and Coq pipeline for the systematic
formal verification of noncommutative geometry (NCG) models of the Standard
Model of particle physics. The tool enforces a discipline of mathematical
honesty by classifying every formula in a model as one of four types —
Rigorous (R), Structural (S), NumericalFit (NF), or Refuted — and blocking
continuous integration (CI) builds that introduce untagged numerological
claims. NCG-Verifier operates on a model specification in YAML or JSON,
optional Coq source files for formal theorems, and optional Lean 4 files for
cross-prover validation. It emits a structured Markdown report and a
machine-readable JSON summary. The tool grew out of the infrastructure
developed in the trinity-s3ai project
(https://github.com/gHashTag/trinity-s3ai), where the H4/600-cell spectral
triple was investigated over ten development waves and 1326 Qed theorems were
accumulated alongside a rigorous audit that classified all formulas and proved
four formal no-go theorems. NCG-Verifier extracts this infrastructure from
the H4-specific context and exposes it as a reusable tool for any NCG
researcher.

---

# Statement of Need

Noncommutative geometry, as developed by Connes and collaborators, provides a
geometric framework for unifying gravity and the Standard Model through the
concept of a spectral triple (A, H, D; J, γ) satisfying seven axioms
[@connes1996; @chamseddine2007]. The program has produced genuine theoretical
achievements, including a geometric derivation of the Standard Model gauge
group, the prediction and subsequent retraction of the Higgs mass, and the
emergence of the Pati-Salam model through relaxation of the first-order
condition [@chamseddine2013]. However, the field faces a reproducibility
problem that has become acute as the number of proposed NCG models has grown.

The reproducibility problem has three components:

**Numerology proliferation.** NCG model building routinely involves
combinations of the golden ratio φ, π, and e (Euler's number) applied to
representation-theoretic integers. Because these constants can approximate
any real number to arbitrary precision given enough freedom in choosing
exponents, unconstrained formula search reliably produces coincidences with
measured Standard Model parameters. Without a formal tool that distinguishes
a genuine derivation from a numerical coincidence, the literature cannot
reliably distinguish the two. The trinity-s3ai project documented this problem
empirically: of 25 formulas in the initial catalog, zero were class R
(rigorously derived from first principles), eight were class S (structurally
motivated), and seventeen were class NF (numerical fit) — a ratio that the
authors argue is typical of the field [@trinity_audit].

**Axiom compliance opacity.** Connes' seven axioms for a real spectral triple
are mathematically precise, but their verification for a proposed model is
rarely carried out explicitly. The axiom checklist in
`derivations/spectral_triple_axioms/axiom_checklist.md` of trinity-s3ai
demonstrates that even in a well-documented project, axioms 5 (first-order
condition), 6 (orientation), and 7 (Poincaré duality) remain open after
substantial formalization effort. A tool that makes this status explicit for
every model — rather than leaving it implicit in scattered proof files —
would improve the field's ability to compare models and identify genuine
progress.

**Absence of cross-validation.** The NCG literature contains both Coq and
Lean 4 formalizations, but no established toolchain for validating that a
theorem proved in one system holds in the other. The Lean 4 Mathlib library
contains substantially richer infrastructure for differential geometry and
Lie algebras than the Coq ecosystem [@mathlib2020], making cross-prover
validation both possible and valuable. The nascent Lean 4 port in
`derivations/lean_port/` of trinity-s3ai demonstrates the feasibility of
this approach for the core algebraic lemmas.

NCG-Verifier addresses all three components through a unified pipeline that
runs in CI and generates auditable reports. The tool is the first to our
knowledge that combines formal proof compilation, formula classification, and
CI enforcement specifically for NCG model verification.

---

# State of the Field

Several related software tools exist in adjacent areas, but none addresses
the specific combination of needs that NCG-Verifier targets.

**Coq and Lean 4 proof assistants** (https://coq.inria.fr,
https://leanprover.github.io) provide the underlying formal verification
infrastructure, but are general-purpose tools that require substantial
expertise to apply to NCG. NCG-Verifier provides an NCG-specific wrapper
that handles model ingestion, axiom template generation, and report
formatting.

**coq-interval** [@melquiond2022] provides certified numerical bounds for
real-valued expressions in Coq and is used extensively in the trinity-s3ai
proof base for formula validation. NCG-Verifier automates the generation of
`interval`-tactic proof obligations and escalates gracefully when
`coq-interval` encounters library gaps.

**Mathlib** [@mathlib2020] provides the Lean 4 mathematical library used in
the cross-prover validation module. Mathlib's `Algebra.Lie.Basic` and
`Analysis.Calculus.DifferentialForm.Basic` modules are particularly relevant
for NCG formalization.

**Specialized NCG software** such as the computer algebra implementations of
spectral action computations by van Suijlekom et al. target the physics
computation layer (computing spectral action coefficients, running coupling
constants) rather than the formal verification layer. NCG-Verifier is
complementary: it verifies the claims that such computations generate, rather
than performing the computations itself.

The build-versus-contribute question: contributing the anti-numerology gate
and classification engine to an existing proof assistant would require
modifications to proof assistant internals that are not appropriate for a
domain-specific tool. NCG-Verifier is better understood as a domain-specific
quality assurance layer that sits on top of existing proof assistants, rather
than as a modification of them.

---

# Functionality

NCG-Verifier is organized into seven modules, described briefly here; full
API documentation is in the software repository.

**Algebra Parser** reads a YAML or JSON model specification describing the
spectral triple components (algebra A, Hilbert space H, Dirac operator D,
real structure J, grading γ) and emits a canonical internal representation.
The YAML schema is designed to be human-readable and incrementally
completable: a researcher can begin with a minimal description and add formal
references to Coq files as their formalization matures.

**Axiom Checker** generates Coq proof obligations for each of the seven
Connes axioms and compiles them against the user's proof files. Axioms 2
(regularity) and 3 (finiteness) are proved automatically for any finite
spectral triple; axiom 5 (first-order condition) is always tagged
`[MATH_TODO]` with a documentation comment explaining why it is the primary
obstruction. This behavior is grounded in the findings of
`derivations/spectral_triple_axioms/axiom_checklist.md`.

**Classification Engine** assigns each formula one of four tags — Rigorous,
Structural, NumericalFit, Refuted — based on the proof state of its Coq
source (Qed vs. Admitted vs. Axiom), the assumption set revealed by `Print
Assumptions`, and the honesty tags in comment blocks. The four-class taxonomy
was developed during the Wave 4 audit of trinity-s3ai and is documented in
`derivations/catalog_audit/audit_report.md`.

**Numerical Validator** generates `coq-interval` proof obligations for each
formula, verifying that the predicted value falls within the experimental
error bar of the cited PDG measurement. The module handles the `simpl`-before-
`interval` pattern required for `powZ` expressions, as documented in
`admitted_log.md` entries 2–5 of trinity-s3ai.

**Cross-Prover Validator** compiles Lean 4 ports of Coq theorems and verifies
statement correspondence. The initial release covers the ten lemmas in
`derivations/lean_port/TrinityLean/CorePhi.lean`.

**Anti-Numerology CI Gate** is a direct generalization of
`scripts/anti_numerology_gate.py` in trinity-s3ai. It scans Coq source files
for untagged combinations of φ, π, and e, and exits with code 1 if any are
found. The gate is configurable via `ncg_verifier/config.yaml` and ships with
a GitHub Actions workflow template.

**Report Generator** produces a structured Markdown report and a JSON summary
of the full verification run, including per-formula classifications, axiom
compliance status, proof statistics (Qed/Admitted/Axiom counts), and a list
of open problems.

---

# Use Cases

## UC1: trinity-s3ai as First Client

The trinity-s3ai project (https://github.com/gHashTag/trinity-s3ai) is the
primary development client for NCG-Verifier. Running the verifier on the
H4/600-cell model produces a report that consolidates the results of ten
development waves: the four no-go theorems (NGT1–NGT4) in
`proofs/trinity/NoGoTheorems.v` are classified as Refuted (formally proved
impossibility results), the eleven SG-class formulas in
`proofs/trinity/Catalog42.v` are classified as NF (tagged
`[phenomenological_fit]` with Qed interval bounds), and the structural axioms
in `derivations/spectral_triple_axioms/SpectralTripleAxioms.v` are reported
with their honest partial status. The A1 audit statistics (1326 Qed, 37
Admitted, 94 Axiom) are reported in the JSON summary, providing a quantitative
basis for comparison with future versions.

## UC2: Gresnigt Cl(8) Model

The Gresnigt Cl(8) model uses the Clifford algebra Cl(8) and S³-orbits to
derive the Standard Model fermion content. NCG-Verifier can be applied to
this model by providing a YAML specification of the spectral triple data and
a set of Coq files formalizing the S³-orbit linear independence claims. The
numerical validator checks whether the KO-dimension smoke test (KO-dim = 6
mod 8 requirement for the Standard Model) is satisfied. This use case
validates that NCG-Verifier is not specific to the H4 geometry.

## UC3: Chamseddine-Connes Pati-Salam Baseline

The Pati-Salam model derived by Chamseddine, Connes, and van Suijlekom
[@chamseddine2013] provides a positive baseline: a model known to satisfy the
NCG axioms with the first-order condition relaxed. Running NCG-Verifier on a
Coq formalization of this model should produce a report where axiom 5 is
tagged `[PHYSICAL_AXIOM]` (first-order condition relaxed by construction)
and the remaining axioms are verified. This provides a regression test: if
a future version of NCG-Verifier incorrectly classifies a known-good model,
the Pati-Salam baseline will catch the error.

---

# Research Impact Statement

NCG-Verifier addresses a reproducibility gap that has been recognized
informally in the NCG community but has lacked a concrete software tool.
The trinity-s3ai project, which generated the tool's core infrastructure,
has been developed openly on GitHub since its inception, with a public
commit history, CI badges, and a Zenodo archive planned for archival. The
four no-go theorems in `proofs/trinity/NoGoTheorems.v` represent formally
verified negative results that are the first of their kind for H4/600-cell
NCG models. The anti-numerology gate, running in CI since Wave 4, has
prevented the introduction of untagged formulas across all subsequent
development. These infrastructure artifacts constitute a working proof of
concept for the NCG-Verifier approach.

The potential for broader impact is significant: the Chamseddine-Connes
program has produced dozens of proposed models since 1996, few of which have
undergone systematic axiom compliance checks or formula classification.
NCG-Verifier provides the tooling to make such checks routine.

---

# AI Usage Disclosure

The authors used large language model assistance in drafting documentation
and in generating initial Coq proof templates. All generated content was
reviewed and validated by the authors against the formal proof base. No AI
tool was used to generate or modify Coq proof terms; all formal proofs were
written and compiled by human authors using the Coq proof assistant.

---

# Acknowledgements

The authors acknowledge the infrastructure contributions of the trinity-s3ai
development community, the Coq development team, and the Lean 4 / Mathlib
community. This work builds on the theoretical foundations established by
Alain Connes and Ali Chamseddine in the noncommutative geometry approach to
the Standard Model.

---

# References

[@connes1996]: Connes, A. (1996). Gravity coupled with matter and the
foundation of non-commutative geometry. *Communications in Mathematical
Physics*, 182, 155–176. https://arxiv.org/abs/hep-th/9603053

[@chamseddine2007]: Chamseddine, A.H., Connes, A. (2007). Why the Standard
Model. *Journal of Geometry and Physics*, 58(1), 38–47.
https://arxiv.org/abs/0706.3688

[@chamseddine2013]: Chamseddine, A.H., Connes, A., van Suijlekom, W.D.
(2013). Beyond the spectral standard model: emergence of Pati-Salam
unification. *Journal of High Energy Physics*, 2013, 132.
https://arxiv.org/abs/1304.8050

[@chamseddine2019]: Chamseddine, A.H., van Suijlekom, W.D. (2019). A survey
of spectral models of gravity coupled to matter.
https://arxiv.org/abs/1904.12392

[@mathlib2020]: The Mathlib Community (2020). The Lean Mathematical Library.
*Proceedings of CPP 2020*. https://leanprover-community.github.io/mathlib4_docs/

[@melquiond2022]: Melquiond, G. (2022). Coq-interval: A Coq Tactic for
Verifying Bounds on Numerical Expressions.
https://coqinterval.gitlabpages.inria.fr/

[@trinity_audit]: trinity-s3ai contributors (2025). Catalog audit report.
`derivations/catalog_audit/audit_report.md`.
https://github.com/gHashTag/trinity-s3ai

[@connes1996recon]: Connes, A. (1996). Noncommutative geometry and reality.
*Journal of Mathematical Physics*, 36(11), 6194–6231.

[@gracia_bondia]: Gracia-Bondía, J.M., Várilly, J.C., Figueroa, H. (2001).
*Elements of Noncommutative Geometry*. Birkhäuser.

[@distler_garibaldi]: Distler, J., Garibaldi, S. (2010). There is no "Theory
of Everything" inside E8. *Communications in Mathematical Physics*, 298,
419–436. https://arxiv.org/abs/0905.2658

[@iochum2006]: Iochum, B., Jureit, J.H., Krajewski, T., Stephan, C.A.
(2006). Classification of finite spectral triples.
https://arxiv.org/abs/hep-th/0610040
