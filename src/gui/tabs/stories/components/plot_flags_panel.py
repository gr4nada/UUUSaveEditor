"""
Plot Flags Panel — Main story progression flags
"""

import tkinter as tk
from tkinter import ttk
from src.gui.constants import THEME


class PlotFlagsPanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text=" Plot Flags ", padding=10)
        self._vars = {}
        self._build()

    def _build(self):
        row = 0

        # Cup
        self._add_checkbox("Cup Found", "cup_found", row)
        ttk.Label(self, text="Dream Index:").grid(row=row, column=2, sticky="e", padx=(20, 8))
        self._add_spin("cup_dream_index", 0, 5, row, column=3)
        row += 1

        # Sapling
        self._add_checkbox("Sapling Planted", "sapling_planted", row)
        ttk.Label(self, text="Level:").grid(row=row, column=2, sticky="e", padx=(20, 8))
        self._add_spin("sapling_level", 0, 9, row, column=3)
        row += 1

        # Moonstone
        self._add_checkbox("Moonstone Dropped", "moonstone_dropped", row)
        ttk.Label(self, text="Level:").grid(row=row, column=2, sticky="e", padx=(20, 8))
        self._add_spin("moonstone_level", 0, 9, row, column=3)
        row += 1

        # Others
        self._add_checkbox("Garamon at Rest", "garamon_at_rest", row); row += 1
        self._add_checkbox("Entered Green Moongate", "entered_green_moongate", row); row += 1
        self._add_checkbox("Said to Fanlo", "said_fanlo", row); row += 1

        # Talismans
        ttk.Separator(self, orient="horizontal").grid(row=row, column=0, columnspan=4, sticky="ew", pady=8)
        row += 1

        ttk.Label(self, text="Talismans Collected:").grid(row=row, column=0, sticky="e", padx=(0,8))
        self._add_spin("talismans_collected", 0, 64, row, column=1)
        row += 1

        ttk.Label(self, text="Talismans Destroyed:").grid(row=row, column=0, sticky="e", padx=(0,8))
        self._add_spin("talismans_destroyed", 0, 64, row, column=1)

    def _add_checkbox(self, text: str, key: str, row: int):
        var = tk.BooleanVar()
        self._vars[key] = var
        ttk.Checkbutton(self, text=text, variable=var).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=3)

    def _add_spin(self, key: str, from_: int, to: int, row: int, column: int = 1):
        var = tk.StringVar(value="0")
        self._vars[key] = var
        ttk.Spinbox(self, from_=from_, to=to, textvariable=var, width=6).grid(
            row=row, column=column, sticky="w", pady=3)

    def load(self, story):
        for key, var in self._vars.items():
            if isinstance(var, tk.BooleanVar):
                var.set(getattr(story, key, False))
            else:
                var.set(str(getattr(story, key, 0)))