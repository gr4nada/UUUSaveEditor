# src/gui/tabs/stories/story_model.py
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class StoryState:
    """Modelo do estado da história."""

    easy: bool = False
    current_level: int = 0
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})

    cup_found: bool = False
    cup_dream_index: int = 0
    sapling_planted: bool = False
    sapling_level: int = 0
    moonstone_dropped: bool = False
    moonstone_level: int = 0
    garamon_at_rest: bool = False
    entered_green_moongate: bool = False
    said_fanlo: bool = False
    talismans_collected: int = 0
    talismans_destroyed: int = 0

    _node: Dict[str, Any] | None = None

    @classmethod
    def from_save(cls, save_game) -> "StoryState":
        p = save_game.player
        return cls(
            easy=p.easy,
            current_level=getattr(save_game, "current_level", 0),
            position=getattr(p, "position", {"x": 0.0, "y": 0.0, "z": 0.0}),
            cup_found=getattr(p, "cup_found", False),
            cup_dream_index=getattr(p, "cup_dream_index", 0),
            sapling_planted=getattr(p, "sapling_planted", False),
            sapling_level=getattr(p, "sapling_planted_level", 0),
            moonstone_dropped=getattr(p, "moonstone_dropped", False),
            moonstone_level=getattr(p, "moonstone_dropped_level", 0),
            garamon_at_rest=getattr(p, "garamon_at_rest", False),
            entered_green_moongate=getattr(p, "entered_green_moongate", False),
            said_fanlo=getattr(p, "said_fanlo", False),
            talismans_collected=getattr(p, "talismans_collected", 0),
            talismans_destroyed=getattr(p, "talismans_destroyed", 0),
        )