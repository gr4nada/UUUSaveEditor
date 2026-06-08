# src/gui/app.py
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import logging

from src.core.save_manager import load_save, save_game_data
from src.core.enums import NOMES_SKILLS
from src.core.character import get_character_summary, update_character, cheat_max_all_skills
from src.core.inventory import get_equipment_summary

# Modularized Local Imports
from src.gui.constants import UNDERWORLD_CLASSES, QUEST_FLAGS
from src.gui.dialogs import open_equipment_tuning_dialog

logger = logging.getLogger("gui.app")

class EditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultima Underworld Unity - Save Editor")
        self.root.geometry("950x800")
        self.root.resizable(False, False)
        
        self.raw_save_data = None
        self.selected_slot = 0
        
        self.attr_vars = {}
        self.skill_vars = {}
        self.quest_vars = {}
        self.equipment_slots_ui = []
        self.loaded_icons_cache = []
        
        self.setup_styles()
        self.create_widgets()

    def load_slot_icon(self, object_type: int):
        """Loads and processes individual slot icons, handling aspect ratio and filters."""
        icon_path = os.path.join("assets", "icons", f"{object_type}.png")
        display_size = (44, 44)
        
        if object_type != 0 and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).convert("RGBA")
                datas = img.getdata()
                new_data = []
                for item in datas:
                    if item[0] >= 245 and item[1] >= 245 and item[2] >= 245:
                        new_data.append((0, 0, 0, 0))
                    else:
                        new_data.append(item)
                img.putdata(new_data)
                
                img.thumbnail(display_size, Image.Resampling.NEAREST)
                canvas = Image.new("RGBA", display_size, (0, 0, 0, 0))
                
                x_offset = (display_size[0] - img.width) // 2
                y_offset = (display_size[1] - img.height) // 2
                canvas.paste(img, (x_offset, y_offset), img)
                return ImageTk.PhotoImage(canvas)
            except Exception as e:
                logger.error("Error processing icon ID %d: %s", object_type, e)
                img = Image.new("RGBA", display_size, (34, 34, 34, 255))
        else:
            img = Image.new("RGBA", display_size, (34, 34, 34, 255))
            
        return ImageTk.PhotoImage(img)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def create_widgets(self):
        """Builds all tabs and major interface containers."""
        # --- Top Header ---
        top_frame = ttk.LabelFrame(self.root, text=" Save Slot ", padding=10)
        top_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Label(top_frame, text="Select Slot:").pack(side="left", padx=5)
        self.slot_combo = ttk.Combobox(top_frame, values=[f"Slot {i}" for i in range(10)], state="readonly", width=10)
        self.slot_combo.current(0)
        self.slot_combo.pack(side="left", padx=5)
        
        self.load_btn = ttk.Button(top_frame, text="Load Data", command=self.on_load_clicked)
        self.load_btn.pack(side="left", padx=10)
        
        self.char_lbl = ttk.Label(top_frame, text="No character loaded", font=("Arial", 10, "bold"))
        self.char_lbl.pack(side="right", padx=15)

        # --- Tab System ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=5)
        
        # TAB 1: Player Stats
        self.char_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.char_tab, text="Player Data")
        
        self.left_frame = ttk.LabelFrame(self.char_tab, text=" Identity & Attributes ", padding=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.right_frame = ttk.LabelFrame(self.char_tab, text=" Skills Matrix ", padding=10)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        self.draw_attribute_fields()
        self.draw_skill_fields()

        # TAB 2: Equipment
        self.equip_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.equip_tab, text="Equipped Items")
        self.draw_equipment_grid()

        # TAB 3: Quests
        self.quest_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.quest_tab, text="Quest Flags Engine")
        self.draw_quest_tab()

        # --- Footer ---
        footer_frame = ttk.Frame(self.root, padding=10)
        footer_frame.pack(fill="x", side="bottom")
        
        self.skills_cheat_btn = ttk.Button(footer_frame, text="Maximize All Skills (30)", command=self.on_cheat_skills_clicked, state="disabled")
        self.skills_cheat_btn.pack(side="left", padx=15)
        
        self.save_btn = ttk.Button(footer_frame, text="Save Changes", command=self.on_save_clicked, state="disabled")
        self.save_btn.pack(side="right", padx=15, ipady=3)

    def draw_attribute_fields(self):
        canvas = tk.Canvas(self.left_frame, borderwidth=0, highlightthickness=0)
        scroll = ttk.Scrollbar(self.left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        ttk.Label(scrollable_frame, text="Character Identity", font=("Arial", 9, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        ttk.Label(scrollable_frame, text="Player Name:").grid(row=1, column=0, sticky="w", pady=3)
        self.var_name = tk.StringVar()
        self.ent_name = ttk.Entry(scrollable_frame, textvariable=self.var_name, state="disabled", width=16)
        self.ent_name.grid(row=1, column=1, sticky="w", pady=3)

        ttk.Label(scrollable_frame, text="Player Class:").grid(row=2, column=0, sticky="w", pady=3)
        self.combo_class = ttk.Combobox(scrollable_frame, values=UNDERWORLD_CLASSES, state="disabled", width=14)
        self.combo_class.grid(row=2, column=1, sticky="w", pady=3)

        ttk.Label(scrollable_frame, text="Gender:").grid(row=3, column=0, sticky="w", pady=3)
        self.combo_gender = ttk.Combobox(scrollable_frame, values=["Male", "Female"], state="disabled", width=14)
        self.combo_gender.grid(row=3, column=1, sticky="w", pady=3)

        ttk.Label(scrollable_frame, text="Dominant Hand:").grid(row=4, column=0, sticky="w", pady=3)
        self.combo_hand = ttk.Combobox(scrollable_frame, values=["Right-Handed", "Left-Handed"], state="disabled", width=14)
        self.combo_hand.grid(row=4, column=1, sticky="w", pady=3)

        ttk.Label(scrollable_frame, text="Portrait ID (0-31):").grid(row=5, column=0, sticky="w", pady=3)
        self.var_portrait = tk.StringVar()
        self.ent_portrait = ttk.Entry(scrollable_frame, textvariable=self.var_portrait, state="disabled", width=6)
        self.ent_portrait.grid(row=5, column=1, sticky="w", pady=3)

        ttk.Separator(scrollable_frame, orient="horizontal").grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(scrollable_frame, text="Attributes & Vitals", font=("Arial", 9, "bold")).grid(row=7, column=0, columnspan=2, sticky="w", pady=5)

        fields = [
            ("charLevel", "Level:"), ("exp", "Experience (EXP):"),
            ("strength", "Strength (STR):"), ("intellect", "Intellect (INT):"), ("dexterity", "Dexterity (DEX):"),
            ("hp", "Health Points (HP):"), ("vitality", "Max Vitality:"),
            ("mana", "Current Mana:"), ("maxMana", "Max Mana:"),
            ("skillPoints", "Unspent Skill Points:")
        ]
        
        current_row = 8
        for key, label_text in fields:
            ttk.Label(scrollable_frame, text=label_text).grid(row=current_row, column=0, sticky="w", pady=3)
            var = tk.StringVar()
            entry = ttk.Entry(scrollable_frame, textvariable=var, state="disabled", width=12)
            entry.grid(row=current_row, column=1, sticky="w", pady=3)
            self.attr_vars[key] = (var, entry)
            current_row += 1

        ttk.Separator(scrollable_frame, orient="horizontal").grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10)
        current_row += 1

        ttk.Label(scrollable_frame, text="Survival States", font=("Arial", 9, "bold")).grid(row=current_row, column=0, columnspan=2, sticky="w", pady=5)
        current_row += 1

        survival_fields = [
            ("poison", "Poison Level:"), ("hunger", "Hunger Level:"),
            ("fatigue", "Fatigue Level:"), ("drunkenness", "Drunkenness Level:")
        ]

        for key, label_text in survival_fields:
            ttk.Label(scrollable_frame, text=label_text).grid(row=current_row, column=0, sticky="w", pady=3)
            var = tk.StringVar()
            entry = ttk.Entry(scrollable_frame, textvariable=var, state="disabled", width=12)
            entry.grid(row=current_row, column=1, sticky="w", pady=3)
            self.attr_vars[key] = (var, entry)
            current_row += 1

    def draw_skill_fields(self):
        canvas = tk.Canvas(self.right_frame, borderwidth=0, highlightthickness=0)
        scroll = ttk.Scrollbar(self.right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        for idx, skill_name in enumerate(NOMES_SKILLS):
            ttk.Label(scrollable_frame, text=f"{skill_name}:").grid(row=idx, column=0, sticky="w", pady=2, padx=5)
            var = tk.StringVar()
            entry = ttk.Entry(scrollable_frame, textvariable=var, state="disabled", width=6)
            entry.grid(row=idx, column=1, sticky="w", pady=2, padx=5)
            self.skill_vars[skill_name] = (var, entry)

    def draw_equipment_grid(self):
        self.inventory_canvas = tk.Canvas(self.equip_tab, width=550, height=400, bg="#2b2b2b", highlightthickness=1, highlightbackground="#444")
        self.inventory_canvas.pack(pady=20)
        
        self.inventory_canvas.create_rectangle(210, 50, 340, 350, fill="#1f1f1f", outline="#555")
        self.inventory_canvas.create_text(275, 200, text="AVATAR", fill="#444", font=("Arial", 16, "bold"))

        self.slot_positions = [
            (80,  60), (243, 60), (400, 60), (80,  160), (243, 150),
            (400, 160), (80,  260), (145, 110), (243, 240), (335, 110), (243, 320)
        ]
        slot_names = ["Light Source", "Head", "Neck", "Right Hand", "Chest", "Left Hand", "Gloves", "Ring 1", "Legs", "Ring 2", "Boots"]

        for idx, (x, y) in enumerate(self.slot_positions):
            lbl_bg = tk.Label(self.inventory_canvas, bg="#111", width=9, height=4, bd=2, relief="groove")
            self.inventory_canvas.create_window(x + 32, y + 32, window=lbl_bg)
            
            lbl_img = tk.Label(self.inventory_canvas, bg="#222", text="Empty", fg="#666")
            self.inventory_canvas.create_window(x + 32, y + 32, window=lbl_img)
            
            self.inventory_canvas.create_text(x + 32, y - 10, text=slot_names[idx], fill="#bbb", font=("Arial", 8, "bold"))
            lbl_img.bind("<Button-1>", lambda e, slot=idx: self.on_equipment_slot_clicked(slot))
            self.equipment_slots_ui.append(lbl_img)

    def draw_quest_tab(self):
        lbl_info = ttk.Label(self.quest_tab, text="Stygian Abyss Progression Flags (EQuestFlag)", font=("Arial", 11, "bold"))
        lbl_info.pack(pady=10)

        container_frame = ttk.LabelFrame(self.quest_tab, text=" Active State Mutators ", padding=15)
        container_frame.pack(fill="both", expand=True, padx=10, pady=5)

        for idx, q in enumerate(QUEST_FLAGS):
            flag_name = q["flag"]
            var = tk.BooleanVar(value=False)
            self.quest_vars[flag_name] = var
            
            display_text = f"[{q['floor']}] {flag_name}"
            chk = ttk.Checkbutton(container_frame, text=display_text, variable=var, state="disabled")
            
            row = idx % 8
            col = idx // 8
            chk.grid(row=row, column=col, sticky="w", padx=20, pady=8)
            
            chk.bind("<Enter>", lambda e, d=q["desc"]: self.root.title(f"Quest Info: {d}"))
            chk.bind("<Leave>", lambda e: self.root.title("Ultima Underworld Unity - Save Editor"))

    def on_load_clicked(self):
        self.selected_slot = self.slot_combo.current()
        try:
            self.raw_save_data = load_save(self.selected_slot)
            summary = get_character_summary(self.raw_save_data)
            attrs = summary["attributes"]
            
            self.ent_name.config(state="normal")
            self.var_name.set(str(attrs.get("playerName", "Avatar")))
            
            self.combo_class.config(state="readonly")
            self.combo_class.set(attrs.get("playerClass", "Fighter") if attrs.get("playerClass") in UNDERWORLD_CLASSES else "Fighter")
                
            self.combo_gender.config(state="readonly")
            self.combo_gender.set("Female" if attrs.get("female", False) else "Male")
            
            self.combo_hand.config(state="readonly")
            self.combo_hand.set("Left-Handed" if attrs.get("leftHanded", False) else "Right-Handed")
            
            self.ent_portrait.config(state="normal")
            self.var_portrait.set(str(attrs.get("portrait", 0)))
            
            for key, (var, entry) in self.attr_vars.items():
                entry.config(state="normal")
                var.set(str(attrs.get(key, 0)))
                
            for skill_name, (var, entry) in self.skill_vars.items():
                entry.config(state="normal")
                var.set(str(summary["skills"].get(skill_name, 0)))

            quests_state = self.raw_save_data.get("quest_flags", {})
            for q in QUEST_FLAGS:
                self.quest_vars[q["flag"]].set(quests_state.get(q["flag"], False))
                
            for child in self.quest_tab.winfo_children():
                for chk in child.winfo_children():
                    if isinstance(chk, ttk.Checkbutton): chk.config(state="normal")
                
            self.refresh_equipment_ui()
            self.save_btn.config(state="normal")
            self.skills_cheat_btn.config(state="normal")
            self.char_lbl.config(text=f"Avatar: {self.var_name.get()} ({self.combo_class.get()})")
            messagebox.showinfo("Success", f"Slot {self.selected_slot} compiled into workspace successfully!")
        except Exception as e:
            messagebox.showerror("Fatal Error", f"Failed to process save data: {e}")

    def refresh_equipment_ui(self):
        data_to_parse = self.raw_save_data if self.raw_save_data is not None else {}
        equip_summary = get_equipment_summary(data_to_parse)
        self.loaded_icons_cache.clear()
        
        for item in equip_summary:
            idx = item["slot_index"]
            label_widget = self.equipment_slots_ui[idx]
            obj_type = item["objectType"]
            
            if item["is_empty"] or obj_type == 0:
                label_widget.config(image="", text="Empty", bg="#222")
                label_widget.image = None
            else:
                photo_icon = self.load_slot_icon(obj_type)
                self.loaded_icons_cache.append(photo_icon)
                label_widget.config(image=photo_icon, text="", bg="#1a1a1a")
                label_widget.image = photo_icon
                
                spell_str = f" | Magic: {item['enchantment']}" if item.get("enchantment") else ""
                label_widget.bind("<Enter>", lambda e, n=item["objectName"], s=spell_str: self.root.title(f"Item: {n}{s}"))
                label_widget.bind("<Leave>", lambda e: self.root.title("Ultima Underworld Unity - Save Editor"))

    def on_equipment_slot_clicked(self, slot_index):
        if self.raw_save_data is None:
            messagebox.showwarning("No Save Loaded", "Please load a valid character save file first!")
            return

        equip_summary = get_equipment_summary(self.raw_save_data)
        slot_name = equip_summary[slot_index]["slot_name"]

        # Call the imported modular dialog
        open_equipment_tuning_dialog(
            self.root, 
            self.raw_save_data, 
            slot_index, 
            slot_name, 
            self.refresh_equipment_ui
        )

    def on_save_clicked(self):
        if not self.raw_save_data: return
        try:
            updated_attributes = {key: int(var.get()) for key, (var, _) in self.attr_vars.items()}
            updated_attributes["playerName"] = self.var_name.get()
            updated_attributes["playerClass"] = self.combo_class.get()
            updated_attributes["female"] = (self.combo_gender.get() == "Female")
            updated_attributes["leftHanded"] = (self.combo_hand.get() == "Left-Handed")
            updated_attributes["portrait"] = int(self.var_portrait.get())

            updated_skills = {name: int(var.get()) for name, (var, _) in self.skill_vars.items()}
            self.raw_save_data["quest_flags"] = {q["flag"]: self.quest_vars[q["flag"]].get() for q in QUEST_FLAGS}
            
            update_character(self.raw_save_data, updated_attributes, updated_skills)
            save_game_data(self.selected_slot, self.raw_save_data)
            
            self.char_lbl.config(text=f"Avatar: {updated_attributes['playerName']} ({updated_attributes['playerClass']})")
            messagebox.showinfo("Success", "All identities, survival bounds, quest flags, and equipment written to save block!")
        except ValueError:
            messagebox.showerror("Input Error", "Please verify numerical inputs. Formats must match integers!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not write back data: {e}")

    def on_cheat_skills_clicked(self):
        if not self.raw_save_data: return
        cheat_max_all_skills(self.raw_save_data, value=30)
        for skill_name, (var, _) in self.skill_vars.items():
            var.set("30")
        messagebox.showinfo("Cheat Applied", "Skills maximized globally!")