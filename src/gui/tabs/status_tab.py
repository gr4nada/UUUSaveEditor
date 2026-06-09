# src/gui/tabs/status_tab.py
"""Status Tab — Handles temporary character conditions and environmental effects."""
import tkinter as tk
from tkinter import ttk

# (key, label, color when active, description)
_STATUSES = [
    ("poison",      "Poison",      "#a8ff78", "Character has been poisoned. Reduces HP over time."),
    ("hunger",      "Hunger",      "#ffe066", "Hunger level. High values cause fatigue and weakness."),
    ("fatigue",     "Fatigue",     "#ff9966", "Physical exhaustion. Impacts combat effectiveness."),
    ("drunkenness", "Drunkenness", "#cc99ff", "Alcohol intoxication level. Distorts vision and movement."),
]

_STATUS_BOOLEAN = [
    ("dead",    "Dead",    "#ff4444", "Character is currently dead."),
]


class StatusTab(ttk.Frame):
    """
    'Status' Tab Component.

    Public API:
        load(player)        → Populates data parameters and enables input states.
        get_values() → dict → Collects visual field data to pass down to storage routines.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=20)
        self._vars:    dict[str, tk.StringVar]  = {}
        self._widgets: dict[str, tk.Widget]      = {}
        self._indicators: dict[str, tk.Label]    = {}
        self._build()

    def load(self, player) -> None:
        values = {
            "poison":      player.poison,
            "hunger":      player.hunger,
            "fatigue":     player.fatigue,
            "drunkenness": player.drunkenness,
        }
        for key, val in values.items():
            self._widgets[key].config(state="normal")
            self._vars[key].set(str(val))
            self._update_indicator(key, val, values)

        # Dead state parameter flag is strictly read-only
        dead_val = "YES" if player.dead else "NO"
        dead_color = "#ff4444" if player.dead else "#88ff88"
        self._indicators["dead"].config(text=dead_val, foreground=dead_color)

    def get_values(self) -> dict:
        return {key: int(self._vars[key].get() or 0)
                for key in ("poison", "hunger", "fatigue", "drunkenness")}

    def _build(self) -> None:
        # — Editable Numerical Status Conditions —
        card = ttk.LabelFrame(self, text=" Active Conditions ", padding=20)
        card.pack(anchor="n", padx=40, pady=(20, 10), fill="x")

        for row_idx, (key, label, color, desc) in enumerate(_STATUSES):
            var = tk.StringVar()
            self._vars[key] = var

            # Severity visual notification dot indicator node
            indicator = tk.Label(card, text="●", foreground="#555",
                                 font=("Arial", 12))
            indicator.grid(row=row_idx, column=0, padx=(0, 8), pady=6)
            self._indicators[key] = indicator

            ttk.Label(card, text=label + ":", width=14, anchor="e").grid(
                row=row_idx, column=1, sticky="e", pady=6, padx=(0, 8))

            entry = ttk.Entry(card, textvariable=var, state="disabled", width=8)
            entry.grid(row=row_idx, column=2, sticky="w", pady=6)
            self._widgets[key] = entry

            var.trace_add("write", lambda *a, k=key, c=color: self._on_value_change(k, c))

            ttk.Label(card, text=desc, foreground="#777",
                      font=("Arial", 8)).grid(row=row_idx, column=3, sticky="w", padx=14)

        # — Read-Only Environmental Condition State Flags —
        flags_card = ttk.LabelFrame(self, text=" State Flags (read-only) ", padding=20)
        flags_card.pack(anchor="n", padx=40, pady=(0, 20), fill="x")

        for row_idx, (key, label, color, desc) in enumerate(_STATUS_BOOLEAN):
            ttk.Label(flags_card, text=label + ":", width=14, anchor="e").grid(
                row=row_idx, column=0, sticky="e", pady=6, padx=(0, 8))
            ind = ttk.Label(flags_card, text="—", foreground="#888",
                            font=("Arial", 10, "bold"))
            ind.grid(row=row_idx, column=1, sticky="w", pady=6)
            self._indicators[key] = ind

            ttk.Label(flags_card, text=desc, foreground="#777",
                      font=("Arial", 8)).grid(row=row_idx, column=2, sticky="w", padx=14)

    def _on_value_change(self, key: str, active_color: str) -> None:
        try:
            val = int(self._vars[key].get() or 0)
            self._update_indicator(key, val, {})
        except ValueError:
            pass

    def _update_indicator(self, key: str, val: int, _all: dict) -> None:
        ind = self._indicators.get(key)
        if not ind:
            return
        if val == 0:
            ind.config(foreground="#333")
        elif val <= 3:
            ind.config(foreground="#ffaa00")
        else:
            ind.config(foreground="#ff4444")