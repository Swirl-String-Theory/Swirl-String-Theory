# SST v0.8.16 patch bundle

Generated for the uploaded v0.8.16 source set.

## Highest-priority patch
1. `SST-73_A_Poisson-Type_Gravity_Program_from_Organized_Swirl_Transport.patch`
   - Downgrades Candidate C from candidate monopole gravity law to local stress/pressure diagnostic.
   - Corrects the effective mass paragraph so the compact smooth stress integral is not described as a bulk mass law.
   - Keeps the useful no-monopole and alpha_grav dimensional notes already present in v0.8.16.

## Main canon patch
2. `SST_CANON-v0.8.16.patch`
   - Adds a short T-foliation vs local Swirl-Clock time remark.
   - Pressure is explicitly treated as an instantaneous constraint on Sigma_T, not as an operational signal channel.

## Research-track patch
3. `SST_CANON-v0.8.16-research-track.patch`
   - Links Route I of the Relativity Emergence Ladder to SST-63 + SST-23 + SST-56.

## SST-63 integration
4. `SST-63_Holograpic.patch`
   - Adds a section integrating SST-63 with SST-23 and SST-56.
   - Adds a line-piercing entropy bridge and explicitly labels it calibrated/research-track.
   - Adds bibitems for Unruh 1976, Fetter 2009, and Ricca--Moffatt.

## Optional cleanup
5. `SST-64_v2.patch`
   - Adds an SST-corpus status box clarifying that SST-64 is an effective covariant bridge, not a primitive-substrate derivation of EFE.
6. `SST-34_Hydrogen-Gravity.patch`
   - Adds a permanent exclusion note: direct vortex-line coupling is not far-field gravity.

## Suggested merge order
1. SST-73 cleanup.
2. Main canon T-foliation remark.
3. Research-track Route-I source integration.
4. SST-63 integration with SST-23/56.
5. Optional SST-64 and SST-34 notes.

