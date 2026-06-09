# src/gui/tabs/skills_tab.py
"""Skills Tab — Renders and handles 20 editable proficiency skills in a 2-column layout grid."""
import tkinter as tk
from tkinter import ttk
from src.core.enums import NOMES_SKILLS


class SkillsTab(ttk.Frame):
    """
    'Skills' Tab Component.

    Public API:
        load(player)          → Populates skill data variables and enables input states.
        get_values() → dict   → Returns a dictionary containing mapping structures of {name: int}.
        maximize(value)       → Utility cheat bypass shortcut to set all values instantly.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=15)
        self._vars:    dict[str, tk.StringVar] = {}
        self._widgets: dict[str, tk.Widget]    = {}
        self._build()

    def load(self, player) -> None:
        skills = player.get_all_skills()
        for name, val in skills.items():
            self._widgets[name].config(state="normal")
            self._vars[name].set(str(val))

    def get_values(self) -> dict[str, int]:
        return {name: int(self._vars[name].get() or 0) for name in NOMES_SKILLS}

    def maximize(self, value: int = 30) -> None:
        for name in NOMES_SKILLS:
            self._vars[name].set(str(value))

    def _build(self) -> None:
        card = ttk.LabelFrame(self, text=" Skills Matrix ", padding=15)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollable container mechanics
        canvas = tk.Canvas(card, borderwidth=0, highlightthickness=0)
        scroll = ttk.Scrollbar(card, orient="vertical", command=canvas.yview)
        inner  = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # 2-Column layout grid calculation matrices
        col_size = (len(NOMES_SKILLS) + 1) // 2
        for idx, name in enumerate(NOMES_SKILLS):
            col_base = (idx // col_size) * 3
            row      = idx % col_size

            var = tk.StringVar()
            self._vars[name] = var

            ttk.Label(inner, text=f"{name}:", anchor="e", width=13).grid(
                row=row, column=col_base, sticky="e", pady=3, padx=(10, 6))

            entry = ttk.Entry(inner, textvariable=var, state="disabled", width=6)
            entry.grid(row=row, column=col_base + 1, sticky="w", pady=3)
            self._widgets[name] = entry

            # Visual spacer separation line dividing the column structures
            if col_base == 0:
                ttk.Separator(inner, orient="vertical").grid(
                    row=row, column=2, sticky="ns", padx=20)