# src/core/character.py
import logging
from src.core.enums import NOMES_SKILLS

logger = logging.getLogger("core.character")

# FIXED: Replaced "exp" with "xp" to align perfectly with Unity's Assembly definitions
_NUMERIC_ATTRIBUTES = [
    "charLevel",
    "xp",
    "strength",
    "intellect",
    "dexterity",
    "hp",
    "vitality",
    "mana",
    "maxMana",
    "skillPoints",
    "poison",
    "hunger",
    "fatigue",
    "drunkenness",
    "portrait"
]

def get_character_summary(raw_save_data: dict) -> dict:
    """Extracts data primitives from data streams securely."""
    # Ensure nested structural data path layers exist
    player_data = raw_save_data.get("playerData", {})
    
    attributes = {}
    attributes["playerName"] = player_data.get("playerName", "Avatar")
    attributes["playerClass"] = player_data.get("playerClass", "Fighter")
    attributes["female"] = bool(player_data.get("female", False))
    attributes["leftHanded"] = bool(player_data.get("leftHanded", False))
    
    # Read numeric bindings mapped properties securely
    for attr in _NUMERIC_ATTRIBUTES:
        attributes[attr] = int(player_data.get(attr, 0))
        
    # Extract skill lists bindings arrays
    raw_skills = player_data.get("skill", [])
    skills_map = {}
    for idx, skill_name in enumerate(NOMES_SKILLS):
        if idx < len(raw_skills):
            skills_map[skill_name] = int(raw_skills[idx])
        else:
            skills_map[skill_name] = 0
            
    return {
        "attributes": attributes,
        "skills": skills_map
    }

def update_character(raw_save_data: dict, updated_attributes: dict, updated_skills: dict):
    """Mutates original save stream layout mappings with new updates profiles."""
    if "playerData" not in raw_save_data:
        raw_save_data["playerData"] = {}
        
    p = raw_save_data["playerData"]
    
    # Track text fields allocations updates
    p["playerName"] = updated_attributes.get("playerName", "Avatar")
    p["playerClass"] = updated_attributes.get("playerClass", "Fighter")
    p["female"] = bool(updated_attributes.get("female", False))
    p["leftHanded"] = bool(updated_attributes.get("leftHanded", False))
    
    # Pack numeric properties mutations values
    for attr in _NUMERIC_ATTRIBUTES:
        if attr in updated_attributes:
            p[attr] = int(updated_attributes[attr])
            
    # Pack skill collection indexes updates sequence lists
    skills_list = []
    for skill_name in NOMES_SKILLS:
        skills_list.append(int(updated_skills.get(skill_name, 0)))
    p["skill"] = skills_list

def cheat_max_all_skills(raw_save_data: dict, value: int = 30):
    """FIXED: Uses robust design bounds instead of array mutations multi-operators to avoid empty lists bypasses."""
    if "playerData" not in raw_save_data:
        raw_save_data["playerData"] = {}
        
    p = raw_save_data["playerData"]
    # Enforces explicit allocation layout footprint sizes based directly on the authoritative list definition
    p["skill"] = [int(value)] * len(NOMES_SKILLS)