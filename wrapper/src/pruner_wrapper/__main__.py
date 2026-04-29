"""Entry-point — `python -m pruner_wrapper`."""

from __future__ import annotations

import sys

from pruner_wrapper.cli import main


def run() -> None:
    sys.exit(main())


if __name__ == "__main__":  # pragma: no cover
    run()
