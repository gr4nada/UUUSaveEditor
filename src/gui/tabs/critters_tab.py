"""
Critters Tab - Main Controller

Orchestrates the entire Critters tab UI. Acts as the central coordinator
between the toolbar, treeview, and all component panels.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional

from .critters.critter_model import Critter
from .critters.filters import filter_critters
from .critters.components.portrait_panel import PortraitPanel
from .critters.components.detail_panel import DetailPanel
from .critters.components.loot_panel import LootPanel
from .critters.components.editor_panel import EditorPanel
from .critters.components.inspector_panel import InspectorPanel

from src.core.database.critters import ECritterAttitude, ATTITUDE_BY_NAME, ATTITUDE_COLORS
from src.gui.widgets.icon_loader import IconLoader, ICON_SMALL
from src.gui.constants import THEME
from tkinter import messagebox


class CrittersTab(ttk.Frame):
    """
    Main controller for the Critters tab.
    
    Responsibilities:
        - Manage toolbar filters
        - Handle the main Treeview
        - Coordinate all sub-panels (Portrait, Details, Loot, Editor, Inspector)
        - Handle selection, filtering and editing flow
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=4)

        self._all_critters: List[Dict] = []
        self._filtered_critters: List[Dict] = []
        self._selected: Optional[Dict] = None
        self._loader = IconLoader.get_instance()

        self._row_icons: List = []          # Keep references to prevent GC
        self._build_ui()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, critters: List[Dict], save_game=None) -> None:
        """Load critters data and refresh the view."""
        self._save_game = save_game
        self._all_critters = critters
        self._update_level_filter()
        self._apply_filter()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build all UI elements."""
        self._build_toolbar()
        self._build_treeview()
        self._build_bottom_panels()

    def _build_toolbar(self) -> None:
        """Create toolbar with filters."""
        tb = ttk.Frame(self)
        tb.pack(fill="x", pady=(0, 4))

        # Show Dead
        self._show_dead_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tb, text="Show Dead",
                        variable=self._show_dead_var,
                        command=self._apply_filter).pack(side="left", padx=(0, 10))

        # Level Filter
        ttk.Label(tb, text="Level:").pack(side="left", padx=(0, 3))
        self._level_var = tk.StringVar(value="All")
        self._level_cb = ttk.Combobox(tb, textvariable=self._level_var,
                                      values=["All"], state="readonly", width=5)
        self._level_cb.pack(side="left", padx=(0, 10))
        self._level_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        # Attitude Filter
        ttk.Label(tb, text="Attitude:").pack(side="left", padx=(0, 3))
        self._attitude_var = tk.StringVar(value="All")
        ttk.Combobox(tb, textvariable=self._attitude_var,
                     values=["All", "Hostile", "Upset", "Mellow", "Friendly"],
                     state="readonly", width=9).pack(side="left", padx=(0, 10))
        self._attitude_var.trace_add("write", lambda *_: self._apply_filter())

        # Search
        ttk.Label(tb, text="Search:").pack(side="left", padx=(0, 3))
        self._search_var = tk.StringVar()
        ttk.Entry(tb, textvariable=self._search_var, width=20).pack(side="left", padx=(0, 10))
        self._search_var.trace_add("write", lambda *_: self._apply_filter())

        # Count label
        self._count_lbl = ttk.Label(tb, text="", foreground=THEME["fg_faint"],
                                    font=("Arial", 8))
        self._count_lbl.pack(side="right", padx=8)

    def _build_treeview(self) -> None:
        """Build the main critters treeview."""
        tf = ttk.Frame(self)
        tf.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tf, orient="vertical")
        vsb.pack(side="right", fill="y")

        self._tree = ttk.Treeview(
            tf, columns=("name", "type", "clvl", "hp", "state", "attitude", "goal", "loc"),
            show="headings", yscrollcommand=vsb.set, selectmode="browse")
        self._tree.pack(fill="both", expand=True)
        vsb.config(command=self._tree.yview)

        # Column configuration
        cols = {
            "name":     ("Name",      150, "w"),
            "type":     ("Creature",  100, "w"),
            "clvl":     ("Lv",         28, "center"),
            "hp":       ("HP",         68, "center"),
            "state":    ("State",     120, "w"),
            "attitude": ("Attitude",  130, "w"),
            "goal":     ("Goal",      170, "w"),
            "loc":      ("Loc",        72, "center"),
        }

        for col, (heading, width, anchor) in cols.items():
            self._tree.heading(col, text=heading, command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=width, anchor=anchor, stretch=(col in ("name", "state", "attitude", "goal")))

        # Tags
        for att_val, fg in ATTITUDE_COLORS.items():
            self._tree.tag_configure(f"att_{att_val}", foreground=fg)
        self._tree.tag_configure("dead_row", foreground=THEME["fg_dead"])
        self._tree.tag_configure("even", background=THEME["list_row_even"])
        self._tree.tag_configure("odd", background=THEME["list_row_odd"])
        self._tree.tag_configure("named", font=("Arial", 9, "bold"))

        self._tree.bind("<<TreeviewSelect>>", self._on_select)

    def _build_bottom_panels(self) -> None:
        """Create and layout all bottom panels."""
        bottom = ttk.Frame(self)
        bottom.pack(fill="both", expand=True, pady=(6, 0))

        # Top row: Portrait | Details | Editor
        top_row = ttk.Frame(bottom)
        top_row.pack(fill="x", pady=(0, 4))

        self._portrait_panel = PortraitPanel(top_row)
        self._portrait_panel.pack(side="left", fill="y", padx=(0, 4))

        self._detail_panel = DetailPanel(top_row)
        self._detail_panel.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self._editor_panel = EditorPanel(top_row)
        self._editor_panel.pack(side="left", fill="y", padx=(4, 0))

        # Loot panel (full width below)
        self._loot_panel = LootPanel(bottom)
        self._loot_panel.pack(fill="x", pady=(4, 0))

        # Inspector (dynamic)
        self._inspector_panel = InspectorPanel(bottom)

    # ------------------------------------------------------------------
    # Filtering & Display
    # ------------------------------------------------------------------

    def _update_level_filter(self) -> None:
        """Update level combobox with available levels."""
        levels = sorted({c.get("level", 0) for c in self._all_critters})
        self._level_cb.config(values=["All"] + [str(l) for l in levels])

    def _apply_filter(self) -> None:
        """Apply all filters and refresh the treeview."""
        show_dead = self._show_dead_var.get()
        level_str = self._level_var.get()
        min_level = int(level_str) if level_str != "All" else 0

        att_str = self._attitude_var.get()
        attitude_filter = ATTITUDE_BY_NAME.get(att_str) if att_str != "All" else None

        search = self._search_var.get().strip().lower()

        self._filtered_critters = filter_critters(
            self._all_critters,
            show_dead=show_dead,
            min_level=min_level,
            attitude_filter=attitude_filter,
            search_term=search
        )

        self._refresh_treeview()

    def _refresh_treeview(self) -> None:
        """Populate the treeview with filtered critters."""
        self._tree.delete(*self._tree.get_children())
        self._row_icons.clear()

        for i, c in enumerate(self._filtered_critters):
            dead = c.get("dead", False)
            att = c.get("attitude", 0)
            named = c.get("whoami_id", 0) > 0

            tags = ["dead_row"] if dead else [f"att_{att}"]
            if named:
                tags.append("named")
            tags.append("even" if i % 2 == 0 else "odd")

            hp_str = f"{c.get('hp')}/{c.get('max_hp')}" if not dead else "✕"
            loc_str = f"L{c.get('level')} ({c.get('tile_x')},{c.get('tile_y')})"

            self._tree.insert("", "end", iid=str(i), values=(
                c.get("name", "—"),
                c.get("type_name", "—"),
                c.get("critter_level", 0),
                hp_str,
                c.get("state_label", "—"),
                c.get("attitude_label", "—"),
                c.get("goal_label", "—"),
                loc_str,
            ), tags=tags)

        n = len(self._filtered_critters)
        total = len(self._all_critters)
        self._count_lbl.config(
            text=f"{n} critter{'s' if n != 1 else ''}" + (f" of {total}" if n != total else "")
        )

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def _on_select(self, _event) -> None:
        """Handle treeview selection."""
        sel = self._tree.selection()
        if not sel:
            return

        try:
            idx = int(sel[0])
            if idx >= len(self._filtered_critters):
                return
            critter = self._filtered_critters[idx]
        except (ValueError, IndexError):
            return

        self._selected = critter

        self._portrait_panel.update(critter)
        self._detail_panel.update(critter)
        self._loot_panel.update(critter)
        self._editor_panel.refresh(critter)
        self._inspector_panel.load_critter(critter, self._save_game)

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def _sort_by(self, col: str) -> None:
        """Sort treeview by column."""
        # Simple implementation - can be expanded
        pass  # TODO: full sorting if needed

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def get_selected(self) -> Optional[Dict]:
        """Return currently selected critter."""
        return self._selected