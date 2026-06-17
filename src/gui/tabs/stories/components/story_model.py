"""
Story Model - Estado narrativo do jogo
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class StoryState:
    """Modelo do estado da história e progresso narrativo."""

    easy: bool = False
    current_level: int = 0
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})

    # Plot Flags
    cup_found: bool = False
    cup_dream_index: int = 0
    sapling_planted: bool = False
    sapling_level: int = 0
    sapling_position: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})
    moonstone_dropped: bool = False
    moonstone_level: int = 0
    moonstone_position: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})
    garamon_at_rest: bool = False
    entered_green_moongate: bool = False
    said_fanlo: bool = False
    talismans_collected: int = 0
    talismans_destroyed: int = 0

    map_notes: List[Dict] = field(default_factory=list)

    _node: Dict[str, Any] | None = None

    @classmethod
    def from_save(cls, save_game) -> "StoryState":
        p = save_game.player
        return cls(
            easy=p.easy,
            current_level=save_game.current_level,
            position=p.position,
            cup_found=p.cup_found,
            cup_dream_index=p.cup_dream_index,
            sapling_planted=p.sapling_planted,
            sapling_level=p.sapling_planted_level,
            sapling_position=p.sapling_planted_position,
            moonstone_dropped=p.moonstone_dropped,
            moonstone_level=p.moonstone_dropped_level,
            moonstone_position=p.moonstone_dropped_position,
            garamon_at_rest=p.garamon_at_rest,
            entered_green_moongate=p.entered_green_moongate,
            said_fanlo=p.said_fanlo,
            talismans_collected=p.talismans_collected,
            talismans_destroyed=p.talismans_destroyed,
            map_notes=save_game.get_all_map_notes() if hasattr(save_game, 'get_all_map_notes') else [],
            _node=getattr(p, "_node", None),
        )