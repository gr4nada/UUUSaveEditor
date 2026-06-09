# tests/test_skills_roundtrip.py
"""
Skills array and quest progress flags validation tests.

Covers: collection dimensions, isolated elements roundtrips, enum sequential indexing,
cheat maximization functions, and structural recovery during array corruption scenarios.
"""
import logging
import copy
from src.core.character import get_character_summary, update_character, cheat_max_all_skills
from src.core.enums import NOMES_SKILLS

logger = logging.getLogger("tests.test_skills_roundtrip")


# ---------------------------------------------------------------------------
# Dimensions and Layout Verification
# ---------------------------------------------------------------------------

def test_skill_array_length_matches_enum(sample_save):
    """
    Validates that the skill array inside playerData contains exactly len(NOMES_SKILLS) allocations.
    """
    skills = sample_save["playerData"]["skill"]
    assert len(skills) == len(NOMES_SKILLS), (
        f"Skill matrix sizing mismatch! Expected {len(NOMES_SKILLS)} tracking entries, but found {len(skills)}"
    )


def test_quest_flags_length_is_64(sample_save):
    """
    Ensures that questFlags maintains exactly 64 discrete binary indicator slots dictated by the engine.
    """
    flags = sample_save["playerData"]["questFlags"]
    assert len(flags) == 64, f"Quest milestones matrix sizing corrupt! Expected 64 flag bits, but found {len(flags)}"


def test_all_skills_are_integers(sample_save):
    """
    Enforces that every node inside the skills collection resolves explicitly as a native primitive integer.
    """
    for idx, val in enumerate(sample_save["playerData"]["skill"]):
        assert isinstance(val, int), (
            f"Type boundary error at index [{idx}] ({NOMES_SKILLS[idx]}): "
            f"expected primitive int, found type {type(val).__name__}"
        )


def test_skill_names_map_to_correct_indices(sample_save):
    """
    Verifies that get_character_summary matches named descriptors according to the sequence of NOMES_SKILLS.
    An ordering error here causes the application to binding operations onto wrong allocation indices.
    """
    summary = get_character_summary(sample_save)
    raw_skills = sample_save["playerData"]["skill"]

    for idx, name in enumerate(NOMES_SKILLS):
        assert summary["skills"][name] == raw_skills[idx], (
            f"Skill mapping misalignment identified for key '{name}' (Index {idx}): "
            f"expected database state value {raw_skills[idx]}, but parsed summary returned {summary['skills'][name]}"
        )


# ---------------------------------------------------------------------------
# Mutation Control Roundtrips
# ---------------------------------------------------------------------------

def test_single_skill_edit_roundtrip(sample_save):
    """
    Guarantees that mutating a specific skill node keeps all other elements completely isolated.
    Protects against a catastrophic regression where lists are overwritten with defaults or empty sequences.
    """
    original_skills = copy.deepcopy(sample_save["playerData"]["skill"])
    summary = get_character_summary(sample_save)

    target_skill = NOMES_SKILLS[0]  # Resolves targeting index position 0 ("Attack")
    summary["skills"][target_skill] = 25
    update_character(sample_save, summary["attributes"], summary["skills"])

    new_skills = sample_save["playerData"]["skill"]
    assert new_skills[0] == 25, "Target modifier failed to persist updated Attack value node"

    for idx in range(1, len(NOMES_SKILLS)):
        assert new_skills[idx] == original_skills[idx], (
            f"Neighboring node context bleeding: value for '{NOMES_SKILLS[idx]}' (Index {idx}) "
            f"was mutated unexpectedly during an isolated operation pass"
        )


def test_all_skills_edit_roundtrip(sample_save):
    """
    Ensures that modifying all matrix entries with diverse values preserves each element accurately.
    """
    summary = get_character_summary(sample_save)
    for i, name in enumerate(NOMES_SKILLS):
        summary["skills"][name] = i + 1  # Populate unique values ranging sequentially 1..20

    update_character(sample_save, summary["attributes"], summary["skills"])

    saved = sample_save["playerData"]["skill"]
    for i, name in enumerate(NOMES_SKILLS):
        assert saved[i] == i + 1, f"Validation failure on key node '{name}': expected {i+1}, found {saved[i]}"


def test_skills_preserved_after_attribute_only_edit(sample_save):
    """
    Validates that updating purely numerical attributes isolates and keeps the skills collection untouched.
    """
    original_skills = copy.deepcopy(sample_save["playerData"]["skill"])
    summary = get_character_summary(sample_save)

    summary["attributes"]["hp"] = 500
    summary["attributes"]["strength"] = 30
    update_character(sample_save, summary["attributes"], summary["skills"])

    assert sample_save["playerData"]["skill"] == original_skills


# ---------------------------------------------------------------------------
# Modifiers and Error Healing Control Functions
# ---------------------------------------------------------------------------

def test_cheat_fills_exact_skill_count(sample_save):
    """
    Validates that cheat_max_all_skills initializes exactly len(NOMES_SKILLS) entries.
    """
    cheat_max_all_skills(sample_save, value=30)
    assert len(sample_save["playerData"]["skill"]) == len(NOMES_SKILLS)


def test_cheat_sets_all_values_to_target(sample_save):
    """
    Ensures that applying the optimization cheat explicitly sets all elements to the exact target boundary value.
    """
    cheat_max_all_skills(sample_save, value=30)
    for idx, val in enumerate(sample_save["playerData"]["skill"]):
        assert val == 30, f"Cheat allocation error at Index [{idx}] ({NOMES_SKILLS[idx]}): tracked value is {val}, expected 30"


def test_cheat_recovers_from_truncated_array(sample_save):
    """
    Verifies that the modifier automatically heals the structure if it encounters a truncated or corrupted array,
    enforcing complete matrix reconstruction instead of dropping execution pipelines silently.
    """
    sample_save["playerData"]["skill"] = [5, 5]  # Simulate a corrupted payload containing only 2 elements instead of the baseline
    cheat_max_all_skills(sample_save, value=30)

    skills = sample_save["playerData"]["skill"]
    assert len(skills) == len(NOMES_SKILLS), (
        f"Structural recovery mechanism failed to rebuild truncated array footprints! "
        f"Expected baseline size {len(NOMES_SKILLS)}, but collection returned dimension size {len(skills)}"
    )
    assert all(v == 30 for v in skills), "Some elements failed sequence population criteria inside healed context framework"


def test_cheat_custom_value(sample_save):
    """
    Confirms that the cheat routine accepts any arbitrary parameter target variable constraint rather than a fixed limit.
    """
    cheat_max_all_skills(sample_save, value=15)
    assert all(v == 15 for v in sample_save["playerData"]["skill"]), "Matrix element allocation skipped custom integer threshold constraints"


def test_skill_values_survive_json_serialization(sample_save):
    """
    Ensures that updated values survive the JSON serialization pass without precision anomalies or type conversion changes.
    """
    import json
    summary = get_character_summary(sample_save)
    for name in NOMES_SKILLS:
        summary["skills"][name] = 17
    update_character(sample_save, summary["attributes"], summary["skills"])

    serialized = json.dumps(sample_save)
    restored = json.loads(serialized)
    for val in restored["playerData"]["skill"]:
        assert val == 17
        assert isinstance(val, int), f"Serialization layout type pollution: primitive resolved as {type(val).__name__} instead of int"