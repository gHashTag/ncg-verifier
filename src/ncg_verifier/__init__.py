"""
ncg_verifier — Formal verifier for noncommutative geometry spectral triples.

This package provides:
  - SpectralTriple abstract base class (spectral_triple.py)
  - Connes axiom checkers (axioms.py) [STUB: full implementation in M3, week 12]
  - Anti-numerology CI gate (anti_numerology.py) [IMPLEMENTED]
  - Atlas/model loader for YAML/JSON specs (atlas_loader.py) [STUB: M2, week 6]

Version: 0.1.0-alpha
Status:  Pre-alpha scaffold. The anti_numerology module is fully functional.
         All axiom checkers are stubs with clear NotImplementedError messages.

References:
  - Architecture: https://github.com/gHashTag/trinity-s3ai (V1_architecture.md)
  - JOSS paper draft: docs/joss_paper.md
  - Upstream gate: https://github.com/gHashTag/trinity-s3ai/blob/main/scripts/anti_numerology_gate.py
"""

__version__ = "0.1.0-alpha"
__author__ = "trinity-s3ai contributors"
__license__ = "MIT"

from ncg_verifier.anti_numerology import AntiNumerologyGate, FormulaResult, GateResult
from ncg_verifier.spectral_triple import SpectralTriple

__all__ = [
    "__version__",
    "SpectralTriple",
    "AntiNumerologyGate",
    "GateResult",
    "FormulaResult",
]
