"""
Editor Panel Component

Provides direct editing controls for the selected critter:
- HP modification with validation
- Revive / Kill actions
- Attitude selection
- Tile position (teleport)
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging
from typing import Optional, Dict

from src.core.save_model import GameObject
from src.core.database.critters import ECritterAttitude
from src.gui.constants import THEME

logger = logging.getLogger("gui.tabs.critters.editor")


class EditorPanel(ttk.LabelFrame):
    """
    Painel de edição inline para propriedades do critter selecionado.
    """

    def __init__(self, parent):
        super().__init__(parent, text=" Quick Editor ", padding=8)
        self._selected: Optional[dict] = None
        self._build_ui()

    def _build_ui(self) -> None:
        """Constrói a interface do editor."""
        row = 0

        # ==================== HP ====================
        ttk.Label(self, text="HP:", foreground=THEME.get("fg_muted")).grid(
            row=row, column=0, sticky="e", padx=(0, 6), pady=4)

        self._hp_var = tk.StringVar()
        self._hp_entry = ttk.Entry(self, textvariable=self._hp_var, width=8, state="disabled")
        self._hp_entry.grid(row=row, column=1, sticky="w", pady=4)

        self._apply_hp_btn = ttk.Button(
            self, text="Apply", command=self._apply_hp, state="disabled", width=6)
        self._apply_hp_btn.grid(row=row, column=2, padx=(8, 0), pady=4)
        row += 1

        # ==================== Revive / Kill ====================
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=3, sticky="we", pady=8)

        self._revive_btn = ttk.Button(
            btn_frame, text="Revive", command=self._on_revive, state="disabled")
        self._revive_btn.pack(side=tk.LEFT, padx=(0, 6))

        self._kill_btn = ttk.Button(
            btn_frame, text="Kill", command=self._on_kill, state="disabled")
        self._kill_btn.pack(side=tk.LEFT)
        row += 1

        # ==================== Attitude ====================
        ttk.Separator(self, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="we", pady=10)
        row += 1

        ttk.Label(self, text="Attitude:", foreground=THEME.get("fg_muted")).grid(
            row=row, column=0, sticky="e", padx=(0, 6), pady=4)

        self._attitude_var = tk.StringVar()
        attitude_options = [a.name.capitalize() for a in ECritterAttitude]

        self._attitude_cb = ttk.Combobox(
            self, textvariable=self._attitude_var,
            values=attitude_options, state="disabled", width=14)
        self._attitude_cb.grid(row=row, column=1, columnspan=2, sticky="w", pady=4)
        row += 1

        self._apply_att_btn = ttk.Button(
            self, text="Apply Attitude", command=self._apply_attitude, state="disabled")
        self._apply_att_btn.grid(row=row, column=0, columnspan=3, sticky="we", pady=(2, 8))
        row += 1

        # ==================== Tile Position (Teleport) ====================
        ttk.Separator(self, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="we", pady=8)
        row += 1

        ttk.Label(self, text="Tile X:", foreground=THEME.get("fg_muted")).grid(
            row=row, column=0, sticky="e", padx=(0, 6), pady=4)
        self._tile_x_var = tk.IntVar()
        self._tile_x_spin = ttk.Spinbox(
            self, textvariable=self._tile_x_var, from_=0, to=127, width=7, state="disabled")
        self._tile_x_spin.grid(row=row, column=1, sticky="w", pady=4)
        row += 1

        ttk.Label(self, text="Tile Y:", foreground=THEME.get("fg_muted")).grid(
            row=row, column=0, sticky="e", padx=(0, 6), pady=4)
        self._tile_y_var = tk.IntVar()
        self._tile_y_spin = ttk.Spinbox(
            self, textvariable=self._tile_y_var, from_=0, to=127, width=7, state="disabled")
        self._tile_y_spin.grid(row=row, column=1, sticky="w", pady=4)
        row += 1

        self._teleport_btn = ttk.Button(
            self, text="Teleport", command=self._apply_position, state="disabled")
        self._teleport_btn.grid(row=row, column=0, columnspan=3, sticky="we", pady=(6, 0))

        # Hint
        self._hint = ttk.Label(
            self,
            text="Select a critter to enable editing.",
            foreground=THEME.get("fg_muted"),
            font=("Arial", 8, "italic"),
            wraplength=200
        )
        self._hint.grid(row=row+1, column=0, columnspan=3, pady=(12, 0))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh(self, critter: dict) -> None:
        """Atualiza o painel com o critter selecionado."""
        self._selected = critter

        if not critter:
            self._disable_all()
            return

        self._enable_all()

        # HP
        self._hp_var.set(str(critter.get("hp", 0)))

        # Revive / Kill
        is_dead = critter.get("dead", False)
        self._revive_btn.config(state="normal" if is_dead else "disabled")
        self._kill_btn.config(state="normal" if not is_dead else "disabled")

        # Attitude
        try:
            att_name = ECritterAttitude(critter.get("attitude", 0)).name.capitalize()
            self._attitude_var.set(att_name)
        except:
            self._attitude_var.set("Mellow")

        # Position
        self._tile_x_var.set(critter.get("tile_x", 0))
        self._tile_y_var.set(critter.get("tile_y", 0))

        name = critter.get("name") or critter.get("type_name", "Critter")
        self._hint.config(text=f"Editing: {name}")

    def _disable_all(self):
        """Desabilita todos os controles."""
        for w in (self._hp_entry, self._apply_hp_btn, self._revive_btn,
                  self._kill_btn, self._attitude_cb, self._apply_att_btn,
                  self._tile_x_spin, self._tile_y_spin, self._teleport_btn):
            w.config(state="disabled")

    def _enable_all(self):
        """Habilita todos os controles."""
        for w in (self._hp_entry, self._apply_hp_btn, self._attitude_cb,
                  self._apply_att_btn, self._tile_x_spin, self._tile_y_spin,
                  self._teleport_btn):
            w.config(state="normal")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _apply_hp(self):
        if not self._selected:
            return
        try:
            value = int(self._hp_var.get())
        except ValueError:
            messagebox.showerror("Erro", "HP deve ser um número inteiro.")
            return

        obj = GameObject(self._selected["_node"])
        obj.hp = value

        self._selected["hp"] = obj.hp
        self._selected["dead"] = obj.is_dead
        self._notify_parent()

    def _on_revive(self):
        if not self._selected:
            return
        obj = GameObject(self._selected["_node"])
        obj.revive()

        self._selected["hp"] = obj.hp
        self._selected["dead"] = False
        self._notify_parent()

    def _on_kill(self):
        if not self._selected:
            return
        obj = GameObject(self._selected["_node"])
        obj.kill()

        self._selected["hp"] = 0
        self._selected["dead"] = True
        self._notify_parent()

    def _apply_attitude(self):
        if not self._selected:
            return

        att_name = self._attitude_var.get().upper()
        try:
            att_value = ECritterAttitude[att_name].value
        except KeyError:
            messagebox.showerror("Erro", f"Atitude inválida: {att_name}")
            return

        obj = GameObject(self._selected["_node"])
        obj.parsed_data["attitude"] = att_value
        obj.commit()

        self._selected["attitude"] = att_value
        self._notify_parent()

    def _apply_position(self):
        if not self._selected:
            return
        try:
            x = int(self._tile_x_var.get())
            y = int(self._tile_y_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Coordenadas devem ser números inteiros.")
            return

        x = max(0, min(x, 127))
        y = max(0, min(y, 127))

        obj = GameObject(self._selected["_node"])
        data = obj.parsed_data
        data["initialTileX"] = x
        data["initialTileY"] = y
        data["xhome"] = x
        data["yhome"] = y
        obj.commit()

        self._selected["tile_x"] = x
        self._selected["tile_y"] = y
        self._notify_parent()

    def _notify_parent(self):
        """Notifica o tab pai para atualizar a UI."""
        if hasattr(self.master, "_sync_after_edit"):
            self.master._sync_after_edit()
        elif hasattr(self.master.master, "_sync_after_edit"):
            self.master.master._sync_after_edit()