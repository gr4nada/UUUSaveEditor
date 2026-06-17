"""
Map Notes Panel — Add, edit and delete map annotations
"""

import tkinter as tk
from tkinter import ttk
from src.gui.constants import THEME


class MapNotesPanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text=" Map Notes ", padding=8)
        self._save_game = None
        self._tree = None
        self._note_vars = {}
        self._build()

    def _build(self):
        # Page selector
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 6))
        ttk.Label(top, text="Page:").pack(side="left", padx=(0, 6))
        self._page_var = tk.IntVar(value=0)
        self._page_spin = ttk.Spinbox(top, from_=0, to=0, textvariable=self._page_var, width=5,
                                      command=self._refresh_notes)
        self._page_spin.pack(side="left")

        # Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, pady=(0, 6))

        self._tree = ttk.Treeview(tree_frame, columns=("x", "y", "text"), show="headings", height=8)
        self._tree.heading("x", text="X")
        self._tree.heading("y", text="Y")
        self._tree.heading("text", text="Note Text")
        self._tree.column("x", width=60, anchor="center")
        self._tree.column("y", width=60, anchor="center")
        self._tree.column("text", width=400, anchor="w")
        self._tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self._tree.bind("<<TreeviewSelect>>", self._on_note_select)

        # Edit Form
        form = ttk.LabelFrame(self, text=" Edit Note ")
        form.pack(fill="x")

        row = 0
        for label, key in [("X:", "x"), ("Y:", "y")]:
            ttk.Label(form, text=label, width=8, anchor="e").grid(row=row, column=0, sticky="e", pady=4)
            var = tk.StringVar(value="0")
            self._note_vars[key] = var
            ttk.Entry(form, textvariable=var, width=10).grid(row=row, column=1, sticky="w", pady=4)
            row += 1

        ttk.Label(form, text="Text:", width=8, anchor="ne").grid(row=2, column=0, sticky="ne", pady=4)
        self._text_widget = tk.Text(form, width=50, height=4, font=("Arial", 9))
        self._text_widget.grid(row=2, column=1, pady=4)

        # Buttons
        btns = ttk.Frame(form)
        btns.grid(row=3, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Add", command=self._add_note).pack(side="left", padx=4)
        ttk.Button(btns, text="Update", command=self._update_note).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete", command=self._delete_note).pack(side="left", padx=4)

    def load(self, story, save_game):
        self._save_game = save_game
        self._refresh_notes()

    def _refresh_notes(self):
        if not self._tree or not self._save_game:
            return
        # Implementação similar à original (page handling)
        self._tree.delete(*self._tree.get_children())
        # ... (preencher com notas da página atual)

    def _on_note_select(self, event):
        # Carregar dados no form
        pass

    def _add_note(self):
        pass  # Implementar conforme lógica original

    def _update_note(self):
        pass

    def _delete_note(self):
        pass