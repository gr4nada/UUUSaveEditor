# src/core/models/player.py
"""PlayerModel — typed wrapper over playerData from save."""
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
    Typed wrapper over playerData.

    Usage:
        model = PlayerModel(raw_save["playerData"])
        model.hp           # read
        model.hp = 999     # write back to original dict
    """

    def __init__(self, player_data: dict) -> None:
        self._p = player_data

    # — Identity —
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

    # — Attributes —
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

    # — Status / Survival — (silent clamp, no ValidationError)
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
        """Player position in the world: {'x': float, 'y': float, 'z': float}."""
        pos = self._p.get("position", {})
        return {"x": float(pos.get("x", 0.0)),
                "y": float(pos.get("y", 0.0)),
                "z": float(pos.get("z", 0.0))}

    @position.setter
    def position(self, value: dict) -> None:
        """
        Sets the player's position (teleport). Accepts a dict with
        any subset of {'x','y','z'} — missing fields preserve the
        current value. Coordinates outside [-2000, 2000] are clamped
        (game maps don't exceed this range).
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
        """Position {'x','y','z'} where the sapling was planted."""
        pos = self._p.get("saplingPlantedPosition", {})
        return {"x": float(pos.get("x", 0.0)),
                "y": float(pos.get("y", 0.0)),
                "z": float(pos.get("z", 0.0))}

    @sapling_planted_position.setter
    def sapling_planted_position(self, value: dict) -> None:
        """Same semantics as `position`: partial merge + clamp to world_position."""
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
        """Position {'x','y','z'} where the moonstone was dropped."""
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
        Count of map tiles revealed (fog of war). Read-only
        — it is derived from the tile matrix in mapData (mappedRLE), not an
        independent counter that can be safely edited without
        recalculating the corresponding matrix.
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

    # — Progression —
    @property
    def dreams_remaining(self) -> list:  return list(self._p.get("dreamsRemaining", []))

    @dreams_remaining.setter
    def dreams_remaining(self, values: list[int]) -> None:
        """
        Sets dreamsRemaining (list of 6 dream counters remaining
        per talisman). Each value is clamped to FIELD_LIMITS["dream_count"].
        Only indexes present in `values` are overwritten; the
        original list size is preserved.
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
        Updates globalVars[64] (private global variables — see format
        bglobals.dat) from a dict {index: value}.

        Each slot is an Int16 from original format; values are clamped to
        FIELD_LIMITS["global_var"] = (-32768, 32767). Indexes out of current
        globalVars range are ignored (list is never resized —
        its size is defined by bglobals.dat and must not change).
        """
        lo, hi = FIELD_LIMITS["global_var"]
        gv = list(self._p.get("globalVars", []))
        for idx, val in values.items():
            idx = int(idx)
            if 0 <= idx < len(gv):
                gv[idx] = _clamp(int(val), lo, hi)
            else:
                logger.warning("global_vars: index %d out of range (0-%d), ignored", idx, len(gv) - 1)
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
    def quest_flags(self, flags_by_name: dict[str, int | bool]) -> None:
        """
        Rewrites only the IDs declared in QUEST_FLAGS within questFlags,
        from a dict {flag_name: int | bool}. Expands list with 0 if
        needed; IDs outside editor's knowledge are preserved.

        Accepts both bool (compatibility with old UI, where True/False
        map to 1/0) and int (Sprint 13 — Quest Intelligence, where
        the value encodes a narrative state from 0..N). Negative values are
        clamped to 0; upper limit is validated against
        quest_states.max_known_state() only as reference — higher values
        are preserved (may be legitimate game states still
        undocumented), only logged.
        """
        from src.core.database.quest_states import max_known_state
        import logging
        logger = logging.getLogger("core.models.player")

        qlist = list(self._p.get("questFlags", []))
        max_id = max(q["id"] for q in QUEST_FLAGS)
        # Expand with False (not 0) to preserve `is True`/`is False` in
        # legacy tests that compare bool identity on newly-created slots
        # — bool is subclass of int, so 0/1 work the same for any numeric use,
        # but `qlist[i] is False` is only true if the expanded value is
        # actually the bool singleton.
        while len(qlist) <= max_id:
            qlist.append(False)
        for q in QUEST_FLAGS:
            if q["flag"] in flags_by_name:
                raw = flags_by_name[q["flag"]]
                if isinstance(raw, bool):
                    # Compatibility with old UI / existing tests:
                    # bool is persisted as bool (True/False), not as
                    # int, to preserve `is True`/`is False`.
                    qlist[q["id"]] = raw
                    continue
                value = max(0, int(raw))
                known_max = max_known_state(q["flag"])
                if value > known_max:
                    logger.info(
                        "questFlags[%s] = %d exceeds largest documented state "
                        "(%d) — value preserved unchanged.",
                        q["flag"], value, known_max,
                    )
                qlist[q["id"]] = value
        self._p["questFlags"] = qlist

    def get_quest_flags_by_name(self) -> dict[str, bool]:
        """
        Returns {flag_name: bool} for all known QUEST_FLAGS.

        Kept for compatibility with existing code that only needs
        to know if the flag is "active" (value != 0), without distinguishing
        estados narrativos. Para o valor inteiro completo, use
        get_quest_states_by_name().
        """
        qlist = self._p.get("questFlags", [])
        result = {}
        for q in QUEST_FLAGS:
            idx = q["id"]
            result[q["flag"]] = bool(qlist[idx]) if idx < len(qlist) else False
        return result

    def get_quest_states_by_name(self) -> dict[str, int]:
        """
        Retorna {flag_name: int} com o valor bruto de questFlags para cada
        QUEST_FLAGS conhecido — Sprint 13 (Quest Intelligence).

        Use junto com src.core.database.quest_states.describe_state() para
        obter o label/descrição narrativa do estado atual.
        """
        qlist = self._p.get("questFlags", [])
        result = {}
        for q in QUEST_FLAGS:
            idx = q["id"]
            result[q["flag"]] = int(qlist[idx]) if idx < len(qlist) else 0
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
