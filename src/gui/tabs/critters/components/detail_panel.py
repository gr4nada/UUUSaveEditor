"""
Detail Panel Component

Rich informational panel showing detailed status of the selected critter/NPC.
"""

import tkinter as tk
from tkinter import ttk
import logging

from src.gui.constants import THEME
from src.core.database.critters import attitude_color

logger = logging.getLogger("gui.tabs.critters.detail")


class DetailPanel(ttk.LabelFrame):
    """
    Painel de detalhes rico para exibir informações do critter selecionado.
    """

    def __init__(self, parent):
        super().__init__(parent, text=" Critter Details ", padding=8)
        self._build_ui()

    def _build_ui(self) -> None:
        self._text = tk.Text(
            self,
            height=12,
            font=("Consolas", 9),
            background=THEME.get("bg_deep", "#1e1e1e"),
            foreground=THEME.get("fg_muted", "#cccccc"),
            relief="flat",
            wrap="word",
            state="disabled",
            padx=6,
            pady=6
        )
        self._text.pack(fill=tk.BOTH, expand=True)

        # Configure tags for colored text
        self._configure_tags()

    def _configure_tags(self):
        """Configura tags de cor para melhor legibilidade."""
        tags = {
            "key":      THEME.get("tag_detail_key", "#7f7f7f"),
            "value":    THEME.get("fg", "#ffffff"),
            "hostile":  "#ff6b6b",
            "upset":    "#ff9944",
            "mellow":   "#ffd93d",
            "friendly": "#6bcb77",
            "dead":     "#ff4444",
            "state":    "#8be9fd",
            "goal":     "#ff79c6",
            "move":     "#bd93f9",
        }

        for tag, color in tags.items():
            self._text.tag_configure(tag, foreground=color, font=("Consolas", 9, "bold"))

    def update(self, critter: dict) -> None:
        """Atualiza o painel com os dados do critter selecionado."""
        if not critter:
            self.clear()
            return

        t = self._text
        t.config(state="normal")
        t.delete("1.0", tk.END)

        def kv(key: str, value: str, tag: str = "value") -> None:
            t.insert("end", f"{key:<18}", "key")
            t.insert("end", f"{value}\n", tag)

        # Basic Info
        name = critter.get("name", "Unknown")
        whoami = critter.get("whoami_id", 0)
        display_name = f"{name} (WhoAmI #{whoami})" if whoami > 0 else name

        kv("Name", display_name)
        kv("Type", f"{critter.get('type_name', 'Unknown')} (ID: {critter.get('object_type')})")
        kv("Level", str(critter.get("level", 0)))

        # HP
        hp = critter.get("hp", 0)
        max_hp = critter.get("max_hp", 0)
        hp_tag = "dead" if critter.get("dead") or hp <= 0 else "value"
        kv("HP", f"{hp} / {max_hp}", hp_tag)

        # Attitude
        att_id = critter.get("attitude", 0)
        att_label = critter.get("attitude_label", "Unknown")
        att_tag = {0: "hostile", 1: "upset", 2: "mellow", 3: "friendly"}.get(att_id, "value")
        kv("Attitude", att_label, att_tag)

        # State & Goal
        kv("State", f"{critter.get('state_label', 'Unknown')} ({critter.get('state')})", "state")
        kv("Goal",  f"{critter.get('goal_label', 'Unknown')} ({critter.get('goal')})", "goal")

        # Movement
        kv("Movement", f"{critter.get('movement_label', 'Unknown')} ({critter.get('movement_type')})", "move")

        # Position
        x = critter.get("tile_x", "?")
        y = critter.get("tile_y", "?")
        kv("Tile Position", f"({x}, {y})")

        # Extra flags
        talked = "Yes" if critter.get("talked_to") else "No"
        ally = "Yes" if critter.get("player_ally") else "No"
        kv("Talked To", talked)
        kv("Player Ally", ally)

        t.config(state="disabled")

    def clear(self) -> None:
        """Limpa o conteúdo do painel."""
        t = self._text
        t.config(state="normal")
        t.delete("1.0", tk.END)
        t.insert("end", "No critter selected.\n", "key")
        t.config(state="disabled")