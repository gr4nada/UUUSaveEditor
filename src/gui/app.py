import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from src.core.save_manager import load_save, save_game_data
from src.core.enums import NOMES_SKILLS
from src.core.character import get_character_summary, update_character, cheat_max_all_skills
from src.core.inventory import get_equipment_summary, get_sprite_coordinates, ITEM_DATABASE

class EditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultima Underworld Unity - Save Editor")
        self.root.geometry("800x700")  # Made slightly wider to fit the gorgeous paper layout
        self.root.resizable(False, False)
        
        self.raw_save_data = None
        self.selected_slot = 0
        
        self.attr_vars = {}
        self.skill_vars = {}
        self.equipment_slots_ui = [] # Holds the labels displaying item icons
        self.loaded_icons_cache = [] # Prevents Tkinter garbage collection from wiping cropped assets
        
        self.spritesheet = None
        self.load_spritesheet()
        
        self.setup_styles()
        self.create_widgets()

    def load_spritesheet(self):
        """Loads the items PNG image using Pillow."""
        assets_path = os.path.join("assets", "image_2222a2.png")
        if os.path.exists(assets_path):
            try:
                self.spritesheet = Image.open(assets_path)
            except Exception as e:
                print(f"Warning: Could not open spritesheet image: {e}")

    def get_item_icon(self, sprite_index: int) -> ImageTk.PhotoImage:
        """Cuts out a 64x64 sub-image from the spritesheet and prepares it for Tkinter."""
        if not self.spritesheet:
            # Fallback to a blank transparent image block if asset is missing
            return ImageTk.PhotoImage(Image.new("RGBA", (64, 64), (40, 40, 40, 255)))
        
        coords = get_sprite_coordinates(sprite_index)
        cropped_img = self.spritesheet.crop(coords)
        return ImageTk.PhotoImage(cropped_img)

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
        
        # TAB 1: Avatar Engine
        self.char_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.char_tab, text="Avatar Editor")
        
        self.left_frame = ttk.LabelFrame(self.char_tab, text=" Base Attributes ", padding=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.right_frame = ttk.LabelFrame(self.char_tab, text=" Skills Matrix (19) ", padding=10)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        self.draw_attribute_fields()
        self.draw_skill_fields()

        # TAB 2: Equipment Matrix (The Insane Part!)
        self.equip_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.equip_tab, text="Equipment Matrix")
        self.draw_equipment_grid()

        # --- Footer ---
        footer_frame = ttk.Frame(self.root, padding=10)
        footer_frame.pack(fill="x", side="bottom")
        
        self.skills_cheat_btn = ttk.Button(footer_frame, text="Maximize All Skills (30)", command=self.on_cheat_skills_clicked, state="disabled")
        self.skills_cheat_btn.pack(side="left", padx=15)
        
        self.save_btn = ttk.Button(footer_frame, text="Save Changes", command=self.on_save_clicked, state="disabled")
        self.save_btn.pack(side="right", padx=15, ipady=3)

    def draw_attribute_fields(self):
        fields = [
            ("charLevel", "Level:"), ("exp", "Experience (EXP):"),
            ("hp", "Health Points (HP):"), ("vitality", "Max Vitality:"),
            ("mana", "Current Mana:"), ("maxMana", "Max Mana:"),
            ("strength", "Strength (STR):"), ("dexterity", "Dexterity (DEX):"),
            ("intellect", "Intellect (INT):"), ("skillPoints", "Unspent Skill Points:")
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

    def draw_equipment_grid(self):
        """Creates the grid blueprint mirroring the paper doll equipment slots layout."""
        # Main Canvas mimicking the inventory box container
        self.inventory_canvas = tk.Canvas(self.equip_tab, width=550, height=400, bg="#2b2b2b", highlightthickness=1, highlightbackground="#444")
        self.inventory_canvas.pack(pady=20)
        
        # Draw a sleek center rectangle simulating the avatar silhouette background
        self.inventory_canvas.create_rectangle(210, 50, 340, 350, fill="#1f1f1f", outline="#555")
        self.inventory_canvas.create_text(275, 200, text="AVATAR", fill="#444", font=("Arial", 16, "bold"))

        # Define grid coordinates (X, Y) inside the canvas container for each slot
        # Ordering: Light, Head, Neck, Right Hand, Chest, Left Hand, Gloves, Ring 1, Legs, Ring 2, Boots
        self.slot_positions = [
            (80,  60),  # Light Source
            (243, 60),  # Head
            (400, 60),  # Neck
            (80,  160), # Right Hand (Weapon)
            (243, 150), # Chest (Armor)
            (400, 160), # Left Hand (Shield)
            (80,  260), # Gloves
            (145, 110), # Ring 1
            (243, 240), # Legs
            (335, 110), # Ring 2
            (243, 320)  # Boots
        ]
        
        slot_names = [
            "Light Source", "Head", "Neck", "Right Hand", "Chest", 
            "Left Hand", "Gloves", "Ring 1", "Legs", "Ring 2", "Boots"
        ]

        # Draw empty template item frames
        for idx, (x, y) in enumerate(self.slot_positions):
            # Label background block
            lbl_bg = tk.Label(self.inventory_canvas, bg="#111", width=9, height=4, bd=2, relief="groove")
            self.inventory_canvas.create_window(x + 32, y + 32, window=lbl_bg)
            
            # Label container that will hold the live graphical images
            lbl_img = tk.Label(self.inventory_canvas, bg="#222", text="Empty", fg="#666")
            self.inventory_canvas.create_window(x + 32, y + 32, window=lbl_img)
            
            # Label title above slot
            self.inventory_canvas.create_text(x + 32, y - 10, text=slot_names[idx], fill="#bbb", font=("Arial", 8, "bold"))
            
            # Bind click event for swapping items visually
            lbl_img.bind("<Button-1>", lambda e, slot=idx: self.on_equipment_slot_clicked(slot))
            
            self.equipment_slots_ui.append(lbl_img)

    # --- UI Event Handlers ---

    def on_load_clicked(self):
        self.selected_slot = self.slot_combo.current()
        try:
            self.raw_save_data = load_save(self.selected_slot)
            
            # 1. Populate Character Tab Data
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
                
            # 2. Populate Equipment Tab Data (Slices and renders pictures!)
            self.refresh_equipment_ui()
                
            self.save_btn.config(state="normal")
            self.skills_cheat_btn.config(state="normal")
            messagebox.showinfo("Success", f"Slot {self.selected_slot} data compiled successfully!")
            
        except FileNotFoundError as e:
            messagebox.showerror("File Not Found", str(e))
        except Exception as e:
            messagebox.showerror("Fatal Error", f"Failed to process save data: {e}")

    def refresh_equipment_ui(self):
        """Re-reads the save dictionary array and updates the item images on the grid screen."""
        data_to_parse = self.raw_save_data if self.raw_save_data is not None else {}
        equip_summary = get_equipment_summary(data_to_parse)
        
        # Flush the old icon memory cache to clean leakage space
        self.loaded_icons_cache = []
        
        for item in equip_summary:
            idx = item["slot_index"]
            label_widget = self.equipment_slots_ui[idx]
            
            if item["is_empty"]:
                label_widget.config(image="", text="Empty", bg="#222")
            else:
                photo_icon = self.get_item_icon(item["sprite_idx"])
                self.loaded_icons_cache.append(photo_icon) # Anchor reference protection from garbage collector
                
                label_widget.config(image=photo_icon, bg="#1a1a1a")
                
                # Bind hover events safely capturing the current explicit item loop name payload
                label_widget.bind("<Enter>", lambda e, name=item["objectName"]: self.root.title(f"Item: {name}"))
                label_widget.bind("<Leave>", lambda e: self.root.title("Ultima Underworld Unity - Save Editor"))

    def on_equipment_slot_clicked(self, slot_index):
        """Opens a visual modal pop-up list allowing selection of an item to spawn inside that slot."""
        if not self.raw_save_data: return
        
        # 1. Toplevel modal window initialization
        popup = tk.Toplevel(self.root)
        popup.title(f"Change Equipment - Slot {slot_index}")
        popup.geometry("300x400")
        popup.transient(self.root)
        popup.grab_set()
        
        ttk.Label(popup, text="Select new item to inject:", font=("Arial", 10, "bold")).pack(pady=10)
        
        # 2. Listbox container generation within the popup scope
        popup_listbox = tk.Listbox(popup, font=("Arial", 10))
        popup_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Populate Listbox UI with available elements from our database matrix
        available_items = list(ITEM_DATABASE.items())
        for code, info in available_items:
            popup_listbox.insert(tk.END, f"{info['name']} (ID: {code})")
            
        # 3. Selection routine callback (Declaring after popup_listbox definition for proper variable scoping)
        def confirm_selection():
            selection = popup_listbox.curselection()
            if selection:
                idx = selection[0]
                selected_code, selected_info = available_items[idx]
                
                # Check explicitly to satisfy static type checkers and clear the assignment warning
                if self.raw_save_data is None:
                    popup.destroy()
                    return
                
                # Directly mutate the dynamic object list inside the target save dictionary
                from src.core.inventory import update_equipped_item
                update_equipped_item(self.raw_save_data, slot_index, selected_code, selected_info["name"], selected_info["type_name"])
                
                # Re-render the graphical equipment grid view
                self.refresh_equipment_ui()
                popup.destroy()
                messagebox.showinfo("Injected", f"Successfully spawned {selected_info['name']} into slot!")
            else:
                messagebox.showwarning("Selection Error", "Please select an item from the list first.")
        # 4. Command trigger button execution
        ttk.Button(popup, text="Equip Item", command=confirm_selection).pack(pady=10)  

    def on_save_clicked(self):
        if not self.raw_save_data: return
        try:
            updated_attributes = {key: int(var.get()) for key, (var, _) in self.attr_vars.items()}
            updated_skills = {name: int(var.get()) for name, (var, _) in self.skill_vars.items()}
            
            update_character(self.raw_save_data, updated_attributes, updated_skills)
            save_game_data(self.selected_slot, self.raw_save_data)
            
            messagebox.showinfo("Success", "All attributes, skills, and equipment mutations written to disk!")
            
        except ValueError:
            messagebox.showerror("Input Error", "Attribute entries only accept integers!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not write back data: {e}")

    def on_cheat_skills_clicked(self):
        if not self.raw_save_data: return
        cheat_max_all_skills(self.raw_save_data, value=30)
        for skill_name, (var, _) in self.skill_vars.items():
            var.set("30")
        messagebox.showinfo("Cheat Applied", "Skills maximized globally!")