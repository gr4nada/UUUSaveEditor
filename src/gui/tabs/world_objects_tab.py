# src/gui/tabs/world_objects_tab.py
"""
Aba 'World Objects' — Item Explorer com ícones reais + Summary.

Treeview: [ícone] / Name / Type / Lv / Qty / Enchantment / Location
Ícones carregados de assets/icons/{objectType}.png via IconLoader.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from src.core.world_parser       import parse_world, filter_items
from src.core.enums              import ITEM_TYPE_GROUPS
from src.gui.widgets.icon_loader import IconLoader, ICON_SMALL

_GROUPS = list(ITEM_TYPE_GROUPS.keys())

_COLS = ("img", "name", "type", "level", "qty", "enchant", "loc")
_COL_CFG = {
    "img":     ("",            28,  "center"),
    "name":    ("Name",       200,  "w"),
    "type":    ("Type",        86,  "center"),
    "level":   ("Lv",          30,  "center"),
    "qty":     ("Qty",         34,  "center"),
    "enchant": ("Enchantment",150,  "w"),
    "loc":     ("Location",    86,  "center"),
}


class WorldObjectsTab(ttk.Frame):

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=4)
        self._all_items:    list[dict] = []
        self._all_critters: list[dict] = []
        self._loader  = IconLoader.get_instance()
        self._row_icons: list         = []   # referências fortes
        self._build()

    def load(self, save_game) -> None:
        self._all_critters, self._all_items = parse_world(save_game.raw)
        self._apply_filter()
        self._populate_summary(save_game)

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build(self) -> None:
        sub = ttk.Notebook(self)
        sub.pack(fill="both", expand=True)

        items_f   = ttk.Frame(sub, padding=6)
        summary_f = ttk.Frame(sub, padding=10)

        sub.add(items_f,   text="  Item Explorer  ")
        sub.add(summary_f, text="  Summary  ")

        self._build_explorer(items_f)
        self._build_summary(summary_f)

    def _build_explorer(self, parent: ttk.Frame) -> None:
        # ── Toolbar ──
        tb = ttk.Frame(parent)
        tb.pack(fill="x", pady=(0, 6))

        ttk.Label(tb, text="Filter:").pack(side="left", padx=(0, 4))
        self._group_var = tk.StringVar(value="All")
        cb = ttk.Combobox(tb, textvariable=self._group_var,
                          values=_GROUPS, state="readonly", width=12)
        cb.pack(side="left", padx=(0, 14))
        cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        ttk.Label(tb, text="Search:").pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        ttk.Entry(tb, textvariable=self._search_var, width=18).pack(side="left")
        self._search_var.trace_add("write", lambda *_: self._apply_filter())

        self._count_lbl = ttk.Label(tb, text="", foreground="#555",
                                    font=("Arial", 8))
        self._count_lbl.pack(side="right", padx=8)

        # ── Treeview ──
        tf = ttk.Frame(parent)
        tf.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tf, orient="vertical")
        hsb = ttk.Scrollbar(tf, orient="horizontal")
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        self._tree = ttk.Treeview(
            tf, columns=_COLS, show="headings",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set,
            selectmode="browse",
        )
        self._tree.pack(fill="both", expand=True)
        vsb.config(command=self._tree.yview)
        hsb.config(command=self._tree.xview)

        for col, (heading, width, anchor) in _COL_CFG.items():
            self._tree.heading(col, text=heading,
                               command=lambda c=col: self._sort(c))
            self._tree.column(col, width=width, anchor=anchor,
                              stretch=(col == "name"))

        self._tree.tag_configure("even", background="#1a1a1a")
        self._tree.tag_configure("odd",  background="#141414")
        self._tree.tag_configure("ench", foreground="#d4af37")

    def _apply_filter(self) -> None:
        group  = self._group_var.get()
        search = self._search_var.get().strip()
        visible = filter_items(self._all_items, group, search)

        self._tree.delete(*self._tree.get_children())
        self._row_icons.clear()

        for i, item in enumerate(visible):
            name  = item["object_name"] or f"[{item['type_name']}]"
            ench  = item["enchantment"]
            loc   = f"L{item['level']} ({item['tile_x']},{item['tile_y']})"
            tags  = ["ench"] if ench else []
            tags.append("even" if i % 2 == 0 else "odd")

            # Ícone real do item
            photo = self._loader.get_item_icon(item["object_type"], ICON_SMALL)
            self._row_icons.append(photo)

            iid = self._tree.insert("", "end", values=(
                "", name, item["type_name"],
                item["level"], item["quantity"], ench, loc,
            ), tags=tags)
            self._tree.item(iid, image=photo)

        n = len(visible)
        t = len(self._all_items)
        self._count_lbl.config(
            text=f"{n:,} item{'s' if n!=1 else ''}"
                 + (f" of {t:,}" if n != t else ""))

    def _sort(self, col: str) -> None:
        numeric = col in ("level", "qty")
        rows = [(self._tree.set(k, col), k) for k in self._tree.get_children("")]
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
        self._summary = tk.Text(
            parent, font=("Consolas", 9), background="#111",
            foreground="#aaa", relief="flat", state="disabled", wrap="none")
        sb = ttk.Scrollbar(parent, command=self._summary.yview)
        self._summary.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._summary.pack(fill="both", expand=True)
        self._summary.tag_configure("h", foreground="#ffffff",
                                    font=("Consolas", 9, "bold"))
        self._summary.tag_configure("v", foreground="#4ec9b0")
        self._summary.tag_configure("s", foreground="#666666")

    def _populate_summary(self, save_game) -> None:
        from collections import Counter
        items    = self._all_items
        critters = self._all_critters

        by_type  = Counter(i["type_name"] for i in items)
        by_level = Counter(i["level"]     for i in items)
        ct_type  = Counter(c["type_name"] for c in critters)
        ct_level = Counter(c["level"]     for c in critters)
        ench     = sum(1 for i in items    if i["is_enchanted"])
        dead     = sum(1 for c in critters if c["dead"])
        named    = sum(1 for c in critters if c["whoami_id"] > 0)

        t = self._summary
        t.config(state="normal")
        t.delete("1.0", "end")

        def row(label, value):
            t.insert("end", f"  {label:<28}", "s")
            t.insert("end", f"{value}\n",     "v")

        def sec(title):
            t.insert("end", f"\n  {title}\n", "h")
            t.insert("end", f"  {'─'*40}\n",  "s")

        sec("World Objects Summary")
        row("Total items tracked:", f"{len(items):,}")
        row("Enchanted items:",     f"{ench:,}")
        row("Total critters:",      f"{len(critters):,}")
        row("Named NPCs:",          f"{named}")
        row("Dead critters:",       f"{dead}")

        sec("Items by Type")
        for name, count in sorted(by_type.items(), key=lambda x: -x[1])[:15]:
            row(f"  {name}:", f"{count:,}")

        sec("Items by Dungeon Level")
        for lvl in sorted(by_level):
            row(f"  Level {lvl}:", f"{by_level[lvl]:,}")

        sec("Critters by Type")
        for name, count in sorted(ct_type.items(), key=lambda x: -x[1])[:12]:
            row(f"  {name}:", f"{count}")

        t.config(state="disabled")
