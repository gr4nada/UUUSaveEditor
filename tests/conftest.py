# tests/conftest.py
import os, json, copy, logging
import pytest

logger = logging.getLogger("tests.conftest")
_FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample_save.json")


@pytest.fixture
def sample_save_path():
    return _FIXTURE


@pytest.fixture
def sample_save(sample_save_path):
    with open(sample_save_path, encoding="utf-8") as f:
        data = json.load(f)
    return copy.deepcopy(data)


@pytest.fixture
def save_game(sample_save):
    from src.core.save_model import SaveGame
    return SaveGame(sample_save)


@pytest.fixture
def player(save_game):
    return save_game.player
