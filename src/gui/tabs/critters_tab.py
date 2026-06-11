# src/gui/tabs/critters_tab.py
"""
Aba 'Critters' — explorer de NPCs e criaturas do mundo.

Colunas:  Name / Type / Lv / HP / State / Attitude / Dead / Loot
Filtros:  [Show Dead ☑]  [Level ▼]
"""
import tkinter as tk
from tkinter import ttk
from src.core.world_parser import filter_critters

_COLS = ("name", "type", "clvl", "hp", "state", "attitude", "dead", "loot")
_COL_CFG = {
    "name":     ("Name",       160, "w"),
    "type":     ("Creature",   110, "w"),
    "clvl":     ("Lv",          32, "center"),
    "hp":       ("HP",          70, "center"),
    "state":    ("State",       72, "center"),
    "attitude": ("Attitude",    82, "center"),
    "dead":     ("Dead",        44, "center"),
    "loot":     ("Loot",        44, "center"),
}

_ATTITUDE_COLORS = {
    "Hostile":  "#ff6b6b",
    "Neutral":  "#ffd93d",
    "Friendly": "#6bcb77",
    "Ally":     "#4d96ff",
}


class CrittersTab(ttk.Frame):
    """
    Aba Critters.

    API pública:
        load(critters: list[dict]) → popula a tabela
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=4)
        self._all_critters: list[dict] = []
        self._build()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def load(self, critters: list[dict]) -> None:
        self._all_critters = critters
        self._update_level_filter()
        self._apply_filter()

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # ── Toolbar ──
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 6))

        # Show dead
        self._show_dead_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Show Dead",
                        variable=self._show_dead_var,
                        command=self._apply_filter).pack(side="left", padx=(0, 14))

        # Filtro por dungeon level
        ttk.Label(toolbar, text="Dungeon Level:").pack(side="left", padx=(0, 4))
        self._level_var = tk.StringVar(value="All")
        self._level_cb  = ttk.Combobox(toolbar, textvariable=self._level_var,
                                        values=["All"], state="readonly", width=6)
        self._level_cb.pack(side="left", padx=(0, 14))
        self._level_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        # Busca por nome
        ttk.Label(toolbar, text="Search:").pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self._search_var, width=16).pack(side="left")
        self._search_var.trace_add("write", lambda *_: self._apply_filter())

        self._count_lbl = ttk.Label(toolbar, text="", foreground="#666",
                                    font=("Arial", 8))
        self._count_lbl.pack(side="right", padx=8)

        # ── Treeview ──
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        self._tree = ttk.Treeview(
            tree_frame,
            columns=_COLS,
            show="headings",
            yscrollcommand=vsb.set,
            selectmode="browse",
        )
        self._tree.pack(fill="both", expand=True)
        vsb.config(command=self._tree.yview)

        for col, (heading, width, anchor) in _COL_CFG.items():
            self._tree.heading(col, text=heading,
                               command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=width, anchor=anchor,
                              stretch=(col == "name"))

        # Tags de cor por attitude
        for att, color in _ATTITUDE_COLORS.items():
            self._tree.tag_configure(att.lower(), foreground=color)
        self._tree.tag_configure("dead_row", foreground="#555")
        self._tree.tag_configure("even",     background="#1a1a1a")
        self._tree.tag_configure("odd",      background="#141414")
        self._tree.tag_configure("named",    font=("Arial", 9, "bold"))

        # Detail panel (aparece ao selecionar)
        self._detail = tk.Text(
            self,
            height=5,
            font=("Consolas", 8),
            background="#0d0d0d",
            foreground="#888",
            relief="flat",
            state="disabled",
            wrap="word",
        )
        self._detail.pack(fill="x", pady=(6, 0))
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

    # ------------------------------------------------------------------
    # Lógica
    # ------------------------------------------------------------------

    def _update_level_filter(self) -> None:
        levels = sorted({c["level"] for c in self._all_critters})
        self._level_cb.config(values=["All"] + [str(l) for l in levels])
        self._level_var.set("All")

    def _apply_filter(self) -> None:
        show_dead = self._show_dead_var.get()
        lvl_str   = self._level_var.get()
        level     = int(lvl_str) if lvl_str != "All" else 0
        search    = self._search_var.get().strip().lower()

        visible = filter_critters(self._all_critters, show_dead, level)
        if search:
            visible = [c for c in visible
                       if search in c["name"].lower()
                       or search in c["type_name"].lower()]

        self._tree.delete(*self._tree.get_children())
        for i, c in enumerate(visible):
            att   = c["attitude_label"].lower()
            dead  = c["dead"]
            named = c["whoami_id"] > 0

            tags = [att]
            if dead:
                tags = ["dead_row"]
            elif named:
                tags.append("named")
            tags.append("even" if i % 2 == 0 else "odd")

            hp_str   = f"{c['hp']}/{c['max_hp']}" if not dead else "✕"
            dead_str = "✕" if dead else ""

            self._tree.insert("", "end", iid=str(i), values=(
                c["name"],
                c["type_name"],
                c["critter_level"],
                hp_str,
                f"State {c['state']}",
                c["attitude_label"],
                dead_str,
                c["loot_count"] or "",
            ), tags=tags)

        n = len(visible)
        total = len(self._all_critters)
        self._count_lbl.config(
            text=f"{n} critter{'s' if n != 1 else ''}"
                 + (f" of {total}" if n != total else ""))

    def _on_select(self, _event) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        try:
            idx = int(sel[0])
            # Reconstruir lista filtrada para pegar o item certo
            show_dead = self._show_dead_var.get()
            lvl_str   = self._level_var.get()
            level     = int(lvl_str) if lvl_str != "All" else 0
            visible   = filter_critters(self._all_critters, show_dead, level)
            if idx >= len(visible):
                return
            c = visible[idx]
        except (ValueError, IndexError):
            return

        detail = (
            f"  Name:          {c['name']}  (whoami={c['whoami_id']})\n"
            f"  Type:          {c['type_name']}  (objectType={c['object_type']})\n"
            f"  Dungeon Level: {c['level']}   Critter Level: {c['critter_level']}\n"
            f"  HP:            {c['hp']} / {c['max_hp']}\n"
            f"  Attitude:      {c['attitude_label']} ({c['attitude']})"
            f"   State: {c['state']}   PlayerAlly: {c['player_ally']}\n"
            f"  Talked To:     {c['talked_to']}   Loot slots: {c['loot_count']}"
            f"   Dead: {c['dead']}"
        )
        self._detail.config(state="normal")
        self._detail.delete("1.0", "end")
        self._detail.insert("end", detail)
        self._detail.config(state="disabled")

    def _sort_by(self, col: str) -> None:
        col_map = {k: i for i, k in enumerate(_COLS)}
        idx = col_map.get(col, 0)
        numeric = col in ("clvl", "loot")
        rows = [(self._tree.set(k, col), k) for k in self._tree.get_children("")]
        try:
            rows.sort(key=lambda t: int(t[0]) if numeric and t[0].isdigit() else t[0].lower())
        except Exception:
            rows.sort(key=lambda t: t[0].lower())
        for i, (_, k) in enumerate(rows):
            self._tree.move(k, "", i)
