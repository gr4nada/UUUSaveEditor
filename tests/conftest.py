# tests/conftest.py
import os
import json
import copy
import logging
import pytest

logger = logging.getLogger("tests.conftest")

@pytest.fixture
def sample_save_path():
    """
    Returns the absolute file system path to the baseline sample_save.json fixture.
    """
    return os.path.join(os.path.dirname(__file__), "fixtures", "sample_save.json")

@pytest.fixture
def sample_save(sample_save_path):
    """
    Provides a clean, isolated deep copy of the save data stream for each independent test execution.
    Prevents cross-test environment contamination from mutations or cheats.
    """
    with open(sample_save_path, "r", encoding="utf-8") as file_stream:
        data = json.load(file_stream)
    return copy.deepcopy(data)