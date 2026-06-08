import logging

# Initialize the logger instance for this specific core module
logger = logging.getLogger("core.inventory")

# Item types mapping to their respective index in the 16x16 grid (0 to 255)
# and their clean English display names.
ITEM_DATABASE = {
    0:   {"name": "Empty Slot", "type_name": "", "sprite_idx": 0},
    10:  {"name": "A Shiny Sword", "type_name": "Weapon", "sprite_idx": 1},
    34:  {"name": "A Breastplate", "type_name": "Armour", "sprite_idx": 2},
    36:  {"name": "Mail Leggings", "type_name": "Armour", "sprite_idx": 3},
    40:  {"name": "Plate Gauntlets", "type_name": "Armour", "sprite_idx": 4},
    42:  {"name": "Chain Boots", "type_name": "Armour", "sprite_idx": 5},
    46:  {"name": "A Helmet", "type_name": "Armour", "sprite_idx": 6},
    57:  {"name": "A Silver Ring", "type_name": "Armour", "sprite_idx": 7},
    60:  {"name": "A Wooden Shield", "type_name": "Armour", "sprite_idx": 8},
    147: {"name": "Light Source", "type_name": "LightSource", "sprite_idx": 9}
}

def find_key_recursive(data: dict, target_key: str):
    """
    Recursively searches for a target key within deeply nested dictionaries or lists.
    """
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for key, value in data.items():
            result = find_key_recursive(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_key_recursive(item, target_key)
            if result is not None:
                return result
    return None

def get_equipment_summary(data: dict) -> list:
    """
    Extracts the 11 equipped items by searching for the accurate 'equippedItems' key inside the JSON structure.
    """
    slot_names = [
        "Light Source", "Head", "Neck", "Right Hand", "Chest", 
        "Left Hand", "Gloves", "Ring 1", "Legs", "Ring 2", "Boots"
    ]
    
    # Locate the list of equipped items anywhere inside the save file structure
    raw_equipment = find_key_recursive(data, "equippedItems")
    
    # Fallback procedure if the targeted key structure is missing or blank
    if not data or not raw_equipment:
        logger.warning("Key 'equippedItems' was not found inside the save JSON structure!")
        return [{
            "slot_index": idx, "slot_name": name, "objectName": "Empty",
            "objectTypeName": "", "objectType": 0, "objectIndex": 0,
            "sprite_idx": 0, "is_empty": True
        } for idx, name in enumerate(slot_names)]
        
    logger.debug("Successfully localized %d active slots inside 'equippedItems'.", len(raw_equipment))
    
    equipment_summary = []
    
    for idx, slot_title in enumerate(slot_names):
        if idx < len(raw_equipment):
            item = raw_equipment[idx]
            obj_type = item.get("objectType", 0)
            obj_name = item.get("objectName", "")
            
            # Cross-reference parsed object type IDs against our internal application database
            db_info = ITEM_DATABASE.get(obj_type, {
                "name": obj_name if obj_name != "" else f"Item #{obj_type}", 
                "type_name": item.get("objectTypeName", "Item"), 
                "sprite_idx": 0
            })
            
            equipment_summary.append({
                "slot_index": idx,
                "slot_name": slot_title,
                "objectName": db_info["name"],
                "objectTypeName": db_info["type_name"],
                "objectType": obj_type,
                "objectIndex": item.get("objectIndex", 0),
                "sprite_idx": db_info["sprite_idx"],
                "is_empty": obj_type == 0
            })
            
    return equipment_summary

def update_equipped_item(data: dict, slot_index: int, new_object_type: int, new_name: str, new_type_name: str):
    """
    Updates a specific equipment slot inside the dynamically localized 'equippedItems' array structure.
    """
    raw_equipment = find_key_recursive(data, "equippedItems")
    
    if not raw_equipment:
        logger.error("Failed to update slot: key 'equippedItems' could not be located inside the JSON.")
        return
        
    if slot_index >= len(raw_equipment):
        raise IndexError("Target equipment slot index out of bounds.")
        
    item_slot = raw_equipment[slot_index]
    item_slot["objectType"] = int(new_object_type)
    item_slot["objectName"] = new_name
    item_slot["objectTypeName"] = new_type_name
    
    # Clean inner structural data parameters if the slot is mutated to empty (ID 0)
    if int(new_object_type) == 0:
        item_slot["objectName"] = ""
        item_slot["objectTypeName"] = ""
        item_slot["objectIndex"] = 0
        item_slot["jsonData"] = ""
        
    logger.info("Slot #%d mutated successfully in memory to ID %d (%s)", slot_index, new_object_type, new_name)

def get_sprite_coordinates(sprite_index: int, sprite_size: int = 32) -> tuple:
    """
    Calculates the exact bounding box for cropping a single 32x32 icon out of a 16-column sheet layout.
    """
    columns = 16
    row = sprite_index // columns
    col = sprite_index % columns
    return (col * sprite_size, row * sprite_size, (col + 1) * sprite_size, (row + 1) * sprite_size)