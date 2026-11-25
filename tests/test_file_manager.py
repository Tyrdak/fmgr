"""Tests unitaires de FileManager : les 3 dependances sont simulees avec des mocks"""
from unittest.mock import MagicMock

import pytest

from fmgr_app.file_manager import FileManager
from fmgr_app.interfaces import FileSelection, FileSystem, UserInterface


@pytest.fixture
def selection():
    return MagicMock(spec=FileSelection)


@pytest.fixture
def fs():
    return MagicMock(spec=FileSystem)


@pytest.fixture
def ui():
    return MagicMock(spec=UserInterface)


@pytest.fixture
def manager(selection, fs, ui):
    return FileManager(selection, fs, ui)


def test_creation(manager):
    assert manager is not None
