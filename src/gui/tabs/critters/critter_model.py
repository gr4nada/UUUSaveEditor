"""
Critter Model

Typed representation of a critter/NPC from the world parser.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Critter:
    """
    Representa um Critter ou NPC com dados tipados e limpos.
    """

    # Identificação
    whoami_id: int = 0
    critter_id: Optional[int] = None
    object_type: int = 0
    object_index: int = 0
    name: str = "Unknown"
    type_name: str = "Unknown"

    # Status
    level: int = 0
    hp: int = 0
    max_hp: int = 0
    dead: bool = False

    # IA e Comportamento
    attitude: int = 0
    attitude_label: str = ""
    state: int = 0
    state_label: str = ""
    goal: int = 0
    goal_label: str = ""
    movement_type: int = 0
    movement_label: str = ""

    # Posição
    tile_x: int = 0
    tile_y: int = 0
    initial_tile_x: int = 0
    initial_tile_y: int = 0

    # Flags
    talked_to: bool = False
    player_ally: bool = False
    gtarg: int = 0

    # Dados avançados
    loot: List[Dict[str, Any]] = field(default_factory=list)
    char_globals: List[int] = field(default_factory=list)

    # Referência ao nó original do save (para edição)
    _node: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Propriedades úteis
    # ------------------------------------------------------------------

    @property
    def is_named(self) -> bool:
        """Retorna True se for um NPC nomeado (whoami > 0)."""
        return self.whoami_id > 0

    @property
    def is_dead(self) -> bool:
        """Alias conveniente."""
        return self.dead

    @property
    def position(self) -> tuple[int, int]:
        """Posição atual no mapa."""
        return (self.tile_x, self.tile_y)

    @property
    def home_position(self) -> tuple[int, int]:
        """Posição original de spawn."""
        return (self.initial_tile_x, self.initial_tile_y)

    def is_merchant(self) -> bool:
        """Verifica se é um mercador (geralmente tem charGlobals grande)."""
        return self.whoami_id in {2, 5, 28, 10}  # Shak, Eyesnack, Zak, etc.

    # ------------------------------------------------------------------
    # Métodos de Conversão
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Critter':
        """Cria instância a partir do dicionário retornado por parse_world()."""
        return cls(
            whoami_id=data.get("whoami_id", 0),
            critter_id=data.get("critter_id"),
            object_type=data.get("object_type", 0),
            object_index=data.get("object_index", 0),
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
            initial_tile_x=data.get("initialTileX", data.get("tile_x", 0)),
            initial_tile_y=data.get("initialTileY", data.get("tile_y", 0)),
            talked_to=data.get("talked_to", False),
            player_ally=data.get("player_ally", False),
            gtarg=data.get("gtarg", 0),
            loot=data.get("loot", []),
            char_globals=data.get("char_globals", data.get("charGlobals", [])),
            _node=data.get("_node"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict (útil para debug e serialização)."""
        return {
            "whoami_id": self.whoami_id,
            "name": self.name,
            "type_name": self.type_name,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "dead": self.dead,
            "attitude": self.attitude,
            "attitude_label": self.attitude_label,
            "tile_x": self.tile_x,
            "tile_y": self.tile_y,
            "talked_to": self.talked_to,
            "player_ally": self.player_ally,
        }