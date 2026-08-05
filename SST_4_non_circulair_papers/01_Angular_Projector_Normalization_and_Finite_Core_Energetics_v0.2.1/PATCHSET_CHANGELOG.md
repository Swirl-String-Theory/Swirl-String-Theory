# Patchset changelog — FINAL

Changes relative to the uploaded four-patch set:

1. Replaced the unsupported strict curvature `lower bound` with an epistemically
   guarded `optimistic lower estimate`.
2. Filled the provenance fields supported by `ideal_favorites.txt` and the
   historical Knot Atlas record.
3. Replaced `redistributed verbatim` with a payload/header distinction.
4. Recorded the unresolved file-specific licence and public-redistribution
   status rather than inventing terms.
5. Replaced the non-idempotent `sha256sum *` workflow with a cross-platform
   deterministic manifest builder.
6. Added a release finalizer for the internal v0.2.1 version and source filename.
7. Added a machine-checkable release verifier with optional LaTeX compilation.
