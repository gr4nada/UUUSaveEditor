# src/core/save_controller.py
"""
SaveController — orquestra load/save do save game, sem dependências de Tkinter.

Concentra a lógica que antes vivia em EditorApp (_on_load, _on_save, _on_cheat,
_equipped_for_preview, _inject_dungeon_level), permitindo testá-la isoladamente
da camada de UI.

Uso típico (na GUI):

    controller = SaveController()
    save_game  = controller.load(slot)          # levanta exceção em caso de erro
    ...
    controller.save(SavePayload(attrs=..., skills=..., flags=..., cast_spells=...))
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from src.core.character    import update_character, cheat_max_all_skills
from src.core.inventory     import get_equipment_summary
from src.core.save_manager  import load_save, save_game_data
from src.core.save_model    import SaveGame
from src.core.world_parser  import parse_world
# QUEST_FLAGS é dado puro (sem dependências de Tkinter); importado daqui por
# conveniência para não duplicar a tabela. Candidato a mover para src/core
# se mais lógica de core passar a depender dela.
from src.gui.constants       import QUEST_FLAGS

logger = logging.getLogger("core.save_controller")


@dataclass
class SavePayload:
    """Dados coletados da UI no momento de gravar."""
    attrs:       dict
    skills:      dict
    flags:       dict              # {flag_name: bool}, vindos de get_flags()
    cast_spells: list[bool] = field(default_factory=list)  # vazio = não altera magicData


class SaveController:
    """
    Mantém o estado do save atualmente carregado e oferece operações de
    load/save/cheat sobre ele. Não conhece widgets — devolve dados puros
    (dict, SaveGame, listas) para a camada de UI consumir.
    """

    def __init__(self) -> None:
        self.raw_save:      dict | None     = None
        self.save_game:     SaveGame | None = None
        self.selected_slot: int             = 0

    # ------------------------------------------------------------------
    # Estado derivado
    # ------------------------------------------------------------------

    @property
    def is_loaded(self) -> bool:
        return self.raw_save is not None

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self, slot: int) -> SaveGame:
        """
        Carrega o save do slot indicado, atualiza o estado interno e retorna
        o SaveGame resultante. Propaga exceções de load_save/SaveGame para
        que a UI decida como reportar o erro.
        """
        self.selected_slot = slot
        self.raw_save  = load_save(slot)
        self.save_game = SaveGame(self.raw_save)
        self._inject_dungeon_level()
        return self.save_game

    def parse_world(self) -> tuple[list, list]:
        """Retorna (critters, items) do save atual via world_parser."""
        if not self.raw_save:
            return [], []
        return parse_world(self.raw_save)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, payload: SavePayload) -> SaveGame:
        """
        Aplica o payload ao raw_save atual, persiste em disco e retorna o
        novo SaveGame (já recarregado a partir do raw_save atualizado).

        Levanta ValueError se algum campo numérico for inválido, ou
        qualquer outra exceção de I/O propagada de save_game_data.
        """
        if not self.raw_save:
            raise RuntimeError("Nenhum save carregado.")

        self._apply_quest_flags(payload.flags)
        update_character(self.raw_save, payload.attrs, payload.skills)

        if payload.cast_spells:
            self.raw_save["playerData"].setdefault("magicData", {})["castSpells"] = payload.cast_spells

        save_game_data(self.selected_slot, self.raw_save)

        self.save_game = SaveGame(self.raw_save)
        self._inject_dungeon_level()
        return self.save_game

    def _apply_quest_flags(self, editor_flags: dict) -> None:
        """
        Reescreve apenas os IDs declarados em QUEST_FLAGS dentro de questFlags,
        operando sobre uma cópia da lista original para não corromper flags
        fora do escopo do editor (a lista pode ter mais entradas do que o
        editor conhece).
        """
        original_qlist: list = self.raw_save["playerData"].get("questFlags", [])
        qlist = list(original_qlist)            # cópia — nunca muta a lista original diretamente
        max_id = max(q["id"] for q in QUEST_FLAGS)
        while len(qlist) <= max_id:             # expande só se necessário
            qlist.append(False)
        for q in QUEST_FLAGS:
            qlist[q["id"]] = editor_flags[q["flag"]]  # sobrescreve apenas os IDs conhecidos
        self.raw_save["playerData"]["questFlags"] = qlist

    # ------------------------------------------------------------------
    # Cheats
    # ------------------------------------------------------------------

    def cheat_max_skills(self, value: int = 30) -> None:
        if not self.raw_save:
            raise RuntimeError("Nenhum save carregado.")
        cheat_max_all_skills(self.raw_save, value=value)

    # ------------------------------------------------------------------
    # Equipamento / Preview
    # ------------------------------------------------------------------

    def equipment_summary(self) -> list[dict]:
        if not self.raw_save:
            return []
        return get_equipment_summary(self.raw_save)

    def equipped_for_preview(self) -> dict:
        """Retorna {slot_index: {objectType, qualityClass}} do save atual."""
        if not self.raw_save:
            return {}
        result = {}
        items = self.raw_save.get("inventoryData", {}).get("equippedItems", [])
        for idx, item in enumerate(items):
            jd = {}
            if item.get("jsonData"):
                try:
                    jd = json.loads(item["jsonData"])
                except Exception:
                    pass
            result[idx] = {
                "objectType":   item.get("objectType", 0),
                "qualityClass": jd.get("qualityClass", 0),
            }
        return result

    def preview_data(self, portrait_id: int | None = None) -> dict:
        """
        Monta os kwargs esperados por CharacterPreviewWidget.update(...).
        Se portrait_id não for informado, usa o portrait atual do player.
        """
        if not self.save_game or not self.raw_save:
            return {}
        p = self.save_game.player
        return {
            "portrait_id":    portrait_id if portrait_id is not None else p.portrait,
            "equipped_slots": self.equipped_for_preview(),
            "name":           p.name,
            "class_name":     p.player_class_name,
            "level":          p.level,
            "dungeon_level":  self.raw_save.get("currentLevel", 0),
        }

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _inject_dungeon_level(self) -> None:
        """
        Injeta o dungeon level atual no playerData temporariamente para que
        character_tab.load() o possa exibir sem alterar o model persistido.
        """
        if not self.save_game or not self.raw_save:
            return
        self.save_game.player._p["__dungeon_level__"] = self.raw_save.get("currentLevel", "—")
