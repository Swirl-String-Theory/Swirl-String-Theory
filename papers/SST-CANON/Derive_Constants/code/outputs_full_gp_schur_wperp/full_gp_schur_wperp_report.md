# Full-field GP Schur proxy for w_perp

Hessians:
\[
H_{00}=1.36488803897,\qquad H_{\perp\perp}=9.09337339724.
\]

Measured:
\[
w_\perp=6.66235847749.
\]

Then:
\[
\sigma=3+rac23w_\perp=7.44157231833,
\qquad
c_2=0.465098269895.
\]

Target:
\[
w_\perp=1,\qquad c_2=11/48=0.229166666667.
\]

Status: `OPEN_GATE_FULL_FIELD_PROXY_NOT_EQUAL_1`.

This is a finite-grid full-field relaxation proxy.  It closes the gate only if
\(w_\perp	o1\) under grid, radius, boundary, and relaxation convergence.
