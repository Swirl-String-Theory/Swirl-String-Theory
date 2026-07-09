"""Shared path constants for been_processed build scripts."""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
