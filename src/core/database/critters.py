# src/core/database/critters.py
"""
Enciclopédia de critters / NPCs do jogo.

Fonte única de verdade para:
  - estados de IA (ECritterState)  → state_label(id)
  - objetivos de IA (ECritterGoal) → goal_label(id)
  - atitudes (ECritterAttitude)    → attitude_label(id), ATTITUDE_COLORS
  - tipo de movimento              → movement_label(id)

Anteriormente espalhado entre:
  - src/core/enums.py (ECritterState, ECritterGoal, ECritterAttitude, EMovementType
                       + critter_state_label, critter_goal_label,
                         critter_attitude_label, movement_type_label)
  - src/gui/constants.py (ATTITUDE_COLORS)
"""
from __future__ import annotations
from enum import IntEnum


# ---------------------------------------------------------------------------
# Enums de comportamento de critter
# ---------------------------------------------------------------------------

class ECritterState(IntEnum):
    """Estado de execução ativo da IA do critter."""
    INITIALIZE        = 0
    ENABLE            = 1
    CROUCH            = 2
    IDLE              = 3
    FIDGET            = 4
    TURN_TO_WANDER    = 5
    WANDER            = 6
    CONVERSE          = 7
    TURN_TO_APPROACH  = 8
    APPROACH          = 9
    COMBAT_IDLE       = 10
    COMBAT_TURN       = 11
    ATTACK            = 12
    PROJECTILE_IDLE   = 13
    PROJECTILE_ATTACK = 14
    TURN_TO_FLEE      = 15
    FLEE              = 16
    FLINCH            = 17
    DIE               = 18
    DEAD              = 19
    CLEANUP           = 20


_STATE_LABELS: dict[int, str] = {
    0:  "Initializing",
    1:  "Enabled / Active",
    2:  "Crouching",
    3:  "Idling",
    4:  "Fidgeting",
    5:  "Turning to Wander",
    6:  "Wandering",
    7:  "Conversing / Talking",
    8:  "Turning to Approach",
    9:  "Approaching Target",
    10: "Combat Idle",
    11: "Turning in Combat",
    12: "Attacking (Melee)",
    13: "Ranged Combat Idle",
    14: "Attacking (Ranged)",
    15: "Turning to Flee",
    16: "Fleeing",
    17: "Flinching / Reeling",
    18: "Dying Animation",
    19: "Dead / Corpse State",
    20: "Cleaning Up Instance",
}


class ECritterGoal(IntEnum):
    """Objetivo de alto nível atribuído ao critter."""
    STAND_0             = 0
    GO_TO               = 1
    WANDER_2            = 2
    FOLLOW_TARGET       = 3
    WANDER_4            = 4
    ATTACK_TARGET_5     = 5
    FLEE_TARGET         = 6
    STAND_7             = 7
    WANDER_8            = 8
    ATTACK_TARGET_9     = 9
    AWAIT_CONVERSATION  = 10
    STAND_11            = 11
    STAND_12            = 12
    STAND_13            = 13
    STAND_14            = 14


_GOAL_LABELS: dict[int, str] = {
    0:  "Standing Still (Static)",
    1:  "Moving to Coordinate",
    2:  "Wandering Area (Type 2)",
    3:  "Following / Guarding Target",
    4:  "Patrolling Perimeter (Type 4)",
    5:  "Engaging Target in Combat",
    6:  "Fleeing from Threat",
    7:  "Alert Standing (Guard Duty)",
    8:  "Searching Area (Type 8)",
    9:  "Hunting Down Target",
    10: "Waiting for Player Chat",
    11: "Passive Standing (Civilian)",
    12: "Sleeping / Inert",
    13: "Standing (Variant 13)",
    14: "Standing (Variant 14)",
}


class ECritterAttitude(IntEnum):
    """Disposição moral do NPC em relação ao Avatar."""
    HOSTILE  = 0
    UPSET    = 1
    MELLOW   = 2
    FRIENDLY = 3


_ATTITUDE_LABELS: dict[int, str] = {
    0: "Hostile (Attack on Sight)",
    1: "Upset / Suspicious",
    2: "Mellow / Neutral",
    3: "Friendly / Ally",
}

# Cores de UI por atitude — fonte única (antes duplicadas em constants.py e critters_tab.py)
ATTITUDE_COLORS: dict[int, str] = {
    0: "#ff6b6b",   # Hostile  — vermelho
    1: "#ff9944",   # Upset    — laranja
    2: "#ffd93d",   # Mellow   — amarelo
    3: "#6bcb77",   # Friendly — verde
}

# Mapa nome → valor (para filtros de UI)
ATTITUDE_BY_NAME: dict[str, int] = {
    "Hostile":  0,
    "Upset":    1,
    "Mellow":   2,
    "Friendly": 3,
}


class EMovementType(IntEnum):
    """Restrições de locomoção do arquétipo da criatura."""
    TWILIGHT_ZONE = 0
    WALKING       = 1
    FLYING        = 2
    SWIMMING      = 3
    CREEPING      = 4
    CRAWLING      = 5


_MOVEMENT_LABELS: dict[int, str] = {
    0: "Twilight Zone",
    1: "Walking",
    2: "Flying",
    3: "Swimming",
    4: "Creeping",
    5: "Crawling",
}

# ---------------------------------------------------------------------------
# API pública — funções de resolução int → string legível
# ---------------------------------------------------------------------------

def state_label(state_id: int) -> str:
    """int → label legível do estado de IA do critter."""
    return _STATE_LABELS.get(state_id, f"State {state_id}")


def goal_label(goal_id: int) -> str:
    """int → label legível do objetivo do critter."""
    return _GOAL_LABELS.get(goal_id, f"Goal {goal_id}")


def attitude_label(attitude_id: int) -> str:
    """int → label legível da atitude do critter."""
    return _ATTITUDE_LABELS.get(attitude_id, f"Attitude {attitude_id}")


def movement_label(movement_id: int) -> str:
    """int → label legível do tipo de movimento."""
    return _MOVEMENT_LABELS.get(movement_id, f"Move {movement_id}")


def attitude_color(attitude_id: int) -> str:
    """int → cor hex da atitude (para uso na UI)."""
    return ATTITUDE_COLORS.get(attitude_id, "#888888")
