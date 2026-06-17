# src/gui/tabs/characters/components/identity_panel.py
"""
IdentityPanel — Name, Class, Hand, Gender, Portrait, Dungeon Level.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.gui.constants          import UNDERWORLD_CLASSES, THEME
from src.gui.tabs.characters.character_model import (
    LABEL_WIDTH, PORTRAIT_MALE, PORTRAIT_FEMALE,
)


class IdentityPanel:
    """
    Painel de identidade do personagem.

    Expõe dois callbacks que o orquestrador (CharacterTab) conecta
    a outros painéis (ex: atualizar preview de portrait):
        on_portrait_change(pid: int)
        on_gender_change(female: bool)
    """

    def __init__(self, parent: tk.Widget) -> None:
        self._suppress = False
        self._on_portrait_change: Callable[[int], None] | None  = None
        self._on_gender_change:   Callable[[bool], None] | None = None

        # StringVars — acessíveis pelo orquestrador via get_vars()
        self.vars: dict[str, tk.StringVar | tk.BooleanVar] = {}
        self._portrait_spin: ttk.Spinbox | None = None
        self._dungeon_lbl:   ttk.Label | None   = None

        self._build(parent)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, player, save_game) -> None:
        """Popula o painel a partir de PlayerModel."""
        self._suppress = True

        self.vars["playerName"].set(player.name)
        self.vars["playerClass"].set(player.player_class_name)
        self.vars["leftHanded"].set(
            "Left-Handed" if player.left_handed else "Right-Handed")

        gender_str = "Female" if player.female else "Male"
        self.vars["female"].set(gender_str)
        self._update_portrait_options(player.female)

        portrait_options = PORTRAIT_FEMALE if player.female else PORTRAIT_MALE
        pid = player.portrait if player.portrait in portrait_options else portrait_options[0]
        self.vars["portrait"].set(str(pid))

        if self._dungeon_lbl:
            self._dungeon_lbl.config(text=str(save_game.dungeon_level or "—"))

        self._suppress = False

    def get_vars(self) -> dict[str, tk.Variable]:
        return dict(self.vars)

    def set_widget_states(self, state: str) -> None:
        """Habilita/desabilita todos os widgets editáveis."""
        for key in ("playerName", "playerClass", "leftHanded", "female", "portrait"):
            w = self._widgets.get(key)
            if w:
                w.config(state=state)

    def on_portrait_change(self, fn: Callable[[int], None]) -> None:
        self._on_portrait_change = fn

    def on_gender_change(self, fn: Callable[[bool], None]) -> None:
        self._on_gender_change = fn

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self, parent: tk.Widget) -> None:
        lf = ttk.LabelFrame(parent, text=" Identity ", padding=10)
        lf.pack(fill="x", pady=(0, 8))
        self._widgets: dict[str, tk.Widget] = {}
        row = 0

        # Name
        self._lbl(lf, "Name:", row)
        v = tk.StringVar()
        self.vars["playerName"] = v
        w = ttk.Entry(lf, textvariable=v, width=16, state="disabled")
        w.grid(row=row, column=1, sticky="w", pady=3)
        self._widgets["playerName"] = w
        row += 1

        # Class
        self._lbl(lf, "Class:", row)
        v = tk.StringVar()
        self.vars["playerClass"] = v
        w = ttk.Combobox(lf, textvariable=v, values=UNDERWORLD_CLASSES,
                         state="disabled", width=14)
        w.grid(row=row, column=1, sticky="w", pady=3)
        self._widgets["playerClass"] = w
        row += 1

        # Dominant Hand
        self._lbl(lf, "Dominant Hand:", row)
        v = tk.StringVar()
        self.vars["leftHanded"] = v
        w = ttk.Combobox(lf, textvariable=v,
                         values=["Right-Handed", "Left-Handed"],
                         state="disabled", width=14)
        w.grid(row=row, column=1, sticky="w", pady=3)
        self._widgets["leftHanded"] = w
        row += 1

        ttk.Separator(lf, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=8)
        row += 1

        # Gender
        self._lbl(lf, "Gender:", row)
        v = tk.StringVar()
        self.vars["female"] = v
        w = ttk.Combobox(lf, textvariable=v, values=["Male", "Female"],
                         state="disabled", width=10)
        w.grid(row=row, column=1, sticky="w", pady=3)
        self._widgets["female"] = w
        v.trace_add("write", self._on_gender_written)
        row += 1

        # Portrait
        self._lbl(lf, "Portrait:", row)
        v = tk.StringVar()
        self.vars["portrait"] = v
        spin = ttk.Spinbox(lf, textvariable=v, values=PORTRAIT_MALE,
                           state="disabled", width=5,
                           command=self._on_portrait_spun)
        spin.grid(row=row, column=1, sticky="w", pady=3)
        self._portrait_spin = spin
        self._widgets["portrait"] = spin
        v.trace_add("write", self._on_portrait_written)
        row += 1

        ttk.Separator(lf, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=8)
        row += 1

        # Dungeon Level (read-only)
        self._lbl(lf, "Dungeon Level:", row)
        lbl = ttk.Label(lf, text="—", foreground=THEME["fg_dungeon"])
        lbl.grid(row=row, column=1, sticky="w", pady=3)
        self._dungeon_lbl = lbl

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _lbl(self, parent: tk.Widget, text: str, row: int) -> None:
        ttk.Label(parent, text=text, width=LABEL_WIDTH, anchor="e").grid(
            row=row, column=0, sticky="e", pady=3, padx=(0, 8))

    def _update_portrait_options(self, female: bool) -> None:
        opts = PORTRAIT_FEMALE if female else PORTRAIT_MALE
        if self._portrait_spin:
            self._portrait_spin.config(values=opts)

    def _on_gender_written(self, *_) -> None:
        if self._suppress:
            return
        female = self.vars["female"].get() == "Female"
        self._update_portrait_options(female)
        first = PORTRAIT_FEMALE[0] if female else PORTRAIT_MALE[0]
        self._suppress = True
        self.vars["portrait"].set(str(first))
        self._suppress = False
        if self._on_gender_change:
            self._on_gender_change(female)
        self._fire_portrait(first)

    def _on_portrait_spun(self) -> None:
        self._fire_portrait_from_var()

    def _on_portrait_written(self, *_) -> None:
        if self._suppress:
            return
        self._fire_portrait_from_var()

    def _fire_portrait_from_var(self) -> None:
        try:
            self._fire_portrait(int(self.vars["portrait"].get()))
        except (ValueError, tk.TclError):
            pass

    def _fire_portrait(self, pid: int) -> None:
        if self._on_portrait_change:
            self._on_portrait_change(pid)
