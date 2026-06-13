# src/gui/dialogs.py
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from src.gui.constants import SPELL_DATABASE, THEME
from src.core.inventory import WIKI_ITEM_DATABASE, update_equipped_item

logger = logging.getLogger("gui.dialogs")

def open_equipment_tuning_dialog(parent, raw_save_data, slot_index, slot_name, on_success_callback):
    """Builds the dual-column modal frame handling structural item and spell mutations."""
    allowed_options = WIKI_ITEM_DATABASE.get(slot_name, [])

    dialog = tk.Toplevel(parent)
    dialog.title(f"Tuning Slot: {slot_name}")
    dialog.geometry("680x480")
    dialog.transient(parent)
    dialog.grab_set()

    left_box = ttk.LabelFrame(dialog, text=" 1. Base Item Selection ", padding=10)
    left_box.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    listbox = tk.Listbox(left_box, width=38, height=18, font=("Courier", 9))
    listbox.pack(fill="both", expand=True)
    listbox.insert(tk.END, " [ Clear Slot ] -> (ID: 0)")
    for item in allowed_options:
        stat = f"DMG: {item['damage']}" if "damage" in item else f"PRT: {item['protection']}" if "protection" in item else "UTILITY"
        listbox.insert(tk.END, f" {item['name']:<16} | {stat:<8} | ID: {item['id']}")

    right_box = ttk.LabelFrame(dialog, text=" 2. Injected Magic Tuning (SSpell) ", padding=10)
    right_box.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    spell_listbox = tk.Listbox(right_box, width=38, height=18, font=("Courier", 9), fg=THEME["dialog_spell_fg"])
    spell_listbox.pack(fill="both", expand=True)
    spell_listbox.insert(tk.END, " [ Non-Magical / Clean Item ]")
    for spell in SPELL_DATABASE:
        rune_txt = f"[{spell['rune']}]" if spell['rune'] else "[Innate]"
        spell_listbox.insert(tk.END, f" {spell['name']:<20} {rune_txt:>8}")

    listbox.activate(0)
    spell_listbox.activate(0)

    def confirm_selection():
        item_sel = listbox.curselection()
        spell_sel = spell_listbox.curselection()
        
        if not item_sel or not spell_sel:
            messagebox.showwarning("Incomplete Selection", "You must pick both an Item and a Spell state!")
            return
        
        i_idx = item_sel[0]
        if i_idx == 0:
            new_id, new_name = 0, ""
        else:
            selected_item = allowed_options[i_idx - 1]
            new_id, new_name = selected_item["id"], selected_item["name"]
            
        s_idx = spell_sel[0]
        chosen_spell_name = "" if s_idx == 0 else SPELL_DATABASE[s_idx - 1]["name"]

        update_equipped_item(raw_save_data, slot_index, new_id, new_name, chosen_spell_name)
        on_success_callback()
        dialog.destroy()
        messagebox.showinfo("Matrix Updated", f"Successfully tuned {slot_name} contents!")

    btn_select = ttk.Button(dialog, text="Apply Tuning Matrix", command=confirm_selection)
    btn_select.pack(side="bottom", fill="x", padx=10, pady=10)