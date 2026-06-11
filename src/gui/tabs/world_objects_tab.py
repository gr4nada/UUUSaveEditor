# src/gui/tabs/world_objects_tab.py
"""
Aba 'World Objects' — explorer de items do mundo.

Sub-notebook:
  Items   — Treeview com Icon / Name / Type / Level / Qty / Enchantment
             Filtro por grupo + campo de busca
  Summary — contagens por tipo e por nível
"""
import tkinter as tk
from tkinter import ttk
from src.core.world_parser import parse_world, filter_items
from src.core.enums        import ITEM_TYPE_GROUPS


_GROUPS = list(ITEM_TYPE_GROUPS.keys())

# Colunas do Treeview de items
_COLS = ("icon", "name", "type", "level", "qty", "enchant")
_COL_CFG = {
    "icon":    ("",            40,  "center"),
    "name":    ("Name",       220,  "w"),
    "type":    ("Type",        90,  "center"),
    "level":   ("Lv",          32,  "center"),
    "qty":     ("Qty",         36,  "center"),
    "enchant": ("Enchantment",160,  "w"),
}


class WorldObjectsTab(ttk.Frame):
    """
    Aba World Objects.

    API pública:
        load(save_game) → parse + popula os dois sub-tabs
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=4)
        self._all_items:    list[dict] = []
        self._all_critters: list[dict] = []
        self._build()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def load(self, save_game) -> None:
        self._all_critters, self._all_items = parse_world(save_game.raw)
        self._populate_items()
        self._populate_summary(save_game)

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build(self) -> None:
        sub = ttk.Notebook(self)
        sub.pack(fill="both", expand=True)

        items_frame   = ttk.Frame(sub, padding=6)
        summary_frame = ttk.Frame(sub, padding=16)

        sub.add(items_frame,   text="  Item Explorer  ")
        sub.add(summary_frame, text="  Summary  ")

        self._build_item_explorer(items_frame)
        self._build_summary(summary_frame)

    # ------------------------------------------------------------------
    # Item Explorer
    # ------------------------------------------------------------------

    def _build_item_explorer(self, parent: ttk.Frame) -> None:
        # ── Toolbar ──
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 6))

        ttk.Label(toolbar, text="Filter:").pack(side="left", padx=(0, 4))
        self._group_var = tk.StringVar(value="All")
        group_cb = ttk.Combobox(toolbar, textvariable=self._group_var,
                                values=_GROUPS, state="readonly", width=12)
        group_cb.pack(side="left", padx=(0, 12))
        group_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        ttk.Label(toolbar, text="Search:").pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self._search_var, width=18)
        search_entry.pack(side="left")
        self._search_var.trace_add("write", lambda *_: self._apply_filter())

        self._count_lbl = ttk.Label(toolbar, text="", foreground="#666",
                                    font=("Arial", 8))
        self._count_lbl.pack(side="right", padx=8)

        # ── Treeview ──
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")

        self._tree = ttk.Treeview(
            tree_frame,
            columns=_COLS,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse",
        )
        self._tree.pack(fill="both", expand=True)
        vsb.config(command=self._tree.yview)
        hsb.config(command=self._tree.xview)

        for col, (heading, width, anchor) in _COL_CFG.items():
            self._tree.heading(col, text=heading,
                               command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=width, anchor=anchor,
                              stretch=(col == "name"))

        # Cor alternada de linhas
        self._tree.tag_configure("even", background="#1a1a1a")
        self._tree.tag_configure("odd",  background="#141414")
        self._tree.tag_configure("ench", foreground="#d4af37")

    def _populate_items(self) -> None:
        self._apply_filter()

    def _apply_filter(self) -> None:
        group  = self._group_var.get()
        search = self._search_var.get().strip()
        visible = filter_items(self._all_items, group, search)

        self._tree.delete(*self._tree.get_children())
        for i, item in enumerate(visible):
            name  = item["object_name"] or f"[{item['type_name']}]"
            ench  = item["enchantment"]
            tags  = []
            if ench:
                tags.append("ench")
            tags.append("even" if i % 2 == 0 else "odd")

            self._tree.insert("", "end", values=(
                item["icon"],
                name,
                item["type_name"],
                item["level"],
                item["quantity"],
                ench,
            ), tags=tags)

        n = len(visible)
        total = len(self._all_items)
        self._count_lbl.config(
            text=f"{n:,} item{'s' if n != 1 else ''}"
                 + (f" of {total:,}" if n != total else ""))

    def _sort_by(self, col: str) -> None:
        """Ordena o Treeview pela coluna clicada."""
        col_map = {"icon": 0, "name": 1, "type": 2,
                   "level": 3, "qty": 4, "enchant": 5}
        idx = col_map.get(col, 1)
        rows = [(self._tree.set(k, col), k) for k in self._tree.get_children("")]
        numeric = col in ("level", "qty")
        try:
            rows.sort(key=lambda t: int(t[0]) if numeric else t[0].lower())
        except ValueError:
            rows.sort(key=lambda t: t[0].lower())
        for i, (_, k) in enumerate(rows):
            self._tree.move(k, "", i)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def _build_summary(self, parent: ttk.Frame) -> None:
        self._summary_text = tk.Text(
            parent,
            font=("Consolas", 9),
            background="#111",
            foreground="#aaa",
            relief="flat",
            state="disabled",
            wrap="none",
        )
        sb = ttk.Scrollbar(parent, command=self._summary_text.yview)
        self._summary_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._summary_text.pack(fill="both", expand=True)

        self._summary_text.tag_configure("header",  foreground="#ffffff",
                                          font=("Consolas", 9, "bold"))
        self._summary_text.tag_configure("value",   foreground="#4ec9b0")
        self._summary_text.tag_configure("section", foreground="#888888")

    def _populate_summary(self, save_game) -> None:
        from collections import Counter

        critters = self._all_critters
        items    = self._all_items

        # Contagens
        by_type  = Counter(i["type_name"] for i in items)
        by_level = Counter(i["level"]     for i in items)
        c_by_type  = Counter(c["type_name"] for c in critters)
        c_by_level = Counter(c["level"]     for c in critters)
        dead = sum(1 for c in critters if c["dead"])
        named = sum(1 for c in critters if c["whoami_id"] > 0)
        ench_count = sum(1 for i in items if i["is_enchanted"])

        t = self._summary_text
        t.config(state="normal")
        t.delete("1.0", "end")

        def line(text, tag=""):
            t.insert("end", text + "\n", tag)

        line(f"  World Objects Summary", "header")
        line(f"  ──────────────────────────────────────", "section")
        line(f"  Total items tracked:    ", "section")
        t.insert("end", f"{len(items):,}\n", "value")
        line(f"  Enchanted items:        ", "section")
        t.insert("end", f"{ench_count:,}\n", "value")
        line(f"  Total critters:         ", "section")
        t.insert("end", f"{len(critters):,}\n", "value")
        line(f"  Named NPCs (whoami>0):  ", "section")
        t.insert("end", f"{named:,}\n", "value")
        line(f"  Dead critters:          ", "section")
        t.insert("end", f"{dead}\n", "value")
        line("")

        line("  Items by Type", "header")
        line("  ──────────────────────────────────────", "section")
        for tname, count in sorted(by_type.items(), key=lambda x: -x[1])[:15]:
            line(f"  {tname:<20} ", "section")
            t.insert("end", f"{count:,}\n", "value")
        line("")

        line("  Items by Dungeon Level", "header")
        line("  ──────────────────────────────────────", "section")
        for lvl in sorted(by_level):
            line(f"  Level {lvl:<5}             ", "section")
            t.insert("end", f"{by_level[lvl]:,}\n", "value")
        line("")

        line("  Critters by Type", "header")
        line("  ──────────────────────────────────────", "section")
        for tname, count in sorted(c_by_type.items(), key=lambda x: -x[1])[:12]:
            line(f"  {tname:<20} ", "section")
            t.insert("end", f"{count}\n", "value")
        line("")

        line("  Critters by Dungeon Level", "header")
        line("  ──────────────────────────────────────", "section")
        for lvl in sorted(c_by_level):
            line(f"  Level {lvl:<5}             ", "section")
            t.insert("end", f"{c_by_level[lvl]}\n", "value")

        t.config(state="disabled")
