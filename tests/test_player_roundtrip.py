# tests/test_player_roundtrip.py
"""
Integrity and validation tests for the playerData block.

Covers: primitive types, values boundaries, modification roundtrips,
survival mechanism metrics, and structural boolean flags for class, gender, and dominant hand.
"""
import copy
from src.core.character import get_character_summary, update_character
from src.core.save_diff import SaveDiff


# ---------------------------------------------------------------------------
# Layout Structure and Type Verification
# ---------------------------------------------------------------------------

def test_player_fields_exist_and_types(sample_save):
    """
    Validates that all mandatory keys exist inside playerData and maintain correct primitive types.
    """
    p = sample_save["playerData"]
    expected = {
        "playerName": str, "female": bool, "leftHanded": bool,
        "hp": int, "vitality": int, "mana": int, "maxMana": int,
        "xp": int, "charLevel": int, "skillPoints": int,
        "skill": list, "questFlags": list,
        "poison": int, "hunger": int, "fatigue": int, "drunkenness": int,
    }
    for field, expected_type in expected.items():
        assert field in p, f"Mandatory field missing from schema context: {field}"
        assert isinstance(p[field], expected_type), (
            f"Type boundary mismatch on field '{field}': "
            f"expected {expected_type.__name__}, found {type(p[field]).__name__}"
        )


def test_player_position_has_xyz(sample_save):
    """
    Ensures that the spatial coordinate position node maps x, y, and z as floating point numbers.
    """
    pos = sample_save["playerData"]["position"]
    for axis in ("x", "y", "z"):
        assert axis in pos, f"Spatial vector tracking axis '{axis}' missing from position model"
        assert isinstance(pos[axis], float), f"Spatial coordinate axis '{axis}' must resolve as a float pointer"


# ---------------------------------------------------------------------------
# Editable Fields Mutation Roundtrips
# ---------------------------------------------------------------------------

def test_edit_player_name_roundtrip(sample_save):
    """
    Verifies that updating the playerName entry persists the exact text string across processing modules.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["playerName"] = "SIR_ROUNDTRIP"
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["playerName"] == "SIR_ROUNDTRIP"


def test_edit_hp_roundtrip(sample_save):
    """
    Ensures mutating health points reflects the exact value adjustments without truncation anomalies.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["hp"] = 999
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["hp"] == 999


def test_edit_all_numeric_attributes_roundtrip(sample_save):
    """
    Validates that every editable numeric field updates securely within the save stream map.
    Protects against attributes being silently bypassed or dropped during character updates.
    """
    from src.core.character import _NUMERIC_ATTRIBUTES
    summary = get_character_summary(sample_save)

    # Assign a unique, isolated incremental value per field to catch cross-key binding bleeding
    for i, key in enumerate(_NUMERIC_ATTRIBUTES):
        summary["attributes"][key] = 100 + i

    update_character(sample_save, summary["attributes"], summary["skills"])

    p = sample_save["playerData"]
    for i, key in enumerate(_NUMERIC_ATTRIBUTES):
        assert p[key] == 100 + i, f"Target operational tracking property key field '{key}' failed persistence sequence mapping"


def test_female_flag_toggle_roundtrip(sample_save):
    """
    Validates that toggling the boolean gender profile flag across cyclic transitions operates accurately.
    """
    summary = get_character_summary(sample_save)
    assert sample_save["playerData"]["female"] is False  # Baseline structural expectation matching the fixture baseline

    summary["attributes"]["female"] = True
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["female"] is True

    summary["attributes"]["female"] = False
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["female"] is False


def test_left_handed_flag_roundtrip(sample_save):
    """
    Guarantees that dominant hand adjustments persist explicitly as booleans rather than parsing into string patterns.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["leftHanded"] = True
    update_character(sample_save, summary["attributes"], summary["skills"])
    val = sample_save["playerData"]["leftHanded"]
    assert val is True
    assert isinstance(val, bool), f"Data footprint corruption: leftHanded resolved as {type(val)} instead of bool"


def test_survival_fields_roundtrip(sample_save):
    """
    Verifies state tracking parameters (poison, hunger, fatigue, drunkenness) remain mutable and persist cleanly.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["poison"]      = 3
    summary["attributes"]["hunger"]      = 7
    summary["attributes"]["fatigue"]     = 12
    summary["attributes"]["drunkenness"] = 1
    update_character(sample_save, summary["attributes"], summary["skills"])

    p = sample_save["playerData"]
    assert p["poison"]      == 3
    assert p["hunger"]      == 7
    assert p["fatigue"]     == 12
    assert p["drunkenness"] == 1


# ---------------------------------------------------------------------------
# Non-Editable Fields Isolation Protections
# ---------------------------------------------------------------------------

def test_non_editable_fields_preserved(sample_save):
    """
    Ensures data sectors untouched by the editor interface remain completely isolated and intact.
    Protects critical engine mechanisms from unintentional data loss during serialization passes.
    """
    preserved = [
        "position", "rotation", "globalVars", "playTime", "gameTime",
        "dreamsRemaining", "encounteredCritters", "openedChest",
        "magicData", "booksRead", "numFishCaught",
    ]
    original = {k: copy.deepcopy(sample_save["playerData"][k])
                for k in preserved if k in sample_save["playerData"]}

    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])

    for key, original_val in original.items():
        assert sample_save["playerData"][key] == original_val, (
            f"Read-only subsystem field node '{key}' was altered unexpectedly during character update mutations!"
        )


def test_portrait_value_roundtrip(sample_save):
    """
    Verifies that portrait node definitions persist strictly as standardized integers.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["portrait"] = 15
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["portrait"] == 15
    assert isinstance(sample_save["playerData"]["portrait"], int), "Portrait descriptor type mutated away from integer bounds"