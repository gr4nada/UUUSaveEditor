import tkinter as tk
from tkinter import ttk, messagebox
from src.core.save_manager import load_save, save_game_data
from src.core.enums import NOMES_SKILLS
from src.core.character import get_character_summary, update_character, cheat_max_all_skills

class EditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultima Underworld Unity - Save Editor")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # State variables
        self.raw_save_data = None
        self.selected_slot = 0
        
        self.attr_vars = {}
        self.skill_vars = {}
        
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def create_widgets(self):
        # --- Top Header: File / Slot Manager ---
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

        # --- Central Tabs System ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.char_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.char_tab, text="Avatar Editor")
        
        # Grid splits: Attributes Left, Skills Right
        self.left_frame = ttk.LabelFrame(self.char_tab, text=" Base Attributes ", padding=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.right_frame = ttk.LabelFrame(self.char_tab, text=" Skills Matrix (19) ", padding=10)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        self.draw_attribute_fields()
        self.draw_skill_fields()

        # --- Footer: Global Commands ---
        footer_frame = ttk.Frame(self.root, padding=10)
        footer_frame.pack(fill="x", side="bottom")
        
        self.skills_cheat_btn = ttk.Button(footer_frame, text="Maximize All Skills (30)", command=self.on_cheat_skills_clicked, state="disabled")
        self.skills_cheat_btn.pack(side="left", padx=15)
        
        self.save_btn = ttk.Button(footer_frame, text="Save Changes", command=self.on_save_clicked, state="disabled")
        self.save_btn.pack(side="right", padx=15, ipady=3)

    def draw_attribute_fields(self):
        fields = [
            ("charLevel", "Level:"),
            ("exp", "Experience (EXP):"),
            ("hp", "Health Points (HP):"),
            ("vitality", "Max Vitality:"),
            ("mana", "Current Mana:"),
            ("maxMana", "Max Mana:"),
            ("strength", "Strength (STR):"),
            ("dexterity", "Dexterity (DEX):"),
            ("intellect", "Intellect (INT):"),
            ("skillPoints", "Unspent Skill Points:")
        ]
        
        for idx, (key, label_text) in enumerate(fields):
            ttk.Label(self.left_frame, text=label_text).grid(row=idx, column=0, sticky="w", pady=4, padx=5)
            
            var = tk.StringVar()
            entry = ttk.Entry(self.left_frame, textvariable=var, state="disabled", width=12)
            entry.grid(row=idx, column=1, sticky="w", pady=4, padx=5)
            
            self.attr_vars[key] = (var, entry)

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

    # --- UI Event Handlers ---

    def on_load_clicked(self):
        self.selected_slot = self.slot_combo.current()
        try:
            self.raw_save_data = load_save(self.selected_slot)
            summary = get_character_summary(self.raw_save_data)
            
            name = summary["attributes"]["playerName"]
            char_class = summary["attributes"]["playerClass"]
            self.char_lbl.config(text=f"Avatar: {name} ({char_class})")
            
            for key, (var, entry) in self.attr_vars.items():
                entry.config(state="normal")
                var.set(str(summary["attributes"].get(key, 0)))
                
            for skill_name, (var, entry) in self.skill_vars.items():
                entry.config(state="normal")
                var.set(str(summary["skills"].get(skill_name, 0)))
                
            self.save_btn.config(state="normal")
            self.skills_cheat_btn.config(state="normal")
            messagebox.showinfo("Success", f"Slot {self.selected_slot} loaded successfully!")
            
        except FileNotFoundError as e:
            messagebox.showerror("File Not Found", str(e))
        except Exception as e:
            messagebox.showerror("Fatal Error", f"Failed to process save data: {e}")

    def on_save_clicked(self):
        if not self.raw_save_data: return
        try:
            updated_attributes = {key: int(var.get()) for key, (var, _) in self.attr_vars.items()}
            updated_skills = {name: int(var.get()) for name, (var, _) in self.skill_vars.items()}
            
            update_character(self.raw_save_data, updated_attributes, updated_skills)
            save_game_data(self.selected_slot, self.raw_save_data)
            
            messagebox.showinfo("Success", "Modifications written to compressed save file!")
            
        except ValueError:
            messagebox.showerror("Input Error", "All fields only accept whole numbers (integers)!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not write back data: {e}")

    def on_cheat_skills_clicked(self):
        if not self.raw_save_data: return
        cheat_max_all_skills(self.raw_save_data, value=30)
        for skill_name, (var, _) in self.skill_vars.items():
            var.set("30")
        messagebox.showinfo("Cheat Applied", "All 19 skills set to maximum level (30) internally!")