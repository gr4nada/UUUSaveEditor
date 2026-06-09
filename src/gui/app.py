# src/gui/app.py
"""
EditorApp — Main application orchestrator.

Implements the complete layout navigation tree:
  Player | Attributes | Status | Progression | Skills |
  Magic  | Quests     | Statistics | Inventory | World Objects
"""
import logging
import tkinter as tk
from tkinter import ttk, messagebox

from src.core.save_manager    import load_save, save_game_data
from src.core.character       import update_character, cheat_max_all_skills
from src.core.inventory       import get_equipment_summary
from src.core.save_model      import SaveGame
from src.gui.constants        import QUEST_FLAGS
from src.gui.dialogs          import open_equipment_tuning_dialog
from src.gui.widgets          import SaveHeaderFrame

from src.gui.tabs.player_tab        import PlayerTab
from src.gui.tabs.attributes_tab    import AttributesTab
from src.gui.tabs.status_tab        import StatusTab
from src.gui.tabs.progression_tab   import ProgressionTab
from src.gui.tabs.skills_tab        import SkillsTab
from src.gui.tabs.magic_tab         import MagicTab
from src.gui.tabs.quests_tab        import QuestsTab
from src.gui.tabs.statistics_tab    import StatisticsTab
from src.gui.tabs.inventory_tab     import InventoryTab
from src.gui.tabs.world_objects_tab import WorldObjectsTab

logger = logging.getLogger("gui.app")

_WINDOW_TITLE = "Ultima Underworld Unity - Save Editor"


class EditorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(_WINDOW_TITLE)
        self.root.geometry("980x860")
        self.root.resizable(False, False)

        self._save_game:    SaveGame | None = None
        self._raw_save:     dict | None     = None
        self._selected_slot: int            = 0

        self._setup_styles()
        self._build_ui()

    # ------------------------------------------------------------------
    # User Interface Construction
    # ------------------------------------------------------------------

    def _setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        # Notebook tab padding
        style.configure("TNotebook.Tab", padding=[10, 4])

    def _build_ui(self) -> None:
        # SaveHeaderFrame component layout
        # self.save_header = SaveHeaderFrame(self.root)
        # self.save_header.pack(fill="x", padx=15, pady=(10, 0))

        # Slot selector + Load data trigger controls
        slot_frame = ttk.LabelFrame(self.root, text=" Save Slot ", padding=8)
        slot_frame.pack(fill="x", padx=15, pady=(6, 4))

        ttk.Label(slot_frame, text="Select Slot:").pack(side="left", padx=5)
        self._slot_combo = ttk.Combobox(
            slot_frame,
            values=[f"Slot {i}" for i in range(10)],
            state="readonly", width=10)
        self._slot_combo.current(0)
        self._slot_combo.pack(side="left", padx=5)

        self._load_btn = ttk.Button(slot_frame, text="Load Save",
                                    command=self._on_load)
        self._load_btn.pack(side="left", padx=10)

        self._char_lbl = ttk.Label(slot_frame, text="No save loaded",
                                   font=("Arial", 10, "bold"))
        self._char_lbl.pack(side="right", padx=15)

        # Primary application main notebook
        self._nb = ttk.Notebook(self.root)
        self._nb.pack(fill="both", expand=True, padx=15, pady=4)

        self._tab_player      = PlayerTab(self._nb)
        self._tab_attrs       = AttributesTab(self._nb)
        self._tab_status      = StatusTab(self._nb)
        self._tab_progression = ProgressionTab(self._nb)
        self._tab_skills      = SkillsTab(self._nb)
        self._tab_magic       = MagicTab(self._nb)
        self._tab_quests      = QuestsTab(self._nb)
        self._tab_statistics  = StatisticsTab(self._nb)
        self._tab_inventory   = InventoryTab(self._nb)
        self._tab_world       = WorldObjectsTab(self._nb)

        self._nb.add(self._tab_player,      text="  Player  ")
        self._nb.add(self._tab_attrs,       text="  Attributes  ")
        self._nb.add(self._tab_status,      text="  Status  ")
        self._nb.add(self._tab_progression, text="  Progression  ")
        self._nb.add(self._tab_skills,      text="  Skills  ")
        self._nb.add(self._tab_magic,       text="  Magic  ")
        self._nb.add(self._tab_quests,      text="  Quests  ")
        self._nb.add(self._tab_statistics,  text="  Statistics  ")
        self._nb.add(self._tab_inventory,   text="  Inventory  ")
        self._nb.add(self._tab_world,       text="  World Objects  ")

        # Injects click listener callback function into the equipment inventory slot grid
        self._tab_inventory.set_on_slot_clicked(self._on_equipment_slot_clicked)

        # Bottom view control toolbar footer
        footer = ttk.Frame(self.root, padding=8)
        footer.pack(fill="x", side="bottom")

        self._cheat_btn = ttk.Button(
            footer, text="⚡ Max All Skills (30)",
            command=self._on_cheat, state="disabled")
        self._cheat_btn.pack(side="left", padx=15)

        self._save_btn = ttk.Button(
            footer, text="💾  Save Changes",
            command=self._on_save, state="disabled")
        self._save_btn.pack(side="right", padx=15, ipady=3)

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------

    def _on_load(self) -> None:
        self._selected_slot = self._slot_combo.current()
        try:
            self._raw_save  = load_save(self._selected_slot)
            self._save_game = SaveGame(self._raw_save)
            player = self._save_game.player

            # Propagate raw updates across all visual tab panes
            self._tab_player.load(player)
            self._tab_attrs.load(player)
            self._tab_status.load(player)
            self._tab_progression.load(player)
            self._tab_skills.load(player)
            self._tab_magic.load(player)
            self._tab_quests.load(player)
            self._tab_statistics.load(player)
            self._tab_inventory.refresh(self._raw_save)
            self._tab_world.load(self._save_game)

            # Update header node context and active character status string
            # self.save_header.update_from_save(self._raw_save, self._selected_slot)
            self._char_lbl.config(
                text=f"Avatar: {player.name}  ·  {player.player_class_name}  ·  Lv {player.level}")
            self._save_btn.config(state="normal")
            self._cheat_btn.config(state="normal")

            messagebox.showinfo(
                "Loaded",
                f"Slot {self._selected_slot} loaded — {player.name} ({player.player_class_name})")
        except Exception as exc:
            logger.exception("Failed to load save slot %d", self._selected_slot)
            messagebox.showerror("Load Error", str(exc))

    def _on_save(self) -> None:
        if not self._raw_save:
            return
        try:
            # Query and harvest state dict arrays from each input form tab module
            attrs: dict = {}
            attrs.update(self._tab_player.get_values())
            attrs.update(self._tab_attrs.get_values())
            attrs.update(self._tab_status.get_values())
            attrs.update(self._tab_progression.get_values())
            skills = self._tab_skills.get_values()

            # Quest flags → Sync state flags back to raw save schema array structures
            quests_list: list = self._raw_save["playerData"].get("questFlags", [])
            max_id = max(q["id"] for q in QUEST_FLAGS)
            while len(quests_list) <= max_id:
                quests_list.append(False)
            for q in QUEST_FLAGS:
                quests_list[q["id"]] = self._tab_quests.get_flags()[q["flag"]]
            self._raw_save["playerData"]["questFlags"] = quests_list

            update_character(self._raw_save, attrs, skills)
            save_game_data(self._selected_slot, self._raw_save)

            name = attrs.get("playerName", "Avatar")
            cls  = attrs.get("playerClass", "")
            self._char_lbl.config(text=f"Avatar: {name}  ·  {cls}")
            messagebox.showinfo("Saved", "All changes written to save file.")
        except ValueError:
            messagebox.showerror("Input Error",
                                 "Invalid value in a numeric field — check your inputs.")
        except Exception as exc:
            logger.exception("Failed to write to save slot %d", self._selected_slot)
            messagebox.showerror("Save Error", str(exc))

    def _on_cheat(self) -> None:
        if not self._raw_save:
            return
        cheat_max_all_skills(self._raw_save, value=30)
        self._tab_skills.maximize(30)
        messagebox.showinfo("Cheat Applied", "All skills set to 30.")

    def _on_equipment_slot_clicked(self, slot_index: int) -> None:
        if not self._raw_save:
            messagebox.showwarning("No Save", "Load a save file first.")
            return
        equip_summary = get_equipment_summary(self._raw_save)
        slot_name = equip_summary[slot_index]["slot_name"]
        open_equipment_tuning_dialog(
            self.root,
            self._raw_save,
            slot_index,
            slot_name,
            lambda: self._tab_inventory.refresh(self._raw_save),
        )