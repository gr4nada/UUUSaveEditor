# src/core/database/critters.py
"""
Critter / NPC encyclopedia of the game.

Single source of truth for:
  - AI states (ECritterState)     → state_label(id)
  - AI objectives (ECritterGoal)  → goal_label(id)
  - attitudes (ECritterAttitude)  → attitude_label(id), ATTITUDE_COLORS
  - movement type                 → movement_label(id)

Previously scattered across:
  - src/core/enums.py (ECritterState, ECritterGoal, ECritterAttitude, EMovementType
                      + critter_state_label, critter_goal_label,
                        critter_attitude_label, movement_type_label)
  - src/gui/constants.py (ATTITUDE_COLORS)
"""
from __future__ import annotations
from enum import IntEnum


# ---------------------------------------------------------------------------
# Critter behavior enums
# ---------------------------------------------------------------------------

class ECritterState(IntEnum):
    """Active execution state of critter/NPC AI."""
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
    """High-level objective or agenda assigned to a critter."""
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
    """Moral disposition of the NPC toward the Avatar."""
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

# UI colors by attitude — single source of truth (previously duplicated in constants.py and critters_tab.py)
ATTITUDE_COLORS: dict[int, str] = {
    0: "#ff6b6b",   # Hostile  — red
    1: "#ff9944",   # Upset    — orange
    2: "#ffd93d",   # Mellow   — yellow
    3: "#6bcb77",   # Friendly — green
}

# Mapa nome → valor (para filtros de UI)
ATTITUDE_BY_NAME: dict[str, int] = {
    "Hostile":  0,
    "Upset":    1,
    "Mellow":   2,
    "Friendly": 3,
}


class EMovementType(IntEnum):
    """Physics locomotion restrictions of the creature archetype."""
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
# Public API — functions for int → readable string resolution
# ---------------------------------------------------------------------------

def state_label(state_id: int) -> str:
    """int → readable critter AI state label."""
    return _STATE_LABELS.get(state_id, f"State {state_id}")


def goal_label(goal_id: int) -> str:
    """int → readable critter objective label."""
    return _GOAL_LABELS.get(goal_id, f"Goal {goal_id}")


def attitude_label(attitude_id: int) -> str:
    """int → readable critter attitude label."""
    return _ATTITUDE_LABELS.get(attitude_id, f"Attitude {attitude_id}")


def movement_label(movement_id: int) -> str:
    """int → readable movement type label."""
    return _MOVEMENT_LABELS.get(movement_id, f"Move {movement_id}")


def attitude_color(attitude_id: int) -> str:
    """int → hex color of attitude (for UI use)."""
    return ATTITUDE_COLORS.get(attitude_id, "#888888")
