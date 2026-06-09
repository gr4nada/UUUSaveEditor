# src/gui/tabs/quest_tab.py
import tkinter as tk
from tkinter import ttk
from src.gui.constants import QUEST_FLAGS


class QuestTab(ttk.Frame):
    """
    Aba 'Quest Flags Engine'.

    API pública:
        load_flags(quests_list)      — popula a listbox com o array do save
        get_flags() -> dict[str,bool] — retorna estado atual de todas as flags
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=10)
        self._vars: dict[str, tk.BooleanVar] = {}
        self._create_widgets()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def load_flags(self, quests_list: list) -> None:
        """Popula a listbox a partir do array questFlags do save."""
        self._quest_listbox.delete(0, tk.END)
        self._vars.clear()

        for q in QUEST_FLAGS:
            flag_id:   int = q["id"]
            flag_name: str = q["flag"]
            is_active: bool = bool(quests_list[flag_id]) if flag_id < len(quests_list) else False

            var = tk.BooleanVar(value=is_active)
            self._vars[flag_name] = var
            self._insert_row(tk.END, q["floor"], flag_name, is_active)

    def get_flags(self) -> dict[str, bool]:
        """Retorna {flag_name: bool} para serialização no save."""
        return {name: var.get() for name, var in self._vars.items()}

    # ------------------------------------------------------------------
    # Construção interna
    # ------------------------------------------------------------------

    def _create_widgets(self) -> None:
        ttk.Label(
            self, text="Stygian Abyss Progression Flags (EQuestFlag)",
            font=("Arial", 11, "bold"),
        ).pack(pady=10)

        container = ttk.LabelFrame(
            self, text=" Active Quests & Progression States ", padding=15)
        container.pack(fill="both", expand=True, padx=15, pady=5)

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        self._quest_listbox = tk.Listbox(
            container,
            font=("Consolas", 10),
            background="#1e1e1e",
            foreground="#d4d4d4",
            selectbackground="#264f78",
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        self._quest_listbox.pack(fill="both", expand=True, side="left")
        scrollbar.config(command=self._quest_listbox.yview)

        self._quest_listbox.bind("<<ListboxSelect>>", self._on_select)
        self._quest_listbox.bind("<Double-Button-1>", self._on_toggle)

    def _on_select(self, _event: tk.Event) -> None:
        selection = self._quest_listbox.curselection()
        if selection and selection[0] < len(QUEST_FLAGS):
            desc = QUEST_FLAGS[selection[0]]["desc"]
            self.winfo_toplevel().title(f"Quest Info: {desc}")

    def _on_toggle(self, _event: tk.Event) -> None:
        selection = self._quest_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index >= len(QUEST_FLAGS):
            return

        q = QUEST_FLAGS[index]
        flag_name: str = q["flag"]

        if flag_name not in self._vars:
            return

        new_val = not self._vars[flag_name].get()
        self._vars[flag_name].set(new_val)

        self._quest_listbox.delete(index)
        self._insert_row(index, q["floor"], flag_name, new_val)
        self._quest_listbox.selection_set(index)

    def _insert_row(self, index, floor: str, flag_name: str, is_active: bool) -> None:
        icon = "[X]" if is_active else "[ ]"
        self._quest_listbox.insert(index, f" {icon} Floor {floor} -> {flag_name}")
        if is_active:
            self._quest_listbox.itemconfig(index, foreground="#4ec9b0")
        else:
            self._quest_listbox.itemconfig(index, foreground="#d4d4d4")
