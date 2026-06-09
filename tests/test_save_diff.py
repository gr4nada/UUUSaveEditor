# tests/test_save_diff.py
"""
Unit tests for SaveDiff — the core reverse-engineering diagnostic tool from Sprint 2.

SaveDiff.compare(a, b) serves as the primary instrument to pinpoint structural
and value variances between save records: simple attributes, flat arrays, and nested schemas.
"""
from src.core.save_diff import SaveDiff


# ---------------------------------------------------------------------------
# Baseline Edge Cases
# ---------------------------------------------------------------------------

def test_identical_dicts_produce_no_diff():
    """
    Ensures that identical dictionaries evaluate with no recorded discrepancies.
    """
    a = {"hp": 82, "name": "Avatar", "skills": [10, 20]}
    assert SaveDiff.compare(a, a) == []


def test_single_primitive_change_detected():
    """
    Validates that a mutation within a basic primitive value type is fully identified.
    """
    a = {"hp": 82}
    b = {"hp": 999}
    diffs = SaveDiff.compare(a, b)
    assert len(diffs) == 1
    assert diffs[0]["path"] == "hp"
    assert diffs[0]["old"] == 82
    assert diffs[0]["new"] == 999


def test_multiple_changes_all_detected():
    """
    Ensures that multiple concurrent parameter modifications are isolated independently.
    """
    a = {"hp": 82, "mana": 39, "strength": 18}
    b = {"hp": 999, "mana": 39, "strength": 25}
    diffs = SaveDiff.compare(a, b)
    paths = {d["path"] for d in diffs}
    assert "hp" in paths
    assert "strength" in paths
    assert "mana" not in paths  # Unchanged baseline property nodes remain untouched


def test_missing_key_in_b_reported():
    """
    Verifies that a property removed from the secondary state object registers as None.
    """
    a = {"hp": 82, "extra": "value"}
    b = {"hp": 82}
    diffs = SaveDiff.compare(a, b)
    assert any(d["path"] == "extra" and d["new"] is None for d in diffs)


def test_new_key_in_b_reported():
    """
    Ensures that an entirely new property initialized in the target state registers as missing originally.
    """
    a = {"hp": 82}
    b = {"hp": 82, "newField": 42}
    diffs = SaveDiff.compare(a, b)
    assert any(d["path"] == "newField" and d["old"] is None for d in diffs)


# ---------------------------------------------------------------------------
# Nested Object Matrix Parsing
# ---------------------------------------------------------------------------

def test_nested_dict_change_detected():
    """
    Validates that changes occurring deep inside embedded dictionary properties resolve accurate path notation mapping.
    """
    a = {"playerData": {"hp": 82, "mana": 39}}
    b = {"playerData": {"hp": 82, "mana": 100}}
    diffs = SaveDiff.compare(a, b)
    assert len(diffs) == 1
    assert diffs[0]["path"] == "playerData.mana"
    assert diffs[0]["old"] == 39
    assert diffs[0]["new"] == 100


def test_deeply_nested_path_reported_correctly():
    """
    Enforces that continuous dotted path tracking notations resolve flawlessly for deeply nested data chains.
    """
    a = {"a": {"b": {"c": 1}}}
    b = {"a": {"b": {"c": 2}}}
    diffs = SaveDiff.compare(a, b)
    assert diffs[0]["path"] == "a.b.c"


def test_nested_dict_no_change_silent():
    """
    Confirms that stagnant nested dictionaries skip delta logging completely.
    """
    a = {"playerData": {"hp": 82}}
    assert SaveDiff.compare(a, a) == []


# ---------------------------------------------------------------------------
# Sequence List Evaluations
# ---------------------------------------------------------------------------

def test_list_change_detected():
    """
    Ensures that structural alterations inside sequence listings evaluate completely.
    """
    a = {"skill": [10, 20, 30]}
    b = {"skill": [10, 99, 30]}
    diffs = SaveDiff.compare(a, b)
    assert len(diffs) == 1
    assert diffs[0]["path"] == "skill"
    assert diffs[0]["old"] == [10, 20, 30]
    assert diffs[0]["new"] == [10, 99, 30]


def test_list_length_change_detected():
    """
    Validates array dimensions expansion/truncation limits detection.
    """
    a = {"flags": [1, 0, 0]}
    b = {"flags": [1, 0, 0, 1]}
    diffs = SaveDiff.compare(a, b)
    assert len(diffs) == 1
    assert diffs[0]["path"] == "flags"


def test_identical_lists_no_diff():
    """
    Ensures matching sequence lists evaluate cleanly without generating diagnostic diff records.
    """
    a = {"skill": [10, 20, 30]}
    assert SaveDiff.compare(a, a) == []


# ---------------------------------------------------------------------------
# pretty_print Interface Validations
# ---------------------------------------------------------------------------

def test_pretty_print_empty_list():
    """
    Validates format integrity when stringifying zero deviations entries profiles.
    """
    result = SaveDiff.pretty_print([])
    assert isinstance(result, str)
    assert len(result) > 0


def test_pretty_print_shows_path_and_values():
    """
    Ensures that key location markers and changed primitives values present accurately inside reports outputs.
    """
    diffs = [{"path": "playerData.hp", "old": 82, "new": 999}]
    result = SaveDiff.pretty_print(diffs)
    assert "playerData.hp" in result
    assert "82" in result
    assert "999" in result


def test_pretty_print_multiple_diffs():
    """
    Guarantees formatting consistency when sorting stacked multi-field anomalies entries.
    """
    diffs = [
        {"path": "Player.hp",       "old": 82,  "new": 999},
        {"path": "Player.strength", "old": 18,  "new": 25},
        {"path": "Skills.Attack",   "old": 12,  "new": 15},
    ]
    result = SaveDiff.pretty_print(diffs)
    assert "Player.hp" in result
    assert "Player.strength" in result
    assert "Skills.Attack" in result


# ---------------------------------------------------------------------------
# Real Save-State Scenario Verifications (Sprint 2 Reverse Engineering)
# ---------------------------------------------------------------------------

def test_diff_player_hp_change(sample_save):
    """
    Simulates a user adjusting health pool parameters from 82 to 999.
    SaveDiff must target and expose exactly the altered baseline 'hp' schema node.
    """
    import copy
    original = copy.deepcopy(sample_save["playerData"])
    sample_save["playerData"]["hp"] = 999
    diffs = SaveDiff.compare(original, sample_save["playerData"])
    assert len(diffs) == 1
    assert diffs[0]["path"] == "hp"


def test_diff_quest_flag_toggle(sample_save):
    """
    Simulates an operational pass updating quest tracking indicator array elements.
    SaveDiff must capture the tracking sequence deviation event cleanly.
    """
    import copy
    original = copy.deepcopy(sample_save["playerData"])
    sample_save["playerData"]["questFlags"][36] = 1
    diffs = SaveDiff.compare(original, sample_save["playerData"])
    assert len(diffs) == 1
    assert diffs[0]["path"] == "questFlags"


def test_diff_skill_edit(sample_save):
    """
    Simulates a structural character mutation pass targeting named proficiency indices.
    """
    import copy
    from src.core.character import get_character_summary, update_character
    from src.core.enums import NOMES_SKILLS

    original = copy.deepcopy(sample_save["playerData"])
    summary = get_character_summary(sample_save)
    summary["skills"]["Attack"] = 30
    update_character(sample_save, summary["attributes"], summary["skills"])

    diffs = SaveDiff.compare(original, sample_save["playerData"])
    assert len(diffs) == 1, (
        f"Expected exactly 1 targeted skill matrix variance profile record node, but found {len(diffs)}:\n"
        f"{SaveDiff.pretty_print(diffs)}"
    )
    assert diffs[0]["path"] == "skill"