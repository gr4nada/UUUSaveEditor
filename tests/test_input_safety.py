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

def test_extreme_high_value_raises_validation_error(sample_save):
    """
    Sprint 8: FIELD_LIMITS agora é aplicado em update_character() — o mesmo
    padrão já usado por GameObject.hp e pelos critters do world_parser.

    Um hp de 99_999_999 está muito acima do limite de FIELD_LIMITS["hp"]
    (0–9999) e deve ser rejeitado ANTES de qualquer escrita no save,
    via ValidationError (subclasse de ValueError).

    Comportamento anterior (permitia qualquer valor) foi intencionalmente
    substituído — esse era exatamente o "buraco de integridade" que esta
    sprint fecha.
    """
    from src.core.save_model import ValidationError
    summary = get_character_summary(sample_save)
    original_hp = sample_save["playerData"]["hp"]
    summary["attributes"]["hp"] = 99_999_999

    with pytest.raises(ValidationError):
        update_character(sample_save, summary["attributes"], summary["skills"])

    # save permanece intocado — validação ocorre antes de qualquer escrita
    assert sample_save["playerData"]["hp"] == original_hp


def test_high_value_within_limits_is_accepted(sample_save):
    """Um valor alto mas dentro de FIELD_LIMITS deve ser aceito normalmente."""
    summary = get_character_summary(sample_save)
    summary["attributes"]["hp"] = 9999       # limite superior exato
    summary["attributes"]["vitality"] = 9999  # hp <= vitality
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["hp"] == 9999


def test_negative_survival_value_is_clamped_to_zero(sample_save):
    """
    Sprint 8: campos de sobrevivência (poison, hunger, fatigue, drunkenness)
    agora são clampados silenciosamente em [0, 255] por update_character(),
    via PlayerModel — mesmo padrão de _clamp já usado em GameObject.

    hunger = -100 não é mais persistido como -100; é normalizado para 0
    antes de chegar ao save, evitando o estado inválido na origem em vez
    de depender do client do jogo para normalizá-lo depois.
    """
    summary = get_character_summary(sample_save)
    summary["attributes"]["hunger"] = -100
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["hunger"] == 0


def test_negative_attribute_value_raises_validation_error(sample_save):
    """
    Para campos de atributo (não-sobrevivência), um valor negativo é um
    erro de digitação e deve ser rejeitado via ValidationError, deixando
    o save intocado.
    """
    from src.core.save_model import ValidationError
    summary = get_character_summary(sample_save)
    original_hp = sample_save["playerData"]["hp"]
    summary["attributes"]["hp"] = -1

    with pytest.raises(ValidationError):
        update_character(sample_save, summary["attributes"], summary["skills"])

    assert sample_save["playerData"]["hp"] == original_hp


def test_zero_values_are_valid_where_allowed(sample_save):
    """
    Confirms that assigning 0 resolves as a valid integer for fields whose
    FIELD_LIMITS permitem 0 (hp, mana, xp, skillPoints, status fields, portrait).

    Sprint 8: campos com mínimo > 0 (vitality, charLevel, strength, intellect,
    dexterity — todos com min=1) NÃO aceitam 0; um personagem com vitality=0
    ou level=0 é um estado inválido por definição. Esses ficam de fora deste
    teste e são cobertos por test_zero_raises_for_min_one_fields.
    """
    from src.core.save_model import FIELD_LIMITS

    zero_ok_keys = [
        k for k in _NUMERIC_ATTRIBUTES
        if FIELD_LIMITS[_RAW_TO_MODEL_ATTR_TEST[k]][0] in (0, None)
    ]
    summary = get_character_summary(sample_save)
    for key in zero_ok_keys:
        summary["attributes"][key] = 0
    # vitality/maxMana precisam ficar >= hp/mana para a validação cruzada
    summary["attributes"]["vitality"] = max(summary["attributes"].get("hp", 0), 1)
    summary["attributes"]["maxMana"]  = summary["attributes"].get("mana", 0)

    update_character(sample_save, summary["attributes"], summary["skills"])
    for key in zero_ok_keys:
        assert sample_save["playerData"][key] == 0, f"Numeric property field '{key}' failed to initialize to zero"


def test_zero_raises_for_min_one_fields(sample_save):
    """
    Sprint 8: vitality, charLevel, strength, intellect, dexterity têm
    FIELD_LIMITS mínimo = 1. Um valor de 0 nesses campos é inválido
    (personagem sem vitalidade, nível 0, atributo 0) e deve levantar
    ValidationError, deixando o save intocado.
    """
    from src.core.save_model import ValidationError

    for key in ["vitality", "charLevel", "strength", "intellect", "dexterity"]:
        summary = get_character_summary(sample_save)
        original = sample_save["playerData"][key]
        summary["attributes"][key] = 0
        with pytest.raises(ValidationError):
            update_character(sample_save, summary["attributes"], summary["skills"])
        assert sample_save["playerData"][key] == original, f"'{key}' foi modificado apesar do ValidationError"


# Mapa local usado apenas pelos testes acima — espelha _RAW_TO_MODEL_ATTR de character.py
_RAW_TO_MODEL_ATTR_TEST = {
    "charLevel":   "level",
    "xp":          "xp",
    "strength":    "strength",
    "intellect":   "intellect",
    "dexterity":   "dexterity",
    "hp":          "hp",
    "vitality":    "vitality",
    "mana":        "mana",
    "maxMana":     "max_mana",
    "skillPoints": "skill_points",
    "poison":      "poison",
    "hunger":      "hunger",
    "fatigue":     "fatigue",
    "drunkenness": "drunkenness",
    "portrait":    "portrait",
}


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


def test_portrait_out_of_range_raises_validation_error(sample_save):
    """
    Sprint 8: FIELD_LIMITS["portrait"] = (0, 9) — 10 portraits válidos (0-9).
    portrait=99 agora é rejeitado via ValidationError antes de qualquer
    escrita, em vez de ser persistido sem validação (comportamento anterior,
    documentado como risco de crash ao carregar índice de asset inválido).
    """
    from src.core.save_model import ValidationError, FIELD_LIMITS
    summary = get_character_summary(sample_save)
    original_portrait = sample_save["playerData"]["portrait"]
    summary["attributes"]["portrait"] = 99

    with pytest.raises(ValidationError):
        update_character(sample_save, summary["attributes"], summary["skills"])

    assert sample_save["playerData"]["portrait"] == original_portrait

    # Limite superior exato (9) deve ser aceito
    _, hi = FIELD_LIMITS["portrait"]
    summary2 = get_character_summary(sample_save)
    summary2["attributes"]["portrait"] = hi
    update_character(sample_save, summary2["attributes"], summary2["skills"])
    assert sample_save["playerData"]["portrait"] == hi


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