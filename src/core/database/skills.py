# src/core/database/skills.py
"""
Enciclopédia de skills e classes do jogador.

Fonte única de verdade para:
  - SKILL_NAMES      — lista ordenada dos 20 skills do jogador
  - PLAYER_CLASSES   — nomes das 8 classes jogáveis
  - EPlayerClass     — enum de classes

Anteriormente em:
  - src/core/enums.py (NOMES_SKILLS, EPlayerClass)
"""
from __future__ import annotations
from enum import Enum


# ---------------------------------------------------------------------------
# Classes do jogador
# ---------------------------------------------------------------------------

class EPlayerClass(Enum):
    FIGHTER  = 0
    MAGE     = 1
    BARD     = 2
    TINKER   = 3
    DRUID    = 4
    PALADIN  = 5
    RANGER   = 6
    SHEPHERD = 7


PLAYER_CLASSES: list[str] = [c.name.capitalize() for c in EPlayerClass]

# Mapa nome → id (para lookup reverso)
CLASS_BY_NAME: dict[str, int] = {c.name: c.value for c in EPlayerClass}


def class_name(class_id: int) -> str:
    """int → nome da classe, ou 'Class#N'."""
    try:
        return EPlayerClass(class_id).name.capitalize()
    except ValueError:
        return f"Class#{class_id}"


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

SKILL_NAMES: list[str] = [
    "Attack", "Defense", "Unarmed", "Sword", "Axe", "Mace", "Missile",
    "Mana", "Lore", "Casting", "Traps", "Search", "Track", "Sneak",
    "Repair", "Charm", "Pickpocket", "Acrobat", "Appraise", "Swimming",
]

# Índice por nome para lookup O(1)
SKILL_INDEX: dict[str, int] = {name: i for i, name in enumerate(SKILL_NAMES)}


def skill_name(skill_index: int) -> str:
    """int → nome do skill, ou 'Skill#N'."""
    if 0 <= skill_index < len(SKILL_NAMES):
        return SKILL_NAMES[skill_index]
    return f"Skill#{skill_index}"
