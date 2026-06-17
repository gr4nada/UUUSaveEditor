"""
NPC Inspector Component

Painel detalhado para visualização e edição de um NPC/Critter,
com foco principal na edição de charGlobals.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, Optional

from src.gui.tabs.common.base_tab import BaseTab
from src.core.database.whoami import npc_name
from src.core.database.critters import attitude_label, attitude_color

logger = logging.getLogger("gui.tabs.critters.inspector")


class InspectorPanel(ttk.Frame):
    """
    Componente reutilizável que mostra informações detalhadas de um NPC
    e permite edição avançada de charGlobals.
    """

    def __init__(self, parent):
        super().__init__(parent, padding=8)
        self._current_critter = None
        self._save_game = None
        self._char_globals_vars: Dict[int, tk.StringVar] = {}
        self._original_globals = []

        self._build_ui()

    def _build_ui(self):
        # ==================== Header ====================
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill=tk.X, pady=(0, 12))

        self.lbl_name = ttk.Label(self.header_frame, text="", font=("TkDefaultFont", 12, "bold"))
        self.lbl_name.pack(anchor="w")

        self.lbl_details = ttk.Label(self.header_frame, text="", foreground="#666666")
        self.lbl_details.pack(anchor="w")

        # Separator
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # ==================== charGlobals Grid ====================
        grid_frame = ttk.LabelFrame(self, text=" charGlobals (NPC-specific memory) ", padding=8)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        self.grid_canvas = tk.Canvas(grid_frame)
        scrollbar = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.grid_canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.grid_canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox("all"))
        )

        self.grid_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.grid_canvas.configure(yscrollcommand=scrollbar.set)

        self.grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ==================== Buttons ====================
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=12)

        self.btn_apply = ttk.Button(btn_frame, text="Apply charGlobals", command=self.apply_changes)
        self.btn_apply.pack(side=tk.RIGHT, padx=4)

        self.btn_reset = ttk.Button(btn_frame, text="Reset to Saved", command=self.reset_to_saved)
        self.btn_reset.pack(side=tk.RIGHT, padx=4)

        # Bind mouse wheel
        self.grid_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def load_critter(self, critter: dict, save_game: Any):
        """Carrega um critter no inspector."""
        self._current_critter = critter
        self._save_game = save_game
        self._original_globals = list(critter.get("char_globals", critter.get("charGlobals", [])))

        self._update_header()
        self._build_globals_grid()

    def _update_header(self):
        if not self._current_critter:
            return

        name = self._current_critter.get("name", "Unknown")
        whoami = self._current_critter.get("whoami_id", 0)
        level = self._current_critter.get("level", 0)
        tile_x = self._current_critter.get("tile_x", "?")
        tile_y = self._current_critter.get("tile_y", "?")

        display_name = f"{name} — {npc_name(whoami)}" if whoami > 0 else name

        self.lbl_name.config(text=display_name)
        self.lbl_details.config(
            text=f"WhoAmI: {whoami}  |  Level: {level}  |  Home: ({tile_x}, {tile_y})"
        )

    def _build_globals_grid(self):
        """Constrói a grade de 16 colunas com Spinboxes."""
        # Limpa grid anterior
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self._char_globals_vars.clear()

        globals_list = self._current_critter.get("char_globals",
                       self._current_critter.get("charGlobals", []))
        if not globals_list:
            ttk.Label(self.scrollable_frame, text="No charGlobals data available.").pack(pady=20)
            return

        COLUMNS = 16
        for i, value in enumerate(globals_list):
            row = i // COLUMNS
            col = i % COLUMNS

            frame = ttk.Frame(self.scrollable_frame)
            frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

            var = tk.StringVar(value=str(value))
            self._char_globals_vars[i] = var

            spin = ttk.Spinbox(
                frame, 
                from_=-32768, 
                to=32767, 
                textvariable=var, 
                width=6,
                font=("TkDefaultFont", 9)
            )
            spin.pack()

            # Highlight non-zero values
            if value != 0:
                spin.config(foreground="#0066cc", font=("TkDefaultFont", 9, "bold"))

    def _on_mousewheel(self, event):
        self.grid_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def apply_changes(self) -> bool:
        """Aplica as alterações de charGlobals no critter."""
        if not self._current_critter or not self._save_game:
            return False

        new_globals = []
        for i in range(len(self._original_globals)):
            var = self._char_globals_vars.get(i)
            try:
                val = int(var.get()) if var else 0
                val = max(-32768, min(32767, val))  # Int16 clamp
            except (ValueError, TypeError):
                val = 0
            new_globals.append(val)

        # Atualiza o raw node
        node = self._current_critter.get("_node")
        if node and "jsonData" in node:
            try:
                import json
                data = json.loads(node["jsonData"])
                data["charGlobals"] = new_globals
                node["jsonData"] = json.dumps(data)
                logger.info(f"Applied charGlobals for whoami={self._current_critter.get('whoami_id')}")
                return True
            except Exception as e:
                logger.error(f"Failed to apply charGlobals: {e}")
                return False

        return False

    def reset_to_saved(self):
        """Recarrega os valores originais."""
        if self._current_critter:
            self.load_critter(self._current_critter, self._save_game)

    def get_changes(self) -> Dict[str, Any]:
        """Retorna mudanças para SaveController (se necessário)."""
        if not self._current_critter:
            return {}
        # Por enquanto, as mudanças são aplicadas diretamente no node
        return {}