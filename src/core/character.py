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


# Mapa entre a chave raw do save (usada em _NUMERIC_ATTRIBUTES / updated_attributes)
# e o nome do atributo Python correspondente em PlayerModel.
# Usado por update_character() para delegar a validação aos setters do model.
_RAW_TO_MODEL_ATTR: dict[str, str] = {
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


def update_character(raw_save_data: dict, updated_attributes: dict, updated_skills: dict) -> None:
    """
    Injects mutated attributes and proficiency skills back into the underlying save dictionary.

    Raises KeyError if 'playerData' is completely missing — persisting data onto a broken block 
    creates a partial tracking structure incompatible with the authoritative Unity deserializer.

    Validação de ranges:
      Cada campo numérico é aplicado via um setter validado de PlayerModel
      (src.core.save_model), que levanta ValidationError (subclasse de
      ValueError) se o valor estiver fora dos limites definidos em
      FIELD_LIMITS — exatamente o mesmo padrão já usado por GameObject.hp
      e pelos critters do world_parser. Campos de status (poison, hunger,
      fatigue, drunkenness) são clampados silenciosamente em vez de
      levantar exceção, pois valores extremos são válidos em edição.

    Functional sanitization bounds for invalid parameters:
      - Numeric text string ("30") -> Automatically coerced into primitive int format.
      - Floating-point number (3.9) -> Truncated clean to native int format (3).
      - Alpha non-numeric string ("abc") or None -> Explicitly raises ValueError/TypeError 
        allowing the user interface layer to capture and display useful error messages.
      - Invalid playerClass token (unmapped string name) -> Skipped completely, 
        ensuring the previous legitimate allocation entry remains preserved.
      - Out-of-range numeric value (hp=-1, level=0, level=999) -> Raises
        ValidationError before any field is written, leaving the save untouched.
    """
    from src.core.save_model import PlayerModel, ValidationError, FIELD_LIMITS

    if "playerData" not in raw_save_data:
        raise KeyError(
            "Target 'playerData' block is missing. Cannot commit serialization updates to an unallocated schema."
        )

    p = raw_save_data["playerData"]
    model = PlayerModel(p)

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
            model.player_class = raw_class
        elif isinstance(raw_class, str):
            try:
                # Attempt lookup map validation via enum name indexing (e.g., "Fighter" -> 0)
                model.player_class = EPlayerClass[raw_class.upper()].value
            except KeyError:
                # Unmapped type token fallback: Protect structural layout and dump warning trace logs
                logger.warning(
                    "Supplied playerClass string identifier '%s' does not exist inside EPlayerClass definitions — baseline state preserved.",
                    raw_class,
                )
        # Explicit type guard rejection bounds: Silently drop parameters mapping beyond str or int types

    # --- Core numeric fields ---
    # Validação de range em duas fases:
    #   1ª passada: valida TODOS os campos fornecidos sem escrever nada.
    #               Se qualquer campo violar FIELD_LIMITS, ValidationError é
    #               levantada aqui e raw_save_data permanece intocado.
    #   2ª passada: aplica os valores já validados via setters de PlayerModel
    #               (mesmo padrão de GameObject.hp e dos critters).
    pending: dict[str, int] = {}
    for raw_attr in _NUMERIC_ATTRIBUTES:
        if raw_attr not in updated_attributes:
            continue
        model_attr = _RAW_TO_MODEL_ATTR[raw_attr]
        value = int(updated_attributes[raw_attr])  # ValueError/TypeError se não-numérico
        lo, hi = FIELD_LIMITS[model_attr]
        if model_attr in ("poison", "hunger", "fatigue", "drunkenness"):
            value = _clamp_value(value, lo, hi)
        elif lo is not None and value < lo or hi is not None and value > hi:
            raise ValidationError(model_attr, value, lo=lo, hi=hi)
        pending[model_attr] = value

    for model_attr, value in pending.items():
        setattr(model, model_attr, value)

    # --- Proficiency skill tracking matrices ---
    for name in NOMES_SKILLS:
        if name in updated_skills:
            model.set_skill(name, int(updated_skills[name]))
        else:
            model.set_skill(name, 0)


def _clamp_value(value: int, lo: int | None, hi: int | None) -> int:
    if lo is not None: value = max(lo, value)
    if hi is not None: value = min(hi, value)
    return value


def cheat_max_all_skills(raw_save_data: dict, value: int = 30) -> None:
    """
    Overwrites every skill node entry to match the given target value constraint, 
    rebuilding the full structural array sequence if layout truncation is identified.
    """
    if "playerData" not in raw_save_data:
        raise KeyError("Target tracking schema reference node 'playerData' could not be resolved.")
    raw_save_data["playerData"]["skill"] = [int(value)] * len(NOMES_SKILLS)