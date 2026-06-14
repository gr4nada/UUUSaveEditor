# src/core/save_controller.py
"""
SaveController — orquestra load/save do save game, sem dependências de Tkinter.

Concentra a lógica que antes vivia em EditorApp (_on_load, _on_save, _on_cheat,
_equipped_for_preview, _inject_dungeon_level), permitindo testá-la isoladamente
da camada de UI.

Sprint 2: o controller agora opera sobre `SaveGame` (src.core.save_model) em
vez de indexar `raw_save` diretamente. `raw_save` continua exposto (é o que
save_manager persiste), mas leituras/escritas de domínio passam pela API
tipada — quest flags, magicData, equipped/main inventory, dungeon level.

Uso típico (na GUI):

    controller = SaveController()
    save_game  = controller.load(slot)          # levanta exceção em caso de erro
    ...
    controller.save(SavePayload(attrs=..., skills=..., flags=..., cast_spells=...))
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from src.core.character    import update_character, cheat_max_all_skills
from src.core.inventory     import get_equipment_summary
from src.core.save_manager  import load_save, save_game_data
from src.core.save_model    import SaveGame

logger = logging.getLogger("core.save_controller")


@dataclass
class SavePayload:
    """Dados coletados da UI no momento de gravar."""
    attrs:       dict
    skills:      dict
    flags:       dict              # {flag_name: bool}, vindos de get_flags()
    cast_spells: list[bool] = field(default_factory=list)  # vazio = não altera magicData
    story:       dict | None = None  # Sprint 10 — campos da aba Story (ver StoryTab.get_story_data())


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
        return self.save_game is not None

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
        """Retorna (critters, items) do save atual via SaveGame.parse_world()."""
        if not self.save_game:
            return [], []
        return self.save_game.parse_world()

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, payload: SavePayload) -> SaveGame:
        """
        Aplica o payload ao save atual, persiste em disco e retorna o
        SaveGame resultante (reconstruído a partir do raw_save atualizado).

        Levanta ValueError se algum campo numérico for inválido, ou
        qualquer outra exceção de I/O propagada de save_game_data.
        """
        if not self.save_game or not self.raw_save:
            raise RuntimeError("Nenhum save carregado.")

        # --- Validação cruzada antes de gravar qualquer campo ---
        # hp não pode exceder vitality, mana não pode exceder maxMana.
        # Valores ausentes em payload.attrs caem no valor atual do player,
        # então editar só um dos dois lados da relação continua seguro.
        from src.core.save_model import ValidationError
        p = self.save_game.player

        new_hp       = int(payload.attrs.get("hp",       p.hp))
        new_vitality = int(payload.attrs.get("vitality", p.vitality))
        new_mana     = int(payload.attrs.get("mana",     p.mana))
        new_max_mana = int(payload.attrs.get("maxMana",  p.max_mana))

        if new_hp > new_vitality:
            raise ValidationError(
                "hp", new_hp,
                msg=f"'hp' ({new_hp}) não pode ser maior que 'vitality' ({new_vitality})"
            )
        if new_mana > new_max_mana:
            raise ValidationError(
                "mana", new_mana,
                msg=f"'mana' ({new_mana}) não pode ser maior que 'maxMana' ({new_max_mana})"
            )

        self.save_game.player.quest_flags = payload.flags
        self.save_game.player.cast_spells = payload.cast_spells

        # --- Sprint 10: campos da aba Story ---
        # Aplicados via setters tipados de PlayerModel/SaveGame (cada um já
        # clampa/valida no padrão estabelecido). Todos os campos são
        # opcionais — apenas os presentes em payload.story são tocados.
        if payload.story:
            self._apply_story(payload.story)

        update_character(self.raw_save, payload.attrs, payload.skills)

        save_game_data(self.selected_slot, self.raw_save)

        self.save_game = SaveGame(self.raw_save)
        self._inject_dungeon_level()
        return self.save_game

    def _apply_story(self, story: dict) -> None:
        """
        Aplica os campos da aba Story a save_game.player / save_game.

        Mapa de chaves esperadas em `story` (todas opcionais):
            easy, position, current_level, cup_found, cup_dream_index,
            sapling_planted, sapling_planted_level, moonstone_dropped,
            moonstone_dropped_level, garamon_at_rest, entered_green_moongate,
            said_fanlo, talismans_collected, talismans_destroyed,
            dreams_remaining, global_vars
        """
        p  = self.save_game.player
        sg = self.save_game

        _BOOL_FIELDS = (
            "easy", "cup_found", "sapling_planted", "moonstone_dropped",
            "garamon_at_rest", "entered_green_moongate", "said_fanlo",
        )
        _INT_FIELDS = (
            "cup_dream_index", "sapling_planted_level", "moonstone_dropped_level",
            "talismans_collected", "talismans_destroyed",
        )

        for field_name in _BOOL_FIELDS:
            if field_name in story:
                setattr(p, field_name, bool(story[field_name]))

        for field_name in _INT_FIELDS:
            if field_name in story:
                setattr(p, field_name, int(story[field_name]))

        if "position" in story:
            p.position = story["position"]

        if "sapling_planted_position" in story:
            p.sapling_planted_position = story["sapling_planted_position"]

        if "moonstone_dropped_position" in story:
            p.moonstone_dropped_position = story["moonstone_dropped_position"]

        if "current_level" in story:
            sg.current_level = int(story["current_level"])

        if "dreams_remaining" in story:
            p.dreams_remaining = story["dreams_remaining"]

        if "global_vars" in story:
            # global_vars vem como {index: value} — chaves podem ser str (JSON) ou int
            p.global_vars = {int(k): v for k, v in story["global_vars"].items()}

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
        if not self.save_game:
            return {}
        result = {}
        for idx, obj in enumerate(self.save_game.equipped_items):
            result[idx] = {
                "objectType":   obj.object_type,
                "qualityClass": obj.parsed_data.get("qualityClass", 0),
            }
        return result

    def preview_data(self, portrait_id: int | None = None) -> dict:
        """
        Monta os kwargs esperados por CharacterPreviewWidget.update(...).
        Se portrait_id não for informado, usa o portrait atual do player.
        """
        if not self.save_game:
            return {}
        p = self.save_game.player
        return {
            "portrait_id":    portrait_id if portrait_id is not None else p.portrait,
            "equipped_slots": self.equipped_for_preview(),
            "name":           p.name,
            "class_name":     p.player_class_name,
            "level":          p.level,
            "dungeon_level":  self.save_game.dungeon_level,
        }

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _inject_dungeon_level(self) -> None:
        """
        Injeta o dungeon level atual no playerData temporariamente para que
        character_tab.load() o possa exibir sem alterar o model persistido.

        TODO (Sprint 2 cont.): mover character_tab para receber `SaveGame`
        em vez de `PlayerModel` e ler `save_game.dungeon_level` diretamente,
        eliminando este hack de injeção.
        """
        if not self.save_game:
            return
        self.save_game.player._p["__dungeon_level__"] = self.save_game.dungeon_level
