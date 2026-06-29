#!/usr/bin/env python3
"""Apply CALIBRATED / circularity-honesty audit to v0.8.5 canon copies."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
    ROOT / "been_processed" / "v0.8.5" / "SST_CANON-v0.8.5.tex",
]

REPLACEMENTS = [
    (
        r"\textbf{[DERIVED] Empirical closure}: Within the present canonical calibration, this connects the characteristic swirl velocity to the fine-structure constant.",
        r"\textbf{[CALIBRATED] Empirical closure}: Within the present canonical calibration, this fixes the characteristic swirl velocity \emph{from} the fine-structure constant ($\vnorm=\alpha c/2$); $\alpha$ is an input here, not an output.",
    ),
    (
        r"\subsubsection{Strongest non-circular identity: the Rydberg constant}",
        r"\subsubsection{Rydberg consistency identity}",
    ),
    (
        r"\textbf{[DERIVED]} The Rydberg constant is recoverable directly from the three SST primitives without $e$, $\varepsilon_0$, or $m_e$ as explicit input:",
        r"\textbf{[CALIBRATED]} The Rydberg constant is recoverable from the three SST primitives without $e$, $\varepsilon_0$, or $m_e$ appearing \emph{explicitly}:",
    ),
    (
        r"This is the canonical benchmark for the internal non-redundancy of the primitive set. Combining Eq.~\eqref{eq:Rydberg_SST} with Eq.~\eqref{eq:Fmax_def} yields the compact relation",
        r"This is a benchmark for the internal non-redundancy of the primitive set. \textbf{[CRITICAL NOTE]} Substituting the canonical definitions $\vnorm=\alpha c/2$ and $\rc=\vnorm/\omega_c=\alpha\hbar/(2m_ec)$ reduces Eq.~\eqref{eq:Rydberg_SST} \emph{exactly} to the standard $R_\infty=\alpha^2 m_e c/(4\pi\hbar)$ (verified to machine precision): $m_e$ is hidden inside $\rc$ and $\alpha$ inside both $\vnorm$ and $\rc$. The identity is therefore a consistency check, not an independent non-circular derivation of $R_\infty$. Combining Eq.~\eqref{eq:Rydberg_SST} with Eq.~\eqref{eq:Fmax_def} yields the compact relation",
    ),
    (
        r"The quantity $F_{\rm swirl}^{\max}$ admits three distinct physical interpretations, each arising from a different sector of physics. Their numerical coincidence within the canonical constant chain is a non-trivial coherence result.",
        r"The quantity $F_{\rm swirl}^{\max}$ admits three distinct physical interpretations, each arising from a different sector of physics. \textbf{[CRITICAL NOTE]} These three values are algebraically equivalent expressions built from the same primitive set $\{\alpha,m_e,\hbar,c\}$; their numerical agreement is an \emph{identity}, not an independent coincidence, and is not on its own confirmation of the theory.",
    ),
    (
        r"\textbf{[DERIVED]} The maximal Coulomb repulsion at the canonical circulation scale is exactly four times $F_{\rm swirl}^{\max}$. The factor of four matches the denominator structure of Eq.~\eqref{eq:Fgr} and is not numerically coincidental within the canonical chain.",
        r"\textbf{[CALIBRATED]} The maximal Coulomb repulsion at the canonical circulation scale is exactly four times $F_{\rm swirl}^{\max}$. \textbf{[CRITICAL NOTE]} The factor of four is an arithmetic identity once $\vnorm=\alpha c/2$ is adopted (the $4/\alpha$ gate); it is a self-consistency of the calibrated chain, not an independent prediction.",
    ),
]

OLD_EPISTEMIC = """        The only primary status labels used in the present Canon are:
        \\begin{itemize}
            \\item \\textbf{[ORTHODOX]} --- established in standard physics or mathematics
            \\item \\textbf{[DERIVED]} --- obtained internally from the present SST assumptions, definitions, or closures
            \\item \\textbf{[SPECULATIVE]} --- conjectural SST extension, interpretation, or unverified identification
        \\end{itemize}"""

NEW_EPISTEMIC = """        The primary status labels used in the present Canon are:
        \\begin{itemize}
            \\item \\textbf{[ORTHODOX]} --- established in standard physics or mathematics
            \\item \\textbf{[DERIVED]} --- obtained internally from the present SST assumptions, definitions, or closures, \\emph{without re-using the target quantity as an input}
            \\item \\textbf{[CALIBRATED]} --- fixed by, or algebraically equivalent to, a measured constant ($\\alpha$, $m_e$, $\\hbar$, $R_\\infty$, \\dots) that enters through the primitive set; numerically exact but not an independent prediction
            \\item \\textbf{[CONDITIONAL]} --- follows only if a stated, not-yet-proven premise holds (e.g.\\ an open lemma or selection rule)
            \\item \\textbf{[SPECULATIVE]} --- conjectural SST extension, interpretation, or unverified identification
        \\end{itemize}
        A \\textbf{[CRITICAL NOTE]} editorial overlay flags a circularity risk, dimensional issue, or reviewer vulnerability on any of the above."""


def patch(text: str) -> str:
    if "[CALIBRATED] Empirical closure" in text and NEW_EPISTEMIC in text:
        return text
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise SystemExit(f"Missing expected block:\n{old[:120]}...")
    if NEW_EPISTEMIC in text:
        return text
    if OLD_EPISTEMIC not in text:
        raise SystemExit("Epistemic status block not found")
    return text.replace(OLD_EPISTEMIC, NEW_EPISTEMIC, 1)


def main():
    for path in TARGETS:
        if not path.exists():
            print(f"skip missing {path}")
            continue
        text = path.read_text(encoding="utf-8")
        path.write_text(patch(text), encoding="utf-8")
        print(f"CALIBRATED audit applied: {path}")


if __name__ == "__main__":
    main()
