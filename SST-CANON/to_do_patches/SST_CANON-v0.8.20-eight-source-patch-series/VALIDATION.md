# Validation report

- Base main SHA-256: `1e99401f690c7d65a6c9736167b171736a29d0f267f87088cefb92f9e9f77eb4`
- Base Research Track SHA-256: `9c65a2c4d6115e4b7fb5a846ea03cca424c6ba5df939d021b25fe1f0c1a352b2`
- Final main SHA-256: `390160d5c30aa04ccf679f577a321a4aab81f024b60d30a685b86d8076bb4c7c`
- Final Research Track SHA-256: `dd9c94e3e62fae7055fd3c3b52e624e63280b34928e60375f8c99a217da5e9e4`
- Final integrated PDF SHA-256: `1d453ec1b3fe87d0f0a3554a71c413580b62afcd6608c1d9308a3e32abcdc185`

Checks completed:

1. Patches `0001`–`0005` reproduce the previously validated Round-1 endpoint byte-for-byte.
2. The integrated main Canon compiled successfully after patches `0006`, `0007`, and `0008`.
3. The main Canon inputs and thereby compiles the Research-Track fragment.
4. Independent clean application of all eight patches produced byte-identical final `.tex` files.
5. No new duplicate LaTeX labels or bibliography keys were introduced relative to the uploaded base.
6. Patch `0008` repairs the previously empty/misplaced contact-map heading and leaves its scientific content in the correct subsection.
7. The packaged Bash application script reproduced the byte-identical final files from the packaged base.
8. Targeted PDF pages 72--77 and 108--120, containing the new Round-2 sections, were rendered and visually inspected for clipping, overlap, and broken glyphs.

The Research-Track file begins with `\section` and has no standalone preamble; a direct standalone compile is therefore neither expected nor claimed.
