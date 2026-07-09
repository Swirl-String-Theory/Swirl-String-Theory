#!/usr/bin/env python3
"""Insert triadic gravity-response blocks (default v0.8.9)."""
import sys
from _paths import ROOT, SCRIPTS_DIR

MAIN_BLOCK = ROOT / "blocks" / "triadic_gravity_response_main_block.tex"
RT_BLOCK = ROOT / "blocks" / "triadic_gravity_response_rt_block.tex"
MAIN_ANCHOR = (
    "        The electromagnetic projection is controlled by topological flux impulse "
    "\\(\\Delta\\Phi_{\\swirlarrow}=\\Phi_0\\Delta N\\). The gravitational projection is controlled by "
    "\\(\\rhoM\\mathbf{g}_{\\swirlarrow}+\\nabla\\cdot\\boldsymbol{\\sigma}^{\\mathrm{swirl}}\\) with weak closure "
    "\\(\\nabla\\cdot\\mathbf{g}_{\\swirlarrow}=-4\\pi G_{\\mathrm{swirl}}\\rhoM\\). Both recover their orthodox limits when the SST projection channels vanish.\n\n\n"
)
RT_ANCHOR = (
    "        Negative-temperature swirl entropy & Speculative Research Track \\\\\n"
    "        \\hline\n"
    "    \\end{tabular}\n"
    "\\end{center}"
)
MAIN_MARKER = "subsec:triadic_gravity_response_corollary"
RT_MARKER = "sec:rt_flame_photonless_shell"


def apply(version: str = "0.8.9") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    rt = ROOT / f"v{version}" / f"SST_CANON-v{version}-research-track.tex"

    mtext = main.read_text(encoding="utf-8")
    if MAIN_MARKER not in mtext:
        block = MAIN_BLOCK.read_text(encoding="utf-8")
        if MAIN_ANCHOR not in mtext:
            raise SystemExit(f"main anchor not found in v{version}")
        mtext = mtext.replace(MAIN_ANCHOR, MAIN_ANCHOR + block + "\n", 1)
        main.write_text(mtext, encoding="utf-8")
        print(f"triadic gravity main block applied to v{version}.")
    else:
        print(f"triadic gravity main block already present in v{version}.")

    rtext = rt.read_text(encoding="utf-8")
    if RT_MARKER not in rtext:
        block = RT_BLOCK.read_text(encoding="utf-8")
        idx = rtext.rfind(RT_ANCHOR)
        if idx == -1:
            raise SystemExit(f"research-track anchor not found in v{version}")
        insert_at = idx + len(RT_ANCHOR)
        rtext = rtext[:insert_at] + block + rtext[insert_at:]
        rt.write_text(rtext, encoding="utf-8")
        print(f"triadic gravity research-track block applied to v{version}.")
    else:
        print(f"triadic gravity research-track block already present in v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.9"
    apply(version)


if __name__ == "__main__":
    main()
