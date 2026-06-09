# src/gui/tabs/attributes_tab.py
"""Attributes Tab — Handles layout for strength, dexterity, intellect, health, and mana."""
import tkinter as tk
from tkinter import ttk

_FIELDS = [
    ("strength",   "Strength",   "STR"),
    ("dexterity",  "Dexterity",  "DEX"),
    ("intellect",  "Intellect",  "INT"),
    ("hp",         "Health",     "HP"),
    ("vitality",   "Max Vitality","VIT"),
    ("mana",       "Mana",       "MP"),
    ("maxMana",    "Max Mana",   "MAX MP"),
]


class AttributesTab(ttk.Frame):
    """
    'Attributes' Tab Component.

    Public API:
        load(player)        → Populates data parameters and enables input states.
        get_values() → dict → Collects visual field data to pass down to storage routines.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=20)
        self._vars:    dict[str, tk.StringVar] = {}
        self._widgets: dict[str, tk.Widget]    = {}
        self._build()

    def load(self, player) -> None:
        mapping = {
            "strength":  player.strength,
            "dexterity": player.dexterity,
            "intellect": player.intellect,
            "hp":        player.hp,
            "vitality":  player.vitality,
            "mana":      player.mana,
            "maxMana":   player.max_mana,
        }
        for key, val in mapping.items():
            self._widgets[key].config(state="normal")
            self._vars[key].set(str(val))

    def get_values(self) -> dict:
        return {key: int(self._vars[key].get() or 0) for key in self._vars}

    def _build(self) -> None:
        card = ttk.LabelFrame(self, text=" Primary Attributes ", padding=20)
        card.pack(anchor="n", padx=40, pady=20, fill="x")

        for row_idx, (key, label, abbrev) in enumerate(_FIELDS):
            var = tk.StringVar()
            self._vars[key] = var

            # Colored abbreviation identification badge
            badge = tk.Label(card, text=abbrev, bg="#3c3c5e", fg="#aaaaff",
                             font=("Consolas", 8, "bold"), width=7, relief="flat", padx=4)
            badge.grid(row=row_idx, column=0, sticky="e", pady=5, padx=(0, 10))

            ttk.Label(card, text=label + ":", width=14, anchor="e").grid(
                row=row_idx, column=1, sticky="e", pady=5, padx=(0, 8))

            entry = ttk.Entry(card, textvariable=var, state="disabled", width=10)
            entry.grid(row=row_idx, column=2, sticky="w", pady=5)
            self._widgets[key] = entry