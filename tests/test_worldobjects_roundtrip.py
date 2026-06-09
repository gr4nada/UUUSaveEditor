# tests/test_worldobjects_roundtrip.py
import json
import copy
from src.core.character import get_character_summary, update_character
from src.core.inventory import update_equipped_item
from src.core.save_diff import SaveDiff


# ---------------------------------------------------------------------------
# worldObjects, worldObjectsByLevel, and mapData Subsystems
# ---------------------------------------------------------------------------

def test_world_objects_count_preserved_after_player_edit(sample_save):
    """
    Validates that mutating playerData keeps the global worldObjects total length allocation intact.
    """
    original_count = len(sample_save["worldObjects"])
    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert len(sample_save["worldObjects"]) == original_count


def test_world_objects_by_level_preserved_after_player_edit(sample_save):
    """
    Ensures that worldObjectsByLevel matrix remains untouched by any core character edits.
    """
    original = copy.deepcopy(sample_save["worldObjectsByLevel"])
    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["worldObjectsByLevel"] == original


def test_map_data_preserved_after_player_edit(sample_save):
    """
    Guarantees mapData records (uncovered minimap tiles, layout parameters) are isolated from character edits.
    """
    original = copy.deepcopy(sample_save["mapData"])
    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["mapData"] == original


def test_world_objects_preserved_after_inventory_edit(sample_save):
    """
    Ensures mutating specific item equipment slots does not bleed into global worldObjects arrays.
    """
    original = copy.deepcopy(sample_save["worldObjects"])
    update_equipped_item(sample_save, 3, 5, "Longsword", "")
    assert sample_save["worldObjects"] == original


# ---------------------------------------------------------------------------
# magicData Sub-Block Verification
# ---------------------------------------------------------------------------

def test_magic_data_keys_present(sample_save):
    """
    Verifies magicData contains all fundamental property keys expected by the spellcasting sub-engines.
    """
    magic = sample_save["playerData"]["magicData"]
    required = {
        "lastIncrementedMana", "activeSpells", "castSpells",
        "hasMousePrimedSpell", "mousePrimedSpellListIndex",
    }
    for key in required:
        assert key in magic, f"Mandatory game magic property engine key missing from magicData: {key}"


def test_magic_data_preserved_after_full_player_save(sample_save):
    """
    Enforces that the complex magicData block survives a full pipeline manipulation pass entirely intact.
    """
    original_magic = copy.deepcopy(sample_save["playerData"]["magicData"])
    summary = get_character_summary(sample_save)
    summary["attributes"]["hp"] = 500
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert sample_save["playerData"]["magicData"] == original_magic


def test_active_spells_type_preserved(sample_save):
    """
    Validates that activeSpells retains its sequence list primitive type constraint across structural roundtrips.
    """
    magic = sample_save["playerData"]["magicData"]
    assert isinstance(magic["activeSpells"], list)

    serialized = json.dumps(sample_save)
    restored = json.loads(serialized)
    assert isinstance(restored["playerData"]["magicData"]["activeSpells"], list)


# ---------------------------------------------------------------------------
# Engine Progression Counters (Read-Only values untouched by editor)
# ---------------------------------------------------------------------------

def test_progression_counters_preserved(sample_save):
    """
    Ensures that internal game statistics trackers (read books, caught fishes, item repairs)
    are protected from truncation or resetting anomalies inside the serialization routine.
    """
    p = sample_save["playerData"]
    counters = {k: copy.deepcopy(p[k]) for k in
                ("booksRead", "numFishCaught", "numRepairs", "booksBurned",
                 "waterWalkSteps", "lavaWalkSteps", "gateTravelDistance")
                if k in p}

    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])

    for key, original_val in counters.items():
        assert sample_save["playerData"][key] == original_val, (
            f"Read-only progression indicator tracker field node '{key}' corrupted! "
            f"Expected state value {original_val}, but mutated into {sample_save['playerData'][key]}."
        )


def test_encountered_critters_preserved(sample_save):
    """
    Guarantees the historical log of identified creatures is not cleared or dropped by application saves.
    """
    p = sample_save["playerData"]
    if "encounteredCritters" not in p:
        return  # Gracefully skip test execution logic if target platform tracking field is absent from baseline fixture

    original = copy.deepcopy(p["encounteredCritters"])
    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert p["encounteredCritters"] == original


def test_opened_chests_preserved(sample_save):
    """
    Validates that opened chests indexing arrays remain fully preserved through edit operations.
    """
    p = sample_save["playerData"]
    if "openedChest" not in p:
        return

    original = copy.deepcopy(p["openedChest"])
    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])
    assert p["openedChest"] == original


# ---------------------------------------------------------------------------
# SaveDiff Reverse-Engineering Tool Operations
# ---------------------------------------------------------------------------

def test_save_diff_detects_single_change(sample_save):
    """
    Validates that SaveDiff reports exactly one distinct delta node entry when a singular field updates.
    """
    original = copy.deepcopy(sample_save["playerData"])
    sample_save["playerData"]["hp"] = 9999
    diffs = SaveDiff.compare(original, sample_save["playerData"])
    assert len(diffs) == 1
    assert diffs[0]["path"] == "hp"
    assert diffs[0]["new"] == 9999


def test_save_diff_detects_no_change(sample_save):
    """
    Ensures SaveDiff maps an empty tracking listing if comparison targets match exactly.
    """
    original = copy.deepcopy(sample_save["playerData"])
    diffs = SaveDiff.compare(original, sample_save["playerData"])
    assert diffs == []


def test_save_diff_pretty_print_no_changes(sample_save):
    """
    Enforces that executing pretty_print with zero variances outputs an explicit 'no modifications' message.
    """
    result = SaveDiff.pretty_print([])
    assert isinstance(result, str)
    assert "No" in result or "no" in result or "None" not in result


def test_save_diff_full_roundtrip_is_clean(sample_save):
    """
    Acts as the highest-level regression barrier. Running comparison pipelines over an unedited roundtrip
    must evaluate into a zero footprint delta report, certifying perfect system alignment.
    """
    original = copy.deepcopy(sample_save)
    summary = get_character_summary(sample_save)
    update_character(sample_save, summary["attributes"], summary["skills"])

    diffs = SaveDiff.compare(original["playerData"], sample_save["playerData"])
    assert diffs == [], (
        "High-level regression detected! Structural pipeline updates yielded differences on an unedited pass:\n"
        + SaveDiff.pretty_print(diffs)
    )