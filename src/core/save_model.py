# src/core/save_model.py
"""
Domain models — Sprint 4 do plano de refatoração.

Introduz uma camada tipada entre o JSON cru e a GUI.
Padrão de acesso: save.player.attributes.hp
em vez de:        save["playerData"]["hp"]

Os modelos são intencionalmente simples: wrappers sobre o dict original,
sem cópia de dados. Mutações nos models refletem no dict e vice-versa —
o save_manager continua serializado o dict raiz normalmente.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import json
import logging

from src.core.database.skills import SKILL_NAMES as NOMES_SKILLS, EPlayerClass
from src.core.database.quests import QUEST_FLAGS

logger = logging.getLogger("core.save_model")


# ---------------------------------------------------------------------------
# PlayerModel
# ---------------------------------------------------------------------------

class PlayerModel:
    """
    Wrapper tipado sobre playerData.

    Uso:
        model = PlayerModel(raw_save["playerData"])
        model.hp           # lê
        model.hp = 999     # escreve de volta no dict original
    """

    def __init__(self, player_data: dict) -> None:
        self._p = player_data

    # — Identidade —
    @property
    def name(self) -> str:       return self._p.get("playerName", "Avatar")
    @name.setter
    def name(self, v: str):      self._p["playerName"] = str(v)

    @property
    def player_class(self) -> int:    return self._p.get("playerClass", 0)
    @player_class.setter
    def player_class(self, v: int):   self._p["playerClass"] = int(v)

    @property
    def player_class_name(self) -> str:
        try:
            return EPlayerClass(self._p.get("playerClass", 0)).name.capitalize()
        except ValueError:
            return "Unknown"

    @property
    def female(self) -> bool:    return bool(self._p.get("female", False))
    @female.setter
    def female(self, v: bool):   self._p["female"] = bool(v)

    @property
    def left_handed(self) -> bool:   return bool(self._p.get("leftHanded", False))
    @left_handed.setter
    def left_handed(self, v: bool):  self._p["leftHanded"] = bool(v)

    @property
    def portrait(self) -> int:   return int(self._p.get("portrait", 0))
    @portrait.setter
    def portrait(self, v: int):  self._p["portrait"] = int(v)

    # — Atributos —
    @property
    def level(self) -> int:      return int(self._p.get("charLevel", 0))
    @level.setter
    def level(self, v: int):     self._p["charLevel"] = int(v)

    @property
    def xp(self) -> int:         return int(self._p.get("xp", 0))
    @xp.setter
    def xp(self, v: int):        self._p["xp"] = int(v)

    @property
    def skill_points(self) -> int:   return int(self._p.get("skillPoints", 0))
    @skill_points.setter
    def skill_points(self, v: int):  self._p["skillPoints"] = int(v)

    @property
    def hp(self) -> int:         return int(self._p.get("hp", 0))
    @hp.setter
    def hp(self, v: int):        self._p["hp"] = int(v)

    @property
    def vitality(self) -> int:   return int(self._p.get("vitality", 0))
    @vitality.setter
    def vitality(self, v: int):  self._p["vitality"] = int(v)

    @property
    def mana(self) -> int:       return int(self._p.get("mana", 0))
    @mana.setter
    def mana(self, v: int):      self._p["mana"] = int(v)

    @property
    def max_mana(self) -> int:   return int(self._p.get("maxMana", 0))
    @max_mana.setter
    def max_mana(self, v: int):  self._p["maxMana"] = int(v)

    @property
    def strength(self) -> int:   return int(self._p.get("strength", 0))
    @strength.setter
    def strength(self, v: int):  self._p["strength"] = int(v)

    @property
    def intellect(self) -> int:  return int(self._p.get("intellect", 0))
    @intellect.setter
    def intellect(self, v: int): self._p["intellect"] = int(v)

    @property
    def dexterity(self) -> int:  return int(self._p.get("dexterity", 0))
    @dexterity.setter
    def dexterity(self, v: int): self._p["dexterity"] = int(v)

    # — Status / Survival —
    @property
    def poison(self) -> int:         return int(self._p.get("poison", 0))
    @poison.setter
    def poison(self, v: int):        self._p["poison"] = int(v)

    @property
    def hunger(self) -> int:         return int(self._p.get("hunger", 0))
    @hunger.setter
    def hunger(self, v: int):        self._p["hunger"] = int(v)

    @property
    def fatigue(self) -> int:        return int(self._p.get("fatigue", 0))
    @fatigue.setter
    def fatigue(self, v: int):       self._p["fatigue"] = int(v)

    @property
    def drunkenness(self) -> int:    return int(self._p.get("drunkenness", 0))
    @drunkenness.setter
    def drunkenness(self, v: int):   self._p["drunkenness"] = int(v)

    @property
    def dead(self) -> bool:          return bool(self._p.get("dead", False))

    @property
    def stamina(self) -> int:        return int(self._p.get("stamina", 0))

    # — Progressão —
    @property
    def dreams_remaining(self) -> list:  return self._p.get("dreamsRemaining", [])
    @property
    def global_vars(self) -> list:       return self._p.get("globalVars", [])

    # — Skills —
    def get_skill(self, name: str) -> int:
        idx = NOMES_SKILLS.index(name) if name in NOMES_SKILLS else -1
        skills = self._p.get("skill", [])
        return int(skills[idx]) if 0 <= idx < len(skills) else 0

    def set_skill(self, name: str, value: int) -> None:
        idx = NOMES_SKILLS.index(name) if name in NOMES_SKILLS else -1
        if idx < 0:
            return
        skills = self._p.get("skill", [])
        while len(skills) <= idx:
            skills.append(0)
        skills[idx] = int(value)
        self._p["skill"] = skills

    def get_all_skills(self) -> dict[str, int]:
        skills = self._p.get("skill", [])
        return {
            name: int(skills[i]) if i < len(skills) else 0
            for i, name in enumerate(NOMES_SKILLS)
        }

    # — Quest Flags —
    @property
    def quest_flags(self) -> list:  return self._p.get("questFlags", [])

    @quest_flags.setter
    def quest_flags(self, flags_by_name: dict[str, bool]) -> None:
        """
        Reescreve apenas os IDs declarados em QUEST_FLAGS dentro de questFlags,
        a partir de um dict {flag_name: bool}. Expande a lista com False se
        necessário; IDs fora do conhecimento do editor são preservados.
        """
        qlist = list(self._p.get("questFlags", []))
        max_id = max(q["id"] for q in QUEST_FLAGS)
        while len(qlist) <= max_id:
            qlist.append(False)
        for q in QUEST_FLAGS:
            if q["flag"] in flags_by_name:
                qlist[q["id"]] = bool(flags_by_name[q["flag"]])
        self._p["questFlags"] = qlist

    def get_quest_flags_by_name(self) -> dict[str, bool]:
        """Retorna {flag_name: bool} para todos os QUEST_FLAGS conhecidos."""
        qlist = self._p.get("questFlags", [])
        result = {}
        for q in QUEST_FLAGS:
            idx = q["id"]
            result[q["flag"]] = bool(qlist[idx]) if idx < len(qlist) else False
        return result

    # — Estatísticas —
    @property
    def play_time(self) -> float:   return float(self._p.get("playTime", 0))
    @property
    def game_time(self) -> float:   return float(self._p.get("gameTime", 0))
    @property
    def num_repairs(self) -> int:   return int(self._p.get("numRepairs", 0))
    @property
    def num_fish_caught(self) -> int: return int(self._p.get("numFishCaught", 0))
    @property
    def books_read(self) -> int:    return int(self._p.get("booksRead", 0))
    @property
    def books_burned(self) -> int:  return int(self._p.get("booksBurned", 0))
    @property
    def gate_travel_distance(self) -> float: return float(self._p.get("gateTravelDistance", 0))
    @property
    def water_walk_steps(self) -> int: return int(self._p.get("waterWalkSteps", 0))
    @property
    def lava_walk_steps(self) -> int:  return int(self._p.get("lavaWalkSteps", 0))

    # — Magic —
    @property
    def magic_data(self) -> dict:   return self._p.get("magicData", {})

    @property
    def cast_spells(self) -> list[bool]:
        return list(self._p.get("magicData", {}).get("castSpells", []))

    @cast_spells.setter
    def cast_spells(self, spells: list[bool]) -> None:
        if not spells:
            return
        self._p.setdefault("magicData", {})["castSpells"] = list(spells)


# ---------------------------------------------------------------------------
# GameObject — wrapper sobre entradas com jsonData (itens, containers, etc.)
# ---------------------------------------------------------------------------

class GameObject:
    """
    Wrapper sobre um nó de objeto de jogo (item de inventário, world object, etc.)
    que possui um campo `jsonData` com uma string JSON aninhada.

    Uso:
        obj.parsed_data         # dict — faz parse de jsonData uma vez e cacheia
        obj.quantity            # lê de parsed_data, com fallback para o nó externo
        obj.quantity = 5        # escreve em ambos os níveis e re-serializa jsonData
        obj.commit()            # força a re-serialização de jsonData a partir de parsed_data

    Mutações em `parsed_data` (dict) só são persistidas em `jsonData` quando
    `commit()` é chamado — automaticamente disparado pelos setters desta classe.
    """

    def __init__(self, node: dict) -> None:
        self._node = node
        self._parsed: dict | None = None

    @property
    def raw(self) -> dict:
        return self._node

    @property
    def parsed_data(self) -> dict:
        if self._parsed is None:
            raw = self._node.get("jsonData", "")
            try:
                self._parsed = json.loads(raw) if raw else {}
            except Exception:
                logger.warning("Falha ao decodificar jsonData de %r", self._node.get("objectName"))
                self._parsed = {}
        return self._parsed

    def commit(self) -> None:
        """Re-serializa parsed_data para jsonData, se já foi carregado."""
        if self._parsed is not None:
            self._node["jsonData"] = json.dumps(self._parsed)

    # — Campos comuns —
    @property
    def object_name(self) -> str:
        return self._node.get("objectName") or self.parsed_data.get("objectName", "") or ""

    @property
    def object_type_name(self) -> str:
        return self._node.get("objectTypeName", "")

    @property
    def object_type(self) -> int:
        return int(self._node.get("objectType", self.parsed_data.get("objectType", 0)))

    @property
    def quantity(self) -> int:
        return int(self.parsed_data.get("quantity", self._node.get("quantity", 1)))

    @quantity.setter
    def quantity(self, value: int) -> None:
        value = max(1, int(value))
        if "quantity" in self._node:
            self._node["quantity"] = value
        self.parsed_data["quantity"] = value
        self.commit()

    @property
    def enchantment(self) -> str:
        return self.parsed_data.get("enchantmentName", "") or ""

    @property
    def contents(self) -> list[GameObject]:
        items = self._node.get("contents") or self.parsed_data.get("contents") or []
        return [GameObject(it) for it in items]

    @property
    def contents_count(self) -> int:
        items = self._node.get("contents") or self.parsed_data.get("contents") or []
        return len(items)


# ---------------------------------------------------------------------------
# SaveGame — ponto de entrada único
# ---------------------------------------------------------------------------

class SaveGame:
    """
    Ponto de entrada único para acesso ao save.

    Uso:
        sg = SaveGame(raw_dict)
        sg.player.hp = 999
        sg.player.name        → "Avatar"
        sg.slot_name          → "Slot 0"
        sg.raw                → dict original (para save_manager)
    """

    def __init__(self, raw: dict) -> None:
        self._raw = raw
        self.player = PlayerModel(raw.get("playerData", {}))

    # — Metadados do save —
    @property
    def raw(self) -> dict:           return self._raw
    @property
    def version(self) -> str:        return str(self._raw.get("version", ""))
    @property
    def slot_name(self) -> str:      return str(self._raw.get("slotName", ""))
    @property
    def display_name(self) -> str:   return str(self._raw.get("displayName", ""))
    @property
    def saved_at(self) -> str:       return str(self._raw.get("savedAtIso", ""))
    @property
    def current_level(self) -> int:  return int(self._raw.get("currentLevel", 0))

    # — Blocos não-editáveis por enquanto —
    @property
    def inventory_data(self) -> dict:    return self._raw.get("inventoryData", {})
    @property
    def world_objects(self) -> list:     return self._raw.get("worldObjects", [])
    @property
    def world_objects_by_level(self) -> list: return self._raw.get("worldObjectsByLevel", [])
    @property
    def map_data(self) -> dict:          return self._raw.get("mapData", {})

    @property
    def dungeon_level(self) -> int:
        """Nível de masmorra atual do jogador (currentLevel)."""
        return int(self._raw.get("currentLevel", 0))

    # — Main Inventory —
    @property
    def main_inventory(self) -> list[GameObject]:
        items = self._raw.get("inventoryData", {}).get("mainInventory", [])
        return [GameObject(it) for it in items]

    def delete_main_inventory_item(self, index: int) -> None:
        items = self._raw.get("inventoryData", {}).get("mainInventory", [])
        if not (0 <= index < len(items)):
            logger.error("Main inventory index out of range: %d", index)
            return
        removed = items.pop(index)
        logger.info("Main inventory item #%d removed: %r", index, removed.get("objectName"))

    # — Equipped Items —
    @property
    def equipped_items(self) -> list[GameObject]:
        items = self._raw.get("inventoryData", {}).get("equippedItems", [])
        return [GameObject(it) for it in items]

    # — World Objects (parsed) —
    def parse_world(self) -> tuple[list[dict], list[dict]]:
        """Retorna (critters, items) via world_parser.parse_world."""
        from src.core.world_parser import parse_world as _parse_world
        return _parse_world(self._raw)
