# src/gui/tabs/critters_tab.py
"""
Aba 'Critters' — Explorer de NPCs e criaturas do mundo.

Layout:
  ┌─ Toolbar (filtros) ────────────────────────────────────────────────┐
  ├─ Treeview (Name / Creature / Lv / HP / State / Attitude / Dead / Loc) ─┤
  ├─ Painel inferior ─────────────────────────────────────────────────┤
  │  Portrait   │   Details (texto)   │   Loot (treeview com ícones)  │
  └────────────────────────────────────────────────────────────────────┘
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from src.core.world_parser       import filter_critters
from src.gui.widgets.icon_loader import IconLoader, ICON_SMALL, WHOAMI_SIZE

_COLS = ("name", "type", "clvl", "hp", "state", "attitude", "dead", "loc")
_COL_CFG = {
    "name":     ("Name",      160, "w"),
    "type":     ("Creature",  110, "w"),
    "clvl":     ("Lv",         32, "center"),
    "hp":       ("HP",         72, "center"),
    "state":    ("State",      56, "center"),
    "attitude": ("Attitude",   80, "center"),
    "dead":     ("Dead",       40, "center"),
    "loc":      ("Location",   80, "center"),
}

_ATTITUDE_FG = {
    "hostile":  "#ff6b6b",
    "neutral":  "#ffd93d",
    "friendly": "#6bcb77",
    "ally":     "#4d96ff",
}

# Tamanho do portrait no painel inferior
_PORTRAIT_W, _PORTRAIT_H = 80, 80


class CrittersTab(ttk.Frame):
    """
    API pública:
        load(critters: list[dict]) → popula a tabela
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=4)
        self._all:      list[dict]          = []
        self._loader    = IconLoader.get_instance()
        # Referências fortes a PhotoImages para evitar GC
        self._row_icons: list               = []
        self._loot_icons: list              = []
        self._portrait_ref                  = None
        self._build()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def load(self, critters: list[dict]) -> None:
        self._all = critters
        self._update_level_filter()
        self._apply_filter()

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # ── Toolbar ──
        tb = ttk.Frame(self)
        tb.pack(fill="x", pady=(0, 4))

        self._show_dead_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tb, text="Show Dead",
                        variable=self._show_dead_var,
                        command=self._apply_filter).pack(side="left", padx=(0, 12))

        ttk.Label(tb, text="Level:").pack(side="left", padx=(0, 4))
        self._level_var = tk.StringVar(value="All")
        self._level_cb  = ttk.Combobox(tb, textvariable=self._level_var,
                                        values=["All"], state="readonly", width=6)
        self._level_cb.pack(side="left", padx=(0, 12))
        self._level_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        ttk.Label(tb, text="Search:").pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        ttk.Entry(tb, textvariable=self._search_var, width=16).pack(side="left")
        self._search_var.trace_add("write", lambda *_: self._apply_filter())

        self._count_lbl = ttk.Label(tb, text="", foreground="#555",
                                    font=("Arial", 8))
        self._count_lbl.pack(side="right", padx=8)

        # ── Treeview principal ──
        tf = ttk.Frame(self)
        tf.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tf, orient="vertical")
        vsb.pack(side="right", fill="y")

        self._tree = ttk.Treeview(
            tf, columns=_COLS, show="headings",
            yscrollcommand=vsb.set, selectmode="browse")
        self._tree.pack(fill="both", expand=True)
        vsb.config(command=self._tree.yview)

        for col, (heading, width, anchor) in _COL_CFG.items():
            self._tree.heading(col, text=heading,
                               command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=width, anchor=anchor,
                              stretch=(col == "name"))

        for att, fg in _ATTITUDE_FG.items():
            self._tree.tag_configure(att, foreground=fg)
        self._tree.tag_configure("dead_row", foreground="#444")
        self._tree.tag_configure("even",     background="#1a1a1a")
        self._tree.tag_configure("odd",      background="#141414")
        self._tree.tag_configure("named",    font=("Arial", 9, "bold"))

        # ── Painel inferior: Portrait | Detail | Loot ──
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", pady=(6, 0))

        self._build_portrait_panel(bottom)
        self._build_detail_panel(bottom)
        self._build_loot_panel(bottom)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)

    def _build_portrait_panel(self, parent: ttk.Frame) -> None:
        """Portrait do critter (WhoAmI image) — canto esquerdo inferior."""
        lf = ttk.LabelFrame(parent, text=" Portrait ", padding=4)
        lf.pack(side="left", fill="y", padx=(0, 4))

        self._portrait_canvas = tk.Canvas(
            lf,
            width=_PORTRAIT_W, height=_PORTRAIT_H,
            bg="#0d0d0d",
            highlightthickness=1, highlightbackground="#222",
        )
        self._portrait_canvas.pack()

        self._portrait_name_lbl = ttk.Label(
            lf, text="—", foreground="#666",
            font=("Arial", 7), wraplength=_PORTRAIT_W, anchor="center")
        self._portrait_name_lbl.pack(pady=(2, 0))

        self._draw_portrait_placeholder()

    def _build_detail_panel(self, parent: ttk.Frame) -> None:
        """Painel de texto com todos os campos do CritterSaveData."""
        lf = ttk.LabelFrame(parent, text=" Details ", padding=4)
        lf.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self._detail = tk.Text(
            lf, height=6, font=("Consolas", 8),
            background="#0d0d0d", foreground="#888",
            relief="flat", state="disabled", wrap="word")
        self._detail.pack(fill="both", expand=True)

        # Tags de cor para o detail text
        self._detail.tag_configure("key",   foreground="#666")
        self._detail.tag_configure("val",   foreground="#ccc")
        self._detail.tag_configure("alive", foreground="#6bcb77")
        self._detail.tag_configure("dead",  foreground="#ff6b6b")
        self._detail.tag_configure("att",   foreground="#ffd93d")

    def _build_loot_panel(self, parent: ttk.Frame) -> None:
        """Treeview de loot com ícones reais dos items."""
        lf = ttk.LabelFrame(parent, text=" Loot ", padding=4)
        lf.pack(side="left", fill="both", expand=True)

        loot_vsb = ttk.Scrollbar(lf, orient="vertical")
        loot_vsb.pack(side="right", fill="y")

        self._loot_tree = ttk.Treeview(
            lf,
            columns=("img", "name", "qty", "enchant"),
            show="headings",
            height=5,
            yscrollcommand=loot_vsb.set,
        )
        loot_vsb.config(command=self._loot_tree.yview)
        self._loot_tree.pack(fill="both", expand=True)

        for col, heading, width in (
            ("img",    "",          28),
            ("name",   "Item",     165),
            ("qty",    "Qty",       32),
            ("enchant","Enchant",  130),
        ):
            self._loot_tree.heading(col, text=heading)
            self._loot_tree.column(col, width=width,
                                   anchor="w" if col == "name" else "center",
                                   stretch=(col == "name"))

        self._loot_tree.tag_configure("ench", foreground="#d4af37")

    # ------------------------------------------------------------------
    # Lógica de filtro e população
    # ------------------------------------------------------------------

    def _update_level_filter(self) -> None:
        levels = sorted({c["level"] for c in self._all})
        self._level_cb.config(values=["All"] + [str(l) for l in levels])
        self._level_var.set("All")

    def _apply_filter(self) -> None:
        show_dead = self._show_dead_var.get()
        lvl_str   = self._level_var.get()
        level     = int(lvl_str) if lvl_str != "All" else 0
        search    = self._search_var.get().strip().lower()

        visible = filter_critters(self._all, show_dead, level)
        if search:
            visible = [c for c in visible
                       if search in c["name"].lower()
                       or search in c["type_name"].lower()]

        self._tree.delete(*self._tree.get_children())
        self._row_icons.clear()

        for i, c in enumerate(visible):
            att   = c["attitude_label"].lower()
            dead  = c["dead"]
            named = c["whoami_id"] > 0

            tags  = ["dead_row"] if dead else [att] + (["named"] if named else [])
            tags.append("even" if i % 2 == 0 else "odd")

            hp_str  = f"{c['hp']}/{c['max_hp']}" if not dead else "✕"
            loc_str = f"L{c['level']} ({c['tile_x']},{c['tile_y']})"

            self._tree.insert("", "end", iid=str(i), values=(
                c["name"],
                c["type_name"],
                c["critter_level"],
                hp_str,
                c["state"],
                c["attitude_label"],
                "✕" if dead else "",
                loc_str,
            ), tags=tags)

        n = len(visible)
        self._count_lbl.config(
            text=f"{n} critter{'s' if n!=1 else ''}"
                 + (f" of {len(self._all)}" if n != len(self._all) else ""))

    # ------------------------------------------------------------------
    # Seleção — atualiza portrait, detail e loot
    # ------------------------------------------------------------------

    def _on_select(self, _event) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        try:
            idx     = int(sel[0])
            visible = filter_critters(
                self._all,
                self._show_dead_var.get(),
                int(self._level_var.get()) if self._level_var.get() != "All" else 0,
            )
            if idx >= len(visible):
                return
            c = visible[idx]
        except (ValueError, IndexError):
            return

        self._update_portrait(c)
        self._update_detail(c)
        self._update_loot(c)

    # ------------------------------------------------------------------
    # Portrait
    # ------------------------------------------------------------------

    def _update_portrait(self, c: dict) -> None:
        self._portrait_canvas.delete("all")
        self._portrait_ref = None

        wid   = c["whoami_id"]
        photo = self._loader.get_whoami_portrait(wid, size=(_PORTRAIT_W, _PORTRAIT_H))

        if photo:
            self._portrait_ref = photo   # referência forte
            cx, cy = _PORTRAIT_W // 2, _PORTRAIT_H // 2
            self._portrait_canvas.create_image(cx, cy, image=photo, anchor="center")
        else:
            self._draw_portrait_placeholder()

        # Nome do NPC abaixo da imagem
        label = c["name"] if c["whoami_id"] > 0 else c["type_name"]
        self._portrait_name_lbl.config(text=label, foreground="#999")

    def _draw_portrait_placeholder(self) -> None:
        w, h = _PORTRAIT_W, _PORTRAIT_H
        self._portrait_canvas.create_rectangle(
            2, 2, w - 2, h - 2, outline="#1e1e1e", fill="#080808")
        self._portrait_canvas.create_text(
            w // 2, h // 2, text="?", fill="#2a2a2a",
            font=("Arial", 28, "bold"))

    # ------------------------------------------------------------------
    # Detail
    # ------------------------------------------------------------------

    def _update_detail(self, c: dict) -> None:
        talked = "Yes" if c["talked_to"] else "No"
        ally   = "Yes" if c["player_ally"] else "No"

        t = self._detail
        t.config(state="normal")
        t.delete("1.0", "end")

        def kv(key: str, val: str, val_tag: str = "val") -> None:
            t.insert("end", f"  {key:<16}", "key")
            t.insert("end", f"{val}\n", val_tag)

        kv("Name",        f"{c['name']}  (whoami={c['whoami_id']})")
        kv("Creature",    f"{c['type_name']}  (type={c['object_type']})")
        kv("HP",          f"{c['hp']} / {c['max_hp']}",
           "alive" if not c["dead"] else "dead")
        kv("Level",       str(c["critter_level"]))
        kv("Attitude",    f"{c['attitude_label']} ({c['attitude']})", "att")
        kv("Ally / Talked", f"{ally}  /  {talked}")
        kv("State",       f"{c['state']}   Goal: {c['goal']}   Target: {c['gtarg']}")
        kv("Location",    f"L{c['level']} tile ({c['tile_x']}, {c['tile_y']})")

        t.config(state="disabled")

    # ------------------------------------------------------------------
    # Loot (com ícones reais)
    # ------------------------------------------------------------------

    def _update_loot(self, c: dict) -> None:
        self._loot_tree.delete(*self._loot_tree.get_children())
        self._loot_icons.clear()

        loot = c.get("loot", [])
        if not loot:
            self._loot_tree.insert("", "end", values=("", "— empty —", "", ""))
            return

        for item in loot:
            otype = item.get("object_type", 0)
            photo = self._loader.get_item_icon(otype, size=ICON_SMALL)
            self._loot_icons.append(photo)   # referência forte

            tags = ("ench",) if item["enchantment"] else ()
            iid  = self._loot_tree.insert("", "end", values=(
                "", item["name"], item["quantity"], item["enchantment"],
            ), tags=tags)
            # Associar imagem à célula usando tag image do Treeview
            self._loot_tree.item(iid, image=photo)

    # ------------------------------------------------------------------
    # Ordenação
    # ------------------------------------------------------------------

    def _sort_by(self, col: str) -> None:
        numeric = col in ("clvl", "state")
        rows = [(self._tree.set(k, col), k) for k in self._tree.get_children("")]
        try:
            rows.sort(
                key=lambda t: int(t[0]) if numeric and t[0].lstrip("-").isdigit()
                else t[0].lower())
        except Exception:
            rows.sort(key=lambda t: t[0].lower())
        for i, (_, k) in enumerate(rows):
            self._tree.move(k, "", i)
