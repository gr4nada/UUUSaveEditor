"""
Critter Model Module

Defines the Critter dataclass and helper methods for representing
NPCs and creatures in the save file.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class Critter:
    """
    Represents a single critter/NPC with clean, typed data.
    
    Attributes:
        whoami_id: Unique identifier for named NPCs
        critter_id: Base creature type ID
        name: Display name
        ... (other fields)
    """
    whoami_id: int
    critter_id: Optional[int]
    name: str
    type_name: str
    level: int
    hp: int
    max_hp: int
    dead: bool
    attitude: int
    attitude_label: str
    state: int
    state_label: str
    goal: int
    goal_label: str
    movement_type: int
    movement_label: str
    tile_x: int
    tile_y: int
    talked_to: bool
    player_ally: bool
    gtarg: int
    loot: List[Dict] = None
    _node: Optional[Dict] = None  # Raw save node reference

    @property
    def is_named(self) -> bool:
        """Returns True if this is a named NPC (whoami_id > 0)."""
        return self.whoami_id > 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Critter':
        """Create a Critter instance from a raw dictionary."""
        return cls(
            whoami_id=data.get("whoami_id", 0),
            critter_id=data.get("critter_id"),
            name=data.get("name", "Unknown"),
            type_name=data.get("type_name", "Unknown"),
            level=data.get("level", 0),
            hp=data.get("hp", 0),
            max_hp=data.get("max_hp", 0),
            dead=data.get("dead", False),
            attitude=data.get("attitude", 0),
            attitude_label=data.get("attitude_label", ""),
            state=data.get("state", 0),
            state_label=data.get("state_label", ""),
            goal=data.get("goal", 0),
            goal_label=data.get("goal_label", ""),
            movement_type=data.get("movement_type", 0),
            movement_label=data.get("movement_label", ""),
            tile_x=data.get("tile_x", 0),
            tile_y=data.get("tile_y", 0),
            talked_to=data.get("talked_to", False),
            player_ally=data.get("player_ally", False),
            gtarg=data.get("gtarg", 0),
            loot=data.get("loot", []),
            _node=data.get("_node")
        )