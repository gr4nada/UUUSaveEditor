from src.core.enums import NOMES_SKILLS, EPlayerClass

def get_character_summary(data: dict) -> dict:
    """
    Parses the raw JSON dictionary and extracts a clean structure
    containing the character's attributes and skills for the GUI.
    """
    if 'playerData' not in data:
        raise KeyError("'playerData' structure not found in save file.")
        
    p = data['playerData']
    
    # Translate numeric class ID to string representation via Enum
    class_id = p.get('playerClass', 0)
    try:
        class_name = EPlayerClass(class_id).name
    except ValueError:
        class_name = f"Unknown ({class_id})"
        
    summary = {
        "attributes": {
            "playerName": p.get("playerName", "Unknown"),
            "playerClass": class_name,
            "charLevel": p.get("charLevel", 1),
            "exp": p.get("exp", 0),
            "hp": p.get("hp", 0),
            "vitality": p.get("vitality", 0),
            "mana": p.get("mana", 0),
            "maxMana": p.get("maxMana", 0),
            "strength": p.get("strength", 0),
            "dexterity": p.get("dexterity", 0),
            "intellect": p.get("intellect", 0),
            "skillPoints": p.get("skillPoints", 0),
        },
        "skills": {}
    }
    
    # Map the numerical skill array (indexes 0 to 18) to friendly names
    save_skills = p.get('skill', [])
    for idx, skill_name in enumerate(NOMES_SKILLS):
        """
        Extracts and formats character attributes and skills from raw JSON data for GUI display.
        
        Parameters:
        data (dict): Raw JSON dictionary containing player data.
        
        Returns:
        dict: Cleaned dictionary with character attributes and skill mappings.
        
        Raises:
        KeyError: If 'playerData' key is missing in the input data.
        """
        if idx < len(save_skills):
            summary["skills"][skill_name] = save_skills[idx]
        else:
            summary["skills"][skill_name] = 0
            
    return summary


def update_character(data: dict, new_attributes: dict, new_skills: dict):
    """
    Safely injects updated attribute and skill matrices back into the save dictionary.
    """
    if 'playerData' not in data:
        raise KeyError("'playerData' structure not found for update.")
        
    p = data['playerData']
    
    # Update base character stats
    numeric_keys = [
        "charLevel", "exp", "hp", "vitality", "mana", "maxMana", 
        "strength", "dexterity", "intellect", "skillPoints"
    ]
    
    for key in numeric_keys:
        if key in new_attributes and new_attributes[key] is not None:
            p[key] = int(new_attributes[key])
            
    # Update the skill array, expanding it if needed
    if 'skill' in p and isinstance(p['skill'], list):
        updated_skills = list(p['skill'])
        
        for idx, skill_name in enumerate(NOMES_SKILLS):
            if skill_name in new_skills and new_skills[skill_name] is not None:
                new_value = int(new_skills[skill_name])
                
                if idx < len(updated_skills):
                    updated_skills[idx] = new_value
                else:
                    updated_skills.append(new_value)
                    
        p['skill'] = updated_skills


def cheat_max_all_skills(data: dict, value: int = 30):
    """Fast core cheat routine to force all 19 skills to a set value."""
    if 'playerData' in data:
        p = data['playerData']
        if 'skill' in p and isinstance(p['skill'], list):
            p['skill'] = [int(value)] * len(p['skill'])