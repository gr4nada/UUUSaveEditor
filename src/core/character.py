# src/core/character.py
import logging
from src.core.database.skills import SKILL_NAMES as NOMES_SKILLS, EPlayerClass

logger = logging.getLogger("core.character")

_NUMERIC_ATTRIBUTES = [
    "charLevel", "xp", "strength", "intellect", "dexterity",
    "hp", "vitality", "mana", "maxMana", "skillPoints",
    "poison", "hunger", "fatigue", "drunkenness", "portrait",
]


def get_character_summary(raw_save_data: dict) -> dict:
    """
    Extracts core attributes and skills from the raw save data dictionary.
    Raises KeyError if 'playerData' is missing from the save payload structure.
    """
    if "playerData" not in raw_save_data:
        raise KeyError("'playerData' node not found in save payload. The data structure may be corrupted.")

    p = raw_save_data["playerData"]

    attributes = {
        "playerName": p.get("playerName", "Avatar"),
        "playerClass": p.get("playerClass", 0),  # Matches corresponding EPlayerClass enum integer boundary
        "female":      bool(p.get("female", False)),
        "leftHanded":  bool(p.get("leftHanded", False)),
    }
    for attr in _NUMERIC_ATTRIBUTES:
        attributes[attr] = int(p.get(attr, 0))

    raw_skills = p.get("skill", [])
    skills_map = {
        name: int(raw_skills[idx]) if idx < len(raw_skills) else 0
        for idx, name in enumerate(NOMES_SKILLS)
    }

    return {"attributes": attributes, "skills": skills_map}


def update_character(raw_save_data: dict, updated_attributes: dict, updated_skills: dict) -> None:
    """
    Injects mutated attributes and proficiency skills back into the underlying save dictionary.

    Raises KeyError if 'playerData' is completely missing — persisting data onto a broken block 
    creates a partial tracking structure incompatible with the authoritative Unity deserializer.

    Functional sanitization bounds for invalid parameters:
      - Numeric text string ("30") -> Automatically coerced into primitive int format.
      - Floating-point number (3.9) -> Truncated clean to native int format (3).
      - Alpha non-numeric string ("abc") or None -> Explicitly raises ValueError/TypeError 
        allowing the user interface layer to capture and display useful error messages.
      - Invalid playerClass token (unmapped string name) -> Skipped completely, 
        ensuring the previous legitimate allocation entry remains preserved.
    """
    if "playerData" not in raw_save_data:
        raise KeyError(
            "Target 'playerData' block is missing. Cannot commit serialization updates to an unallocated schema."
        )

    p = raw_save_data["playerData"]

    # --- Structural text and boolean flag fields ---
    if "playerName" in updated_attributes:
        p["playerName"] = str(updated_attributes["playerName"])

    if "female" in updated_attributes:
        p["female"] = bool(updated_attributes["female"])

    if "leftHanded" in updated_attributes:
        p["leftHanded"] = bool(updated_attributes["leftHanded"])

    # --- playerClass parsing: Maps text string name back to integer enum coordinates ---
    if "playerClass" in updated_attributes:
        raw_class = updated_attributes["playerClass"]
        if isinstance(raw_class, int):
            p["playerClass"] = raw_class
        elif isinstance(raw_class, str):
            try:
                # Attempt lookup map validation via enum name indexing (e.g., "Fighter" -> 0)
                p["playerClass"] = EPlayerClass[raw_class.upper()].value
            except KeyError:
                # Unmapped type token fallback: Protect structural layout and dump warning trace logs
                logger.warning(
                    "Supplied playerClass string identifier '%s' does not exist inside EPlayerClass definitions — baseline state preserved.",
                    raw_class,
                )
        # Explicit type guard rejection bounds: Silently drop parameters mapping beyond str or int types

    # --- Core numeric fields (int() cast forces string coercion and clamps floats) ---
    for attr in _NUMERIC_ATTRIBUTES:
        if attr in updated_attributes:
            p[attr] = int(updated_attributes[attr])  # Explicitly drops into ValueError/TypeError blocks if invalid

    # --- Proficiency skill tracking matrices ---
    p["skill"] = [int(updated_skills.get(name, 0)) for name in NOMES_SKILLS]


def cheat_max_all_skills(raw_save_data: dict, value: int = 30) -> None:
    """
    Overwrites every skill node entry to match the given target value constraint, 
    rebuilding the full structural array sequence if layout truncation is identified.
    """
    if "playerData" not in raw_save_data:
        raise KeyError("Target tracking schema reference node 'playerData' could not be resolved.")
    raw_save_data["playerData"]["skill"] = [int(value)] * len(NOMES_SKILLS)