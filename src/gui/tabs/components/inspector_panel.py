"""
Inspector Panel Component

Advanced panel for named NPCs (whoami > 0). Displays identity information
and allows editing of charGlobals (conversation memory / private variables).
"""

import tkinter as tk
from tkinter import ttk
import json
from typing import Optional, List

from src.gui.constants import THEME


class InspectorPanel(ttk.LabelFrame):
    """
    Advanced inspector panel for named NPCs.
    
    Shows:
        - Identity information (name, whoami, home, etc.)
        - Editable charGlobals grid (Int16 values)
    
    Only visible when a named NPC (whoami_id > 0) is selected.
    """

    def __init__(self, parent):
        super().__init__(parent, text=" NPC Inspector ", padding=6)
        self._selected: Optional[dict] = None
        self._cg_vars: List[tk.StringVar] = []
        self._cg_length: int = 0
        self._whoami: int = 0

        self._build()

    def _build(self) -> None:
        """Build the inspector UI."""
        # Identity row
        id_row = ttk.Frame(self)
        id_row.pack(fill="x", pady=(0, 6))

        self._name_lbl = ttk.Label(
            id_row, text="—", font=("Arial", 10, "bold"),
            foreground=THEME["fg_primary"])
        self._name_lbl.pack(side="left", padx=(0, 16))

        self._whoami_lbl = ttk.Label(id_row, text="", foreground=THEME["fg_muted"], font=("Arial", 9))
        self._whoami_lbl.pack(side="left", padx=(0, 14))

        self._home_lbl = ttk.Label(id_row, text="", foreground=THEME["fg_muted"], font=("Arial", 9))
        self._home_lbl.pack(side="left", padx=(0, 14))

        self._conv_lbl = ttk.Label(id_row, text="", foreground=THEME["fg_muted"], font=("Arial", 9))
        self._conv_lbl.pack(side="left", padx=(0, 14))

        self._level_lbl = ttk.Label(id_row, text="", foreground=THEME["fg_muted"], font=("Arial", 9))
        self._level_lbl.pack(side="left")

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=(0, 6))

        # Hint
        hint_text = (
            "charGlobals — Private conversation memory (per-NPC slots in bglobals.dat).\n"
            "Edit with caution: incorrect values may break NPC dialogues."
        )
        ttk.Label(
            self, text=hint_text, foreground=THEME["fg_muted"],
            font=("Arial", 8, "italic"), wraplength=780, justify="left"
        ).pack(anchor="w", pady=(0, 6))

        # Scrollable grid container
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(
            canvas_frame, height=140, highlightthickness=0,
            background=THEME.get("bg_deep", "#1e1e1e"))
        
        self._scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._grid_frame = ttk.Frame(self._canvas)
        self._grid_window = self._canvas.create_window((0, 0), window=self._grid_frame, anchor="nw")

        self._grid_frame.bind("<Configure>", self._on_grid_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(btn_frame, text="Apply charGlobals", command=self._apply_char_globals).pack(side="left")
        ttk.Button(btn_frame, text="Reset to Saved", command=self._reset_to_saved).pack(side="left", padx=(8, 0))

    def _on_grid_configure(self, event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self._canvas.itemconfig(self._grid_window, width=event.width)

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh(self, critter: dict) -> None:
        """Refresh inspector for the given critter."""
        self._selected = critter

        if not critter or critter.get("whoami_id", 0) == 0:
            self.pack_forget()
            return

        # Show panel
        self.pack(fill="x", padx=4, pady=(4, 0))

        whoami = critter.get("whoami_id", 0)
        self._whoami = whoami

        # Update identity labels
        self._name_lbl.config(text=critter.get("name", "Unknown"))
        self._whoami_lbl.config(text=f"whoami #{whoami}")
        self._home_lbl.config(text=f"Home: ({critter.get('tile_x', 0)}, {critter.get('tile_y', 0)})")
        self._level_lbl.config(text=f"L{critter.get('level', 0)}")
        self._conv_lbl.config(text=f"conv slot: {whoami}")

        # Load charGlobals
        self._load_char_globals(critter)

    def _load_char_globals(self, critter: dict) -> None:
        """Load and display charGlobals in editable grid."""
        # Clear previous widgets
        for widget in self._grid_frame.winfo_children():
            widget.destroy()
        self._cg_vars.clear()

        try:
            parsed = json.loads(critter["_node"]["jsonData"])
            cg = parsed.get("charGlobals", [])
        except Exception:
            cg = []

        self._cg_length = len(cg)

        if not cg:
            ttk.Label(self._grid_frame, text="(no charGlobals data)", 
                      foreground=THEME["fg_muted"]).grid(row=0, column=0, padx=20, pady=10)
            return

        ROWS_PER_COLUMN = 16

        for i, value in enumerate(cg):
            row = i % ROWS_PER_COLUMN
            col_group = (i // ROWS_PER_COLUMN) * 3

            is_nonzero = value != 0
            fg = THEME["fg_primary"] if is_nonzero else THEME["fg_muted"]

            # Index label
            ttk.Label(
                self._grid_frame,
                text=f"[{i:02d}]",
                font=("Consolas", 9),
                foreground=fg,
                anchor="e", width=4
            ).grid(row=row, column=col_group, sticky="e", padx=(8 if col_group == 0 else 4, 2), pady=1)

            # Editable Spinbox
            var = tk.StringVar(value=str(value))
            self._cg_vars.append(var)

            spin = ttk.Spinbox(
                self._grid_frame,
                textvariable=var,
                from_=-32768,
                to=32767,
                width=8,
                font=("Consolas", 9)
            )
            spin.grid(row=row, column=col_group + 1, sticky="w", pady=1)

            # Vertical separator between column groups
            if (i // ROWS_PER_COLUMN) < (len(cg) - 1) // ROWS_PER_COLUMN and row == ROWS_PER_COLUMN - 1:
                ttk.Separator(self._grid_frame, orient="vertical").grid(
                    row=row, column=col_group + 2, sticky="ns", rowspan=ROWS_PER_COLUMN, padx=8)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _apply_char_globals(self) -> None:
        """Save edited charGlobals back to the critter node."""
        if not self._selected or not self._cg_vars:
            return

        try:
            parsed = json.loads(self._selected["_node"]["jsonData"])
        except Exception:
            return

        cg = parsed.get("charGlobals", [])
        if len(cg) != self._cg_length:
            return

        changed = 0
        for i, var in enumerate(self._cg_vars):
            try:
                new_val = int(var.get())
                new_val = max(-32768, min(32767, new_val))  # clamp Int16
            except (ValueError, tk.TclError):
                new_val = cg[i]  # keep original on error

            if cg[i] != new_val:
                cg[i] = new_val
                changed += 1

        if changed > 0:
            parsed["charGlobals"] = cg
            self._selected["_node"]["jsonData"] = json.dumps(parsed)
            # Refresh display
            self.refresh(self._selected)

    def _reset_to_saved(self) -> None:
        """Reload charGlobals from current save data."""
        if self._selected:
            self.refresh(self._selected)

    def clear(self) -> None:
        """Hide and clear the inspector."""
        self.pack_forget()