# tests/test_input_safety.py
"""
Input safety and sanitization tests — Sprint 1.5

Covers four core risk vectors arriving from the user interface (GUI):

  1. Numeric boundaries (overflow thresholds, negative constraints, float handling)
  2. Dynamic type coercions (string "30" -> primitive int 30)
  3. Character string encodings with special glyphs / unicode profiles
  4. Partial attribute payload mappings and unmapped invalid tokens

Each individual case isolates expected functional behaviors AND details the operational
consequence if the subsystem deviates (noted explicitly via inline "Risk:" comments).
"""
import logging
import json
import copy
import pytest
from src.core.character import get_character_summary, update_character, _NUMERIC_ATTRIBUTES
from src.core.enums import NOMES_SKILLS, EPlayerClass

logger = logging.getLogger("tests.test_input_safety")


# ===========================================================================
# 1. NUMERIC BOUNDARY CONSTRAINTS
# ===========================================================================

def test_extreme_high_value_passes_through(sample_save):
    """
    Ensures that extremely high out-of-bounds numeric allocations evaluate without exceptions.
    The core editor does not enforce gameplay balance caps — that remains the game engine's task.
    Risk if failed: Application interface (GUI) freezes when a user fills a large numeric sequence.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["hp"] = 99_999_999
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["hp"] == 99_999_999


def test_negative_value_passes_through(sample_save):
    """
    Validates that negative variables persist cleanly into the file format map without errors.
    Risk if failed: Component crash; while properties like 'hunger' naturally clamp at 0 during gameplay,
    the data modifier must not prematurely enforce layout validation rules here.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["hunger"] = -100
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["hunger"] == -100


def test_zero_values_are_valid(sample_save):
    """
    Confirms that assigning 0 resolves as a valid integer across all numeric fields.
    Risk if failed: Stripped properties generate unhandled null reference exceptions inside the runtime.
    """
    summary = get_character_summary(sample_save)
    for key in _NUMERIC_ATTRIBUTES:
        summary["attributes"][key] = 0
    update_character(sample_save, summary["attributes"], summary["skills"])
    for key in _NUMERIC_ATTRIBUTES:
        assert sample_save["playerData"][key] == 0, f"Numeric property field '{key}' failed to initialize to zero"


def test_float_attribute_is_truncated_to_int(sample_save):
    """
    If the interface passes a floating-point number (e.g., 3.9 from a scale calculation), it must truncate to int.
    Risk if failed: JSON serializes a float where an integer constraint is expected -> crash on save load.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["hp"] = 3.9
    update_character(sample_save, summary["attributes"], summary["skills"])
    saved = sample_save["playerData"]["hp"]
    assert isinstance(saved, int), f"Property hp type boundary error: expected int, found {type(saved).__name__}"
    assert saved == 3  # int(3.9) == 3


def test_float_skill_is_truncated_to_int(sample_save):
    """
    Skills passed as float coordinates must truncate down to raw integers before persistence sequences execute.
    Risk if failed: Skill value matrices structured as floating points cause runtime failures inside Unity.
    """
    summary = get_character_summary(sample_save)
    summary["skills"]["Attack"] = 15.9
    update_character(sample_save, summary["attributes"], summary["skills"])
    val = sample_save["playerData"]["skill"][0]
    assert isinstance(val, int)
    assert val == 15


def test_all_saved_numeric_fields_are_int_not_float(sample_save):
    """
    Enforces that after execution, NO core numeric fields evaluate as floats within the JSON structure.
    Guarantees reliable compatibility with the authoritative Unity deserializer schema.
    Risk if failed: Unity reads 'hp: 82.0' as a float variable, throwing deserialization faults or ignoring blocks.
    """
    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])

    p = sample_save["playerData"]
    for key in _NUMERIC_ATTRIBUTES:
        val = p.get(key)
        assert isinstance(val, int), (
            f"Target mapping key field '{key}' resolved as unsafe type {type(val).__name__} ({val}) — must be int"
        )
    for val in p.get("skill", []):
        assert isinstance(val, int), f"Array index element type resolved as {type(val).__name__} instead of primitive int"


# ===========================================================================
# 2. TYPE COERCION (Sanitizing text entry widget inputs)
# ===========================================================================

def test_string_number_attribute_is_coerced_to_int(sample_save):
    """
    UI form elements (like ttk.Entry) return text string data. If unhandled by the GUI, the core must coerce types.
    Risk if failed: File saves literal strings like 'hp: "150"' -> game parsing routines skip the property node.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["hp"] = "150"
    update_character(sample_save, summary["attributes"], summary["skills"])
    saved = sample_save["playerData"]["hp"]
    assert saved == 150
    assert isinstance(saved, int)


def test_string_number_skill_is_coerced_to_int(sample_save):
    """
    Validates that proficiency nodes received as string characters automatically convert into primitive numbers.
    """
    summary = get_character_summary(sample_save)
    summary["skills"]["Attack"] = "28"
    update_character(sample_save, summary["attributes"], summary["skills"])
    val = sample_save["playerData"]["skill"][0]
    assert val == 28
    assert isinstance(val, int)


def test_all_numeric_attributes_coerced_from_string(sample_save):
    """
    Simulates a worst-case form transmission: EVERY single numeric field arrives formatted as a text string.
    The system must cleanly intercept and cast all properties back into standard machine integers.
    """
    summary = get_character_summary(sample_save)
    for key in _NUMERIC_ATTRIBUTES:
        summary["attributes"][key] = str(summary["attributes"][key])

    update_character(sample_save, summary["attributes"], summary["skills"])

    for key in _NUMERIC_ATTRIBUTES:
        val = sample_save["playerData"][key]
        assert isinstance(val, int), (
            f"Key element node '{key}' skipped casting pipeline from string to int: found type {type(val).__name__}"
        )


def test_non_numeric_string_raises_value_error(sample_save):
    """
    If a user supplies alpha characters or leaves form fields completely empty, a ValueError must raise.
    The data layer must reject corrupt or un-parsable clutter from entering the JSON schema.
    The application interface is expected to trap this error state and print a clean error dialog.
    Risk if failed: Arbitrary script strings overwrite memory layouts -> Unity engine crashes.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["hp"] = "abc"

    with pytest.raises((ValueError, TypeError)):
        update_character(sample_save, summary["attributes"], summary["skills"])


def test_none_in_numeric_field_raises(sample_save):
    """
    Passing a None value into a typed numeric index must drop out via exception instead of committing as null.
    Risk if failed: Compiling 'hp: null' inside the data tree breaks deserialization sequences upon loading.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["hp"] = None

    with pytest.raises((TypeError, ValueError)):
        update_character(sample_save, summary["attributes"], summary["skills"])


# ===========================================================================
# 3. SPECIAL CHARACTERS AND UNICODE ENCODINGS
# ===========================================================================

def test_unicode_player_name_survives_roundtrip(sample_save):
    """
    Character names carrying emojis and complex unicode entities must persist through the cycle safely.
    Transformation pipeline: update -> json.dumps -> json.loads must finalize without translation data loss.
    Risk if failed: Accented vowels or text glyph descriptors present as broken text representations inside the game.
    """
    unicode_name = "Sir ⚔️ Aldric 🛡️ von Última"
    summary = get_character_summary(sample_save)
    summary["attributes"]["playerName"] = unicode_name
    update_character(sample_save, summary["attributes"], summary["skills"])

    serialized = json.dumps(sample_save, ensure_ascii=False)
    restored = json.loads(serialized)
    assert restored["playerData"]["playerName"] == unicode_name


def test_special_chars_in_name_survive_json(sample_save):
    """
    Escaped quotes, backslashes, and layout control markers inside names must not invalidate the JSON structure.
    Risk if failed: json.dumps generates formatting faults or builds corrupted tokens that Unity declines to parse.
    """
    tricky_name = 'Sir \'Break\' "Json" \\ Tab\there'
    summary = get_character_summary(sample_save)
    summary["attributes"]["playerName"] = tricky_name
    update_character(sample_save, summary["attributes"], summary["skills"])

    serialized = json.dumps(sample_save, ensure_ascii=False)
    restored = json.loads(serialized)
    assert restored["playerData"]["playerName"] == tricky_name


def test_empty_string_player_name(sample_save):
    """
    Blank string names must process without failures (UX string constraints belong entirely in the GUI layer).
    Risk if failed: Editor logic crashes when a user wipes the character name input field completely and clicks save.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["playerName"] = ""
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["playerName"] == ""


def test_very_long_player_name(sample_save):
    """
    Extremely bloated text sequences (e.g., 500 characters) must serialize cleanly through the JSON formatter.
    Risk if failed: Curious edge-case inputs cause application crashes or overflow buffer boundaries in the backend.
    """
    long_name = "A" * 500
    summary = get_character_summary(sample_save)
    summary["attributes"]["playerName"] = long_name
    update_character(sample_save, summary["attributes"], summary["skills"])
    serialized = json.dumps(sample_save, ensure_ascii=False)
    restored = json.loads(serialized)
    assert restored["playerData"]["playerName"] == long_name


# ===========================================================================
# 4. PARTIAL PAYLOADS AND REAL BUG REGRESSIONS
# ===========================================================================

def test_partial_attributes_preserves_untouched_fields(sample_save):
    """
    Transmitting an isolated map slice like {'playerName': 'X'} must leave adjacent nodes intact.
    Risk if failed: A targeted single-field operation tool feature inadvertently purges all unchanged values.
    """
    original_hp     = sample_save["playerData"]["hp"]
    original_skills = copy.deepcopy(sample_save["playerData"]["skill"])
    summary = get_character_summary(sample_save)

    update_character(sample_save, {"playerName": "MODERN_HERO"}, summary["skills"])

    assert sample_save["playerData"]["playerName"] == "MODERN_HERO"
    assert sample_save["playerData"]["hp"] == original_hp
    assert sample_save["playerData"]["skill"] == original_skills


def test_partial_payload_only_hp_and_name(sample_save):
    """
    A partial dictionary passing only name and health markers must shield strength, mana, and other properties.
    """
    original = copy.deepcopy(sample_save["playerData"])
    summary = get_character_summary(sample_save)

    update_character(sample_save, {"playerName": "X", "hp": 999}, summary["skills"])

    assert sample_save["playerData"]["hp"] == 999
    assert sample_save["playerData"]["playerName"] == "X"
    
    # Confirm every other unrelated numeric element retains its previous data value
    for key in _NUMERIC_ATTRIBUTES:
        if key == "hp":
            continue
        assert sample_save["playerData"][key] == original[key], (
            f"Property boundary bleed: structural field node '{key}' modified by an isolated payload map"
        )


def test_invalid_player_class_is_rejected_or_preserved(sample_save):
    """
    CRITICAL BEHAVE EXCLUSION: Passing unmapped string descriptors like 'NECROMANCER' must never write to JSON.
    The underlying engine parser explicitly relies on a primitive int (matching the C# EPlayerClass enum architecture).

    Writing 'NECROMANCER' as a literal string creates a CRITICAL BUG.
    This test serves as a concrete block to intercept and document that regression.
    Risk: Unity parser encounters string values where integer data is expected -> load routine crash or class reset.
    """
    original_class = sample_save["playerData"]["playerClass"]
    summary = get_character_summary(sample_save)
    summary["attributes"]["playerClass"] = "NECROMANCER"  # Supply an invalid, unmapped text token value

    update_character(sample_save, summary["attributes"], summary["skills"])

    saved = sample_save["playerData"]["playerClass"]
    # Saved output must match a valid integer enum map — never a raw text error string token
    assert isinstance(saved, int), (
        f"Critical structure regression: playerClass committed as type {type(saved).__name__} ('{saved}') — "
        f"must retain integer bounds. Invalid strings must drop out while keeping original structures."
    )
    assert saved == original_class, (
        f"Invalid reference property error: token 'NECROMANCER' does not resolve against standard enum items; "
        f"the baseline original tracking integer ({original_class}) should remain preserved instead."
    )


def test_portrait_out_of_range_is_flagged(sample_save):
    """
    Standard texture ranges evaluate between 0–31. Passing portrait=99 is accepted without validation.
    This explicit tracking case documents current behavior patterns and provides an audible alert mechanism
    should the game framework crash when parsing asset identifier pointers beyond intended index limits.

    To bind absolute index boundary restrictions in future iterations, convert the validation rule to:
        assert sample_save["playerData"]["portrait"] <= 31
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["portrait"] = 99
    update_character(sample_save, summary["attributes"], summary["skills"])
    
    # Documenting baseline system behavior: processing executes without inline boundary clamping
    assert sample_save["playerData"]["portrait"] == 99, (
        "Core structural behavior shifted: value 99 was not preserved. "
        "Adding strict asset range constraint filters (0-31) is recommended."
    )


def test_missing_player_data_key_raises(sample_save):
    """
    If the foundational 'playerData' block is stripped (simulating file corruption), update_character
    must crash immediately with a clear KeyError instead of spawning a blank dictionary node structure.
    Risk if failed: Backend populates a fragmented layout block which the client engine rejects upon reading.
    """
    del sample_save["playerData"]
    summary_attrs = {
        "playerName": "Test", "playerClass": "Fighter", "female": False,
        "leftHanded": False, "hp": 82, "vitality": 82, "mana": 39,
        "maxMana": 39, "xp": 100, "charLevel": 14, "skillPoints": 1,
        "strength": 18, "intellect": 15, "dexterity": 20,
        "poison": 0, "hunger": 0, "fatigue": 0, "drunkenness": 0, "portrait": 0,
    }
    skills = {name: 10 for name in NOMES_SKILLS}

    with pytest.raises(KeyError):
        update_character(sample_save, summary_attrs, skills)