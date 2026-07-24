#!/usr/bin/env python3
"""Unit tests for v0.8.27 hygiene transforms (no full edition rebuild)."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS.parent))
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location(
    "apply_v0827", SCRIPTS / "apply_v0827.py"
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class TestV0827Hygiene(unittest.TestCase):
    def test_strip_commented_duplicate_labels(self) -> None:
        sample = (
            "%        \\label{sec:consistency}\n"
            "\\section{Consistency}\n"
            "    \\label{sec:consistency}\n"
            "%        \\label{sec:delay}\n"
            "\\section{Delay}\n"
            "    \\label{sec:delay}\n"
            "%        \\label{sec:atomic}\n"
            "\\section{Atomic}\n"
            "    \\label{sec:atomic}\n"
            "%        \\label{sec:spectroscopy}\n"
            "\\section{Spectroscopy}\n"
            "    \\label{sec:spectroscopy}\n"
            "%        \\label{sec:unification}\n"
            "\\section{Unification}\n"
            "    \\label{sec:unification}\n"
        )
        out = mod.strip_commented_duplicate_labels(sample)
        self.assertNotIn("%        \\label{sec:consistency}", out)
        self.assertIn("    \\label{sec:consistency}", out)
        self.assertEqual(out.count("\\label{sec:delay}"), 1)

    def test_stub_rt_keeps_quark_module(self) -> None:
        rt = (
            "\\textbf{[CRITICAL NOTE] (duplication guard):} several subsections of this part "
            "(\\emph{Thermodynamic Radiation Interface}, \\emph{Minimal Coupling Interface to QED}, "
            "\\emph{Ribbon-Invariant Chirality Refinement}, \\emph{Particle-Candidate Mapping Layer}, "
            "\\emph{Hydrodynamic Exchange and the Pauli Barrier}, \\emph{Numerical Benchmark Layer}, "
            "\\emph{Gauge-Sector Roadmap}) currently still have full-text counterparts inside the main "
            "canon (Selective Recovery layer). Until de-duplication is executed, the main-canon "
            "versions are authoritative (Level~1 of the source hierarchy) and any label divergence "
            "must be resolved in favour of the main canon.\n"
            "\\subsection{Thermodynamic Radiation Interface}\nFULL1\n"
            "\\subsection{Minimal Coupling Interface to QED}\nFULL2\n"
            "\\subsection{Ribbon-Invariant Chirality Refinement}\nFULL3\n"
            "\\subsection{Particle-Candidate Mapping Layer}\nFULL4\n"
            "\\subsection{Quark-Like Twist Knots as Quasi-Unknot Defects}\nKEEP\n"
            "\\subsection{Hydrodynamic Exchange and the Pauli Barrier}\nFULL5\n"
            "\\subsection{Numerical Benchmark Layer}\n"
            "predictive candidate\n"
            "\\subsection{Helicity-by-base archive (diagnostic layer)}\nKEEP2\n"
            "\\subsection{Gauge-Sector Roadmap}\nFULL6\n"
            "\\section{Dark-sector and galactic canonization execution package (v0.8.x)}\nKEEP3\n"
        )
        out = mod.stub_rt_duplicates(rt)
        self.assertIn("duplication resolved in v0.8.27", out)
        self.assertIn("Quark-Like Twist Knots", out)
        self.assertIn("KEEP", out)
        self.assertNotIn("FULL1", out)
        self.assertNotIn("predictive candidate", out)
        self.assertIn("subsec:integration_thermo", out)

    def test_insert_canonversion(self) -> None:
        text = "\\newcommand{\\papertitle}{Swirl-String-Theory Canon-v0.8.26}\n"
        out = mod.insert_canonversion_macro(text)
        self.assertIn("\\newcommand{\\canonversion}{0.8.27}", out)


if __name__ == "__main__":
    unittest.main()
