"""
spectral_triple.py — Abstract base class for a Connes spectral triple.

A *real spectral triple* (A, H, D; J, γ) consists of:
  A — a unital *-algebra represented on H
  H — a Hilbert space
  D — a self-adjoint operator on H (the Dirac operator)
  J — an anti-linear isometry J: H → H (the real structure)
  γ — a self-adjoint unitary on H (the chirality/grading operator)

These satisfy Connes' seven axioms (hep-th/9603053). This module provides
the Python interface; axiom verification is in axioms.py.

References:
  Connes (1996): https://arxiv.org/abs/hep-th/9603053
  Gracia-Bondía, Várilly, Figueroa (2001): Elements of Noncommutative Geometry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SpectralTriple(ABC):
    """
    Abstract base class representing a real spectral triple (A, H, D; J, γ).

    Subclasses must implement all abstract properties. The concrete objects
    returned by these properties can be any Python representation appropriate
    to the implementation (numpy arrays, symbolic matrices, metadata dicts, etc.).

    The canonical concrete implementation shipped with NCG-Verifier wraps
    the H4/600-cell model from trinity-s3ai as an illustration of a spectral
    triple that FAILS the first-order condition (axiom 5) — see NGT4 in
    proofs/trinity/NoGoTheorems.v.

    Design note (alpha): In v0.1.0-alpha, this class carries the interface
    contract. Operator-algebraic functionality (boundedness checks, commutator
    computations) will be added in M3 (week 12) when the Coq axiom checker
    module is integrated.
    """

    # ------------------------------------------------------------------
    # Core components (abstract properties)
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def algebra(self) -> Any:
        """
        The unital *-algebra A represented on H.

        In the finite / almost-commutative setting this is typically a
        direct sum of matrix algebras, e.g. ℂ ⊕ ℍ ⊕ M₃(ℂ) for the
        Standard Model algebra. Return value format is implementation-defined.
        """

    @property
    @abstractmethod
    def hilbert_space(self) -> Any:
        """
        The Hilbert space H on which A and D act.

        In the finite-dimensional case this is ℂⁿ. Return value may be an
        integer dimension, a numpy array representing a basis, or a metadata
        dict describing the space.
        """

    @property
    @abstractmethod
    def dirac(self) -> Any:
        """
        The Dirac operator D: a self-adjoint operator on H satisfying
        the compact resolvent condition (axiom 1) and the first-order
        condition [[D, a], b°] = 0 for all a ∈ A, b° ∈ J A J⁻¹ (axiom 5).

        Axiom 5 is the primary structural obstruction for discrete NCG models;
        the H4/600-cell model fails it (NGT4 in trinity-s3ai).
        """

    @property
    @abstractmethod
    def gamma(self) -> Any:
        """
        The chirality (grading) operator γ: a self-adjoint unitary on H.

        Must satisfy:
          γ² = 1          (axiom 6 / orientation)
          γD = -Dγ        (γ anticommutes with D)
          γa = aγ         for all a ∈ A (γ commutes with the algebra)
          γJ = ±Jγ        (sign depends on KO-dimension)
        """

    @property
    @abstractmethod
    def J(self) -> Any:  # noqa: N802  (J is conventional name in NCG)
        """
        The real structure J: an anti-linear isometry J: H → H.

        Must satisfy:
          J² = ε · 1      where ε ∈ {+1, -1} depends on KO-dimension
          JD = ε' DJ      where ε' ∈ {+1, -1}
          Jγ = ε'' γJ     where ε'' ∈ {+1, -1}
          [a, JbJ⁻¹] = 0 for all a, b ∈ A  (axiom 4 / reality)

        The sign triple (ε, ε', ε'') determines the KO-dimension mod 8.
        For KO-dim=6: (ε, ε', ε'') = (+1, -1, +1).
        """

    # ------------------------------------------------------------------
    # Derived / optional attributes
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Human-readable name for this spectral triple. Override in subclasses."""
        return self.__class__.__name__

    @property
    def ko_dimension(self) -> int | None:
        """
        KO-dimension mod 8 of this spectral triple, if known.
        Returns None if not specified; the axiom checker will attempt to
        determine it from the sign triple (ε, ε', ε'').
        """
        return None

    @property
    def sign_triple(self) -> tuple[int, int, int] | None:
        """
        The sign triple (ε, ε', ε'') for the real structure J.
        ε   = sign of J²
        ε'  = sign of JD - ε'DJ  (JD = ε'DJ)
        ε'' = sign of Jγ - ε''γJ (Jγ = ε''γJ)
        Returns None if not specified.
        """
        return None

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        ko = self.ko_dimension
        ko_str = f", KO-dim={ko}" if ko is not None else ""
        return f"<SpectralTriple '{self.name}'{ko_str}>"

    def summary(self) -> str:
        """Return a human-readable summary of this spectral triple's components."""
        lines = [
            f"Spectral Triple: {self.name}",
            f"  KO-dimension : {self.ko_dimension}",
            f"  Sign triple  : {self.sign_triple}",
            f"  Algebra (A)  : {self.algebra}",
            f"  Hilbert sp.  : {self.hilbert_space}",
            f"  Dirac (D)    : {self.dirac}",
            f"  Chirality γ  : {self.gamma}",
            f"  Real struct J: {self.J}",
        ]
        return "\n".join(lines)
