"""Smoke tests: the package imports and exposes its entry points."""

import dnd_worldgen
from dnd_worldgen import cli


def test_package_has_version() -> None:
    assert dnd_worldgen.__version__


def test_cli_entry_point_exists() -> None:
    assert callable(cli.main)
