# src/gui/tabs/characters/components/dungeon_state_panel.py
"""
DungeonStatePanel — Easy Mode checkbox + Position (X/Y/Z) teleport.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from src.gui.constants import THEME


class DungeonStatePanel:

    def __init__(self, parent: tk.Widget) -> None:
        self.easy_var  = tk.BooleanVar(value=False)
        self.pos_x_var = tk.StringVar(value="0.000")
        self.pos_y_var = tk.StringVar(value="0.000")
        self.pos_z_var = tk.StringVar(value="0.000")
        self._build(parent)

    def load(self, player, _save_game=None) -> None:
        self.easy_var.set(player.easy)
        pos = player.position
        self.pos_x_var.set(f"{pos['x']:.3f}")
        self.pos_y_var.set(f"{pos['y']:.3f}")
        self.pos_z_var.set(f"{pos['z']:.3f}")

    def _build(self, parent: tk.Widget) -> None:
        lf = ttk.LabelFrame(parent, text=" Dungeon & State ", padding=10)
        lf.pack(fill="x", pady=(0, 8))

        ttk.Checkbutton(lf, text="Easy Mode", variable=self.easy_var).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(lf, text="Position (Teleport):", anchor="w",
                  font=("Arial", 8, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 4))

        pos_row = ttk.Frame(lf)
        pos_row.grid(row=2, column=0, columnspan=2, sticky="w")
        for label, var in [
            ("X:", self.pos_x_var),
            ("Y:", self.pos_y_var),
            ("Z:", self.pos_z_var),
        ]:
            ttk.Label(pos_row, text=label, width=2, anchor="e").pack(
                side="left", padx=(0, 2))
            ttk.Entry(pos_row, textvariable=var, width=9).pack(
                side="left", padx=(0, 8))

        ttk.Label(lf,
                  text="Editing X/Y/Z and saving will move the character on next load.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic"),
                  justify="left").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))
