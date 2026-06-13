# src/gui/tabs/critters_tab.py
"""
Aba 'Critters' — Explorer de NPCs e criaturas do mundo.

Layout:
  ┌─ Toolbar ─────────────────────────────────────────────────────────┐
  ├─ Treeview  Name / Creature / Lv / HP / State / Attitude / Goal / Loc ─┤
  ├─ Painel inferior ─────────────────────────────────────────────────┤
  │  Portrait   │   Details (texto rico)  │  Loot (treeview + ícones) │
  └────────────────────────────────────────────────────────────────────┘

Usa ECritterState, ECritterGoal, ECritterAttitude, EMovementType
para exibir labels semânticos em vez de inteiros brutos.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from src.core.world_parser       import filter_critters
from src.core.database.critters  import ECritterAttitude, ATTITUDE_BY_NAME, ATTITUDE_COLORS
from src.core.save_model         import GameObject
from src.gui.widgets.icon_loader import IconLoader, ICON_SMALL
from src.gui.constants           import THEME
from tkinter                     import messagebox

# ── Colunas da treeview principal ────────────────────────────────────
_COLS = ("name", "type", "clvl", "hp", "state", "attitude", "goal", "loc")
_COL_CFG = {
    "name":     ("Name",      150, "w"),
    "type":     ("Creature",  100, "w"),
    "clvl":     ("Lv",         28, "center"),
    "hp":       ("HP",         68, "center"),
    "state":    ("State",     120, "w"),
    "attitude": ("Attitude",  130, "w"),
    "goal":     ("Goal",      170, "w"),
    "loc":      ("Loc",        72, "center"),
}

_PORTRAIT_W, _PORTRAIT_H = 80, 80

# Filtros de atitude disponíveis
_ATTITUDE_FILTERS = ["All", "Hostile", "Upset", "Mellow", "Friendly"]

# int attitude value → display label (mirrors critter_attitude_label from world_parser)
from src.core.database.critters import attitude_label as _att_lbl
_ATTITUDE_LABELS: dict[int, str] = {a.value: _att_lbl(a.value) for a in ECritterAttitude}


class CrittersTab(ttk.Frame):
    """
    API pública:
        load(critters: list[dict]) → popula a tabela
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=4)
        self._all:        list[dict] = []
        self._loader      = IconLoader.get_instance()
        self._row_icons:  list       = []
        self._loot_icons: list       = []
        self._portrait_ref           = None
        self._selected: dict | None  = None
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
        self._build_toolbar()
        self._build_treeview()
        self._build_bottom_panel()

    def _build_toolbar(self) -> None:
        tb = ttk.Frame(self)
        tb.pack(fill="x", pady=(0, 4))

        # Show dead
        self._show_dead_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tb, text="Show Dead",
                        variable=self._show_dead_var,
                        command=self._apply_filter).pack(side="left", padx=(0, 10))

        # Filtro por nível
        ttk.Label(tb, text="Level:").pack(side="left", padx=(0, 3))
        self._level_var = tk.StringVar(value="All")
        self._level_cb  = ttk.Combobox(tb, textvariable=self._level_var,
                                        values=["All"], state="readonly", width=5)
        self._level_cb.pack(side="left", padx=(0, 10))
        self._level_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        # Filtro por atitude
        ttk.Label(tb, text="Attitude:").pack(side="left", padx=(0, 3))
        self._attitude_var = tk.StringVar(value="All")
        ttk.Combobox(tb, textvariable=self._attitude_var,
                     values=_ATTITUDE_FILTERS,
                     state="readonly", width=9).pack(side="left", padx=(0, 10))
        self._attitude_var.trace_add("write", lambda *_: self._apply_filter())

        # Busca
        ttk.Label(tb, text="Search:").pack(side="left", padx=(0, 3))
        self._search_var = tk.StringVar()
        ttk.Entry(tb, textvariable=self._search_var, width=15).pack(side="left")
        self._search_var.trace_add("write", lambda *_: self._apply_filter())

        self._count_lbl = ttk.Label(tb, text="", foreground=THEME["fg_faint"],
                                    font=("Arial", 8))
        self._count_lbl.pack(side="right", padx=8)

    def _build_treeview(self) -> None:
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
                              stretch=(col in ("name", "state", "attitude", "goal")))

        # Tags de cor — uma por valor de attitude
        for att_val, fg in ATTITUDE_COLORS.items():
            self._tree.tag_configure(f"att_{att_val}", foreground=fg)
        self._tree.tag_configure("dead_row", foreground=THEME["fg_dead"])
        self._tree.tag_configure("even",     background=THEME["list_row_even"])
        self._tree.tag_configure("odd",      background=THEME["list_row_odd"])
        self._tree.tag_configure("named",    font=("Arial", 9, "bold"))

        self._tree.bind("<<TreeviewSelect>>", self._on_select)

    def _build_bottom_panel(self) -> None:
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", pady=(6, 0))
        self._build_portrait_panel(bottom)
        self._build_detail_panel(bottom)
        self._build_loot_panel(bottom)
        self._build_editor_panel(bottom)

    def _build_portrait_panel(self, parent: ttk.Frame) -> None:
        lf = ttk.LabelFrame(parent, text=" Portrait ", padding=4)
        lf.pack(side="left", fill="y", padx=(0, 4))

        self._portrait_canvas = tk.Canvas(
            lf, width=_PORTRAIT_W, height=_PORTRAIT_H,
            bg=THEME["bg_deep"],
            highlightthickness=1, highlightbackground=THEME["border_deep"])
        self._portrait_canvas.pack()

        self._portrait_name_lbl = ttk.Label(
            lf, text="—", foreground=THEME["fg_faint"],
            font=("Arial", 7), wraplength=_PORTRAIT_W, anchor="center")
        self._portrait_name_lbl.pack(pady=(2, 0))
        from src.gui.widgets.tooltip import Tooltip
        Tooltip(self._portrait_name_lbl,
                lambda: self._portrait_name_lbl.cget("text"), delay=300)

        self._draw_portrait_placeholder()

    def _build_detail_panel(self, parent: ttk.Frame) -> None:
        lf = ttk.LabelFrame(parent, text=" Details ", padding=4)
        lf.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self._detail = tk.Text(
            lf, height=7, font=("Consolas", 8),
            background=THEME["bg_deep"], foreground=THEME["fg_muted"],
            relief="flat", state="disabled", wrap="word")
        self._detail.pack(fill="both", expand=True)

        self._detail.tag_configure("key",      foreground=THEME["tag_detail_key"], font=("Consolas", 8))
        self._detail.tag_configure("val",      foreground=THEME["tag_detail_val"], font=("Consolas", 8))
        self._detail.tag_configure("hostile",  foreground=THEME["attitude_hostile"])
        self._detail.tag_configure("upset",    foreground=THEME["attitude_upset"])
        self._detail.tag_configure("mellow",   foreground=THEME["attitude_mellow"])
        self._detail.tag_configure("friendly", foreground=THEME["attitude_friendly"])
        self._detail.tag_configure("alive",    foreground=THEME["attitude_friendly"])
        self._detail.tag_configure("dead",     foreground=THEME["attitude_hostile"])
        self._detail.tag_configure("move",     foreground=THEME["tag_move"])
        self._detail.tag_configure("goal",     foreground=THEME["tag_goal"])
        self._detail.tag_configure("state",    foreground=THEME["tag_state"])

    def _build_loot_panel(self, parent: ttk.Frame) -> None:
        lf = ttk.LabelFrame(parent, text=" Loot ", padding=4)
        lf.pack(side="left", fill="both", expand=True)

        loot_vsb = ttk.Scrollbar(lf, orient="vertical")
        loot_vsb.pack(side="right", fill="y")

        self._loot_tree = ttk.Treeview(
            lf, columns=("img", "name", "qty", "enchant"),
            show="headings", height=6,
            yscrollcommand=loot_vsb.set)
        loot_vsb.config(command=self._loot_tree.yview)
        self._loot_tree.pack(fill="both", expand=True)

        for col, heading, width in (
            ("img",    "",         28),
            ("name",   "Item",    160),
            ("qty",    "Qty",      32),
            ("enchant","Enchant", 130),
        ):
            self._loot_tree.heading(col, text=heading)
            self._loot_tree.column(col, width=width,
                                   anchor="w" if col == "name" else "center",
                                   stretch=(col == "name"))

        self._loot_tree.tag_configure("ench", foreground=THEME["tag_enchanted"])

    # ------------------------------------------------------------------
    # Filtro e população
    # ------------------------------------------------------------------

    def _get_visible(self) -> list[dict]:
        """
        Retorna a lista de critters que corresponde ao estado atual de todos
        os filtros: show_dead, level, attitude e search.
        Usada tanto por _apply_filter quanto por _on_select para garantir
        que o índice da treeview sempre aponta para o critter correto.
        """
        show_dead  = self._show_dead_var.get()
        lvl_str    = self._level_var.get()
        level      = int(lvl_str) if lvl_str != "All" else 0
        att_filter = self._attitude_var.get()
        search     = self._search_var.get().strip().lower()

        visible = filter_critters(self._all, show_dead, level)

        if att_filter != "All":
            att_val = ATTITUDE_BY_NAME.get(att_filter)
            if att_val is not None:
                visible = [c for c in visible if c["attitude"] == att_val]

        if search:
            visible = [c for c in visible
                       if search in c["name"].lower()
                       or search in c["type_name"].lower()
                       or search in c["state_label"].lower()
                       or search in c["goal_label"].lower()]

        return visible

    def _update_level_filter(self) -> None:
        levels = sorted({c["level"] for c in self._all})
        self._level_cb.config(values=["All"] + [str(l) for l in levels])
        self._level_var.set("All")

    def _apply_filter(self) -> None:
        visible = self._get_visible()

        self._tree.delete(*self._tree.get_children())
        self._row_icons.clear()

        for i, c in enumerate(visible):
            dead  = c["dead"]
            att   = c["attitude"]
            named = c["whoami_id"] > 0

            tags  = ["dead_row"] if dead else [f"att_{att}"] + (["named"] if named else [])
            tags.append("even" if i % 2 == 0 else "odd")

            hp_str  = f"{c['hp']}/{c['max_hp']}" if not dead else "✕"
            loc_str = f"L{c['level']} ({c['tile_x']},{c['tile_y']})"

            # Labels ricos na treeview
            state_col   = c["state_label"]
            attitude_col = c.get("attitude_label", "")
            goal_col    = c["goal_label"]

            self._tree.insert("", "end", iid=str(i), values=(
                c["name"],
                c["type_name"],
                c["critter_level"],
                hp_str,
                state_col,
                attitude_col,
                goal_col,
                loc_str,
            ), tags=tags)

        n = len(visible)
        self._count_lbl.config(
            text=f"{n} critter{'s' if n != 1 else ''}"
                 + (f" of {len(self._all)}" if n != len(self._all) else ""))

    # ------------------------------------------------------------------
    # Seleção
    # ------------------------------------------------------------------

    def _on_select(self, _event) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        try:
            idx     = int(sel[0])
            visible = self._get_visible()   # todos os filtros aplicados, igual ao render atual
            if idx >= len(visible):
                return
            c = visible[idx]
        except (ValueError, IndexError):
            return

        self._update_portrait(c)
        self._update_detail(c)
        self._update_loot(c)
        self._selected = c
        self._refresh_editor_panel()

    # ------------------------------------------------------------------
    # Portrait
    # ------------------------------------------------------------------

    def _update_portrait(self, c: dict) -> None:
        self._portrait_canvas.delete("all")
        self._portrait_ref = None

        photo = self._loader.get_whoami_portrait(
            c["whoami_id"], size=(_PORTRAIT_W, _PORTRAIT_H))

        if photo:
            self._portrait_ref = photo
            cx, cy = _PORTRAIT_W // 2, _PORTRAIT_H // 2
            self._portrait_canvas.create_image(cx, cy, image=photo, anchor="center")
        else:
            self._draw_portrait_placeholder()

        label = c["name"] if c["whoami_id"] > 0 else c["type_name"]
        self._portrait_name_lbl.config(text=label, foreground=THEME["fg_muted"])

    def _draw_portrait_placeholder(self) -> None:
        w, h = _PORTRAIT_W, _PORTRAIT_H
        self._portrait_canvas.create_rectangle(
            2, 2, w - 2, h - 2,
            outline=THEME["border_placeholder"], fill=THEME["bg_panel"])
        self._portrait_canvas.create_text(
            w // 2, h // 2, text="?", fill=THEME["fg_placeholder"],
            font=("Arial", 28, "bold"))

    # ------------------------------------------------------------------
    # Detail panel
    # ------------------------------------------------------------------

    def _update_detail(self, c: dict) -> None:
        att   = c["attitude"]
        att_rich = c.get("attitude_label", "")

        # Tag de cor para a atitude
        att_tag = {0: "hostile", 1: "upset", 2: "mellow", 3: "friendly"}.get(att, "val")

        t = self._detail
        t.config(state="normal")
        t.delete("1.0", "end")

        def kv(key: str, val: str, tag: str = "val") -> None:
            t.insert("end", f"  {key:<16}", "key")
            t.insert("end", f"{val}\n", tag)

        # Identidade
        kv("Name",       f"{c['name']}  (whoami={c['whoami_id']})")
        kv("Creature",   f"{c['type_name']}  (type={c['object_type']})")

        # Vitals
        kv("HP",
           f"{c['hp']} / {c['max_hp']}",
           "alive" if not c["dead"] else "dead")
        kv("Level",      str(c["critter_level"]))

        # ECritterAttitude — label rico com cor
        kv("Attitude",   att_rich, att_tag)

        # ECritterState — azul claro
        kv("State",
           f"{c['state_label']}  ({c['state']})",
           "state")

        # ECritterGoal — roxo
        kv("Goal",
           f"{c['goal_label']}  ({c['goal']})",
           "goal")

        # EMovementType — azul
        kv("Movement",
           f"{c['movement_label']}  ({c['movement_type']})",
           "move")

        # Flags
        talked = "Yes" if c["talked_to"] else "No"
        ally   = "Yes" if c["player_ally"] else "No"
        kv("Ally / Talked", f"{ally}  /  {talked}")
        kv("Target (gtarg)", str(c["gtarg"]))
        kv("Location",
           f"L{c['level']} tile ({c['tile_x']}, {c['tile_y']})")

        t.config(state="disabled")

    # ------------------------------------------------------------------
    # Loot
    # ------------------------------------------------------------------

    def _update_loot(self, c: dict) -> None:
        self._loot_tree.delete(*self._loot_tree.get_children())
        self._loot_icons.clear()

        loot = c.get("loot", [])
        if not loot:
            self._loot_tree.insert("", "end", values=("", "— empty —", "", ""))
            return

        for item in loot:
            photo = self._loader.get_item_icon(
                item.get("object_type", 0), size=ICON_SMALL)
            self._loot_icons.append(photo)

            tags = ("ench",) if item["enchantment"] else ()
            iid  = self._loot_tree.insert("", "end", values=(
                "", item["name"], item["quantity"], item["enchantment"],
            ), tags=tags)
            self._loot_tree.item(iid, image=photo)

    # ------------------------------------------------------------------
    # Ordenação
    # ------------------------------------------------------------------

    def _sort_by(self, col: str) -> None:
        numeric = col in ("clvl",)
        rows = [(self._tree.set(k, col), k) for k in self._tree.get_children("")]
        try:
            rows.sort(
                key=lambda t: int(t[0]) if numeric and t[0].lstrip("-").isdigit()
                else t[0].lower())
        except Exception:
            rows.sort(key=lambda t: t[0].lower())
        for i, (_, k) in enumerate(rows):
            self._tree.move(k, "", i)

    # ------------------------------------------------------------------
    # Editor panel — HP / Status / Attitude / Position
    # ------------------------------------------------------------------

    def _build_editor_panel(self, parent: ttk.Frame) -> None:
        lf = ttk.LabelFrame(parent, text=" Editor ", padding=6)
        lf.pack(side="left", fill="y", padx=(4, 0))

        r = 0

        # ── HP ──────────────────────────────────────────────────
        ttk.Label(lf, text="HP:", foreground=THEME["fg_muted"]).grid(
            row=r, column=0, sticky="e", padx=(0, 4), pady=2)
        self._hp_var = tk.StringVar()
        self._hp_entry = ttk.Entry(lf, textvariable=self._hp_var, width=7, state="disabled")
        self._hp_entry.grid(row=r, column=1, sticky="w", pady=2)
        self._hp_entry.bind("<Return>", lambda _e: self._apply_hp())
        self._apply_hp_btn = ttk.Button(lf, text="Set", command=self._apply_hp,
                                        state="disabled", width=4)
        self._apply_hp_btn.grid(row=r, column=2, padx=(2, 0), pady=2)
        r += 1

        # ── Status: Revive / Kill ───────────────────────────────
        status_row = ttk.Frame(lf)
        status_row.grid(row=r, column=0, columnspan=3, sticky="we", pady=(4, 2))
        self._revive_btn = ttk.Button(status_row, text="Revive",
                                      command=self._on_revive, state="disabled")
        self._revive_btn.pack(side="left", padx=(0, 3))
        self._kill_btn = ttk.Button(status_row, text="Kill",
                                    command=self._on_kill, state="disabled")
        self._kill_btn.pack(side="left")
        r += 1

        # ── Attitude ─────────────────────────────────────────────
        ttk.Separator(lf, orient="horizontal").grid(
            row=r, column=0, columnspan=3, sticky="we", pady=6)
        r += 1

        ttk.Label(lf, text="Attitude:", foreground=THEME["fg_muted"]).grid(
            row=r, column=0, sticky="e", padx=(0, 4), pady=2)
        self._attitude_edit_var = tk.StringVar()
        attitude_names = [a.name.capitalize() for a in ECritterAttitude]
        self._attitude_cb = ttk.Combobox(
            lf, textvariable=self._attitude_edit_var,
            values=attitude_names, state="disabled", width=10)
        self._attitude_cb.grid(row=r, column=1, columnspan=2, sticky="we", pady=2)
        r += 1

        self._apply_attitude_btn = ttk.Button(
            lf, text="Apply Attitude", command=self._apply_attitude, state="disabled")
        self._apply_attitude_btn.grid(row=r, column=0, columnspan=3,
                                      sticky="we", pady=(2, 4))
        r += 1

        # ── Position ─────────────────────────────────────────────
        ttk.Separator(lf, orient="horizontal").grid(
            row=r, column=0, columnspan=3, sticky="we", pady=6)
        r += 1

        ttk.Label(lf, text="Tile X:", foreground=THEME["fg_muted"]).grid(
            row=r, column=0, sticky="e", padx=(0, 4), pady=2)
        self._tile_x_var = tk.IntVar()
        self._tile_x_spin = ttk.Spinbox(
            lf, textvariable=self._tile_x_var,
            from_=0, to=62, width=5, state="disabled")
        self._tile_x_spin.grid(row=r, column=1, sticky="w", pady=2)
        r += 1

        ttk.Label(lf, text="Tile Y:", foreground=THEME["fg_muted"]).grid(
            row=r, column=0, sticky="e", padx=(0, 4), pady=2)
        self._tile_y_var = tk.IntVar()
        self._tile_y_spin = ttk.Spinbox(
            lf, textvariable=self._tile_y_var,
            from_=0, to=62, width=5, state="disabled")
        self._tile_y_spin.grid(row=r, column=1, sticky="w", pady=2)
        r += 1

        self._teleport_btn = ttk.Button(
            lf, text="Teleport", command=self._apply_position, state="disabled")
        self._teleport_btn.grid(row=r, column=0, columnspan=3,
                                sticky="we", pady=(2, 0))
        r += 1

        # ── Hint ─────────────────────────────────────────────────
        self._editor_hint = ttk.Label(
            lf, text="Select a critter.", foreground=THEME["fg_muted"],
            font=("Arial", 7, "italic"), wraplength=130, justify="center")
        self._editor_hint.grid(row=r, column=0, columnspan=3, pady=(8, 0))

    def _refresh_editor_panel(self) -> None:
        c = self._selected
        widgets = [
            self._hp_entry, self._apply_hp_btn,
            self._attitude_cb, self._apply_attitude_btn,
            self._tile_x_spin, self._tile_y_spin, self._teleport_btn,
        ]
        if not c:
            for w in widgets:
                w.config(state="disabled")
            self._revive_btn.config(state="disabled")
            self._kill_btn.config(state="disabled")
            self._editor_hint.config(text="Select a critter.")
            return

        for w in widgets:
            w.config(state="normal")

        # HP
        self._hp_var.set(str(c["hp"]))

        # Revive / Kill
        if c["dead"]:
            self._revive_btn.config(state="normal")
            self._kill_btn.config(state="disabled")
        else:
            self._revive_btn.config(state="disabled")
            self._kill_btn.config(state="normal")

        # Attitude
        att_name = ECritterAttitude(c["attitude"]).name.capitalize()
        self._attitude_edit_var.set(att_name)

        # Position
        self._tile_x_var.set(c["tile_x"])
        self._tile_y_var.set(c["tile_y"])

        self._editor_hint.config(text=f"{c['name']} — {c['type_name']}")

    # ── HP ──────────────────────────────────────────────────────────────

    def _apply_hp(self) -> None:
        c = self._selected
        if not c:
            return
        try:
            value = int(self._hp_var.get())
        except ValueError:
            messagebox.showerror("Invalid HP", "HP must be a whole number.")
            return
        obj = GameObject(c["_node"])
        obj.hp = value
        c["hp"]   = obj.hp
        c["dead"] = obj.is_dead
        self._sync_after_edit()

    def _on_revive(self) -> None:
        c = self._selected
        if not c:
            return
        obj = GameObject(c["_node"])
        obj.revive()
        c["hp"]   = obj.hp
        c["dead"] = obj.is_dead
        self._sync_after_edit()

    def _on_kill(self) -> None:
        c = self._selected
        if not c:
            return
        obj = GameObject(c["_node"])
        obj.kill()
        c["hp"]   = obj.hp
        c["dead"] = obj.is_dead
        self._sync_after_edit()

    # ── Attitude ────────────────────────────────────────────────────────

    def _apply_attitude(self) -> None:
        c = self._selected
        if not c:
            return
        att_name = self._attitude_edit_var.get().upper()
        try:
            att_val = ECritterAttitude[att_name].value
        except KeyError:
            messagebox.showerror("Invalid Attitude", f"Unknown attitude: {att_name!r}")
            return
        obj = GameObject(c["_node"])
        obj.parsed_data["attitude"] = att_val
        obj.commit()
        c["attitude"]       = att_val
        c["attitude_label"] = _ATTITUDE_LABELS[att_val]
        self._sync_after_edit()

    # ── Position ────────────────────────────────────────────────────────

    def _apply_position(self) -> None:
        c = self._selected
        if not c:
            return
        try:
            tx = int(self._tile_x_var.get())
            ty = int(self._tile_y_var.get())
        except (ValueError, tk.TclError):
            messagebox.showerror("Invalid Position", "Tile coordinates must be integers.")
            return
        tx = max(0, min(tx, 62))
        ty = max(0, min(ty, 62))

        obj = GameObject(c["_node"])
        d = obj.parsed_data
        d["initialTileX"] = tx
        d["initialTileY"] = ty
        d["xhome"]        = tx
        d["yhome"]        = ty
        obj.commit()

        c["tile_x"] = tx
        c["tile_y"] = ty
        self._sync_after_edit()

    # ── Shared ──────────────────────────────────────────────────────────

    def _sync_after_edit(self) -> None:
        """Re-renderiza a lista respeitando os filtros activos e re-seleciona o critter editado."""
        self._apply_filter()
        self._reselect_current()
        self._refresh_editor_panel()
        if self._selected:
            self._update_detail(self._selected)

    def _reselect_current(self) -> None:
        c = self._selected
        if not c:
            return
        visible = self._get_visible()
        try:
            idx = visible.index(c)
        except ValueError:
            return
        iid = str(idx)
        if self._tree.exists(iid):
            self._tree.selection_set(iid)
            self._tree.see(iid)
