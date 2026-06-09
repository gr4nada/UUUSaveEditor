# src/gui/tabs/quests_tab.py
"""Quests Tab — Handles game story progression and quest state flag configurations."""
import tkinter as tk
from tkinter import ttk
from src.gui.constants import QUEST_FLAGS


class QuestsTab(ttk.Frame):
    """
    'Quests' Tab Component.

    Public API:
        load(player)              → Populates the layout listbox with quest flag states.
        get_flags() → dict[str, bool] → Returns current mapped boolean flags for saving.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=15)
        self._vars: dict[str, tk.BooleanVar] = {}
        self._build()

    def load(self, player) -> None:
        quests_list = player.quest_flags
        self._listbox.delete(0, tk.END)
        self._vars.clear()

        for q in QUEST_FLAGS:
            flag_id:   int  = q["id"]
            flag_name: str  = q["flag"]
            is_active: bool = bool(quests_list[flag_id]) if flag_id < len(quests_list) else False

            var = tk.BooleanVar(value=is_active)
            self._vars[flag_name] = var
            self._insert_row(tk.END, q["floor"], flag_name, is_active)

    def get_flags(self) -> dict[str, bool]:
        return {name: var.get() for name, var in self._vars.items()}

    def _build(self) -> None:
        ttk.Label(self, text="Stygian Abyss — Quest Progression Flags",
                  font=("Arial", 11, "bold")).pack(pady=(5, 12))

        info = ttk.Label(
            self,
            text="Double-click a flag to toggle its state.  Active flags are highlighted in teal.",
            foreground="#888", font=("Arial", 8, "italic"))
        info.pack(pady=(0, 8))

        container = ttk.LabelFrame(self, text=" EQuestFlag States ", padding=12)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        sb = ttk.Scrollbar(container)
        sb.pack(side="right", fill="y")

        self._listbox = tk.Listbox(
            container,
            font=("Consolas", 10),
            background="#1e1e1e", foreground="#d4d4d4",
            selectbackground="#264f78", highlightthickness=0,
            yscrollcommand=sb.set)
        self._listbox.pack(fill="both", expand=True, side="left")
        sb.config(command=self._listbox.yview)

        self._listbox.bind("<<ListboxSelect>>", self._on_select)
        self._listbox.bind("<Double-Button-1>", self._on_toggle)

    def _on_select(self, _event) -> None:
        sel = self._listbox.curselection()
        if sel and sel[0] < len(QUEST_FLAGS):
            desc = QUEST_FLAGS[sel[0]]["desc"]
            self.winfo_toplevel().title(f"Quest: {desc}")

    def _on_toggle(self, _event) -> None:
        sel = self._listbox.curselection()
        if not sel:
            return
        index = sel[0]
        if index >= len(QUEST_FLAGS):
            return
        q = QUEST_FLAGS[index]
        flag_name = q["flag"]
        if flag_name not in self._vars:
            return
        new_val = not self._vars[flag_name].get()
        self._vars[flag_name].set(new_val)
        self._listbox.delete(index)
        self._insert_row(index, q["floor"], flag_name, new_val)
        self._listbox.selection_set(index)

    def _insert_row(self, index, floor: str, flag_name: str, is_active: bool) -> None:
        icon = "[✓]" if is_active else "[ ]"
        self._listbox.insert(index, f"  {icon}  {floor:<10} {flag_name}")
        if is_active:
            self._listbox.itemconfig(index, foreground="#4ec9b0",
                                     selectforeground="#4ec9b0")
        else:
            self._listbox.itemconfig(index, foreground="#888888",
                                     selectforeground="#d4d4d4")