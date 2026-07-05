# SST Canon v0.8.15 conversation-audit and patch recommendation

## Scope
Audited files:

- `/mnt/data/SST_CANON-v0.8.15.tex`
- `/mnt/data/SST_CANON-v0.8.15-research-track.tex`
- `/mnt/data/work_sst/SST-34_Hydrogen-Gravity.tex`
- `/mnt/data/work_sst/SST-73_A_Poisson-Type_Gravity_Program_from_Organized_Swirl_Transport.tex`
- `/mnt/data/work_sstcore/SSTcore-v0.8.13/src/potential_timefield.*`

## Verdict
v0.8.15 already contains the broad three-channel EM/gravity/optical/stress split. It does not yet fully contain three high-value conclusions from the conversation:

1. The explicit pressure--optical local locking relation
   \[
   \delta n_\gamma = -\frac{\delta p_{\mathrm{swirl}}}{\rhoF c^2}
   \]
   with passive stationary Euler validity conditions.

2. The Lighthill/no-monopole obstruction for SST-73 Candidate C:
   \[
   \partial_i\partial_j(\rhoF u_i u_j)=-\nabla^2p,
   \]
   so the transport-stress candidate is pressure-equivalent and has no smooth compact bulk monopole.

3. The dimensional correction for SST-73's practical axisymmetric proxy:
   \[
   [\alpha_{\grav}]=\mathrm{s^2}.
   \]

## Files produced
Use `patch_blocks_v0_8_15.tex` for copy-ready LaTeX insertion blocks.

Recommended insertions:

- Patch A into `SST_CANON-v0.8.15.tex`, subsection `Triadic Gravity-Response Corollary`, after:  
  `The three modes may share a common source state but are not mutually identical.`

- Patch B into `SST_CANON-v0.8.15-research-track.tex`, after the Flame/Photonless/Shell diagnostic section and before `Research Track: Atomic Gravity Closure and Condensate Coherence`.

- Patch C into `SST-73_A_Poisson-Type_Gravity_Program_from_Organized_Swirl_Transport.tex`, after the Candidate C tensor-law interpretation and after the practical axisymmetric proxy definition.

## Code-lag note
SSTcore 0.8.13 still exposes `compute_gravitational_potential_direct` and `compute_gravitational_potential_gradient` as gravitational-potential functions. The direct method implements a vorticity-dipole kernel, not a Newtonian Poisson gravity potential. This is a code/API patch target, not a canon text patch.
