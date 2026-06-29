#!/usr/bin/env python3
"""Backward-compatible wrapper; use canon_edition.apply_metadata instead."""
from canon_edition import apply_metadata


def main() -> None:
    apply_metadata("0.8.5")
    print("v0.8.5 metadata applied.")


if __name__ == "__main__":
    main()
