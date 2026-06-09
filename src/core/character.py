import logging
from src.core.enums import NOMES_SKILLS, EPlayerClass

logger = logging.getLogger("core.character")

# Campos numéricos simples mapeados diretamente de/para playerData
_NUMERIC_ATTRIBUTES = [
    "charLevel", "exp", "hp", "vitality", "mana", "maxMana",
    "strength", "dexterity", "intellect", "skillPoints",
]

_SURVIVAL_ATTRIBUTES = [
    "poison", "hunger", "fatigue", "drunkenness",
]


def get_character_summary(data: dict) -> dict:
    """
    Extrai atributos e skills do save e retorna um dict limpo para a GUI.
    Lança KeyError se 'playerData' não existir.
    """
    if "playerData" not in data:
        raise KeyError("'playerData' not found in save file.")

    p = data["playerData"]

    class_id = p.get("playerClass", 0)
    try:
        class_name = EPlayerClass(class_id).name.capitalize()
    except ValueError:
        class_name = f"Unknown ({class_id})"

    attributes = {
        "playerName":  p.get("playerName", "Unknown"),
        "playerClass": class_name,
        "female":      p.get("female", False),
        "leftHanded":  p.get("leftHanded", False),
        "portrait":    p.get("portrait", 0),
    }

    for key in _NUMERIC_ATTRIBUTES + _SURVIVAL_ATTRIBUTES:
        attributes[key] = p.get(key, 0)

    skills = {}
    save_skills = p.get("skill", [])
    for idx, skill_name in enumerate(NOMES_SKILLS):
        skills[skill_name] = save_skills[idx] if idx < len(save_skills) else 0

    return {"attributes": attributes, "skills": skills}


def update_character(data: dict, new_attributes: dict, new_skills: dict) -> None:
    """
    Injeta atributos e skills modificados de volta no dicionário do save.
    Lança KeyError se 'playerData' não existir.
    """
    if "playerData" not in data:
        raise KeyError("'playerData' not found for update.")

    p = data["playerData"]

    # Campos de texto e booleanos
    for key in ("playerName", "female", "leftHanded"):
        if key in new_attributes:
            p[key] = new_attributes[key]

    # Classe: converte nome de volta para int via Enum
    if "playerClass" in new_attributes:
        class_name = new_attributes["playerClass"].upper()
        try:
            p["playerClass"] = EPlayerClass[class_name].value
        except KeyError:
            logger.warning("Classe desconhecida '%s' — não atualizada.", new_attributes["playerClass"])

    # Portrait
    if "portrait" in new_attributes:
        p["portrait"] = int(new_attributes["portrait"])

    # Todos os campos numéricos (atributos + survival)
    for key in _NUMERIC_ATTRIBUTES + _SURVIVAL_ATTRIBUTES:
        if key in new_attributes and new_attributes[key] is not None:
            p[key] = int(new_attributes[key])

    # Skills — atualiza o array existente, expande se necessário
    updated = list(p.get("skill", []))
    for idx, skill_name in enumerate(NOMES_SKILLS):
        if skill_name in new_skills and new_skills[skill_name] is not None:
            val = int(new_skills[skill_name])
            if idx < len(updated):
                updated[idx] = val
            else:
                updated.append(val)
    p["skill"] = updated


def cheat_max_all_skills(data: dict, value: int = 30) -> None:
    """Força todos os 19 skills para o valor dado."""
    if "playerData" in data:
        p = data["playerData"]
        if "skill" in p and isinstance(p["skill"], list):
            p["skill"] = [int(value)] * len(p["skill"])
