"""
Game State Panel — Difficulty, Position and Dungeon Level
"""

import tkinter as tk
from tkinter import ttk
from src.gui.constants import THEME


class GameStatePanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text=" Game State ", padding=10)
        self._easy_var = tk.BooleanVar()
        self._pos_vars: dict[str, tk.StringVar] = {}
        self._level_var = tk.StringVar()
        self._build()

    def _build(self):
        # Easy Mode
        ttk.Checkbutton(self, text="Easy Mode", variable=self._easy_var).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        # Position
        ttk.Label(self, text="Player Position (Teleport)", 
                  font=("Arial", 9, "bold")).grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(4, 2))

        pos_frame = ttk.Frame(self)
        pos_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=(0, 8))

        for i, axis in enumerate(["X", "Y", "Z"]):
            var = tk.StringVar(value="0.000")
            self._pos_vars[axis.lower()] = var
            ttk.Label(pos_frame, text=f"{axis}:").pack(side="left", padx=(0 if i == 0 else 8, 4))
            ttk.Entry(pos_frame, textvariable=var, width=10).pack(side="left", padx=(0, 8))

        # Dungeon Level
        ttk.Label(self, text="Dungeon Level:", anchor="e", width=14).grid(
            row=3, column=0, sticky="e", pady=4, padx=(0, 8))
        ttk.Spinbox(self, from_=0, to=9, textvariable=self._level_var, width=6).grid(
            row=3, column=1, sticky="w")

        ttk.Label(self, text="Changes will apply on save.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic")).grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(6, 0))

    def load(self, story: 'StoryState'):
        self._easy_var.set(story.easy)
        for axis in ["x", "y", "z"]:
            val = story.position.get(axis, 0.0)
            self._pos_vars[axis].set(f"{val:.3f}")
        self._level_var.set(str(story.current_level))