# src/gui/tabs/characters/components/progression_panel.py
"""
ProgressionPanel — Level, XP, Skill Points + Dreams Remaining (6 spinboxes).
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from src.gui.tabs.characters.character_model import (
    PROGRESSION, LABEL_WIDTH, DREAMS_COUNT,
)
from src.core.save_model import FIELD_LIMITS


class ProgressionPanel:

    def __init__(self, parent: tk.Widget) -> None:
        self.vars: dict[str, tk.StringVar] = {}
        self._widgets: dict[str, ttk.Entry] = {}
        self.dream_vars: list[tk.StringVar] = [
            tk.StringVar(value="0") for _ in range(DREAMS_COUNT)
        ]
        self._build(parent)

    def load(self, player, _save_game=None) -> None:
        from src.gui.tabs.characters.character_model import ATTR_KEY_MAP
        for key, _ in PROGRESSION:
            if key in self.vars:
                attr = ATTR_KEY_MAP.get(key, key)
                self.vars[key].set(str(getattr(player, attr, 0)))
                self._widgets[key].config(state="normal")

        dreams = player.dreams_remaining
        for i, var in enumerate(self.dream_vars):
            var.set(str(dreams[i] if i < len(dreams) else 0))

    def get_vars(self) -> dict[str, tk.StringVar]:
        return dict(self.vars)

    def _build(self, parent: tk.Widget) -> None:
        lf = ttk.LabelFrame(parent, text=" Progression ", padding=10)
        lf.pack(fill="x", pady=(0, 8))

        for i, (key, label) in enumerate(PROGRESSION):
            ttk.Label(lf, text=label + ":", width=LABEL_WIDTH, anchor="e").grid(
                row=i, column=0, sticky="e", pady=3, padx=(0, 8))
            v = tk.StringVar()
            e = ttk.Entry(lf, textvariable=v, width=10, state="disabled")
            e.grid(row=i, column=1, sticky="w", pady=3)
            self.vars[key]    = v
            self._widgets[key] = e

        next_row = len(PROGRESSION)
        ttk.Separator(lf, orient="horizontal").grid(
            row=next_row, column=0, columnspan=2, sticky="ew", pady=8)
        next_row += 1

        ttk.Label(lf, text="Dreams Remaining:", anchor="w",
                  font=("Arial", 8, "bold")).grid(
            row=next_row, column=0, columnspan=2, sticky="w", pady=(0, 4))
        next_row += 1

        _lo, _hi = FIELD_LIMITS["dream_count"]
        dream_row = ttk.Frame(lf)
        dream_row.grid(row=next_row, column=0, columnspan=2, sticky="w")
        for var in self.dream_vars:
            ttk.Spinbox(dream_row, from_=_lo, to=_hi, textvariable=var,
                        width=4).pack(side="left", padx=(0, 4))
