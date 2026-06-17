# src/gui/tabs/characters/components/attributes_panel.py
"""
AttributesPanel — Max HP, Max Mana, Strength, Dexterity, Intellect.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from src.gui.tabs.characters.character_model import ATTRIBUTES, LABEL_WIDTH


class AttributesPanel:

    def __init__(self, parent: tk.Widget) -> None:
        self.vars: dict[str, tk.StringVar] = {}
        self._widgets: dict[str, ttk.Entry] = {}
        self._build(parent)

    def load(self, player, _save_game=None) -> None:
        from src.gui.tabs.characters.character_model import ATTR_KEY_MAP
        for key, attr in ATTR_KEY_MAP.items():
            if key in self.vars:
                self.vars[key].set(str(getattr(player, attr, 0)))
                self._widgets[key].config(state="normal")

    def get_vars(self) -> dict[str, tk.StringVar]:
        return dict(self.vars)

    def _build(self, parent: tk.Widget) -> None:
        lf = ttk.LabelFrame(parent, text=" Attributes & Vitals ", padding=10)
        lf.pack(fill="x", pady=(0, 8))
        for i, (key, label) in enumerate(ATTRIBUTES):
            ttk.Label(lf, text=label + ":", width=LABEL_WIDTH, anchor="e").grid(
                row=i, column=0, sticky="e", pady=3, padx=(0, 8))
            v = tk.StringVar()
            e = ttk.Entry(lf, textvariable=v, width=10, state="disabled")
            e.grid(row=i, column=1, sticky="w", pady=3)
            self.vars[key]    = v
            self._widgets[key] = e
