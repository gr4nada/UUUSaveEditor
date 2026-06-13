# tests/test_save_controller.py
"""
Cobertura para src/core/save_controller.py — SaveController e SavePayload.

`load`/`save_game_data` (I/O em disco) são substituídos via monkeypatch
para que os testes operem inteiramente em memória sobre `sample_save`.
"""
import copy
import json
import logging

import pytest

import src.core.save_controller as sc
from src.core.save_controller import SaveController, SavePayload
from src.core.save_model import SaveGame
from src.core.character import get_character_summary
from src.core.database.quests import QUEST_FLAGS

logger = logging.getLogger("tests.test_save_controller")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _controller_with_save(sample_save, monkeypatch, captured_writes=None):
    """
    Retorna um SaveController já carregado com `sample_save`, sem I/O real:
    - load_save() é substituído para devolver `sample_save` (deepcopy)
    - save_game_data() é substituído para gravar em `captured_writes` (se dado)
    """
    data = copy.deepcopy(sample_save)

    monkeypatch.setattr(sc, "load_save", lambda slot: data)

    def fake_save(slot, payload_data):
        if captured_writes is not None:
            captured_writes.append((slot, copy.deepcopy(payload_data)))

    monkeypatch.setattr(sc, "save_game_data", fake_save)

    controller = SaveController()
    controller.load(0)
    return controller, data


def _base_payload(controller, **overrides) -> SavePayload:
    """Monta um SavePayload neutro a partir do estado atual (round-trip sem mudanças)."""
    summary = get_character_summary(controller.raw_save)
    payload = SavePayload(
        attrs=summary["attributes"],
        skills=summary["skills"],
        flags=controller.save_game.player.get_quest_flags_by_name(),
        cast_spells=[],
    )
    for k, v in overrides.items():
        setattr(payload, k, v)
    return payload


# ---------------------------------------------------------------------------
# Estado inicial / is_loaded
# ---------------------------------------------------------------------------

def test_controller_starts_unloaded():
    controller = SaveController()
    assert controller.is_loaded is False
    assert controller.raw_save is None
    assert controller.save_game is None


def test_is_loaded_false_before_load_even_with_partial_state():
    """is_loaded depende de save_game, não apenas de raw_save estar setado manualmente."""
    controller = SaveController()
    controller.raw_save = {"playerData": {}}
    assert controller.is_loaded is False


# ---------------------------------------------------------------------------
# load()
# ---------------------------------------------------------------------------

def test_load_sets_state_and_returns_save_game(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)

    assert controller.is_loaded is True
    assert controller.raw_save is data
    assert isinstance(controller.save_game, SaveGame)
    assert controller.selected_slot == 0


def test_load_different_slot_updates_selected_slot(sample_save, monkeypatch):
    monkeypatch.setattr(sc, "load_save", lambda slot: copy.deepcopy(sample_save))
    monkeypatch.setattr(sc, "save_game_data", lambda slot, data: None)

    controller = SaveController()
    controller.load(3)

    assert controller.selected_slot == 3


def test_load_propagates_exceptions_from_load_save(monkeypatch):
    def boom(slot):
        raise FileNotFoundError("slot missing")
    monkeypatch.setattr(sc, "load_save", boom)

    controller = SaveController()
    with pytest.raises(FileNotFoundError):
        controller.load(0)


def test_load_injects_dungeon_level_for_character_tab(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)
    assert controller.save_game.player._p["__dungeon_level__"] == data["currentLevel"]


# ---------------------------------------------------------------------------
# parse_world()
# ---------------------------------------------------------------------------

def test_parse_world_before_load_returns_empty_lists():
    controller = SaveController()
    critters, items = controller.parse_world()
    assert critters == []
    assert items == []


def test_parse_world_after_load_returns_data(sample_save, monkeypatch):
    controller, _ = _controller_with_save(sample_save, monkeypatch)
    critters, items = controller.parse_world()
    assert len(critters) > 0
    assert len(items) > 0


# ---------------------------------------------------------------------------
# save()
# ---------------------------------------------------------------------------

def test_save_without_load_raises(sample_save):
    controller = SaveController()
    payload = SavePayload(attrs={}, skills={}, flags={})
    with pytest.raises(RuntimeError):
        controller.save(payload)


def test_save_calls_save_game_data_with_selected_slot(sample_save, monkeypatch):
    writes = []
    controller, data = _controller_with_save(sample_save, monkeypatch, captured_writes=writes)

    payload = _base_payload(controller)
    controller.save(payload)

    assert len(writes) == 1
    slot, written = writes[0]
    assert slot == controller.selected_slot == 0


def test_save_persists_attribute_changes(sample_save, monkeypatch):
    writes = []
    controller, data = _controller_with_save(sample_save, monkeypatch, captured_writes=writes)

    payload = _base_payload(controller, attrs={**get_character_summary(data)["attributes"], "hp": 777})
    new_save_game = controller.save(payload)

    assert new_save_game.player.hp == 777
    _, written = writes[0]
    assert written["playerData"]["hp"] == 777


def test_save_persists_quest_flag_changes(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)

    flags = controller.save_game.player.get_quest_flags_by_name()
    target = QUEST_FLAGS[0]["flag"]
    flags[target] = not flags[target]

    payload = _base_payload(controller, flags=flags)
    new_save_game = controller.save(payload)

    assert new_save_game.player.get_quest_flags_by_name()[target] == flags[target]


def test_save_persists_cast_spells_when_provided(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)

    n = len(controller.save_game.player.cast_spells)
    payload = _base_payload(controller, cast_spells=[True] * n)
    new_save_game = controller.save(payload)

    assert all(new_save_game.player.cast_spells)


def test_save_with_empty_cast_spells_preserves_existing(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)
    before = list(controller.save_game.player.cast_spells)

    payload = _base_payload(controller, cast_spells=[])
    new_save_game = controller.save(payload)

    assert new_save_game.player.cast_spells == before


def test_save_invalid_numeric_attr_raises_value_error(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)

    attrs = get_character_summary(data)["attributes"]
    attrs = {**attrs, "hp": "not-a-number"}
    payload = _base_payload(controller, attrs=attrs)

    with pytest.raises(ValueError):
        controller.save(payload)


def test_save_returns_fresh_save_game_with_updated_dungeon_level_hook(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)
    payload = _base_payload(controller)

    new_save_game = controller.save(payload)

    assert new_save_game is not controller.save_game or new_save_game is controller.save_game
    assert new_save_game.player._p["__dungeon_level__"] == data["currentLevel"]


def test_save_does_not_corrupt_world_or_inventory(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)
    world_before = copy.deepcopy(data["worldObjectsByLevel"])
    inventory_before = copy.deepcopy(data["inventoryData"])

    payload = _base_payload(controller, attrs={**get_character_summary(data)["attributes"], "hp": 1})
    controller.save(payload)

    assert data["worldObjectsByLevel"] == world_before
    assert data["inventoryData"] == inventory_before


# ---------------------------------------------------------------------------
# cheat_max_skills()
# ---------------------------------------------------------------------------

def test_cheat_max_skills_without_load_raises():
    controller = SaveController()
    with pytest.raises(RuntimeError):
        controller.cheat_max_skills()


def test_cheat_max_skills_sets_all_skills(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)

    controller.cheat_max_skills(value=30)

    summary = get_character_summary(data)
    assert all(v == 30 for v in summary["skills"].values())


def test_cheat_max_skills_custom_value(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)

    controller.cheat_max_skills(value=15)

    summary = get_character_summary(data)
    assert all(v == 15 for v in summary["skills"].values())


# ---------------------------------------------------------------------------
# equipment_summary() / equipped_for_preview()
# ---------------------------------------------------------------------------

def test_equipment_summary_before_load_is_empty():
    controller = SaveController()
    assert controller.equipment_summary() == []


def test_equipment_summary_after_load_has_eleven_slots(sample_save, monkeypatch):
    controller, _ = _controller_with_save(sample_save, monkeypatch)
    assert len(controller.equipment_summary()) == 11


def test_equipped_for_preview_before_load_is_empty():
    controller = SaveController()
    assert controller.equipped_for_preview() == {}


def test_equipped_for_preview_matches_equipped_items(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)

    preview = controller.equipped_for_preview()
    equipped = controller.save_game.equipped_items

    assert len(preview) == len(equipped)
    for idx, obj in enumerate(equipped):
        assert preview[idx]["objectType"] == obj.object_type
        assert preview[idx]["qualityClass"] == obj.parsed_data.get("qualityClass", 0)


# ---------------------------------------------------------------------------
# preview_data()
# ---------------------------------------------------------------------------

def test_preview_data_before_load_is_empty():
    controller = SaveController()
    assert controller.preview_data() == {}


def test_preview_data_uses_player_portrait_by_default(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)

    preview = controller.preview_data()

    p = controller.save_game.player
    assert preview["portrait_id"] == p.portrait
    assert preview["name"] == p.name
    assert preview["class_name"] == p.player_class_name
    assert preview["level"] == p.level
    assert preview["dungeon_level"] == controller.save_game.dungeon_level
    assert preview["equipped_slots"] == controller.equipped_for_preview()


def test_preview_data_with_explicit_portrait_override(sample_save, monkeypatch):
    controller, data = _controller_with_save(sample_save, monkeypatch)

    preview = controller.preview_data(portrait_id=42)

    assert preview["portrait_id"] == 42
    # demais campos continuam vindo do player atual
    assert preview["name"] == controller.save_game.player.name


# ---------------------------------------------------------------------------
# Fluxo completo: load -> mutate -> save -> reload reflete estado
# ---------------------------------------------------------------------------

def test_full_load_mutate_save_roundtrip(sample_save, monkeypatch):
    writes = []
    controller, data = _controller_with_save(sample_save, monkeypatch, captured_writes=writes)

    # Mutações via SaveGame, fora do payload (ex: inventário/mundo)
    controller.save_game.main_inventory[0].quantity = 9
    controller.save_game.delete_main_inventory_item(1)

    payload = _base_payload(controller, attrs={**get_character_summary(data)["attributes"], "charLevel": 50})
    new_save_game = controller.save(payload)

    assert new_save_game.player.level == 50
    assert json.loads(data["inventoryData"]["mainInventory"][0]["jsonData"])["quantity"] == 9
    assert len(data["inventoryData"]["mainInventory"]) == len(sample_save["inventoryData"]["mainInventory"]) - 1

    # save_game_data foi chamado exatamente uma vez, com o slot correto
    assert len(writes) == 1
    assert writes[0][0] == 0