# src/gui/app.py
"""
EditorApp — layout redesenhado.

┌──────────────── save header (slot + load + save info) ────────────────┐
├──────────────────────────────────────┬────────────────────────────────┤
│  Notebook  (6 abas)                  │  CharacterPreviewWidget        │
│    Character                         │  (largura fixa 230px)          │
│    Skills & Quests                   │  Portrait  120×120             │
│    Magic                             │  Paper Doll 180×300            │
│    Inventory                         │                                │
│    World Objects                     │                                │
│    Critters                          │                                │
├──────────────────────────────────────┴────────────────────────────────┤
│  [⚡ Max Skills]                                        [💾 Save]     │
└───────────────────────────────────────────────────────────────────────┘
"""
import logging
import tkinter as tk
from tkinter import ttk, messagebox

from src.core.save_controller import SaveController, SavePayload
from src.gui.constants     import THEME
from src.gui.dialogs       import open_equipment_tuning_dialog
from src.gui.widgets       import SaveHeaderFrame, CharacterPreviewWidget,\
                                   Tooltip, attach_tooltip

from src.gui.tabs.character_tab     import CharacterTab
from src.gui.tabs.skills_quests_tab import SkillsQuestsTab
from src.gui.tabs.magic_tab         import MagicTab
from src.gui.tabs.inventory_tab     import InventoryTab
from src.gui.tabs.world_objects_tab import WorldObjectsTab
from src.gui.tabs.critters_tab      import CrittersTab

logger = logging.getLogger("gui.app")
_TITLE = "Ultima Underworld Unity - Save Editor"

# Largura do painel do paper doll
_PREVIEW_W = 230


class EditorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(_TITLE)
        self.root.geometry("1100x780")
        self.root.resizable(False, False)

        self._controller = SaveController()
        self._dirty: bool = False

        self._setup_styles()
        self._build_ui()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Estilos
    # ------------------------------------------------------------------

    def _setup_styles(self) -> None:
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TNotebook.Tab",     padding=[12, 5], font=("Arial", 9))
        s.configure("TLabelframe",       background=THEME["bg_app"])
        s.configure("TLabelframe.Label", foreground=THEME["fg_labelframe"], font=("Arial", 8, "bold"))
        s.configure("TFrame",            background=THEME["bg_app"])

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # --- Save header (slot + load + metadados do save) ---
        self._header = SaveHeaderFrame(self.root)
        self._header.pack(fill="x", padx=12, pady=(8, 6))
        self._header.set_load_command(self._on_load)
        self._slot_combo = self._header.slot_combo

        # --- Corpo: notebook (esquerda) + preview (direita) ---
        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True, padx=12, pady=0)

        # Preview (direita, largura fixa)
        sidebar = ttk.Frame(body, width=_PREVIEW_W)
        sidebar.pack(side="right", fill="y", padx=(10, 0))
        sidebar.pack_propagate(False)

        self._preview = CharacterPreviewWidget(sidebar)
        self._preview.pack(fill="both", expand=True)

        # Notebook (esquerda, expande)
        self._nb = ttk.Notebook(body)
        self._nb.pack(side="left", fill="both", expand=True)

        self._tab_character = CharacterTab(self._nb)
        self._tab_skills    = SkillsQuestsTab(self._nb)
        self._tab_magic     = MagicTab(self._nb)
        self._tab_inventory = InventoryTab(self._nb)
        self._tab_world     = WorldObjectsTab(self._nb)
        self._tab_critters  = CrittersTab(self._nb)

        self._nb.add(self._tab_character, text="  Character  ")
        self._nb.add(self._tab_skills,    text="  Skills & Quests  ")
        self._nb.add(self._tab_magic,     text="  Magic  ")
        self._nb.add(self._tab_inventory, text="  Inventory  ")
        self._nb.add(self._tab_world,     text="  World Objects  ")
        self._nb.add(self._tab_critters,  text="  Critters  ")

        self._tab_inventory.set_on_slot_clicked(self._on_equipment_slot_clicked)

        # Preview ao vivo: portrait muda → preview atualiza
        self._tab_character.on_portrait_change(self._on_portrait_change)

        # Atalhos de teclado
        self.root.bind_all("<Control-s>", lambda _: self._on_save())
        self.root.bind_all("<Control-S>", lambda _: self._on_save())

        # --- Footer ---
        footer = ttk.Frame(self.root, padding=(12, 6))
        footer.pack(fill="x", side="bottom")

        self._cheat_btn = ttk.Button(
            footer, text="⚡  Max All Skills (30)",
            command=self._on_cheat, state="disabled")
        self._cheat_btn.pack(side="left")
        Tooltip(self._cheat_btn, "Set all 20 skills to 30 (maximum)")

        self._reload_btn = ttk.Button(
            footer, text="↺  Reload from Disk",
            command=self._on_reload, state="disabled")
        self._reload_btn.pack(side="left", padx=(8, 0))
        Tooltip(self._reload_btn, "Discard all unsaved changes and reload from disk")

        self._save_btn = ttk.Button(
            footer, text="💾  Save Changes",
            command=self._on_save, state="disabled")
        self._save_btn.pack(side="right")
        Tooltip(self._save_btn, "Save all changes to the save file  (Ctrl+S)")

    def _placeholder_tab(self, text: str) -> ttk.Frame:
        f = ttk.Frame(self._nb, padding=30)
        ttk.Label(f, text=text, foreground=THEME["fg_dead"],
                  font=("Arial", 10, "italic")).pack(pady=60)
        return f

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refresh_preview(self, portrait_id: int | None = None) -> None:
        if not self._controller.save_game:
            return
        self._preview.update(**self._controller.preview_data(portrait_id))

    def _mark_dirty(self, _event=None) -> None:
        if not self._dirty:
            self._dirty = True
            self._update_title()

    def _update_title(self) -> None:
        """Reflete dirty state no título da janela com prefixo ✱."""
        if self._dirty:
            self.root.title(f"✱ {_TITLE}")
        else:
            self.root.title(_TITLE)

    def _clear_dirty(self) -> None:
        self._dirty = False
        self._update_title()

    def _on_close(self) -> None:
        if self._dirty:
            if not messagebox.askyesno(
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to close without saving?",
                icon="warning"):
                return
        self.root.destroy()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_load(self) -> None:
        self._load_slot(self._slot_combo.current())

    def _on_reload(self) -> None:
        if not self._controller.is_loaded:
            return
        if self._dirty:
            if not messagebox.askyesno(
                "Discard Changes",
                "Reload from disk and discard all unsaved changes?",
                icon="warning"):
                return
        self._load_slot(self._controller.selected_slot)

    def _load_slot(self, slot: int) -> None:
        try:
            save_game = self._controller.load(slot)

            self._tab_character.load(save_game)
            self._tab_skills.load(save_game)
            self._tab_magic.load(save_game)
            self._tab_inventory.refresh(save_game)
            self._tab_world.load(save_game)

            critters, _items = save_game.parse_world()
            self._tab_critters.load(critters)

            self._header.update_from_save(save_game, self._controller.selected_slot)
            self._refresh_preview()

            self._save_btn.config(state="normal")
            self._cheat_btn.config(state="normal")
            self._reload_btn.config(state="normal")

            self._clear_dirty()
            self.root.bind_all("<Key>", self._mark_dirty, add="+")
            self.root.bind_all("<Button-1>", self._mark_dirty, add="+")
        except Exception as exc:
            logger.exception("Load failed slot=%d", slot)
            messagebox.showerror("Load Error", str(exc))

    def _on_save(self) -> None:
        if not self._controller.is_loaded:
            return
        try:
            payload = SavePayload(
                attrs       = self._tab_character.get_values(),
                skills      = self._tab_skills.get_skills(),
                flags       = self._tab_skills.get_flags(),
                cast_spells = self._tab_magic.get_spells(),
            )
            save_game = self._controller.save(payload)

            self._refresh_preview()
            self._header.update_from_save(save_game, self._controller.selected_slot)
            self._clear_dirty()

            messagebox.showinfo("Saved", "Changes written to save file.")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid value — check numeric fields.")
        except Exception as exc:
            logger.exception("Save failed slot=%d", self._controller.selected_slot)
            messagebox.showerror("Save Error", str(exc))

    def _on_cheat(self) -> None:
        if not self._controller.is_loaded:
            return
        self._controller.cheat_max_skills(value=30)
        self._tab_skills.maximize(30)
        messagebox.showinfo("Cheat", "All skills set to 30.")

    def _on_equipment_slot_clicked(self, slot_index: int) -> None:
        if not self._controller.is_loaded:
            messagebox.showwarning("No Save", "Load a save first.")
            return
        equip = self._controller.equipment_summary()
        open_equipment_tuning_dialog(
            self.root,
            self._controller.raw_save,
            slot_index,
            equip[slot_index]["slot_name"],
            lambda: (
                self._tab_inventory.refresh(self._controller.save_game),
                self._refresh_preview(),
            ),
        )

    def _on_portrait_change(self, portrait_id: int) -> None:
        """Portrait muda no CharacterTab → preview atualiza imediatamente."""
        if not self._controller.is_loaded:
            return
        self._refresh_preview(portrait_id)
