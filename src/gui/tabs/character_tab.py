"""
CharacterTab — Orquestrador da aba de personagem.

Responsabilidade única: montar os painéis de componente, rotear
load/get_values/get_story_overrides e conectar os callbacks de
portrait e género entre os painéis e o app.

Toda a lógica de UI vive nos painéis de characters/components/.
Toda a lógica de coerção de dados vive em characters/filters.py.
Toda a constante de campos vive em characters/character_model.py.
"""

import tkinter as tk
from tkinter import ttk

from .common.base_tab import BaseTab

from .characters.components.identity_panel      import IdentityPanel
from .characters.components.attributes_panel    import AttributesPanel
from .characters.components.dungeon_state_panel import DungeonStatePanel
from .characters.components.status_panel        import StatusPanel
from .characters.components.progression_panel   import ProgressionPanel
from .characters.components.statistics_panel    import StatisticsPanel
from .characters.filters import build_attrs_payload, build_story_overrides


class CharacterTab(BaseTab):
    """
    Orquestrador da aba de personagem.

    Layout (3 colunas):
      Col 1:  IdentityPanel + AttributesPanel + DungeonStatePanel
      Col 2:  StatusPanel   + ProgressionPanel
      Col 3:  StatisticsPanel
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        # Painéis instanciados em _build_ui(); declarados aqui para
        # que type-checkers e IDEs os reconheçam antes de super().__init__
        self._identity:    IdentityPanel
        self._attributes:  AttributesPanel
        self._dungeon:     DungeonStatePanel
        self._status:      StatusPanel
        self._progression: ProgressionPanel
        self._statistics:  StatisticsPanel

        super().__init__(parent, title="Character")

    # ------------------------------------------------------------------
    # BaseTab API
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        col1 = ttk.Frame(self)
        col2 = ttk.Frame(self)
        col3 = ttk.Frame(self)
        col1.grid(row=0, column=0, sticky="n", padx=(0, 12))
        col2.grid(row=0, column=1, sticky="n", padx=(0, 12))
        col3.grid(row=0, column=2, sticky="n")

        self._identity    = IdentityPanel(col1)
        self._attributes  = AttributesPanel(col1)
        self._dungeon     = DungeonStatePanel(col1)
        self._status      = StatusPanel(col2)
        self._progression = ProgressionPanel(col2)
        self._statistics  = StatisticsPanel(col3)

    def load(self, save_game) -> None:
        """Propaga o save para todos os painéis."""
        super().load(save_game)
        player = save_game.player

        self._identity.load(player, save_game)
        self._attributes.load(player)
        self._dungeon.load(player)
        self._status.load(player)
        self._progression.load(player)
        self._statistics.load(player)

        self.clear_changes()

    # ------------------------------------------------------------------
    # Getters (interface pública consumida por app.py)
    # ------------------------------------------------------------------

    def get_values(self) -> dict:
        """Consolida os vars de todos os painéis num payload de atributos."""
        all_vars = {}
        all_vars.update(self._identity.get_vars())
        all_vars.update(self._attributes.get_vars())
        all_vars.update(self._status.get_vars())
        all_vars.update(self._progression.get_vars())
        return build_attrs_payload(all_vars)

    def get_story_overrides(self) -> dict:
        """Retorna easy, position e dreams_remaining para SavePayload.story."""
        return build_story_overrides(
            easy_var=self._dungeon.easy_var,
            pos_x=self._dungeon.pos_x_var,
            pos_y=self._dungeon.pos_y_var,
            pos_z=self._dungeon.pos_z_var,
            dream_vars=self._progression.dream_vars,
        )

    # ------------------------------------------------------------------
    # Callbacks (conectados pelo app.py)
    # ------------------------------------------------------------------

    def on_portrait_change(self, fn) -> None:
        """Registra callback chamado quando o portrait muda."""
        self._identity.on_portrait_change(fn)

    def on_gender_change(self, fn) -> None:
        """Registra callback chamado quando o género muda."""
        self._identity.on_gender_change(fn)
