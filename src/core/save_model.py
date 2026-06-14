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
# ValidationError — levantada quando um valor viola os limites do jogo.
#
# Carrega metadados suficientes para a GUI exibir uma mensagem útil:
#   field   → nome do campo (ex: "hp")
#   value   → valor rejeitado
#   lo / hi → limites permitidos (None = sem limite nesse lado)
# ---------------------------------------------------------------------------

class ValidationError(ValueError):
    def __init__(self, field: str, value, lo=None, hi=None, msg: str = ""):
        self.field = field
        self.value = value
        self.lo    = lo
        self.hi    = hi
        if not msg:
            parts = []
            if lo is not None: parts.append(f">= {lo}")
            if hi is not None: parts.append(f"<= {hi}")
            msg = f"'{field}' = {value!r} está fora do intervalo permitido ({' e '.join(parts) or 'desconhecido'})"
        super().__init__(msg)


# ---------------------------------------------------------------------------
# Limites dos campos editáveis do PlayerModel.
#
# Cada entrada: (min_inclusive, max_inclusive); None = sem limite nesse lado.
#
# - Atributos de progressão/combate usam _validate (levanta ValidationError):
#   um HP negativo ou level 0 é um erro de digitação, não uma escolha válida.
# - Campos de status/sobrevivência usam _clamp (silencioso): valores extremos
#   são válidos em edição — o jogo já os normaliza no próprio runtime.
# ---------------------------------------------------------------------------

FIELD_LIMITS: dict[str, tuple] = {
    "hp":           (0,   9999),
    "vitality":     (1,   9999),
    "mana":         (0,   9999),
    "max_mana":     (0,   9999),

    "level":        (1,    255),
    "xp":           (0, 999_999_999),
    "skill_points": (0,  9999),

    "strength":     (1,    255),
    "intellect":    (1,    255),
    "dexterity":    (1,    255),

    "poison":       (0,    255),
    "hunger":       (0,    255),
    "fatigue":      (0,    255),
    "drunkenness":  (0,    255),

    "portrait":     (0,      9),
    "player_class": (0,      7),

    "skill":        (0,     30),

    # — Story / Game State (Sprint 10) —
    "dungeon_level":   (0,      9),   # 10 níveis de masmorra (0-9)
    "cup_dream_index": (0,      5),   # índice no array dreamsRemaining[6]
    "dream_count":     (0,     99),   # contador de sonhos restantes por talismã
    "talismans":       (0,     64),   # talismansCollected / talismansDestroyed
    "global_var":      (-32768, 32767),  # Int16 — formato bglobals.dat
    "world_position":  (-2000.0, 2000.0),  # coordenadas x/y/z do mundo
}


def _clamp(value: int, lo: int | None, hi: int | None) -> int:
    """Aplica min/max sem levantar exceção — usado em campos de sobrevivência."""
    if lo is not None: value = max(lo, value)
    if hi is not None: value = min(hi, value)
    return value


def _validate(field: str, value: int, lo: int | None, hi: int | None) -> int:
    """Valida e retorna o valor, ou levanta ValidationError."""
    if lo is not None and value < lo:
        raise ValidationError(field, value, lo=lo, hi=hi)
    if hi is not None and value > hi:
        raise ValidationError(field, value, lo=lo, hi=hi)
    return value


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

    def __init__(self, node: dict, _parent: "GameObject | None" = None) -> None:
        self._node = node
        self._parsed: dict | None = None
        self._parent = _parent

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
        """
        Re-serializa parsed_data para jsonData, se já foi carregado.
        Propaga para o GameObject pai (se houver), já que o nó deste
        objeto pode viver dentro de parsed_data["contents"] do pai —
        sem propagar, a mudança ficaria presa no parsed_data em cache
        do pai e nunca chegaria ao jsonData persistido dele.
        """
        if self._parsed is not None:
            self._node["jsonData"] = json.dumps(self._parsed)
        if self._parent is not None:
            self._parent.commit()

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
        return [GameObject(it, _parent=self) for it in items]

    @property
    def contents_count(self) -> int:
        items = self._node.get("contents") or self.parsed_data.get("contents") or []
        return len(items)

    def _contents_list(self) -> list | None:
        """Retorna a lista `contents` real (node ou parsed_data), ou None se inexistente."""
        if "contents" in self._node:
            return self._node["contents"]
        if "contents" in self.parsed_data:
            return self.parsed_data["contents"]
        return None

    def delete_content(self, index: int) -> None:
        """Remove o item de índice `index` da lista `contents` deste container."""
        items = self._contents_list()
        if items is None or not (0 <= index < len(items)):
            logger.error("GameObject.delete_content: índice fora de alcance: %d", index)
            return
        removed = items.pop(index)
        self.commit()
        logger.info("Content #%d removed from %r: %r", index, self.object_name, removed.get("objectName"))

    # — Critters (campos lidos/escritos em parsed_data) —
    @property
    def hp(self) -> int:
        return int(self.parsed_data.get("hp", 0))

    @hp.setter
    def hp(self, value: int) -> None:
        """
        Ajusta o HP da criatura. Clampa em [0, originalHp] quando originalHp
        é conhecido, para evitar valores fora de faixa (overheal silencioso).
        Setar para 0 também marca deathProcessed, igual ao comportamento do jogo.
        """
        value = int(value)
        max_hp = self.parsed_data.get("originalHp", value)
        value = max(0, min(value, max_hp) if max_hp else value)
        self.parsed_data["hp"] = value
        if value <= 0:
            self.parsed_data["deathProcessed"] = True
        self.commit()

    @property
    def is_dead(self) -> bool:
        return bool(self.parsed_data.get("deathProcessed", False)) or self.hp <= 0

    def revive(self, hp: int | None = None) -> None:
        """Marca a criatura como viva, restaurando HP (default: originalHp ou 1)."""
        restored = hp if hp is not None else self.parsed_data.get("originalHp", 1)
        self.parsed_data["deathProcessed"] = False
        self.parsed_data["hp"] = max(1, int(restored))
        self.commit()

    def kill(self) -> None:
        """Marca a criatura como morta (hp=0, deathProcessed=True)."""
        self.parsed_data["hp"] = 0
        self.parsed_data["deathProcessed"] = True
        self.commit()


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
    @current_level.setter
    def current_level(self, v: int) -> None:
        """
        Define o nível de masmorra atual do jogador (teleporte entre níveis).
        Clampado em FIELD_LIMITS["dungeon_level"] = (0, 9) — os 10 níveis
        existentes em worldObjectsByLevel.
        """
        lo, hi = FIELD_LIMITS["dungeon_level"]
        # Limita também ao número real de níveis presentes no save, caso
        # worldObjectsByLevel tenha menos de 10 entradas.
        max_level = min(hi, len(self._raw.get("worldObjectsByLevel", [])) - 1)
        if max_level < lo:
            max_level = hi
        self._raw["currentLevel"] = _clamp(int(v), lo, max_level)

    # — Blocos não-editáveis por enquanto —
    @property
    def inventory_data(self) -> dict:    return self._raw.get("inventoryData", {})
    @property
    def world_objects(self) -> list:     return self._raw.get("worldObjects", [])
    @property
    def world_objects_by_level(self) -> list: return self._raw.get("worldObjectsByLevel", [])
    @property
    def map_data(self) -> dict:          return self._raw.get("mapData", {})

    # — Map Annotations (Sprint 10) —
    #
    # mapData = {"pages": [{"mappedRLE": "...", "notes": [...]}]}
    #
    # Cada "note" é um dict de forma livre (tipicamente {"x", "y", "text"}).
    # A API abaixo trata `notes` apenas como uma lista de dicts — não impõe
    # um schema rígido, preservando quaisquer chaves desconhecidas em notas
    # existentes (mappedRLE nunca é tocado).

    def get_map_notes(self, page: int = 0) -> list[dict]:
        """Retorna a lista de anotações da página `page` (cópia rasa)."""
        pages = self._raw.get("mapData", {}).get("pages", [])
        if not (0 <= page < len(pages)):
            return []
        return list(pages[page].get("notes", []))

    def add_map_note(self, page: int, note: dict) -> bool:
        """
        Adiciona uma anotação à página `page`. `note` é armazenado como veio
        (ex: {"x": 10, "y": 20, "text": "Tesouro aqui"}). Retorna False se a
        página não existir.
        """
        pages = self._raw.get("mapData", {}).get("pages", [])
        if not (0 <= page < len(pages)):
            logger.warning("add_map_note: página %d fora do range (%d páginas)", page, len(pages))
            return False
        pages[page].setdefault("notes", []).append(dict(note))
        return True

    def update_map_note(self, page: int, index: int, note: dict) -> bool:
        """
        Substitui a anotação `index` da página `page` por `note`.
        Retorna False se página ou índice forem inválidos.
        """
        pages = self._raw.get("mapData", {}).get("pages", [])
        if not (0 <= page < len(pages)):
            return False
        notes = pages[page].setdefault("notes", [])
        if not (0 <= index < len(notes)):
            logger.warning("update_map_note: índice %d fora do range (%d notas)", index, len(notes))
            return False
        notes[index] = dict(note)
        return True

    def delete_map_note(self, page: int, index: int) -> bool:
        """Remove a anotação `index` da página `page`. Retorna False se inválido."""
        pages = self._raw.get("mapData", {}).get("pages", [])
        if not (0 <= page < len(pages)):
            return False
        notes = pages[page].setdefault("notes", [])
        if not (0 <= index < len(notes)):
            logger.warning("delete_map_note: índice %d fora do range (%d notas)", index, len(notes))
            return False
        notes.pop(index)
        return True

    @property
    def map_page_count(self) -> int:
        return len(self._raw.get("mapData", {}).get("pages", []))

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
