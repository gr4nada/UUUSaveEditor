"""
Editor Panel Component

Provides editing capabilities for the selected critter:
- HP modification
- Revive / Kill
- Attitude change
- Tile position (teleport)
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Optional

from src.core.save_model import GameObject
from src.core.database.critters import ECritterAttitude
from src.gui.constants import THEME


class EditorPanel(ttk.LabelFrame):
    """
    Panel with inline editing controls for critter properties.
    
    Supports:
        - HP editing
        - Revive / Kill buttons
        - Attitude selection
        - Tile position (X/Y) teleport
    """

    def __init__(self, parent):
        super().__init__(parent, text=" Editor ", padding=6)
        self._selected: Optional[dict] = None
        self._build()

    def _build(self) -> None:
        """Build all editor widgets."""
        r = 0

        # ── HP ─────────────────────────────────────────────────────
        ttk.Label(self, text="HP:", foreground=THEME["fg_muted"]).grid(
            row=r, column=0, sticky="e", padx=(0, 4), pady=2)

        self._hp_var = tk.StringVar()
        self._hp_entry = ttk.Entry(self, textvariable=self._hp_var, width=7, state="disabled")
        self._hp_entry.grid(row=r, column=1, sticky="w", pady=2)

        self._apply_hp_btn = ttk.Button(self, text="Set", command=self._apply_hp,
                                        state="disabled", width=5)
        self._apply_hp_btn.grid(row=r, column=2, padx=(4, 0), pady=2)
        r += 1

        # ── Status: Revive / Kill ──────────────────────────────────
        status_frame = ttk.Frame(self)
        status_frame.grid(row=r, column=0, columnspan=3, sticky="we", pady=(6, 4))

        self._revive_btn = ttk.Button(status_frame, text="Revive",
                                      command=self._on_revive, state="disabled")
        self._revive_btn.pack(side="left", padx=(0, 4))

        self._kill_btn = ttk.Button(status_frame, text="Kill",
                                    command=self._on_kill, state="disabled")
        self._kill_btn.pack(side="left")
        r += 1

        # ── Attitude ───────────────────────────────────────────────
        ttk.Separator(self, orient="horizontal").grid(
            row=r, column=0, columnspan=3, sticky="we", pady=8)
        r += 1

        ttk.Label(self, text="Attitude:", foreground=THEME["fg_muted"]).grid(
            row=r, column=0, sticky="e", padx=(0, 4), pady=2)

        self._attitude_var = tk.StringVar()
        attitude_names = [a.name.capitalize() for a in ECritterAttitude]
        self._attitude_cb = ttk.Combobox(
            self, textvariable=self._attitude_var,
            values=attitude_names, state="disabled", width=12)
        self._attitude_cb.grid(row=r, column=1, columnspan=2, sticky="we", pady=2)
        r += 1

        self._apply_attitude_btn = ttk.Button(
            self, text="Apply Attitude", command=self._apply_attitude, state="disabled")
        self._apply_attitude_btn.grid(row=r, column=0, columnspan=3, sticky="we", pady=(2, 6))
        r += 1

        # ── Position (Teleport) ────────────────────────────────────
        ttk.Separator(self, orient="horizontal").grid(
            row=r, column=0, columnspan=3, sticky="we", pady=8)
        r += 1

        ttk.Label(self, text="Tile X:", foreground=THEME["fg_muted"]).grid(
            row=r, column=0, sticky="e", padx=(0, 4), pady=2)
        self._tile_x_var = tk.IntVar()
        self._tile_x_spin = ttk.Spinbox(
            self, textvariable=self._tile_x_var, from_=0, to=62, width=6, state="disabled")
        self._tile_x_spin.grid(row=r, column=1, sticky="w", pady=2)
        r += 1

        ttk.Label(self, text="Tile Y:", foreground=THEME["fg_muted"]).grid(
            row=r, column=0, sticky="e", padx=(0, 4), pady=2)
        self._tile_y_var = tk.IntVar()
        self._tile_y_spin = ttk.Spinbox(
            self, textvariable=self._tile_y_var, from_=0, to=62, width=6, state="disabled")
        self._tile_y_spin.grid(row=r, column=1, sticky="w", pady=2)
        r += 1

        self._teleport_btn = ttk.Button(
            self, text="Teleport", command=self._apply_position, state="disabled")
        self._teleport_btn.grid(row=r, column=0, columnspan=3, sticky="we", pady=(4, 0))
        r += 1

        # Hint
        self._hint_lbl = ttk.Label(
            self, text="Select a critter to edit.",
            foreground=THEME["fg_muted"], font=("Arial", 8, "italic"), wraplength=160)
        self._hint_lbl.grid(row=r, column=0, columnspan=3, pady=(12, 0))

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh(self, critter: dict) -> None:
        """Update editor with currently selected critter."""
        self._selected = critter

        if not critter:
            self._disable_all()
            return

        # Enable all controls
        for widget in (self._hp_entry, self._apply_hp_btn, self._attitude_cb,
                       self._apply_attitude_btn, self._tile_x_spin,
                       self._tile_y_spin, self._teleport_btn):
            widget.config(state="normal")

        # HP
        self._hp_var.set(str(critter.get("hp", 0)))

        # Revive / Kill
        if critter.get("dead", False):
            self._revive_btn.config(state="normal")
            self._kill_btn.config(state="disabled")
        else:
            self._revive_btn.config(state="disabled")
            self._kill_btn.config(state="normal")

        # Attitude
        try:
            att_name = ECritterAttitude(critter.get("attitude", 0)).name.capitalize()
            self._attitude_var.set(att_name)
        except:
            self._attitude_var.set("Neutral")

        # Position
        self._tile_x_var.set(critter.get("tile_x", 0))
        self._tile_y_var.set(critter.get("tile_y", 0))

        name = critter.get("name") or critter.get("type_name", "Critter")
        self._hint_lbl.config(text=f"Editing: {name}")

    def _disable_all(self) -> None:
        """Disable all controls when no critter is selected."""
        for widget in (self._hp_entry, self._apply_hp_btn, self._revive_btn,
                       self._kill_btn, self._attitude_cb, self._apply_attitude_btn,
                       self._tile_x_spin, self._tile_y_spin, self._teleport_btn):
            widget.config(state="disabled")
        self._hint_lbl.config(text="Select a critter to edit.")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _apply_hp(self) -> None:
        """Apply new HP value."""
        if not self._selected:
            return
        try:
            value = int(self._hp_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "HP must be a valid integer.")
            return

        obj = GameObject(self._selected["_node"])
        obj.hp = value

        self._selected["hp"] = obj.hp
        self._selected["dead"] = obj.is_dead

        self._notify_parent()

    def _on_revive(self) -> None:
        """Revive the critter."""
        if not self._selected:
            return
        obj = GameObject(self._selected["_node"])
        obj.revive()

        self._selected["hp"] = obj.hp
        self._selected["dead"] = obj.is_dead
        self._notify_parent()

    def _on_kill(self) -> None:
        """Kill the critter."""
        if not self._selected:
            return
        obj = GameObject(self._selected["_node"])
        obj.kill()

        self._selected["hp"] = obj.hp
        self._selected["dead"] = obj.is_dead
        self._notify_parent()

    def _apply_attitude(self) -> None:
        """Apply new attitude."""
        if not self._selected:
            return

        att_name = self._attitude_var.get().upper()
        try:
            att_val = ECritterAttitude[att_name].value
        except KeyError:
            messagebox.showerror("Invalid Attitude", f"Unknown attitude: {att_name}")
            return

        obj = GameObject(self._selected["_node"])
        obj.parsed_data["attitude"] = att_val
        obj.commit()

        self._selected["attitude"] = att_val
        # attitude_label will be refreshed by parent
        self._notify_parent()

    def _apply_position(self) -> None:
        """Apply new tile position (teleport)."""
        if not self._selected:
            return
        try:
            tx = int(self._tile_x_var.get())
            ty = int(self._tile_y_var.get())
        except ValueError:
            messagebox.showerror("Invalid Position", "Coordinates must be integers.")
            return

        tx = max(0, min(tx, 62))
        ty = max(0, min(ty, 62))

        obj = GameObject(self._selected["_node"])
        d = obj.parsed_data
        d["initialTileX"] = tx
        d["initialTileY"] = ty
        d["xhome"] = tx
        d["yhome"] = ty
        obj.commit()

        self._selected["tile_x"] = tx
        self._selected["tile_y"] = ty

        self._notify_parent()

    def _notify_parent(self) -> None:
        """
        Notify parent tab to refresh UI after an edit.
        This method should be overridden or connected by the parent (CrittersTab).
        """
        # This will be called from CrittersTab to trigger full refresh
        if hasattr(self.master, '_sync_after_edit'):
            self.master._sync_after_edit()
        elif hasattr(self.master.master, '_sync_after_edit'):  # fallback
            self.master.master._sync_after_edit()