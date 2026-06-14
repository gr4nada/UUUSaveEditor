# src/gui/tabs/skills_quests_tab.py
"""Aba 'Skills & Quests' — skills + quest flags + global vars em sub-notebook."""
import tkinter as tk
from tkinter import ttk
from src.core.database.skills  import SKILL_NAMES as NOMES_SKILLS
from src.core.database.quests  import QUEST_FLAGS
from src.gui.constants         import THEME
from src.core.save_model       import FIELD_LIMITS


class SkillsQuestsTab(ttk.Frame):
    """
    Aba consolidada 'Skills & Quests'.

    API pública:
        load(player)
        get_skills() → dict[str, int]
        get_flags()  → dict[str, bool]
        maximize(value)
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=4)
        self._skill_vars: dict[str, tk.StringVar]   = {}
        self._skill_widgets: dict[str, tk.Widget]    = {}
        self._quest_vars: dict[str, tk.BooleanVar]   = {}
        self._gv_vars: list[tk.StringVar]            = []  # 64 slots — Sprint 11
        self._build()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def load(self, save_game) -> None:
        player = save_game.player

        # Skills
        skills = player.get_all_skills()
        for name, val in skills.items():
            self._skill_widgets[name].config(state="normal")
            self._skill_vars[name].set(str(val))

        # Quest flags
        flags_by_name = player.get_quest_flags_by_name()
        self._quest_listbox.delete(0, tk.END)
        self._quest_vars.clear()
        for q in QUEST_FLAGS:
            flag_name = q["flag"]
            is_active = flags_by_name.get(flag_name, False)
            var = tk.BooleanVar(value=is_active)
            self._quest_vars[flag_name] = var
            self._insert_quest_row(tk.END, q["floor"], flag_name, is_active)

        # Global vars — grade editável de 64 slots (Sprint 11)
        gv = player.global_vars
        for i, var in enumerate(self._gv_vars):
            var.set(str(gv[i] if i < len(gv) else 0))

    def get_skills(self) -> dict[str, int]:
        return {name: int(self._skill_vars[name].get() or 0) for name in NOMES_SKILLS}

    def get_flags(self) -> dict[str, bool]:
        return {name: var.get() for name, var in self._quest_vars.items()}

    def get_global_vars(self) -> dict[int, int]:
        """
        Retorna {índice: valor} para os 64 slots de global vars (Sprint 11).
        Entradas não-numéricas caem em 0 (mesma tolerância usada em
        story_tab). Clamp em FIELD_LIMITS["global_var"] é feito por
        PlayerModel.global_vars; aqui só convertemos para int.
        """
        result: dict[int, int] = {}
        for i, var in enumerate(self._gv_vars):
            try:
                result[i] = int(var.get())
            except (ValueError, tk.TclError):
                result[i] = 0
        return result

    def maximize(self, value: int = 30) -> None:
        for name in NOMES_SKILLS:
            self._skill_vars[name].set(str(value))

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build(self) -> None:
        sub = ttk.Notebook(self)
        sub.pack(fill="both", expand=True)

        skills_frame = ttk.Frame(sub, padding=8)
        sub.add(skills_frame, text="  Skills  ")
        self._build_skills(skills_frame)

        quests_frame = ttk.Frame(sub, padding=8)
        sub.add(quests_frame, text="  Quest Flags  ")
        self._build_quests(quests_frame)

        gv_frame = ttk.Frame(sub, padding=8)
        sub.add(gv_frame, text="  Global Vars  ")
        self._build_global_vars(gv_frame)

    def _build_skills(self, parent) -> None:
        canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner  = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        col_size = (len(NOMES_SKILLS) + 1) // 2
        for idx, name in enumerate(NOMES_SKILLS):
            col_base = (idx // col_size) * 3
            row      = idx % col_size
            var = tk.StringVar()
            self._skill_vars[name] = var
            ttk.Label(inner, text=f"{name}:", anchor="e", width=14).grid(
                row=row, column=col_base, sticky="e", pady=3, padx=(10, 6))
            entry = ttk.Entry(inner, textvariable=var, state="disabled", width=6)
            entry.grid(row=row, column=col_base + 1, sticky="w", pady=3)
            self._skill_widgets[name] = entry
            if col_base == 0:
                ttk.Separator(inner, orient="vertical").grid(
                    row=row, column=2, sticky="ns", padx=18)

    def _build_quests(self, parent) -> None:
        ttk.Label(parent,
                  text="Double-click to toggle a flag.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic")).pack(pady=(0, 6))
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(container)
        sb.pack(side="right", fill="y")
        self._quest_listbox = tk.Listbox(
            container, font=("Consolas", 10),
            background=THEME["list_bg"], foreground=THEME["tag_quest_off"],
            selectbackground=THEME["list_select"], highlightthickness=0,
            yscrollcommand=sb.set)
        self._quest_listbox.pack(fill="both", expand=True, side="left")
        sb.config(command=self._quest_listbox.yview)
        self._quest_listbox.bind("<<ListboxSelect>>", self._on_select)
        self._quest_listbox.bind("<Double-Button-1>", self._on_toggle)

    def _build_global_vars(self, parent) -> None:
        """
        Grade scrollável de 64 linhas [índice] [valor int16] editável.

        Sem nomes — os índices correspondem aos slots de conversação
        privados descritos em bglobals.dat (ver §7.2 da spec do jogo):
        cada conversa de NPC tem seu próprio conjunto de globals copiado
        para/de este array no início/fim do diálogo. O significado de
        cada índice depende dos scripts de conversa de cada NPC e não
        está mapeado — por isso a marcação "advanced/unknown".
        """
        ttk.Label(parent,
                  text="⚠ Advanced / Unknown — variáveis privadas de conversação (bglobals.dat). "
                       "Sem nomes mapeados; edite com cautela.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic"),
                  wraplength=520, justify="left").pack(anchor="w", pady=(0, 6))

        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner  = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        lo, hi = FIELD_LIMITS["global_var"]

        # 64 slots em 4 colunas de 16 linhas — [índice] [valor]
        n_cols = 4
        rows_per_col = 16
        for i in range(64):
            col = i // rows_per_col
            row = i % rows_per_col
            base_col = col * 3  # label + entry + spacer

            ttk.Label(inner, text=f"[{i:02d}]", anchor="e", width=5,
                      font=("Consolas", 9)).grid(
                row=row, column=base_col, sticky="e", padx=(10 if col == 0 else 4, 4), pady=2)

            var = tk.StringVar(value="0")
            self._gv_vars.append(var)
            ttk.Spinbox(inner, from_=lo, to=hi, textvariable=var,
                        width=8, font=("Consolas", 9)).grid(
                row=row, column=base_col + 1, sticky="w", pady=2)

            if col < n_cols - 1:
                ttk.Separator(inner, orient="vertical").grid(
                    row=row, column=base_col + 2, sticky="ns", padx=12)

    def _on_select(self, _event) -> None:
        sel = self._quest_listbox.curselection()
        if sel and sel[0] < len(QUEST_FLAGS):
            self.winfo_toplevel().title(f"Quest: {QUEST_FLAGS[sel[0]]['desc']}")

    def _on_toggle(self, _event) -> None:
        sel = self._quest_listbox.curselection()
        if not sel or sel[0] >= len(QUEST_FLAGS):
            return
        index = sel[0]
        q = QUEST_FLAGS[index]
        fname = q["flag"]
        if fname not in self._quest_vars:
            return
        new_val = not self._quest_vars[fname].get()
        self._quest_vars[fname].set(new_val)
        self._quest_listbox.delete(index)
        self._insert_quest_row(index, q["floor"], fname, new_val)
        self._quest_listbox.selection_set(index)

    def _insert_quest_row(self, index, floor, flag_name, is_active) -> None:
        icon = "[✓]" if is_active else "[ ]"
        self._quest_listbox.insert(index, f"  {icon}  {floor:<10} {flag_name}")
        fg = THEME["tag_quest_on"] if is_active else THEME["tag_quest_off"]
        self._quest_listbox.itemconfig(index, foreground=fg)
