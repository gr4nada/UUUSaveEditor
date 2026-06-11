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
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox

from src.core.save_manager import load_save, save_game_data
from src.core.character    import update_character, cheat_max_all_skills
from src.core.inventory    import get_equipment_summary
from src.core.save_model   import SaveGame
from src.gui.constants     import QUEST_FLAGS
from src.gui.dialogs       import open_equipment_tuning_dialog
from src.gui.widgets       import SaveHeaderFrame, CharacterPreviewWidget

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

        self._raw_save:      dict | None     = None
        self._save_game:     SaveGame | None = None
        self._selected_slot: int             = 0

        self._setup_styles()
        self._build_ui()

    # ------------------------------------------------------------------
    # Estilos
    # ------------------------------------------------------------------

    def _setup_styles(self) -> None:
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TNotebook.Tab",     padding=[12, 5], font=("Arial", 9))
        s.configure("TLabelframe",       background="#252525")
        s.configure("TLabelframe.Label", foreground="#777", font=("Arial", 8, "bold"))
        s.configure("TFrame",            background="#252525")

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

        # --- Footer ---
        footer = ttk.Frame(self.root, padding=(12, 6))
        footer.pack(fill="x", side="bottom")

        self._cheat_btn = ttk.Button(
            footer, text="⚡  Max All Skills (30)",
            command=self._on_cheat, state="disabled")
        self._cheat_btn.pack(side="left")

        self._save_btn = ttk.Button(
            footer, text="💾  Save Changes",
            command=self._on_save, state="disabled")
        self._save_btn.pack(side="right")

    def _placeholder_tab(self, text: str) -> ttk.Frame:
        f = ttk.Frame(self._nb, padding=30)
        ttk.Label(f, text=text, foreground="#555",
                  font=("Arial", 10, "italic")).pack(pady=60)
        return f

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _equipped_for_preview(self) -> dict:
        """Retorna {slot_index: {objectType, qualityClass}} do save atual."""
        if not self._raw_save:
            return {}
        result = {}
        items = self._raw_save.get("inventoryData", {}).get("equippedItems", [])
        for idx, item in enumerate(items):
            jd = {}
            if item.get("jsonData"):
                try:
                    jd = json.loads(item["jsonData"])
                except Exception:
                    pass
            result[idx] = {
                "objectType":   item.get("objectType", 0),
                "qualityClass": jd.get("qualityClass", 0),
            }
        return result

    def _refresh_preview(self) -> None:
        if not self._save_game:
            return
        self._preview.update(
            portrait_id    = self._save_game.player.portrait,
            equipped_slots = self._equipped_for_preview(),
        )

    def _inject_dungeon_level(self, player, raw_save: dict) -> None:
        """
        Injeta o dungeon level actual no playerData temporariamente
        para que character_tab.load() o possa exibir sem alterar o model.
        """
        player._p["__dungeon_level__"] = raw_save.get("currentLevel", "—")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_load(self) -> None:
        self._selected_slot = self._slot_combo.current()
        try:
            self._raw_save  = load_save(self._selected_slot)
            self._save_game = SaveGame(self._raw_save)
            player = self._save_game.player

            self._inject_dungeon_level(player, self._raw_save)

            self._tab_character.load(player)
            self._tab_skills.load(player)
            self._tab_magic.load(player)
            self._tab_inventory.refresh(self._raw_save)
            self._tab_world.load(self._save_game)

            from src.core.world_parser import parse_world
            _critters, _items = parse_world(self._raw_save)
            self._tab_critters.load(_critters)

            self._header.update_from_save(self._raw_save, self._selected_slot)
            self._refresh_preview()

            self._save_btn.config(state="normal")
            self._cheat_btn.config(state="normal")
        except Exception as exc:
            logger.exception("Load failed slot=%d", self._selected_slot)
            messagebox.showerror("Load Error", str(exc))

    def _on_save(self) -> None:
        if not self._raw_save:
            return
        try:
            attrs  = self._tab_character.get_values()
            skills = self._tab_skills.get_skills()

            qlist: list = self._raw_save["playerData"].get("questFlags", [])
            max_id = max(q["id"] for q in QUEST_FLAGS)
            while len(qlist) <= max_id:
                qlist.append(False)
            for q in QUEST_FLAGS:
                qlist[q["id"]] = self._tab_skills.get_flags()[q["flag"]]
            self._raw_save["playerData"]["questFlags"] = qlist

            update_character(self._raw_save, attrs, skills)
            save_game_data(self._selected_slot, self._raw_save)

            self._save_game = SaveGame(self._raw_save)
            self._inject_dungeon_level(self._save_game.player, self._raw_save)
            self._refresh_preview()
            self._header.update_from_save(self._raw_save, self._selected_slot)

            messagebox.showinfo("Saved", "Changes written to save file.")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid value — check numeric fields.")
        except Exception as exc:
            logger.exception("Save failed slot=%d", self._selected_slot)
            messagebox.showerror("Save Error", str(exc))

    def _on_cheat(self) -> None:
        if not self._raw_save:
            return
        cheat_max_all_skills(self._raw_save, value=30)
        self._tab_skills.maximize(30)
        messagebox.showinfo("Cheat", "All skills set to 30.")

    def _on_equipment_slot_clicked(self, slot_index: int) -> None:
        if not self._raw_save:
            messagebox.showwarning("No Save", "Load a save first.")
            return
        equip = get_equipment_summary(self._raw_save)
        open_equipment_tuning_dialog(
            self.root,
            self._raw_save,
            slot_index,
            equip[slot_index]["slot_name"],
            lambda: (
                self._tab_inventory.refresh(self._raw_save),
                self._refresh_preview(),
            ),
        )

    def _on_portrait_change(self, portrait_id: int) -> None:
        """Portrait muda no CharacterTab → preview atualiza imediatamente."""
        if self._raw_save:
            self._preview.update(
                portrait_id    = portrait_id,
                equipped_slots = self._equipped_for_preview(),
            )
