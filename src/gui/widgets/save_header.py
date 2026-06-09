# src/gui/widgets/save_header.py
import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime

logger = logging.getLogger("gui.widgets.save_header")


class SaveHeaderFrame(ttk.LabelFrame):
    """
    Fixed information panel at the top of the editor.
    Displays key save information read-only and automatically updates on load.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, text=" Save Information ", padding=10, **kwargs)
        self._setup_widgets()
        self._clear_display()

    def _setup_widgets(self):
        """Create the header UI layout."""
        # Header info displayed in two rows for compact layout
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", expand=True)

        # Left column: Player identity
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)

        ttk.Label(left_frame, text="Player:", font=("Arial", 9, "bold")).grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.player_name = ttk.Label(left_frame, text="—", foreground="#888")
        self.player_name.grid(row=0, column=1, sticky="w", padx=(5, 20))

        ttk.Label(left_frame, text="Class:", font=("Arial", 9, "bold")).grid(
            row=0, column=2, sticky="w"
        )
        self.player_class = ttk.Label(left_frame, text="—", foreground="#888")
        self.player_class.grid(row=0, column=3, sticky="w", padx=(5, 20))

        ttk.Label(left_frame, text="Level:", font=("Arial", 9, "bold")).grid(
            row=0, column=4, sticky="w"
        )
        self.player_level = ttk.Label(left_frame, text="—", foreground="#888")
        self.player_level.grid(row=0, column=5, sticky="w", padx=(5, 0))

        # Right column: Experience and time info
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        ttk.Label(right_frame, text="XP:", font=("Arial", 9, "bold")).pack(
            side="left", padx=(0, 5)
        )
        self.player_xp = ttk.Label(right_frame, text="—", foreground="#888")
        self.player_xp.pack(side="left", padx=(0, 20))

        ttk.Label(right_frame, text="Game Time:", font=("Arial", 9, "bold")).pack(
            side="left", padx=(0, 5)
        )
        self.game_time = ttk.Label(right_frame, text="—", foreground="#888")
        self.game_time.pack(side="left", padx=(0, 20))

        ttk.Label(right_frame, text="Saved:", font=("Arial", 9, "bold")).pack(
            side="left", padx=(0, 5)
        )
        self.saved_date = ttk.Label(right_frame, text="—", foreground="#888")
        self.saved_date.pack(side="left", padx=(0, 0))

    def _clear_display(self):
        """Reset all header fields to default state."""
        self.player_name.config(text="—", foreground="#888")
        self.player_class.config(text="—", foreground="#888")
        self.player_level.config(text="—", foreground="#888")
        self.player_xp.config(text="—", foreground="#888")
        self.game_time.config(text="—", foreground="#888")
        self.saved_date.config(text="—", foreground="#888")

    def update_from_save(self, raw_save_data: dict, slot_number: int) -> None:
        """
        Update header display from loaded save data.

        Args:
            raw_save_data: The raw save dictionary loaded from the slot
            slot_number: The slot number (0-9) for display purposes
        """
        try:
            player_data = raw_save_data.get("playerData", {})

            # Extract player information
            player_name = player_data.get("playerName", "Avatar")
            player_class = self._get_class_name(
                player_data.get("playerClass", 0)
            )
            player_level = player_data.get("charLevel", 0)
            player_xp = player_data.get("xp", 0)

            # Extract game time (stored as total game seconds)
            game_seconds = int(player_data.get("gameTime", 0))
            hours = game_seconds // 3600
            minutes = (game_seconds % 3600) // 60
            game_time_str = f"{hours:02d}:{minutes:02d}"

            # Format save date (check root level first, then playerData)
            saved_date = raw_save_data.get("savedAtIso") or player_data.get("savedAtIso")
            if isinstance(saved_date, str):
                saved_date = saved_date.split("T")[0]
            else:
                saved_date = datetime.now().strftime("%Y-%m-%d")

            # Update display with actual values
            self.player_name.config(text=player_name, foreground="#fff")
            self.player_class.config(text=player_class, foreground="#fff")
            self.player_level.config(text=str(player_level), foreground="#fff")
            self.player_xp.config(text=f"{player_xp:,}", foreground="#fff")
            self.game_time.config(text=game_time_str, foreground="#fff")
            self.saved_date.config(text=saved_date, foreground="#fff")

            logger.info(
                "Save header updated: Slot %d, Player: %s (%s), Level: %d",
                slot_number,
                player_name,
                player_class,
                player_level,
            )
        except Exception as e:
            logger.error("Error updating save header: %s", e)
            self._clear_display()

    @staticmethod
    def _get_class_name(class_id: int) -> str:
        """Map class ID to display name."""
        from src.gui.constants import UNDERWORLD_CLASSES

        if 0 <= class_id < len(UNDERWORLD_CLASSES):
            return UNDERWORLD_CLASSES[class_id]
        return "Unknown"
