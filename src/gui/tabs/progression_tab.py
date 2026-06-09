# src/gui/tabs/progression_tab.py
"""Progression Tab — Handles character level, XP, skill points, and quest states."""
import tkinter as tk
from tkinter import ttk

_NUMERIC = [
    ("charLevel",   "Character Level", ""),
    ("xp",          "Experience (XP)", ""),
    ("skillPoints", "Skill Points",    "Unspent points to distribute"),
]


class ProgressionTab(ttk.Frame):
    """
    'Progression' Tab Component.

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
            "charLevel":   player.level,
            "xp":          player.xp,
            "skillPoints": player.skill_points,
        }
        for key, val in mapping.items():
            self._widgets[key].config(state="normal")
            self._vars[key].set(str(val))

        # Dreams — Read-only integer array tracking sequence remaining
        dreams = player.dreams_remaining
        if isinstance(dreams, list):
            self._dreams_lbl.config(
                text=f"{len(dreams)} dream(s) remaining  {dreams}",
                foreground="#fff")
        else:
            self._dreams_lbl.config(text=str(dreams), foreground="#fff")

        # globalVars — Read-only state flags schema
        gv = player.global_vars
        self._gvars_lbl.config(
            text=f"{len(gv)} global variables",
            foreground="#aaa")

    def get_values(self) -> dict:
        return {key: int(self._vars[key].get() or 0) for key in self._vars}

    def _build(self) -> None:
        # — Mutable Input Fields —
        card = ttk.LabelFrame(self, text=" Character Progression ", padding=20)
        card.pack(anchor="n", padx=40, pady=(20, 10), fill="x")

        for row_idx, (key, label, hint) in enumerate(_NUMERIC):
            var = tk.StringVar()
            self._vars[key] = var
            ttk.Label(card, text=label + ":", width=20, anchor="e").grid(
                row=row_idx, column=0, sticky="e", pady=6, padx=(0, 8))
            entry = ttk.Entry(card, textvariable=var, state="disabled", width=12)
            entry.grid(row=row_idx, column=1, sticky="w", pady=6)
            self._widgets[key] = entry
            if hint:
                ttk.Label(card, text=hint, foreground="#777",
                          font=("Arial", 8)).grid(row=row_idx, column=2, sticky="w", padx=10)

        # — Read-Only Environmental Context: Dreams & World Triggers —
        dreams_card = ttk.LabelFrame(self, text=" Dreams & Global State (read-only) ", padding=20)
        dreams_card.pack(anchor="n", padx=40, pady=(0, 10), fill="x")

        ttk.Label(dreams_card, text="Dreams Remaining:", width=20,
                  anchor="e").grid(row=0, column=0, sticky="e", pady=6, padx=(0, 8))
        self._dreams_lbl = ttk.Label(dreams_card, text="—", foreground="#888")
        self._dreams_lbl.grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(dreams_card, text="Global Variables:", width=20,
                  anchor="e").grid(row=1, column=0, sticky="e", pady=6, padx=(0, 8))
        self._gvars_lbl = ttk.Label(dreams_card, text="—", foreground="#888")
        self._gvars_lbl.grid(row=1, column=1, sticky="w", pady=6)