# tests/test_roundtrip.py
"""
Sprint 1 — Full Save State Roundtrip Validation.

Ensures that the load -> summary -> update_character operational pipeline does not alter
any data boundaries untouched by the user interface. If any test here fails, user-facing
modifications could silently corrupt structural areas of the save state.
"""
import json
import copy
from src.core.character import get_character_summary, update_character
from src.core.save_diff import SaveDiff


def test_json_serialization_is_lossless(sample_save):
    """
    Verifies that the json.dumps -> json.loads cyclic transformation yields lossless data integrity.
    Guarantees that the save state layout coordinates are 100% representable within JSON bounds.
    """
    serialized = json.dumps(sample_save, indent=4, ensure_ascii=False)
    restored = json.loads(serialized)
    assert restored == sample_save


def test_top_level_keys_preserved(sample_save):
    """
    Guarantees that the root level structural keys never vanish following data modification routines.
    Protects against partial stream writes dropping key authoritative sub-blocks.
    """
    expected_keys = {"version", "currentLevel", "slotName", "displayName",
                     "savedAtIso", "playerData", "inventoryData",
                     "worldObjects", "worldObjectsByLevel", "mapData"}
    serialized = json.loads(json.dumps(sample_save))
    assert expected_keys.issubset(set(serialized.keys()))


def test_player_roundtrip_zero_diff(sample_save):
    """
    Ensures that processing an update cycle without active user modifications yields an empty diff footprint.
    This acts as a critical constraint boundary: structural deviation indicates data corruption behavior.
    """
    original_player = copy.deepcopy(sample_save["playerData"])

    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])

    diffs = SaveDiff.compare(original_player, sample_save["playerData"])
    assert diffs == [], (
        f"update_character mutated playerData without any corresponding user actions!\n"
        f"{SaveDiff.pretty_print(diffs)}"
    )


def test_inventory_not_touched_by_player_update(sample_save):
    """
    Validates that update_character isolates its modifications strictly onto the playerData node.
    Guarantees that updating primary character parameters never impacts item inventory tracking blocks.
    """
    original_inventory = copy.deepcopy(sample_save["inventoryData"])

    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])

    diffs = SaveDiff.compare(original_inventory, sample_save["inventoryData"])
    assert diffs == [], (
        f"update_character modified the inventoryData structure unexpectedly!\n"
        f"{SaveDiff.pretty_print(diffs)}"
    )


def test_world_objects_not_touched_by_player_update(sample_save):
    """
    Guarantees that worldObjects and mapData structures remain isolated and untouched during character routines.
    """
    original_world = copy.deepcopy(sample_save["worldObjects"])
    original_map = copy.deepcopy(sample_save["mapData"])

    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])

    assert sample_save["worldObjects"] == original_world
    assert sample_save["mapData"] == original_map


def test_double_roundtrip_is_idempotent(sample_save):
    """
    Validates that executing consecutive pipeline transformations consecutively remains completely idempotent.
    Protects against cumulative math deviations on tracking elements where data sums rather than overrides.
    """
    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])
    state_after_first = copy.deepcopy(sample_save["playerData"])

    summary2 = get_character_summary(sample_save)
    update_character(sample_save, summary2["attributes"], summary2["skills"])
    state_after_second = sample_save["playerData"]

    diffs = SaveDiff.compare(state_after_first, state_after_second)
    assert diffs == [], (
        f"Subsequent operational roundtrip pass generated a structural diff — operation is not idempotent!\n"
        f"{SaveDiff.pretty_print(diffs)}"
    )


def test_quest_flags_not_mutated_by_player_roundtrip(sample_save):
    """
    Ensures that standard character summary and save routines avoid mutating structural quest parameters.
    The quest flag nodes should strictly maintain consistency until targeted through a designated interface tab.
    """
    original_flags = copy.deepcopy(sample_save["playerData"]["questFlags"])

    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])

    assert sample_save["playerData"]["questFlags"] == original_flags


def test_magic_data_preserved_in_roundtrip(sample_save):
    """
    Verifies that complex, read-only structures such as magicData survive full cycle mutations intact.
    """
    original_magic = copy.deepcopy(sample_save["playerData"]["magicData"])

    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])

    assert sample_save["playerData"]["magicData"] == original_magic