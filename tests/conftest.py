# tests/conftest.py
import os
import json
import copy
import pytest

@pytest.fixture
def sample_save_path():
    """Retorna o caminho absoluto para o ficheiro sample_save.json real."""
    return os.path.join(os.path.dirname(__file__), "fixtures", "sample_save.json")

@pytest.fixture
def sample_save(sample_save_path):
    """Fornece uma cópia limpa e isolada dos dados de save para cada teste."""
    with open(sample_save_path, "r", encoding="utf-8") as file_stream:
        data = json.load(file_stream)
    return copy.deepcopy(data)