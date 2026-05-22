# Contributing to NCG-Verifier

Thank you for your interest in contributing! This project follows an open,
transparent development process. All contributions are welcome.

## How to Contribute

### Reporting Bugs

Open a GitHub issue at https://github.com/gHashTag/ncg-verifier/issues with:
- A clear description of the bug
- Steps to reproduce
- Expected vs. actual behavior
- Python version and OS

### Submitting a New NCG Model

NCG-Verifier is designed to verify any spectral triple model, not just H4/600-cell.
To submit a new model for the V3 Atlas:

1. Create a YAML model spec following the schema in `docs/joss_paper.md` (Section: Functionality).
2. Optionally include Coq source files (`.v`) with your model's formal proofs.
3. Open a pull request with:
   - Your `models/<model_name>.yaml`
   - A short description of the model and its physical motivation
   - Any known open axioms (axiom 5 is open for most discrete models — this is expected)

### Anti-Numerology Policy

**All formulas introduced in PRs must carry an approved honesty tag.**

The anti-numerology gate runs in CI and will block any PR containing an untagged
combination of φ, π, and e. Use one of the approved tags:

```coq
(* [phenomenological_fit] — empirical fit to PDG data *)
(* [NUMERICAL_FIT] — numeric fit from Python computation *)
(* [HONEST: <reason>] — explicit honest disclosure *)
(* [NCG_AXIOM] — axiom from NCG framework *)
(* [PHYSICAL_AXIOM] — input from experiment *)
(* [MATH_TODO] — mathematical gap to be proved later *)
(* [LIBRARY_GAP] — Coq library limitation *)
```

This is intentional and non-negotiable: honest classification of formulas is
the core purpose of this tool. A formula that is a numerical fit **is not wrong**
— it is just classified as NF, not R. Tag it honestly.

### Code Contributions

1. Fork the repository and create a feature branch.
2. Install the development dependencies: `pip install -e ".[dev]"`
3. Run the test suite: `pytest tests/ -v`
4. Run linting: `ruff check src/ tests/`
5. Run type checking: `mypy src/ncg_verifier/`
6. Submit a pull request.

#### Stub implementations

If you are implementing a stub module (see `docs/roadmap.md`), the implementation
must:
- Remove the `# STUB` comment from the relevant function
- Add at least two tests in `tests/` that verify the new functionality
- Update `docs/roadmap.md` to reflect the milestone progress
- Not change the interface of any existing function (backwards compatibility)

### Documentation Contributions

- The JOSS paper draft is in `docs/joss_paper.md`. Corrections to factual
  statements are welcome as PRs.
- The architecture spec is in `docs/roadmap.md`.
- For LaTeX/BibTeX changes, also update `docs/paper.bib`.

## Development Setup

```bash
git clone https://github.com/gHashTag/ncg-verifier
cd ncg-verifier
pip install -e ".[dev]"
pytest tests/ -v
```

Optional (for axiom checker development, M3+):
- Install [Coq / Rocq](https://coq.inria.fr/) ≥ 8.20.1
- Install [coq-interval](https://coqinterval.gitlabpages.inria.fr/) ≥ 4.11

## Code Style

- Python: formatted with [ruff](https://docs.astral.sh/ruff/), line length 88.
- Docstrings: NumPy style.
- Type annotations: required for all public functions.
- Stub functions: must have a `# STUB: full implementation in milestone M<N> (week <W>)` comment.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
Please read it before participating.

## Questions?

Open a GitHub Discussion or email the maintainers listed in `pyproject.toml`.
