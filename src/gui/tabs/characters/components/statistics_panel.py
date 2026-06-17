# src/gui/tabs/characters/components/statistics_panel.py
"""
StatisticsPanel — Play Time, Game Time, Books, Fish, Repairs, etc. (read-only).
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from src.gui.constants import THEME
from src.gui.tabs.characters.character_model import STATISTICS, LABEL_WIDTH


class StatisticsPanel:

    def __init__(self, parent: tk.Widget) -> None:
        self._labels: dict[str, ttk.Label] = {}
        self._build(parent)

    def load(self, player, _save_game=None) -> None:
        for stat in STATISTICS:
            try:
                text = stat.extractor(player)
                fg   = THEME["fg_stat_value"]
            except Exception:
                text = "—"
                fg   = THEME["fg_faint"]
            self._labels[stat.key].config(text=text, foreground=fg)

    def _build(self, parent: tk.Widget) -> None:
        lf = ttk.LabelFrame(parent, text=" Statistics ", padding=10)
        lf.pack(fill="x", pady=(0, 8))

        ttk.Label(lf, text="read-only", foreground=THEME["fg_dead"],
                  font=("Arial", 7, "italic")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        for i, stat in enumerate(STATISTICS):
            ttk.Label(lf, text=stat.label + ":", width=LABEL_WIDTH, anchor="e").grid(
                row=i + 1, column=0, sticky="e", pady=3, padx=(0, 8))
            lbl = ttk.Label(lf, text="—", foreground=THEME["fg_faint"],
                            width=12, anchor="w")
            lbl.grid(row=i + 1, column=1, sticky="w", pady=3)
            self._labels[stat.key] = lbl
