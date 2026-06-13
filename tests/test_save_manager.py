# tests/test_save_manager.py
"""
Cobertura para src/core/save_manager.py — load_save, save_game_data e o
backup automático (backup_save) introduzido para reduzir o risco de
corrupção de save ao gravar.
"""
import gzip
import json
import os

import pytest

import src.core.save_manager as sm


@pytest.fixture
def saves_dir(tmp_path, monkeypatch):
    """Redireciona SAVES_DIR para um diretório temporário isolado."""
    d = tmp_path / "saves"
    d.mkdir()
    monkeypatch.setattr(sm, "SAVES_DIR", str(d))
    return str(d)


def _write_slot(saves_dir, slot, data):
    path = os.path.join(saves_dir, f"slot{slot}.json.gz")
    with gzip.open(path, "wb") as f:
        f.write(json.dumps(data).encode("utf-8"))
    return path


def _read_slot(saves_dir, slot):
    path = os.path.join(saves_dir, f"slot{slot}.json.gz")
    with gzip.open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


def _backup_files(saves_dir, slot=None):
    backups_dir = os.path.join(saves_dir, "backups")
    if not os.path.isdir(backups_dir):
        return []
    files = os.listdir(backups_dir)
    if slot is not None:
        files = [f for f in files if f.startswith(f"slot{slot}_")]
    return files


# ---------------------------------------------------------------------------
# load_save
# ---------------------------------------------------------------------------

def test_load_save_missing_file_raises(saves_dir):
    with pytest.raises(FileNotFoundError):
        sm.load_save(0)


def test_load_save_reads_existing_slot(saves_dir):
    _write_slot(saves_dir, 0, {"hello": "world"})
    assert sm.load_save(0) == {"hello": "world"}


def test_load_save_invalid_json_raises_value_error(saves_dir):
    path = os.path.join(saves_dir, "slot0.json.gz")
    with gzip.open(path, "wb") as f:
        f.write(b"{not valid json")

    with pytest.raises(ValueError):
        sm.load_save(0)


# ---------------------------------------------------------------------------
# save_game_data — escrita básica
# ---------------------------------------------------------------------------

def test_save_game_data_writes_readable_gzip_json(saves_dir):
    sm.save_game_data(0, {"a": 1})
    assert _read_slot(saves_dir, 0) == {"a": 1}


def test_save_game_data_overwrites_existing_slot(saves_dir):
    _write_slot(saves_dir, 0, {"a": 1})
    sm.save_game_data(0, {"a": 2})
    assert _read_slot(saves_dir, 0) == {"a": 2}


def test_save_game_data_creates_file_for_new_slot(saves_dir):
    sm.save_game_data(5, {"new": True})
    assert os.path.exists(os.path.join(saves_dir, "slot5.json.gz"))


# ---------------------------------------------------------------------------
# backup_save — chamado automaticamente por save_game_data
# ---------------------------------------------------------------------------

def test_backup_save_no_existing_file_returns_none(saves_dir):
    assert sm.backup_save(0) is None
    assert _backup_files(saves_dir) == []


def test_backup_save_copies_current_file(saves_dir):
    _write_slot(saves_dir, 0, {"original": True})

    backup_path = sm.backup_save(0)

    assert backup_path is not None
    assert os.path.exists(backup_path)
    with gzip.open(backup_path, "rb") as f:
        assert json.loads(f.read().decode("utf-8")) == {"original": True}


def test_backup_save_filename_includes_slot_number(saves_dir):
    _write_slot(saves_dir, 3, {"x": 1})
    backup_path = sm.backup_save(3)
    assert os.path.basename(backup_path).startswith("slot3_")


def test_save_game_data_creates_backup_of_previous_content(saves_dir):
    """
    O cenário principal: salvar deve preservar o conteúdo ANTERIOR em
    backups/ antes de sobrescrever — essa é a rede de segurança contra
    corrupção introduzida por uma edição ruim.
    """
    _write_slot(saves_dir, 0, {"version": "before"})

    sm.save_game_data(0, {"version": "after"})

    # Arquivo principal tem o conteúdo novo
    assert _read_slot(saves_dir, 0) == {"version": "after"}

    # Backup tem o conteúdo ANTIGO
    backups = _backup_files(saves_dir, slot=0)
    assert len(backups) == 1
    backup_path = os.path.join(saves_dir, "backups", backups[0])
    with gzip.open(backup_path, "rb") as f:
        assert json.loads(f.read().decode("utf-8")) == {"version": "before"}


def test_save_game_data_first_save_creates_no_backup(saves_dir):
    """Primeiro save de um slot novo não tem nada para fazer backup."""
    sm.save_game_data(7, {"first": True})
    assert _backup_files(saves_dir, slot=7) == []


def test_save_game_data_does_not_fail_if_backup_dir_uncreatable(saves_dir, monkeypatch):
    """
    Se o backup falhar por qualquer motivo de I/O, save_game_data ainda
    deve concluir a escrita do save — perder o backup é preferível a
    impedir o usuário de salvar.
    """
    _write_slot(saves_dir, 0, {"version": "before"})

    def boom(*a, **k):
        raise OSError("disk full")
    monkeypatch.setattr(sm.os, "makedirs", boom)

    sm.save_game_data(0, {"version": "after"})

    assert _read_slot(saves_dir, 0) == {"version": "after"}


def test_multiple_saves_create_multiple_backups(saves_dir):
    _write_slot(saves_dir, 0, {"v": 0})

    for i in range(1, 4):
        sm.save_game_data(0, {"v": i})

    # 3 saves sobre o conteúdo original => 3 backups (v0, v1, v2)
    backups = _backup_files(saves_dir, slot=0)
    assert len(backups) == 3


def test_backups_for_different_slots_do_not_mix(saves_dir):
    _write_slot(saves_dir, 0, {"slot": 0})
    _write_slot(saves_dir, 1, {"slot": 1})

    sm.save_game_data(0, {"slot": 0, "v": 2})
    sm.save_game_data(1, {"slot": 1, "v": 2})

    assert len(_backup_files(saves_dir, slot=0)) == 1
    assert len(_backup_files(saves_dir, slot=1)) == 1


# ---------------------------------------------------------------------------
# Pruning de backups antigos
# ---------------------------------------------------------------------------

def test_old_backups_are_pruned_beyond_limit(saves_dir, monkeypatch):
    monkeypatch.setattr(sm, "MAX_BACKUPS_PER_SLOT", 3)
    _write_slot(saves_dir, 0, {"v": 0})

    for i in range(1, 6):  # 5 saves => 5 backups gerados, mas só 3 mantidos
        sm.save_game_data(0, {"v": i})

    backups = _backup_files(saves_dir, slot=0)
    assert len(backups) == 3


def test_pruning_keeps_most_recent_backups(saves_dir, monkeypatch):
    monkeypatch.setattr(sm, "MAX_BACKUPS_PER_SLOT", 2)
    _write_slot(saves_dir, 0, {"v": 0})

    for i in range(1, 5):
        sm.save_game_data(0, {"v": i})

    # Os backups remanescentes devem corresponder aos dois saves mais recentes
    # (conteúdo "v": 2 e "v": 3 — penúltimo e antepenúltimo valor antes da sobrescrita final)
    backups_dir = os.path.join(saves_dir, "backups")
    contents = []
    for f in _backup_files(saves_dir, slot=0):
        with gzip.open(os.path.join(backups_dir, f), "rb") as fh:
            contents.append(json.loads(fh.read().decode("utf-8"))["v"])

    assert sorted(contents) == [2, 3]
