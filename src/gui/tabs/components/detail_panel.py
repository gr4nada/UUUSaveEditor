"""
Detail Panel Component

Displays rich textual information about the selected critter
(HP, attitude, state, goal, movement, etc.).
"""

import tkinter as tk
from tkinter import ttk
from src.gui.constants import THEME


class DetailPanel(ttk.LabelFrame):
    """
    Rich text panel showing detailed information about a critter.
    """

    def __init__(self, parent):
        super().__init__(parent, text=" Details ", padding=4)
        self._build()

    def _build(self) -> None:
        self._text = tk.Text(
            self, height=8, font=("Consolas", 8),
            background=THEME["bg_deep"], foreground=THEME["fg_muted"],
            relief="flat", state="disabled", wrap="word")
        self._text.pack(fill="both", expand=True)

        # Configure tags for colors
        for tag, color in [
            ("key", THEME["tag_detail_key"]),
            ("hostile", THEME["attitude_hostile"]),
            ("upset", THEME["attitude_upset"]),
            ("mellow", THEME["attitude_mellow"]),
            ("friendly", THEME["attitude_friendly"]),
            ("dead", THEME["attitude_hostile"]),
            ("state", THEME["tag_state"]),
            ("goal", THEME["tag_goal"]),
            ("move", THEME["tag_move"]),
        ]:
            self._text.tag_configure(tag, foreground=color)

    def update(self, critter: dict) -> None:
        """Update details with current critter data."""
        t = self._text
        t.config(state="normal")
        t.delete("1.0", "end")

        def kv(key: str, value: str, tag: str = "val") -> None:
            t.insert("end", f"  {key:<16}", "key")
            t.insert("end", f"{value}\n", tag)

        att = critter.get("attitude", 0)
        att_tag = {0: "hostile", 1: "upset", 2: "mellow", 3: "friendly"}.get(att, "")

        kv("Name", f"{critter.get('name')} (whoami={critter.get('whoami_id')})")
        kv("Creature", f"{critter.get('type_name')} (type={critter.get('object_type')})")
        kv("HP", f"{critter.get('hp')}/{critter.get('max_hp')}", "dead" if critter.get("dead") else "friendly")
        kv("Level", str(critter.get("critter_level", 0)))
        kv("Attitude", critter.get("attitude_label", ""), att_tag)
        kv("State", f"{critter.get('state_label')} ({critter.get('state')})", "state")
        kv("Goal", f"{critter.get('goal_label')} ({critter.get('goal')})", "goal")
        kv("Movement", f"{critter.get('movement_label')} ({critter.get('movement_type')})", "move")

        t.config(state="disabled")