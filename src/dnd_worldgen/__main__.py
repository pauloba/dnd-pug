"""Allow running the package with ``python -m dnd_worldgen``."""

import sys

from dnd_worldgen.cli import main

if __name__ == "__main__":
    sys.exit(main())
