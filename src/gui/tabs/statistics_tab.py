# src/gui/tabs/statistics_tab.py
"""Statistics Tab — Displays informational gameplay tracking state data (read-only)."""
import tkinter as tk
from tkinter import ttk


def _fmt_time(seconds: float) -> str:
    s = int(seconds)
    h, m = s // 3600, (s % 3600) // 60
    return f"{h:,}h {m:02d}m"


_STATS = [
    ("play_time",            "Play Time",               lambda p: _fmt_time(p.play_time)),
    ("game_time",            "Game Time (in-world)",    lambda p: _fmt_time(p.game_time)),
    ("num_repairs",          "Items Repaired",          lambda p: str(p.num_repairs)),
    ("num_fish_caught",      "Fish Caught",             lambda p: str(p.num_fish_caught)),
    ("books_read",           "Books Read",              lambda p: str(p.books_read)),
    ("books_burned",         "Books Burned",            lambda p: str(p.books_burned)),
    ("gate_travel_distance", "Gate Travel Distance",    lambda p: f"{p.gate_travel_distance:.1f}"),
    ("water_walk_steps",     "Water Walk Steps",        lambda p: str(p.water_walk_steps)),
    ("lava_walk_steps",      "Lava Walk Steps",         lambda p: str(p.lava_walk_steps)),
]


class StatisticsTab(ttk.Frame):
    """
    'Statistics' Tab Component — Read-only.

    Public API:
        load(player) → Refreshes the visual frame hierarchy with updated states.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=20)
        self._labels: dict[str, ttk.Label] = {}
        self._build()

    def load(self, player) -> None:
        for key, _label, extractor in _STATS:
            try:
                val = extractor(player)
            except Exception:
                val = "—"
            self._labels[key].config(text=val, foreground="#fff")

        # Tracked encountered monster/critter dictionary structures
        critters = player._p.get("encounteredCritters", []) if hasattr(player, "_p") else []
        self._labels["critters"].config(
            text=f"{len(critters)} type(s)", foreground="#fff")

    def _build(self) -> None:
        card = ttk.LabelFrame(self, text=" Gameplay Statistics (read-only) ", padding=20)
        card.pack(anchor="n", padx=40, pady=20, fill="x")

        ttk.Label(card, text="These values are tracked by the game engine and cannot be edited.",
                  foreground="#666", font=("Arial", 8, "italic")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        row_idx = 1
        for key, label, _ in _STATS:
            ttk.Label(card, text=label + ":", width=24, anchor="e").grid(
                row=row_idx, column=0, sticky="e", pady=4, padx=(0, 8))
            lbl = ttk.Label(card, text="—", foreground="#888", width=20, anchor="w")
            lbl.grid(row=row_idx, column=1, sticky="w", pady=4)
            self._labels[key] = lbl
            row_idx += 1

        # Encountered Critters row entry definition
        ttk.Label(card, text="Encountered Critters:", width=24, anchor="e").grid(
            row=row_idx, column=0, sticky="e", pady=4, padx=(0, 8))
        lbl = ttk.Label(card, text="—", foreground="#888")
        lbl.grid(row=row_idx, column=1, sticky="w", pady=4)
        self._labels["critters"] = lbl