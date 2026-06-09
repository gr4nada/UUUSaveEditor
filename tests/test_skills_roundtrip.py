# tests/test_skills_roundtrip.py
from src.core.character import cheat_max_all_skills
from src.core.enums import NOMES_SKILLS

def test_skill_array_exact_bounds(sample_save):
    """
    Validates that the character skill array matches the authoritative definition length.
    Prevents alignment errors and unexpected sizing mismatches against the enum matrix.
    """
    skills = sample_save["playerData"]["skill"]
    expected_length = len(NOMES_SKILLS)
    
    assert len(skills) == expected_length, (
        f"Skill array dimension discrepancy detected! "
        f"Expected {expected_length} defined elements, but save state returned {len(skills)}."
    )


def test_quest_flags_exact_bounds(sample_save):
    """
    Guarantees that the quest progress flags array maintains exactly 64 structural slots
    as defined by the game engine architecture footprints.
    """
    quests = sample_save["playerData"]["questFlags"]
    assert len(quests) == 64, (
        f"Quest flags array sizing corrupted! Expected 64 indices, but found {len(quests)}."
    )


def test_skills_mutation_safety_net(sample_save):
    """
    Verifies that the skill cheat modifier actively patches and rebuilds the matrix,
    even when forced into a critical corruption scenario (e.g., empty or truncated arrays).
    """
    # Inject corrupted empty array state to test safety resilience
    sample_save["playerData"]["skill"] = []

    # Execute the cheat operation which contains the structural healing enforcement
    cheat_max_all_skills(sample_save, value=30)

    # Validate full regeneration and alignment integrity
    restored_skills = sample_save["playerData"]["skill"]
    expected_length = len(NOMES_SKILLS)

    assert len(restored_skills) == expected_length, (
        f"Safety net failed to rebuild skill structural boundaries! "
        f"Expected {expected_length} slots after healing, but array size is {len(restored_skills)}."
    )
    assert all(val == 30 for val in restored_skills), (
        "Matrix assignment failure! Some structural skill nodes were not maximized to 30."
    )