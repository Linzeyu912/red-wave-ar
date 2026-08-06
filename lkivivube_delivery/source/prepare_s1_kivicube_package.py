"""Legacy S1 package entry point.

The original photo-plane implementation was retired by ADR-0006.  Keep this
file only so existing commands continue to work, while delegating all package
generation to the unified static-ground pipeline for the nine model units.
"""

from __future__ import annotations

from prepare_all_kivicube_packages import main


if __name__ == "__main__":
    main()
