# src/gui/tabs/skills_quests_tab.py
"""Aba 'Skills & Quests' — skills + quest flags + global vars em sub-notebook."""
import tkinter as tk
from tkinter import ttk
from src.core.database.skills  import SKILL_NAMES as NOMES_SKILLS
from src.core.database.quests  import QUEST_FLAGS
from src.core.database.quest_states import (
    quest_state_options, describe_state, is_multi_state,
)
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
        self._quest_states: dict[str, int]          = {}  # Sprint 13 — Quest Intelligence
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

        # Quest flags (Sprint 13 — Quest Intelligence)
        states_by_name = player.get_quest_states_by_name()
        self._quest_states = dict(states_by_name)
        self._refresh_quest_tree()

        # Global vars — grade editável de 64 slots (Sprint 11)
        gv = player.global_vars
        for i, var in enumerate(self._gv_vars):
            var.set(str(gv[i] if i < len(gv) else 0))

    def get_skills(self) -> dict[str, int]:
        return {name: int(self._skill_vars[name].get() or 0) for name in NOMES_SKILLS}

    def get_flags(self) -> dict[str, int]:
        """
        Retorna {flag_name: int} com o estado narrativo atual de cada quest
        flag (Sprint 13). PlayerModel.quest_flags aceita int diretamente.
        """
        return dict(self._quest_states)

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
        """
        Sprint 13 — Quest Intelligence.

        Treeview com colunas Flag | Estado Atual | Descrição do Estado.
        Cada flag pode ter 2 estados (binário: Inativo/Ativo) ou N estados
        narrativos documentados em database/quest_states.py. Duplo-clique
        ou o botão "Change State" abrem um diálogo com as opções válidas
        para aquela flag específica.
        """
        ttk.Label(parent,
                  text="Duplo-clique ou 'Change State' para editar o estado narrativo de uma flag.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic")).pack(anchor="w", pady=(0, 6))

        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True)

        cols = ("floor", "flag", "state", "desc")
        self._quest_tree = ttk.Treeview(
            container, columns=cols, show="headings", height=14)
        self._quest_tree.heading("floor", text="Floor")
        self._quest_tree.heading("flag",  text="Flag")
        self._quest_tree.heading("state", text="Estado Atual")
        self._quest_tree.heading("desc",  text="Descrição do Estado")
        self._quest_tree.column("floor", width=70,  anchor="w")
        self._quest_tree.column("flag",  width=180, anchor="w")
        self._quest_tree.column("state", width=160, anchor="w")
        self._quest_tree.column("desc",  width=420, anchor="w")

        sb = ttk.Scrollbar(container, orient="vertical", command=self._quest_tree.yview)
        self._quest_tree.configure(yscrollcommand=sb.set)
        self._quest_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._quest_tree.tag_configure("inactive", foreground=THEME["tag_quest_off"])
        self._quest_tree.tag_configure("active",   foreground=THEME["tag_quest_on"])
        self._quest_tree.tag_configure("unknown",  foreground=THEME["fg_dim"])

        self._quest_tree.bind("<Double-1>", self._on_quest_double_click)

        btn_row = ttk.Frame(parent)
        btn_row.pack(fill="x", pady=(6, 0))
        ttk.Button(btn_row, text="Change State…",
                   command=self._on_change_state_clicked).pack(side="left")
        ttk.Label(btn_row,
                  text="  Flags com 2 estados alternam direto; flags com 3+ estados abrem um seletor.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic")).pack(side="left")

    # ------------------------------------------------------------------
    # Quest Flags — lógica (Sprint 13)
    # ------------------------------------------------------------------

    def _refresh_quest_tree(self) -> None:
        """Repopula o Treeview a partir de self._quest_states."""
        for row in self._quest_tree.get_children():
            self._quest_tree.delete(row)

        for q in QUEST_FLAGS:
            flag_name = q["flag"]
            value = self._quest_states.get(flag_name, 0)
            self._insert_quest_row(flag_name, q["floor"], value)

    def _insert_quest_row(self, flag_name: str, floor: str, value: int) -> None:
        info = describe_state(flag_name, value)
        tag = "unknown" if info["label"].startswith("Desconhecido") else (
            "active" if value > 0 else "inactive")
        self._quest_tree.insert(
            "", "end", iid=flag_name,
            values=(floor, flag_name, info["label"], info["desc"]),
            tags=(tag,))

    def _on_quest_double_click(self, _event) -> None:
        sel = self._quest_tree.selection()
        if sel:
            self._open_state_dialog(sel[0])

    def _on_change_state_clicked(self) -> None:
        sel = self._quest_tree.selection()
        if not sel:
            return
        self._open_state_dialog(sel[0])

    def _open_state_dialog(self, flag_name: str) -> None:
        """
        Abre o seletor de estado para `flag_name`.

        Flags binárias (2 estados): alterna direto entre 0/1, sem diálogo —
        igual ao antigo "double-click to toggle", mas agora atualiza a
        coluna de descrição também.

        Flags com 3+ estados documentados (is_multi_state): abre um
        Toplevel com um Radiobutton por estado, mostrando label + descrição
        completa de cada opção, para que o usuário escolha com contexto
        narrativo — não apenas um número.
        """
        current = self._quest_states.get(flag_name, 0)
        q = next((q for q in QUEST_FLAGS if q["flag"] == flag_name), None)
        if q is None:
            return

        if not is_multi_state(flag_name):
            # Binário: alterna 0 <-> 1 imediatamente.
            new_value = 0 if current > 0 else 1
            self._quest_states[flag_name] = new_value
            self._insert_at_same_position(flag_name, q["floor"], new_value)
            return

        # Multi-estado: diálogo com Radiobuttons
        options = quest_state_options(flag_name)
        win = tk.Toplevel(self)
        win.title(f"Quest State — {flag_name}")
        win.resizable(False, False)
        win.transient(self.winfo_toplevel())
        win.grab_set()

        ttk.Label(win, text=flag_name, font=("Arial", 10, "bold")).pack(
            anchor="w", padx=12, pady=(12, 2))
        ttk.Label(win, text=q["desc"], foreground=THEME["fg_dim"],
                  font=("Arial", 8, "italic"), wraplength=420,
                  justify="left").pack(anchor="w", padx=12, pady=(0, 10))

        selected = tk.IntVar(value=current)
        for value in sorted(options.keys()):
            info = options[value]
            frame = ttk.Frame(win)
            frame.pack(fill="x", padx=12, pady=2, anchor="w")
            ttk.Radiobutton(frame, text=f"{value} — {info['label']}",
                            variable=selected, value=value,
                            width=28).pack(side="left", anchor="n")
            ttk.Label(frame, text=info["desc"], foreground=THEME["fg_secondary"],
                      font=("Arial", 8), wraplength=320,
                      justify="left").pack(side="left", padx=(8, 0))

        def _apply() -> None:
            new_value = selected.get()
            self._quest_states[flag_name] = new_value
            self._insert_at_same_position(flag_name, q["floor"], new_value)
            win.destroy()

        btn_row = ttk.Frame(win)
        btn_row.pack(fill="x", padx=12, pady=(8, 12))
        ttk.Button(btn_row, text="Apply", command=_apply, width=10).pack(side="right")
        ttk.Button(btn_row, text="Cancel", command=win.destroy, width=10).pack(
            side="right", padx=(0, 6))

    def _insert_at_same_position(self, flag_name: str, floor: str, value: int) -> None:
        """
        Atualiza a linha de `flag_name` no Treeview preservando a seleção
        e a posição (delete + insert no índice original, igual ao padrão
        já usado pelo antigo Listbox).
        """
        index = self._quest_tree.index(flag_name)
        self._quest_tree.delete(flag_name)
        info = describe_state(flag_name, value)
        tag = "unknown" if info["label"].startswith("Desconhecido") else (
            "active" if value > 0 else "inactive")
        self._quest_tree.insert(
            "", index, iid=flag_name,
            values=(floor, flag_name, info["label"], info["desc"]),
            tags=(tag,))
        self._quest_tree.selection_set(flag_name)
        self._quest_tree.see(flag_name)

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
