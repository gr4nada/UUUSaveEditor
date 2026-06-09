# src/gui/tabs/player_tab.py
"""Player Tab — Handles layout for identity, traits, and character profile properties."""
import tkinter as tk
from tkinter import ttk
from src.gui.constants import UNDERWORLD_CLASSES


_FIELDS = [
    {"key": "playerName",  "label": "Name",          "type": "entry", "width": 18},
    {"key": "playerClass", "label": "Class",         "type": "combo", "options": UNDERWORLD_CLASSES},
    {"key": "female",      "label": "Gender",        "type": "combo", "options": ["Male", "Female"]},
    {"key": "leftHanded",  "label": "Dominant Hand", "type": "combo", "options": ["Right-Handed", "Left-Handed"]},
    {"key": "portrait",    "label": "Portrait ID",   "type": "entry", "width": 6,
     "hint": "Valid range: 0 – 31"},
]


class PlayerTab(ttk.Frame):
    """
    'Player' Tab Component.

    Public API:
        load(player)        → Populates data parameters and enables input states.
        get_values() → dict → Collects current field data to pass down to storage routines.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=20)
        self._vars:    dict[str, tk.StringVar] = {}
        self._widgets: dict[str, tk.Widget]    = {}
        self._build()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, player) -> None:
        """Receives a PlayerModel entity instance and populates field forms."""
        mapping = {
            "playerName":  player.name,
            "playerClass": player.player_class_name,
            "female":      "Female" if player.female else "Male",
            "leftHanded":  "Left-Handed" if player.left_handed else "Right-Handed",
            "portrait":    str(player.portrait),
        }
        for key, value in mapping.items():
            w = self._widgets[key]
            if isinstance(w, ttk.Combobox):
                w.config(state="readonly")
                w.set(value)
            else:
                w.config(state="normal")
                self._vars[key].set(value)

    def get_values(self) -> dict:
        return {
            "playerName":  self._vars["playerName"].get(),
            "playerClass": self._vars["playerClass"].get(),
            "female":      self._vars["female"].get() == "Female",
            "leftHanded":  self._vars["leftHanded"].get() == "Left-Handed",
            "portrait":    int(self._vars["portrait"].get() or 0),
        }

    # ------------------------------------------------------------------
    # Frame Component Construction
    # ------------------------------------------------------------------

    def _build(self) -> None:
        card = ttk.LabelFrame(self, text=" Character Profile ", padding=20)
        card.pack(anchor="n", padx=40, pady=20, fill="x")

        for row_idx, field in enumerate(_FIELDS):
            key = field["key"]

            ttk.Label(card, text=field["label"] + ":", width=16,
                      anchor="e").grid(row=row_idx, column=0, sticky="e", pady=6, padx=(0, 12))

            var = tk.StringVar()
            self._vars[key] = var

            if field["type"] == "combo":
                w = ttk.Combobox(card, textvariable=var, values=field["options"],
                                 state="disabled", width=18)
            else:
                w = ttk.Entry(card, textvariable=var, state="disabled",
                              width=field.get("width", 12))

            w.grid(row=row_idx, column=1, sticky="w", pady=6)
            self._widgets[key] = w

            if field.get("hint"):
                ttk.Label(card, text=field["hint"],
                          foreground="#888", font=("Arial", 8)).grid(
                    row=row_idx, column=2, sticky="w", padx=10)