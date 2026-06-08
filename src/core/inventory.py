# Item types mapping to their respective index in the 8x8 grid (0 to 63)
# and their clean English display names.
ITEM_DATABASE = {
    0:  {"name": "Empty Slot", "type_name": "", "sprite_idx": 0},
    10: {"name": "A Shiny Sword", "type_name": "Weapon", "sprite_idx": 1},  # Let's test sprite position 1
    34: {"name": "A Breastplate", "type_name": "Armour", "sprite_idx": 2}, # Let's test sprite position 2
    36: {"name": "Mail Leggings", "type_name": "Armour", "sprite_idx": 3},  # Let's test sprite position 3
    40: {"name": "Plate Gauntlets", "type_name": "Armour", "sprite_idx": 4},# Let's test sprite position 4
    42: {"name": "Chain Boots", "type_name": "Armour", "sprite_idx": 5},   # Let's test sprite position 5
    46: {"name": "A Helmet", "type_name": "Armour", "sprite_idx": 6},       # Let's test sprite position 6
    57: {"name": "A Silver Ring", "type_name": "Armour", "sprite_idx": 7},  # Let's test sprite position 7
    60: {"name": "A Wooden Shield", "type_name": "Armour", "sprite_idx": 8}, # Let's test sprite position 8 (Row 1, Col 0)
    147:{"name": "Light Source", "type_name": "LightSource", "sprite_idx": 9}# Let's test sprite position 9
}

def get_equipment_summary(data: dict) -> list:
    """Extracts the list of 11 equipped items from the save root structure."""
    slot_names = [
        "Light Source", "Head", "Neck", "Right Hand", "Chest", 
        "Left Hand", "Gloves", "Ring 1", "Legs", "Ring 2", "Boots"
    ]
    
    # Blindagem: se o arquivo não foi carregado ou não tem a chave, gera layout vazio
    if not data or 'equippedItems' not in data:
        return [{
            "slot_index": idx, "slot_name": name, "objectName": "Empty",
            "objectTypeName": "", "objectType": 0, "objectIndex": 0,
            "sprite_idx": 0, "is_empty": True
        } for idx, name in enumerate(slot_names)]
        
    raw_equipment = data['equippedItems']
    equipment_summary = []
    
    for idx, slot_title in enumerate(slot_names):
        if idx < len(raw_equipment):
            item = raw_equipment[idx]
            obj_type = item.get("objectType", 0)
            
            db_info = ITEM_DATABASE.get(obj_type, {
                "name": item.get("objectName", f"Item #{obj_type}"), 
                "type_name": item.get("objectTypeName", "Item"), 
                "sprite_idx": 0
            })
            
            equipment_summary.append({
                "slot_index": idx,
                "slot_name": slot_title,
                "objectName": db_info["name"] if item.get("objectName") == "" else item.get("objectName"),
                "objectTypeName": db_info["type_name"],
                "objectType": obj_type,
                "objectIndex": item.get("objectIndex", 0),
                "sprite_idx": db_info["sprite_idx"],
                "is_empty": obj_type == 0
            })
    return equipment_summary

def get_sprite_coordinates(sprite_index: int, sprite_size: int = 64) -> tuple:
    """Calculates the bounding box for cutting a 64x64 icon."""
    columns = 8
    row = sprite_index // columns
    col = sprite_index % columns
    return (col * sprite_size, row * sprite_size, (col + 1) * sprite_size, (row + 1) * sprite_size)

def update_equipped_item(data: dict, slot_index: int, new_object_type: int, new_name: str, new_type_name: str):
    """Updates a specific equipment slot inside the raw JSON structure."""
    if not data or 'equippedItems' not in data:
        return
    if slot_index >= len(data['equippedItems']):
        raise IndexError("Target equipment slot index out of bounds.")
        
    item_slot = data['equippedItems'][slot_index]
    item_slot["objectType"] = int(new_object_type)
    item_slot["objectName"] = new_name
    item_slot["objectTypeName"] = new_type_name
    
    if int(new_object_type) == 0:
        item_slot["objectName"] = ""
        item_slot["objectTypeName"] = ""
        item_slot["objectIndex"] = 0
        item_slot["jsonData"] = ""