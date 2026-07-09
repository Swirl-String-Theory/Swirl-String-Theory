#!/usr/bin/env python3
"""Apply final notation hygiene patch (default v0.8.11)."""
import sys
from _paths import ROOT, SCRIPTS_DIR

MARKER = "v0.8.10 architecture"

MAIN_REPLACEMENTS = [
    (
        "        Older SST canon layers often used the triplet $(\\Gamma_0,\\rhoF,\\rc)$ as the primitive parameterization. In the present v0.8.1 architecture, Eq.~\\eqref{eq:rc_definition} and Eq.~\\eqref{eq:gamma0} show that this is a reparameterization of the present primitive set $(\\rhoF,\\vswirl,\\omega_c)$ rather than a distinct axiom.",
        "        Older SST canon layers often used the triplet $(\\Gamma_0,\\rhoF,\\rc)$ as the primitive parameterization. In the present v0.8.10 architecture, Eq.~\\eqref{eq:rc_definition} and Eq.~\\eqref{eq:gamma0} show that this is a reparameterization of the present primitive calibration set $(\\rhoF,\\vchar,\\omega_c)$ rather than a distinct axiom.",
    ),
    (
        "        Hence any dimensional SST quantity written in terms of $(\\Gamma_0,\\rhoF,\\rc)$ can be rewritten in terms of $(\\rhoF,\\vswirl,\\omega_c)$ with no new input.",
        "        Hence any dimensional SST quantity written in terms of $(\\Gamma_0,\\rhoF,\\rc)$ can be rewritten in terms of $(\\rhoF,\\vchar,\\omega_c)$ with no new calibration input.",
    ),
    (
        "        Within the primitive set $\\mathcal{P} = \\{\\rhoF, \\vswirl, \\omega_c\\}$, a characteristic force scale emerges naturally from the Compton energy stored over the canonical circulation cross-section. We define the \\emph{maximal swirl tension} as",
        "        Within the primitive calibration set $\\mathcal{P}_{\\mathrm{cal}} = \\{\\rhoF, \\vchar, \\omega_c\\}$, a characteristic force scale emerges naturally from the Compton energy stored over the canonical circulation cross-section. We define the \\emph{maximal swirl tension} as",
    ),
    (
        "        For any single-valued physical framing $U_{\\rm phys}$ of $K$ (the direction of the core\n        swirl velocity $\\vswirl$), the relative winding",
        "        For any single-valued physical framing $U_{\\rm phys}$ of $K$ (the direction of the local core\n        swirl-velocity field $\\uswirl$), the relative winding",
    ),
    (
        "                \\vswirl^{\\rm eff}\n                \\Bigr),",
        "                \\uswirl^{\\rm eff}\n                \\Bigr),",
    ),
    (
        "                \\item $\\rhoF^{\\rm eff}$ and $\\vswirl^{\\rm eff}$ are the coarse-grained medium parameters seen by the excitation.",
        "                \\item $\\rhoF^{\\rm eff}$ and $\\uswirl^{\\rm eff}$ are the coarse-grained medium density and effective local swirl-velocity field seen by the excitation.",
    ),
    (
        "            \\sqrt{1-\\frac{\\lVert\\mathbf{u}_{\\swirlarrow}\\rVert^2}{c^2}},\n            \\qquad\n            n_\\gamma=\\SwirlClock^{-1}.\n            }\n            \\label{eq:canonical_emg_clock_optical_closure}\n        \\end{align}\n        Photon phase therefore probes \\(n_\\gamma\\), while bulk matter probes Eq.~\\eqref{eq:canonical_sst_grav_force_density}. These are coupled through \\(\\mathbf{u}_{\\swirlarrow}\\), but they need not have identical spatial gradients.",
        "            \\sqrt{1-\\frac{\\lVert\\uswirl\\rVert^2}{c^2}},\n            \\qquad\n            n_\\gamma=\\SwirlClock^{-1}.\n            }\n            \\label{eq:canonical_emg_clock_optical_closure}\n        \\end{align}\n        Photon phase therefore probes \\(n_\\gamma\\), while bulk matter probes Eq.~\\eqref{eq:canonical_sst_grav_force_density}. These are coupled through \\(\\uswirl\\), but they need not have identical spatial gradients.",
    ),
    (
        "            \\frac{\\lVert\\vswirl\\rVert c^3 t_p^2}{\\rc M_e}",
        "            \\frac{\\vchar c^3 t_p^2}{\\rc M_e}",
    ),
    (
        "        At the canonical speed \\(\\lVert\\vswirl\\rVert=1.09384563\\times10^6\\,\\mathrm{m\\,s^{-1}}\\),\n        \\begin{align}\n            \\frac{1}{2}\\rhoF\\lVert\\vswirl\\rVert^2",
        "        At the canonical speed \\(\\vchar=1.09384563\\times10^6\\,\\mathrm{m\\,s^{-1}}\\),\n        \\begin{align}\n            \\frac{1}{2}\\rhoF\\vchar^2",
    ),
]

RT_REPLACEMENTS = [
    (
        "            {5\\lambda_c\\|\\vswirl\\|}.",
        "            {5\\lambda_c\\vchar}.",
    ),
    (
        "            5\\lambda_c\\|\\vswirl\\|\n            =",
        "            5\\lambda_c\\vchar\n            =",
    ),
    (
        "            2\\pi \\rc\\|\\vswirl\\|\n            =",
        "            2\\pi \\rc\\vchar\n            =",
    ),
    (
        "            \\frac{1}{2}\\rhoF\\|\\vswirl\\|^2",
        "            \\frac{1}{2}\\rhoF\\vchar^2",
    ),
    (
        "            \\rhocore\\|\\vswirl\\|^2",
        "            \\rhocore\\vchar^2",
    ),
    (
        "            \\rhocore\\|\\vswirl\\|^2\\pi\\rc^2",
        "            \\rhocore\\vchar^2\\pi\\rc^2",
    ),
    (
        "    =\\sqrt{1-\\frac{\\lVert\\vswirl\\rVert^2}{c^2}}.",
        "    =\\sqrt{1-\\frac{\\lVert\\uswirl(\\mathbf{x},t)\\rVert^2}{c^2}}.",
    ),
    (
        "    \\Gamma &= \\oint_C \\vswirl\\cdot d\\vec\\ell,\\label{eq:gamma_appendix}\\\\\n    \\mathcal H &= \\int_V \\vswirl\\cdot\\vec\\omega\\,d^3x,\\label{eq:helicity_appendix}\\\\\n    \\vec\\omega &= \\nabla\\times\\vswirl.\\label{eq:vorticity_appendix}",
        "    \\Gamma &= \\oint_C \\uswirl\\cdot d\\vec\\ell,\\label{eq:gamma_appendix}\\\\\n    \\mathcal H &= \\int_V \\uswirl\\cdot\\vec\\omega\\,d^3x,\\label{eq:helicity_appendix}\\\\\n    \\vec\\omega &= \\nabla\\times\\uswirl.\\label{eq:vorticity_appendix}",
    ),
    (
        "\\providecommand{\\vnorm}{\\lVert\\mathbf{v}_{\\!\\boldsymbol{\\circlearrowleft}}\\rVert}\n\\providecommand{\\rhoF}{\\rho_{\\!f}}",
        "\\providecommand{\\vnorm}{\\lVert\\mathbf{v}_{\\!\\boldsymbol{\\circlearrowleft}}\\rVert}\n\\providecommand{\\vchar}{v_{\\!\\boldsymbol{\\circlearrowleft}}^{\\ast}}\n\\providecommand{\\uswirl}{\\mathbf{u}_{\\!\\boldsymbol{\\circlearrowleft}}}\n\\providecommand{\\omegaswirl}{\\boldsymbol{\\omega}_{\\!\\boldsymbol{\\circlearrowleft}}}\n\\providecommand{\\rhoF}{\\rho_{\\!f}}",
    ),
    (
        "            \\vswirl\n        } .\n        \\label{eq:swirl_vector_potential_bridge}",
        "            \\uswirl(\\mathbf{x},t)\n        } .\n        \\label{eq:swirl_vector_potential_bridge}",
    ),
    (
        "    \\([(m_e/e)\\vswirl]={\\rm kg\\,C^{-1}}\\cdot{\\rm m\\,s^{-1}}\\), this equation\n    has the correct SI units.",
        "    \\([(m_e/e)\\uswirl]={\\rm kg\\,C^{-1}}\\cdot{\\rm m\\,s^{-1}}\\), this equation\n    has the correct SI units. This use of \\(\\uswirl(\\mathbf{x},t)\\) is intentional: the EM bridge is a local-field bridge, not a curl of the calibrated scalar speed \\(\\vchar\\).",
    ),
    (
        "            \\frac{\\partial\\vswirl}{\\partial t}",
        "            \\frac{\\partial\\uswirl(\\mathbf{x},t)}{\\partial t}",
    ),
    (
        "        \\vswirl\\cdot\\boldsymbol{\\omega}\\,d^3x.",
        "        \\uswirl\\cdot\\boldsymbol{\\omega}\\,d^3x.",
    ),
    (
        "        \\(\\mathbf{A}_{\\rm SI}=(m_e/e)\\vswirl\\) & Research Track, strong candidate \\\\",
        "        \\(\\mathbf{A}_{\\rm SI}=(m_e/e)\\uswirl(\\mathbf{x},t)\\) & Research Track, strong candidate \\\\",
    ),
]


def _apply_pairs(text: str, pairs: list[tuple[str, str]], strict: bool = False) -> str:
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
        elif strict and new not in text:
            raise SystemExit(f"missing expected block:\n{old[:100]}...")
    return text


def apply(version: str = "0.8.11") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    rt = ROOT / f"v{version}" / f"SST_CANON-v{version}-research-track.tex"
    mtext = main.read_text(encoding="utf-8")
    if MARKER in mtext:
        print(f"final hygiene patch already present in v{version}.")
        return
    mtext = _apply_pairs(mtext, MAIN_REPLACEMENTS, strict=True)
    rtext = _apply_pairs(rt.read_text(encoding="utf-8"), RT_REPLACEMENTS, strict=True)
    main.write_text(mtext, encoding="utf-8")
    rt.write_text(rtext, encoding="utf-8")
    print(f"final hygiene patch applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.11"
    apply(version)


if __name__ == "__main__":
    main()
