# src/core/models/player.py
"""PlayerModel — wrapper tipado sobre playerData do save."""
from __future__ import annotations
import logging

from src.core.database.skills import SKILL_NAMES as NOMES_SKILLS, EPlayerClass
from src.core.database.quests import QUEST_FLAGS
from src.core.models.primitives import (
    ValidationError, FIELD_LIMITS, _clamp, _validate,
)

logger = logging.getLogger("core.models.player")

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
    def player_class(self, v: int):
        lo, hi = FIELD_LIMITS["player_class"]
        self._p["playerClass"] = _validate("player_class", int(v), lo, hi)

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
    def portrait(self, v: int):
        lo, hi = FIELD_LIMITS["portrait"]
        self._p["portrait"] = _validate("portrait", int(v), lo, hi)

    # — Atributos —
    @property
    def level(self) -> int:      return int(self._p.get("charLevel", 0))
    @level.setter
    def level(self, v: int):
        lo, hi = FIELD_LIMITS["level"]
        self._p["charLevel"] = _validate("level", int(v), lo, hi)

    @property
    def xp(self) -> int:         return int(self._p.get("xp", 0))
    @xp.setter
    def xp(self, v: int):
        lo, hi = FIELD_LIMITS["xp"]
        self._p["xp"] = _validate("xp", int(v), lo, hi)

    @property
    def skill_points(self) -> int:   return int(self._p.get("skillPoints", 0))
    @skill_points.setter
    def skill_points(self, v: int):
        lo, hi = FIELD_LIMITS["skill_points"]
        self._p["skillPoints"] = _validate("skill_points", int(v), lo, hi)

    @property
    def hp(self) -> int:         return int(self._p.get("hp", 0))
    @hp.setter
    def hp(self, v: int):
        lo, hi = FIELD_LIMITS["hp"]
        self._p["hp"] = _validate("hp", int(v), lo, hi)

    @property
    def vitality(self) -> int:   return int(self._p.get("vitality", 0))
    @vitality.setter
    def vitality(self, v: int):
        lo, hi = FIELD_LIMITS["vitality"]
        self._p["vitality"] = _validate("vitality", int(v), lo, hi)

    @property
    def mana(self) -> int:       return int(self._p.get("mana", 0))
    @mana.setter
    def mana(self, v: int):
        lo, hi = FIELD_LIMITS["mana"]
        self._p["mana"] = _validate("mana", int(v), lo, hi)

    @property
    def max_mana(self) -> int:   return int(self._p.get("maxMana", 0))
    @max_mana.setter
    def max_mana(self, v: int):
        lo, hi = FIELD_LIMITS["max_mana"]
        self._p["maxMana"] = _validate("max_mana", int(v), lo, hi)

    @property
    def strength(self) -> int:   return int(self._p.get("strength", 0))
    @strength.setter
    def strength(self, v: int):
        lo, hi = FIELD_LIMITS["strength"]
        self._p["strength"] = _validate("strength", int(v), lo, hi)

    @property
    def intellect(self) -> int:  return int(self._p.get("intellect", 0))
    @intellect.setter
    def intellect(self, v: int):
        lo, hi = FIELD_LIMITS["intellect"]
        self._p["intellect"] = _validate("intellect", int(v), lo, hi)

    @property
    def dexterity(self) -> int:  return int(self._p.get("dexterity", 0))
    @dexterity.setter
    def dexterity(self, v: int):
        lo, hi = FIELD_LIMITS["dexterity"]
        self._p["dexterity"] = _validate("dexterity", int(v), lo, hi)

    # — Status / Survival — (clamp silencioso, sem ValidationError)
    @property
    def poison(self) -> int:         return int(self._p.get("poison", 0))
    @poison.setter
    def poison(self, v: int):
        lo, hi = FIELD_LIMITS["poison"]
        self._p["poison"] = _clamp(int(v), lo, hi)

    @property
    def hunger(self) -> int:         return int(self._p.get("hunger", 0))
    @hunger.setter
    def hunger(self, v: int):
        lo, hi = FIELD_LIMITS["hunger"]
        self._p["hunger"] = _clamp(int(v), lo, hi)

    @property
    def fatigue(self) -> int:        return int(self._p.get("fatigue", 0))
    @fatigue.setter
    def fatigue(self, v: int):
        lo, hi = FIELD_LIMITS["fatigue"]
        self._p["fatigue"] = _clamp(int(v), lo, hi)

    @property
    def drunkenness(self) -> int:    return int(self._p.get("drunkenness", 0))
    @drunkenness.setter
    def drunkenness(self, v: int):
        lo, hi = FIELD_LIMITS["drunkenness"]
        self._p["drunkenness"] = _clamp(int(v), lo, hi)

    @property
    def dead(self) -> bool:          return bool(self._p.get("dead", False))

    @property
    def stamina(self) -> int:        return int(self._p.get("stamina", 0))

    # — Story / Game State —
    @property
    def easy(self) -> bool:          return bool(self._p.get("easy", False))
    @easy.setter
    def easy(self, v: bool):         self._p["easy"] = bool(v)

    @property
    def position(self) -> dict:
        """Posição do jogador no mundo: {'x': float, 'y': float, 'z': float}."""
        pos = self._p.get("position", {})
        return {"x": float(pos.get("x", 0.0)),
                "y": float(pos.get("y", 0.0)),
                "z": float(pos.get("z", 0.0))}

    @position.setter
    def position(self, value: dict) -> None:
        """
        Define a posição do jogador (teleporte). Aceita um dict com
        qualquer subconjunto de {'x','y','z'} — campos ausentes preservam
        o valor atual. Coordenadas fora de [-2000, 2000] são clampadas
        (mapas do jogo não excedem esse range).
        """
        current = self.position
        merged = {**current, **{k: v for k, v in value.items() if k in ("x", "y", "z")}}
        clamped = {k: _clamp(float(merged[k]), -2000.0, 2000.0) for k in ("x", "y", "z")}
        self._p["position"] = clamped

    # — Plot Flags —
    @property
    def cup_found(self) -> bool:         return bool(self._p.get("cupFound", False))
    @cup_found.setter
    def cup_found(self, v: bool):        self._p["cupFound"] = bool(v)

    @property
    def cup_dream_index(self) -> int:    return int(self._p.get("cupDreamIndex", 0))
    @cup_dream_index.setter
    def cup_dream_index(self, v: int):
        lo, hi = FIELD_LIMITS["cup_dream_index"]
        self._p["cupDreamIndex"] = _clamp(int(v), lo, hi)

    @property
    def sapling_planted(self) -> bool:   return bool(self._p.get("saplingPlanted", False))
    @sapling_planted.setter
    def sapling_planted(self, v: bool):  self._p["saplingPlanted"] = bool(v)

    @property
    def sapling_planted_level(self) -> int: return int(self._p.get("saplingPlantedLevel", 0))
    @sapling_planted_level.setter
    def sapling_planted_level(self, v: int):
        lo, hi = FIELD_LIMITS["dungeon_level"]
        self._p["saplingPlantedLevel"] = _clamp(int(v), lo, hi)

    @property
    def sapling_planted_position(self) -> dict:
        """Posição {'x','y','z'} onde o sapling foi plantado."""
        pos = self._p.get("saplingPlantedPosition", {})
        return {"x": float(pos.get("x", 0.0)),
                "y": float(pos.get("y", 0.0)),
                "z": float(pos.get("z", 0.0))}

    @sapling_planted_position.setter
    def sapling_planted_position(self, value: dict) -> None:
        """Mesma semântica de `position`: merge parcial + clamp em world_position."""
        current = self.sapling_planted_position
        merged = {**current, **{k: v for k, v in value.items() if k in ("x", "y", "z")}}
        lo, hi = FIELD_LIMITS["world_position"]
        clamped = {k: _clamp(float(merged[k]), lo, hi) for k in ("x", "y", "z")}
        self._p["saplingPlantedPosition"] = clamped

    @property
    def moonstone_dropped(self) -> bool:    return bool(self._p.get("moonstoneDropped", False))
    @moonstone_dropped.setter
    def moonstone_dropped(self, v: bool):   self._p["moonstoneDropped"] = bool(v)

    @property
    def moonstone_dropped_level(self) -> int: return int(self._p.get("moonstoneDroppedLevel", 0))
    @moonstone_dropped_level.setter
    def moonstone_dropped_level(self, v: int):
        lo, hi = FIELD_LIMITS["dungeon_level"]
        self._p["moonstoneDroppedLevel"] = _clamp(int(v), lo, hi)

    @property
    def moonstone_dropped_position(self) -> dict:
        """Posição {'x','y','z'} onde a moonstone foi derrubada."""
        pos = self._p.get("moonstoneDroppedPosition", {})
        return {"x": float(pos.get("x", 0.0)),
                "y": float(pos.get("y", 0.0)),
                "z": float(pos.get("z", 0.0))}

    @moonstone_dropped_position.setter
    def moonstone_dropped_position(self, value: dict) -> None:
        current = self.moonstone_dropped_position
        merged = {**current, **{k: v for k, v in value.items() if k in ("x", "y", "z")}}
        lo, hi = FIELD_LIMITS["world_position"]
        clamped = {k: _clamp(float(merged[k]), lo, hi) for k in ("x", "y", "z")}
        self._p["moonstoneDroppedPosition"] = clamped

    @property
    def garamon_at_rest(self) -> bool:      return bool(self._p.get("garamonAtRest", False))
    @garamon_at_rest.setter
    def garamon_at_rest(self, v: bool):     self._p["garamonAtRest"] = bool(v)

    @property
    def entered_green_moongate(self) -> bool:   return bool(self._p.get("enteredGreenMoongate", False))
    @entered_green_moongate.setter
    def entered_green_moongate(self, v: bool):  self._p["enteredGreenMoongate"] = bool(v)

    @property
    def map_tiles_revealed(self) -> int:
        """
        Contagem de tiles do mapa revelados (fog of war). Apenas leitura
        — é derivado da matriz de tiles em mapData (mappedRLE), não um
        contador independente que possa ser editado de forma segura sem
        recalcular a matriz correspondente.
        """
        return int(self._p.get("mapTilesRevealed", 0))

    @property
    def said_fanlo(self) -> bool:    return bool(self._p.get("saidFanlo", False))
    @said_fanlo.setter
    def said_fanlo(self, v: bool):   self._p["saidFanlo"] = bool(v)

    @property
    def talismans_collected(self) -> int:    return int(self._p.get("talismansCollected", 0))
    @talismans_collected.setter
    def talismans_collected(self, v: int):
        lo, hi = FIELD_LIMITS["talismans"]
        self._p["talismansCollected"] = _validate("talismans_collected", int(v), lo, hi)

    @property
    def talismans_destroyed(self) -> int:    return int(self._p.get("talismansDestroyed", 0))
    @talismans_destroyed.setter
    def talismans_destroyed(self, v: int):
        lo, hi = FIELD_LIMITS["talismans"]
        self._p["talismansDestroyed"] = _validate("talismans_destroyed", int(v), lo, hi)

    # — Progressão —
    @property
    def dreams_remaining(self) -> list:  return list(self._p.get("dreamsRemaining", []))

    @dreams_remaining.setter
    def dreams_remaining(self, values: list[int]) -> None:
        """
        Define dreamsRemaining (lista de 6 contadores de sonhos restantes
        por talismã). Cada valor é clampado em FIELD_LIMITS["dream_count"].
        Apenas os índices presentes em `values` são sobrescritos; o
        tamanho da lista original é preservado.
        """
        lo, hi = FIELD_LIMITS["dream_count"]
        current = list(self._p.get("dreamsRemaining", []))
        for i, v in enumerate(values):
            if i >= len(current):
                current.append(0)
            current[i] = _clamp(int(v), lo, hi)
        self._p["dreamsRemaining"] = current

    @property
    def time_of_last_dream(self) -> float:   return float(self._p.get("timeOfLastDream", 0))

    @property
    def global_vars(self) -> list:       return list(self._p.get("globalVars", []))

    @global_vars.setter
    def global_vars(self, values: dict[int, int]) -> None:
        """
        Atualiza globalVars[64] (private global variables — ver formato
        bglobals.dat) a partir de um dict {índice: valor}.

        Cada slot é um Int16 do formato original; valores são clampados em
        FIELD_LIMITS["global_var"] = (-32768, 32767). Índices fora do range
        atual de globalVars são ignorados (a lista nunca é redimensionada —
        seu tamanho é definido por babglobs.dat e não deve mudar).
        """
        lo, hi = FIELD_LIMITS["global_var"]
        gv = list(self._p.get("globalVars", []))
        for idx, val in values.items():
            idx = int(idx)
            if 0 <= idx < len(gv):
                gv[idx] = _clamp(int(val), lo, hi)
            else:
                logger.warning("global_vars: índice %d fora do range (0-%d), ignorado", idx, len(gv) - 1)
        self._p["globalVars"] = gv

    def get_global_var(self, index: int) -> int:
        gv = self._p.get("globalVars", [])
        return int(gv[index]) if 0 <= index < len(gv) else 0

    # — Skills —
    def get_skill(self, name: str) -> int:
        idx = NOMES_SKILLS.index(name) if name in NOMES_SKILLS else -1
        skills = self._p.get("skill", [])
        return int(skills[idx]) if 0 <= idx < len(skills) else 0

    def set_skill(self, name: str, value: int) -> None:
        idx = NOMES_SKILLS.index(name) if name in NOMES_SKILLS else -1
        if idx < 0:
            return
        lo, hi = FIELD_LIMITS["skill"]
        value = _validate(f"skill[{name}]", int(value), lo, hi)
        skills = self._p.get("skill", [])
        while len(skills) <= idx:
            skills.append(0)
        skills[idx] = value
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
