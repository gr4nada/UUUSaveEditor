# src/core/models/world.py
"""
CritterModel — wrapper tipado sobre os dicts de critter retornados por
parse_world(), dando acesso às mesmas edições que critters_tab já faz via
GameObject, mas com interface de propriedades nomeadas.

Design:
  - Não faz cópia do dict nem do _node — mutações refletem no save original.
  - Propriedades read-only espelham os campos do dict (para uso na GUI).
  - Mutações (hp, attitude, position, revive, kill) delegam para
    GameObject(_node) exatamente como critters_tab já faz hoje, garantindo
    que existe apenas UM caminho de escrita.
  - O dict original ainda pode ser acessado via .raw para compatibilidade
    com código existente de treeview/filtros que lê c["hp"], c["attitude"] etc.

Uso:
    critters, _ = save_game.parse_world()
    cm = CritterModel(critters[0])
    cm.name          → "Troll"
    cm.hp            → 54
    cm.hp = 10       # escreve via GameObject + atualiza o dict interno
    cm.kill()        # marca morto em _node + atualiza dict
    cm.attitude = 3  # 0=Hostile … 3=Friendly
"""
from __future__ import annotations
import logging

from src.core.models.objects import GameObject

logger = logging.getLogger("core.models.world")


class CritterModel:
    """
    Wrapper tipado sobre um dict de critter produzido por parse_world().

    Parâmetro:
        critter_dict — o dict retornado em critters[i] por parse_world().
                       Deve conter "_node" (referência ao nó raw do save).
    """

    def __init__(self, critter_dict: dict) -> None:
        self._d    = critter_dict          # o dict de leitura (GUI / treeview)
        self._node = critter_dict["_node"] # nó raw do save (escrita via GameObject)

    # — Acesso ao dict raw (compatibilidade com código existente) —
    @property
    def raw(self) -> dict:
        return self._d

    # ── Campos read-only (parse_world já os calculou) ────────────────────

    @property
    def name(self) -> str:            return self._d.get("name", "")
    @property
    def type_name(self) -> str:       return self._d.get("type_name", "")
    @property
    def object_type(self) -> int:     return int(self._d.get("object_type", 0))
    @property
    def object_index(self) -> int:    return int(self._d.get("object_index", 0))
    @property
    def level(self) -> int:           return int(self._d.get("level", 0))
    @property
    def whoami_id(self) -> int:       return int(self._d.get("whoami_id", 0))
    @property
    def critter_level(self) -> int:   return int(self._d.get("critter_level", 0))
    @property
    def max_hp(self) -> int:          return int(self._d.get("max_hp", 0))
    @property
    def attitude_label(self) -> str:  return self._d.get("attitude_label", "")
    @property
    def state(self) -> int:           return int(self._d.get("state", 0))
    @property
    def state_label(self) -> str:     return self._d.get("state_label", "")
    @property
    def goal(self) -> int:            return int(self._d.get("goal", 0))
    @property
    def goal_label(self) -> str:      return self._d.get("goal_label", "")
    @property
    def movement_type(self) -> int:   return int(self._d.get("movement_type", 0))
    @property
    def movement_label(self) -> str:  return self._d.get("movement_label", "")
    @property
    def talked_to(self) -> int:       return int(self._d.get("talked_to", 0))
    @property
    def gtarg(self) -> int:           return int(self._d.get("gtarg", 0))
    @property
    def loot(self) -> list:           return self._d.get("loot", [])
    @property
    def loot_count(self) -> int:      return int(self._d.get("loot_count", 0))

    # ── Campos editáveis ─────────────────────────────────────────────────

    @property
    def hp(self) -> int:
        return int(self._d.get("hp", 0))

    @hp.setter
    def hp(self, value: int) -> None:
        """Delega para GameObject — única via de escrita em jsonData."""
        obj = GameObject(self._node)
        obj.hp = value                  # clampa em [0, originalHp], commit automático
        self._d["hp"]   = obj.hp        # sincroniza o dict de leitura
        self._d["dead"] = obj.is_dead

    @property
    def dead(self) -> bool:
        return bool(self._d.get("dead", False))

    @property
    def attitude(self) -> int:
        return int(self._d.get("attitude", 0))

    @attitude.setter
    def attitude(self, value: int) -> None:
        value = max(0, min(3, int(value)))
        obj = GameObject(self._node)
        obj.parsed_data["attitude"] = value
        obj.commit()
        self._d["attitude"] = value
        # attitude_label é recalculado por quem precisa (GUI já conhece a tabela)

    @property
    def player_ally(self) -> bool:
        return bool(self._d.get("player_ally", False))

    @player_ally.setter
    def player_ally(self, value: bool) -> None:
        obj = GameObject(self._node)
        obj.parsed_data["playerAlly"] = bool(value)
        obj.commit()
        self._d["player_ally"] = bool(value)

    @property
    def tile_x(self) -> int:
        return int(self._d.get("tile_x", 0))

    @property
    def tile_y(self) -> int:
        return int(self._d.get("tile_y", 0))

    def teleport(self, tile_x: int, tile_y: int) -> None:
        """
        Move o critter para (tile_x, tile_y) no nível actual.
        Escreve initialTileX/Y e xhome/yhome — os quatro campos que o
        engine relê ao entrar no nível.  A posição em world units (position.x/z)
        é calculada pelo engine e não é tocada aqui.
        """
        tx = max(0, min(62, int(tile_x)))
        ty = max(0, min(62, int(tile_y)))
        obj = GameObject(self._node)
        d   = obj.parsed_data
        d["initialTileX"] = tx
        d["initialTileY"] = ty
        d["xhome"]        = tx
        d["yhome"]        = ty
        obj.commit()
        self._d["tile_x"] = tx
        self._d["tile_y"] = ty

    # ── Status helpers (delegam para GameObject) ─────────────────────────

    def kill(self) -> None:
        """Marca o critter como morto (hp=0, deathProcessed=True)."""
        obj = GameObject(self._node)
        obj.kill()
        self._d["hp"]   = 0
        self._d["dead"] = True

    def revive(self, hp: int | None = None) -> None:
        """
        Marca o critter como vivo.
        hp=None restaura originalHp; hp=N seta o valor explícito (mín. 1).
        """
        obj = GameObject(self._node)
        obj.revive(hp)
        self._d["hp"]   = obj.hp
        self._d["dead"] = False
