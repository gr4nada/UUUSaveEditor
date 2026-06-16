"""
Story Tab — Narrative state, plot flags, map notes and game progression.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from .common.base_tab import BaseTab
from src.gui.constants import THEME


class StoryTab(BaseTab):
    """
    Story tab — manages narrative state, plot flags, player position overrides,
    and map notes.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        # Initialize all variables BEFORE calling super()
        self._easy_var = tk.BooleanVar(value=False)
        self._pos_x_var = tk.StringVar(value="0.0")
        self._pos_y_var = tk.StringVar(value="0.0")
        self._pos_z_var = tk.StringVar(value="0.0")
        self._level_var = tk.StringVar(value="0")

        # Plot Flags
        self._cup_found_var = tk.BooleanVar(value=False)
        self._cup_dream_index_var = tk.StringVar(value="0")
        self._sapling_planted_var = tk.BooleanVar(value=False)
        self._sapling_level_var = tk.StringVar(value="0")
        self._sapling_pos_x_var = tk.StringVar(value="0.0")
        self._sapling_pos_y_var = tk.StringVar(value="0.0")
        self._sapling_pos_z_var = tk.StringVar(value="0.0")
        self._moonstone_dropped_var = tk.BooleanVar(value=False)
        self._moonstone_level_var = tk.StringVar(value="0")
        self._moonstone_pos_x_var = tk.StringVar(value="0.0")
        self._moonstone_pos_y_var = tk.StringVar(value="0.0")
        self._moonstone_pos_z_var = tk.StringVar(value="0.0")
        self._garamon_var = tk.BooleanVar(value=False)
        self._green_moongate_var = tk.BooleanVar(value=False)
        self._said_fanlo_var = tk.BooleanVar(value=False)
        self._talismans_coll_var = tk.StringVar(value="0")
        self._talismans_dest_var = tk.StringVar(value="0")

        # Map Notes
        self._save_game = None
        self._note_page_var = tk.IntVar(value=0)
        self._note_x_var = tk.StringVar(value="0")
        self._note_y_var = tk.StringVar(value="0")
        self._note_text_var = tk.StringVar(value="")

        self._notes_tree = None
        self._note_text_entry = None
        self._note_page_spin = None

        super().__init__(parent, title="Story")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, save_game) -> None:
        """Load story data from save_game."""
        super().load(save_game)
        self._save_game = save_game
        p = save_game.player

        # Game State
        self._easy_var.set(p.easy)
        pos = p.position
        self._pos_x_var.set(f"{pos['x']:.3f}")
        self._pos_y_var.set(f"{pos['y']:.3f}")
        self._pos_z_var.set(f"{pos['z']:.3f}")
        self._level_var.set(str(save_game.current_level))

        # Plot Flags
        self._cup_found_var.set(p.cup_found)
        self._cup_dream_index_var.set(str(p.cup_dream_index))
        self._sapling_planted_var.set(p.sapling_planted)
        self._sapling_level_var.set(str(p.sapling_planted_level))

        sapling_pos = p.sapling_planted_position
        self._sapling_pos_x_var.set(f"{sapling_pos['x']:.3f}")
        self._sapling_pos_y_var.set(f"{sapling_pos['y']:.3f}")
        self._sapling_pos_z_var.set(f"{sapling_pos['z']:.3f}")

        self._moonstone_dropped_var.set(p.moonstone_dropped)
        self._moonstone_level_var.set(str(p.moonstone_dropped_level))
        moonstone_pos = p.moonstone_dropped_position
        self._moonstone_pos_x_var.set(f"{moonstone_pos['x']:.3f}")
        self._moonstone_pos_y_var.set(f"{moonstone_pos['y']:.3f}")
        self._moonstone_pos_z_var.set(f"{moonstone_pos['z']:.3f}")

        self._garamon_var.set(p.garamon_at_rest)
        self._green_moongate_var.set(p.entered_green_moongate)
        self._said_fanlo_var.set(p.said_fanlo)
        self._talismans_coll_var.set(str(p.talismans_collected))
        self._talismans_dest_var.set(str(p.talismans_destroyed))

        # Map Notes
        self._refresh_notes_list()

        self.clear_changes()

    def get_story_data(self) -> dict:
        """Return story data to be merged into SavePayload.story."""
        return {
            "easy": self._easy_var.get(),
            "position": {
                "x": self._safe_float(self._pos_x_var.get()),
                "y": self._safe_float(self._pos_y_var.get()),
                "z": self._safe_float(self._pos_z_var.get()),
            },
            "current_level": self._safe_int(self._level_var.get()),

            "cup_found": self._cup_found_var.get(),
            "cup_dream_index": self._safe_int(self._cup_dream_index_var.get()),
            "sapling_planted": self._sapling_planted_var.get(),
            "sapling_planted_level": self._safe_int(self._sapling_level_var.get()),
            "sapling_planted_position": {
                "x": self._safe_float(self._sapling_pos_x_var.get()),
                "y": self._safe_float(self._sapling_pos_y_var.get()),
                "z": self._safe_float(self._sapling_pos_z_var.get()),
            },
            "moonstone_dropped": self._moonstone_dropped_var.get(),
            "moonstone_dropped_level": self._safe_int(self._moonstone_level_var.get()),
            "moonstone_dropped_position": {
                "x": self._safe_float(self._moonstone_pos_x_var.get()),
                "y": self._safe_float(self._moonstone_pos_y_var.get()),
                "z": self._safe_float(self._moonstone_pos_z_var.get()),
            },
            "garamon_at_rest": self._garamon_var.get(),
            "entered_green_moongate": self._green_moongate_var.get(),
            "said_fanlo": self._said_fanlo_var.get(),
            "talismans_collected": self._safe_int(self._talismans_coll_var.get()),
            "talismans_destroyed": self._safe_int(self._talismans_dest_var.get()),
        }

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build tab with sub-notebook."""
        sub = ttk.Notebook(self)
        sub.pack(fill="both", expand=True)

        game_state_frame = ttk.Frame(sub, padding=10)
        plot_frame = ttk.Frame(sub, padding=10)
        notes_frame = ttk.Frame(sub, padding=10)

        sub.add(game_state_frame, text="  Game State  ")
        sub.add(plot_frame, text="  Plot Flags  ")
        sub.add(notes_frame, text="  Map Notes  ")

        self._build_game_state(game_state_frame)
        self._build_plot_flags(plot_frame)
        self._build_map_notes(notes_frame)

    def _build_game_state(self, parent) -> None:
        lf = ttk.LabelFrame(parent, text=" Difficulty ", padding=10)
        lf.pack(fill="x", pady=(0, 10))
        ttk.Checkbutton(lf, text="Easy mode", variable=self._easy_var).pack(anchor="w")

        lf2 = ttk.LabelFrame(parent, text=" Player Position (Teleport) ", padding=10)
        lf2.pack(fill="x", pady=(0, 10))

        ttk.Label(lf2,
                  text="Coordenadas do mundo. Valores fora de [-2000, 2000] são clampados ao salvar.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic")).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))

        for col, (label, var) in enumerate([
            ("X:", self._pos_x_var), ("Y:", self._pos_y_var), ("Z:", self._pos_z_var)
        ]):
            ttk.Label(lf2, text=label, width=3, anchor="e").grid(
                row=1, column=col*2, sticky="e", padx=(0, 4), pady=3)
            ttk.Entry(lf2, textvariable=var, width=12).grid(
                row=1, column=col*2+1, sticky="w", padx=(0, 12), pady=3)

        lf3 = ttk.LabelFrame(parent, text=" Dungeon Level ", padding=10)
        lf3.pack(fill="x", pady=(0, 10))
        ttk.Label(lf3, text="Current Level (0-9):", anchor="e", width=20).grid(
            row=0, column=0, sticky="e", padx=(0, 8), pady=3)
        ttk.Spinbox(lf3, from_=0, to=9, textvariable=self._level_var, width=6).grid(
            row=0, column=1, sticky="w", pady=3)
        ttk.Label(lf3, text="Teleporta o jogador para outro nível do dungeon ao salvar.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic")).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

    def _build_plot_flags(self, parent) -> None:
        lf = ttk.LabelFrame(parent, text=" Main Plot ", padding=10)
        lf.pack(fill="x", pady=(0, 10))

        ttk.Checkbutton(lf, text="Cup Found", variable=self._cup_found_var).grid(
            row=0, column=0, sticky="w", pady=3)
        ttk.Label(lf, text="Cup Dream Index (0-5):", anchor="e").grid(
            row=0, column=1, sticky="e", padx=(20, 8))
        ttk.Spinbox(lf, from_=0, to=5, textvariable=self._cup_dream_index_var, width=6).grid(
            row=0, column=2, sticky="w")

        ttk.Checkbutton(lf, text="Garamon at Rest", variable=self._garamon_var).grid(
            row=1, column=0, sticky="w", pady=3)
        ttk.Checkbutton(lf, text="Entered Green Moongate", variable=self._green_moongate_var).grid(
            row=2, column=0, sticky="w", pady=3)
        ttk.Checkbutton(lf, text="Said Fanlo", variable=self._said_fanlo_var).grid(
            row=3, column=0, sticky="w", pady=3)

        lf2 = ttk.LabelFrame(parent, text=" World Events ", padding=10)
        lf2.pack(fill="x", pady=(0, 10))

        ttk.Checkbutton(lf2, text="Sapling Planted", variable=self._sapling_planted_var).grid(
            row=0, column=0, sticky="w", pady=3)
        ttk.Label(lf2, text="Level:", anchor="e").grid(row=0, column=1, sticky="e", padx=(20, 8))
        ttk.Spinbox(lf2, from_=0, to=9, textvariable=self._sapling_level_var, width=6).grid(
            row=0, column=2, sticky="w")

        for col, (label, var) in enumerate([
            ("X:", self._sapling_pos_x_var),
            ("Y:", self._sapling_pos_y_var),
            ("Z:", self._sapling_pos_z_var)
        ]):
            ttk.Label(lf2, text=label, anchor="e", width=3).grid(
                row=0, column=3 + col*2, sticky="e", padx=(12 if col == 0 else 0, 4))
            ttk.Entry(lf2, textvariable=var, width=10).grid(
                row=0, column=4 + col*2, sticky="w", padx=(0, 4))

        ttk.Checkbutton(lf2, text="Moonstone Dropped", variable=self._moonstone_dropped_var).grid(
            row=1, column=0, sticky="w", pady=3)
        ttk.Label(lf2, text="Level:", anchor="e").grid(row=1, column=1, sticky="e", padx=(20, 8))
        ttk.Spinbox(lf2, from_=0, to=9, textvariable=self._moonstone_level_var, width=6).grid(
            row=1, column=2, sticky="w")

        for col, (label, var) in enumerate([
            ("X:", self._moonstone_pos_x_var),
            ("Y:", self._moonstone_pos_y_var),
            ("Z:", self._moonstone_pos_z_var)
        ]):
            ttk.Label(lf2, text=label, anchor="e", width=3).grid(
                row=1, column=3 + col*2, sticky="e", padx=(12 if col == 0 else 0, 4))
            ttk.Entry(lf2, textvariable=var, width=10).grid(
                row=1, column=4 + col*2, sticky="w", padx=(0, 4))

        lf3 = ttk.LabelFrame(parent, text=" Talismans ", padding=10)
        lf3.pack(fill="x", pady=(0, 10))
        ttk.Label(lf3, text="Collected (0-64):", anchor="e", width=16).grid(
            row=0, column=0, sticky="e", padx=(0, 8), pady=3)
        ttk.Spinbox(lf3, from_=0, to=64, textvariable=self._talismans_coll_var, width=6).grid(
            row=0, column=1, sticky="w", pady=3)
        ttk.Label(lf3, text="Destroyed (0-64):", anchor="e", width=16).grid(
            row=1, column=0, sticky="e", padx=(0, 8), pady=3)
        ttk.Spinbox(lf3, from_=0, to=64, textvariable=self._talismans_dest_var, width=6).grid(
            row=1, column=1, sticky="w", pady=3)

    def _build_map_notes(self, parent) -> None:
        top = ttk.Frame(parent)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Page:", anchor="e").pack(side="left", padx=(0, 6))
        self._note_page_spin = ttk.Spinbox(
            top, from_=0, to=0, textvariable=self._note_page_var, width=4,
            command=self._refresh_notes_list)
        self._note_page_spin.pack(side="left")

        ttk.Label(top,
                  text="Anotações de texto sobre o mapa revelado.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic")).pack(
            side="left", padx=(12, 0))

        body = ttk.Frame(parent)
        body.pack(fill="both", expand=True)

        # Lista de notas
        list_frame = ttk.Frame(body)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._notes_tree = ttk.Treeview(
            list_frame, columns=("x", "y", "text"), show="headings", height=12)
        self._notes_tree.heading("x", text="X")
        self._notes_tree.heading("y", text="Y")
        self._notes_tree.heading("text", text="Text")
        self._notes_tree.column("x", width=50, anchor="center")
        self._notes_tree.column("y", width=50, anchor="center")
        self._notes_tree.column("text", width=300, anchor="w")
        self._notes_tree.pack(fill="both", expand=True)
        self._notes_tree.bind("<<TreeviewSelect>>", self._on_note_select)

        # Formulário de edição
        form = ttk.LabelFrame(body, text=" Note ", padding=10)
        form.pack(side="left", fill="y")

        ttk.Label(form, text="X:", anchor="e", width=6).grid(row=0, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self._note_x_var, width=10).grid(row=0, column=1, sticky="w", pady=3)

        ttk.Label(form, text="Y:", anchor="e", width=6).grid(row=1, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self._note_y_var, width=10).grid(row=1, column=1, sticky="w", pady=3)

        ttk.Label(form, text="Text:", anchor="ne", width=6).grid(row=2, column=0, sticky="ne", pady=3)
        self._note_text_entry = tk.Text(form, width=30, height=6, font=("Arial", 9))
        self._note_text_entry.grid(row=2, column=1, sticky="w", pady=3)

        btn_row = ttk.Frame(form)
        btn_row.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Button(btn_row, text="Add", command=self._on_note_add, width=8).pack(side="left", padx=(0, 4))
        ttk.Button(btn_row, text="Update", command=self._on_note_update, width=8).pack(side="left", padx=(0, 4))
        ttk.Button(btn_row, text="Delete", command=self._on_note_delete, width=8).pack(side="left")

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_int(text: str) -> int:
        try:
            return int(float(text))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _safe_float(text: str) -> float:
        try:
            return float(text)
        except (ValueError, TypeError):
            return 0.0

    # ------------------------------------------------------------------
    # Map Notes Logic
    # ------------------------------------------------------------------

    def _refresh_notes_list(self) -> None:
        if not self._save_game or not self._notes_tree:
            return

        page_count = max(0, self._save_game.map_page_count - 1)
        if self._note_page_spin:
            self._note_page_spin.config(to=page_count)

        for row in self._notes_tree.get_children():
            self._notes_tree.delete(row)

        notes = self._save_game.get_map_notes(self._current_page())
        for i, note in enumerate(notes):
            self._notes_tree.insert(
                "", "end", iid=str(i),
                values=(note.get("x", ""), note.get("y", ""), note.get("text", "")))

        self._clear_note_form()

    def _current_page(self) -> int:
        try:
            return int(self._note_page_var.get())
        except (tk.TclError, ValueError):
            return 0

    def _clear_note_form(self) -> None:
        self._note_x_var.set("0")
        self._note_y_var.set("0")
        if self._note_text_entry:
            self._note_text_entry.delete("1.0", "end")

    def _on_note_select(self, _event=None) -> None:
        sel = self._notes_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        notes = self._save_game.get_map_notes(self._current_page())
        if not (0 <= idx < len(notes)):
            return
        note = notes[idx]
        self._note_x_var.set(str(note.get("x", 0)))
        self._note_y_var.set(str(note.get("y", 0)))
        if self._note_text_entry:
            self._note_text_entry.delete("1.0", "end")
            self._note_text_entry.insert("1.0", str(note.get("text", "")))

    def _on_note_add(self) -> None:
        if not self._save_game:
            return
        note = self._note_from_form()
        if self._save_game.add_map_note(self._current_page(), note):
            self._refresh_notes_list()

    def _on_note_update(self) -> None:
        if not self._save_game or not self._notes_tree:
            return
        sel = self._notes_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        notes = self._save_game.get_map_notes(self._current_page())
        if not (0 <= idx < len(notes)):
            return
        note = self._note_from_form(existing=notes[idx])
        if self._save_game.update_map_note(self._current_page(), idx, note):
            self._refresh_notes_list()

    def _on_note_delete(self) -> None:
        if not self._save_game or not self._notes_tree:
            return
        sel = self._notes_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if self._save_game.delete_map_note(self._current_page(), idx):
            self._refresh_notes_list()

    def _note_from_form(self, existing: dict | None = None) -> dict:
        note = dict(existing) if existing else {}
        note["x"] = self._safe_int(self._note_x_var.get())
        note["y"] = self._safe_int(self._note_y_var.get())
        if self._note_text_entry:
            note["text"] = self._note_text_entry.get("1.0", "end").rstrip("\n")
        return note