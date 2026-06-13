import logging

logger = logging.getLogger("core.inventory")

WIKI_ITEM_DATABASE = {
    "Light Source": [
        {"id": 145, "name": "Lantern",     "weight": "2.0", "details": "Standard portable light source"},
        {"id": 146, "name": "Torch",       "weight": "1.0", "details": "Consumable wooden torch"},
        {"id": 147, "name": "Candle",      "weight": "0.2", "details": "Small wax candle"},
        {"id": 148, "name": "Taper",       "weight": "0.1", "details": "Thin wax taper light"},
        {"id": 149, "name": "Lit Lantern", "weight": "2.0", "details": "Active lantern source"},
        {"id": 150, "name": "Lit Torch",   "weight": "1.0", "details": "Active burning torch"},
        {"id": 151, "name": "Lit Candle",  "weight": "0.2", "details": "Active burning candle"},
    ],
    "Head": [
        {"id": 44, "name": "Leather Cap",  "weight": "2.0", "protection": "1", "details": "Basic leather head protection"},
        {"id": 45, "name": "Chain Cowl",   "weight": "4.0", "protection": "3", "details": "Interlinked iron mesh cowl"},
        {"id": 46, "name": "Helmet",       "weight": "7.0", "protection": "5", "details": "Full iron plate helm"},
        {"id": 48, "name": "Crown A",      "weight": "4.0", "protection": "2", "details": "Regal decorative crown"},
        {"id": 49, "name": "Crown B",      "weight": "4.0", "protection": "2", "details": "Regal decorative crown variation"},
        {"id": 50, "name": "Crown C",      "weight": "4.0", "protection": "2", "details": "Regal decorative crown variation"},
    ],
    "Neck": [
        {"id": 21, "name": "Amulet", "weight": "0.5", "details": "Decorative or magical neck amulet"},
    ],
    "Right Hand": [
        {"id": 3,  "name": "Dagger",       "weight": "1.0", "damage": "1-4",  "details": "Slashing / Thrusting weapon"},
        {"id": 4,  "name": "Shortsword",   "weight": "3.5", "damage": "2-7",  "details": "Slashing / Thrusting weapon"},
        {"id": 5,  "name": "Longsword",    "weight": "5.0", "damage": "3-12", "details": "Balanced Slashing / Thrusting weapon"},
        {"id": 6,  "name": "Broadsword",   "weight": "6.0", "damage": "3-11", "details": "Heavy slashing weapon"},
        {"id": 10, "name": "A Shiny Sword","weight": "5.0", "damage": "4-15", "details": "High-quality magical blade"},
        {"id": 12, "name": "Black Sword",  "weight": "6.0", "damage": "5-20", "details": "Rare cursed or enchanted blade"},
        {"id": 13, "name": "Jeweled Sword","weight": "5.5", "damage": "3-14", "details": "Ornate gem-encrusted blade"},
        {"id": 0,  "name": "Hand Axe",     "weight": "4.0", "damage": "2-6",  "details": "Light chopping weapon"},
        {"id": 1,  "name": "Battle Axe",   "weight": "8.0", "damage": "4-16", "details": "Heavy two-handed executioner axe"},
        {"id": 2,  "name": "Axe",          "weight": "6.0", "damage": "3-10", "details": "Standard woodcutter axe"},
        {"id": 11, "name": "Jeweled Axe",  "weight": "7.0", "damage": "4-14", "details": "Ornate ceremonial axe"},
        {"id": 7,  "name": "Cudgel",       "weight": "3.0", "damage": "1-6",  "details": "Basic wooden bludgeon"},
        {"id": 8,  "name": "Light Mace",   "weight": "4.5", "damage": "2-7",  "details": "Flanged iron light mace"},
        {"id": 9,  "name": "Mace",         "weight": "7.0", "damage": "3-10", "details": "Heavy iron crushing mace"},
        {"id": 14, "name": "Jeweled Mace", "weight": "7.5", "damage": "3-12", "details": "Ornate ceremonial crushing mace"},
        {"id": 24, "name": "Sling",        "weight": "0.5", "details": "Simple leather ranged projectile launcher"},
        {"id": 25, "name": "Bow",          "weight": "3.0", "details": "Standard wooden shortbow"},
        {"id": 26, "name": "Crossbow",     "weight": "6.0", "details": "Mechanical heavy ranged weapon"},
        {"id": 31, "name": "Jeweled Bow",  "weight": "3.5", "details": "Enchanted masterwork bow"},
    ],
    "Chest": [
        {"id": 32, "name": "Leather Vest",  "weight": "5.0",  "protection": "2", "details": "Light cured leather torso armour"},
        {"id": 33, "name": "Mail Shirt",    "weight": "15.0", "protection": "5", "details": "Medium chainlink torso protection"},
        {"id": 34, "name": "A Breastplate", "weight": "25.0", "protection": "8", "details": "Heavy steel plate torso protection"},
    ],
    "Left Hand": [
        {"id": 62, "name": "Buckler",         "weight": "3.0",  "protection": "1", "details": "Small fast parrying shield"},
        {"id": 61, "name": "Small Shield",    "weight": "5.0",  "protection": "2", "details": "Standard light round shield"},
        {"id": 60, "name": "A Wooden Shield", "weight": "7.0",  "protection": "3", "details": "Medium reinforced wooden shield"},
        {"id": 55, "name": "Shiny Shield",    "weight": "8.0",  "protection": "4", "details": "Polished magical shield"},
        {"id": 59, "name": "Tower Shield",    "weight": "14.0", "protection": "6", "details": "Massive rectangular plate shield"},
        {"id": 63, "name": "Jeweled Shield",  "weight": "10.0", "protection": "5", "details": "Ornate gem-gilded shield"},
    ],
    "Gloves": [
        {"id": 38, "name": "Leather Gloves",   "weight": "1.0", "protection": "1", "details": "Supple leather hand covers"},
        {"id": 39, "name": "Chain Gauntlets",  "weight": "2.5", "protection": "2", "details": "Chainlink reinforced hand gauntlets"},
        {"id": 40, "name": "Plate Gauntlets",  "weight": "4.0", "protection": "3", "details": "Heavy rigid plate steel gauntlets"},
    ],
    "Ring 1": [
        {"id": 54, "name": "Iron Ring",    "weight": "0.1", "details": "Plain heavy iron band"},
        {"id": 56, "name": "Gold Ring",    "weight": "0.1", "details": "Valuable polished gold band"},
        {"id": 57, "name": "A Silver Ring","weight": "0.1", "details": "Ornate reflective silver band"},
        {"id": 58, "name": "Red Ring",     "weight": "0.1", "details": "Magical ring set with a glowing ruby"},
    ],
    "Legs": [
        {"id": 35, "name": "Leather Leggings","weight": "4.0",  "protection": "1", "details": "Light leather lower body protection"},
        {"id": 36, "name": "Mail Leggings",   "weight": "11.0", "protection": "4", "details": "Chainlink greaves and cuisses"},
        {"id": 37, "name": "Plate Leggings",  "weight": "18.0", "protection": "6", "details": "Rigid steel plate lower body guards"},
    ],
    "Ring 2": [
        {"id": 54, "name": "Iron Ring",    "weight": "0.1", "details": "Plain heavy iron band"},
        {"id": 56, "name": "Gold Ring",    "weight": "0.1", "details": "Valuable polished gold band"},
        {"id": 57, "name": "A Silver Ring","weight": "0.1", "details": "Ornate reflective silver band"},
        {"id": 58, "name": "Red Ring",     "weight": "0.1", "details": "Magical ring set with a glowing ruby"},
    ],
    "Boots": [
        {"id": 41, "name": "Leather Boots",    "weight": "2.0", "protection": "1", "details": "Soft traveler leather boots"},
        {"id": 42, "name": "Chain Boots",      "weight": "4.5", "protection": "2", "details": "Reinforced mail-lined military boots"},
        {"id": 43, "name": "Plate Boots",      "weight": "6.0", "protection": "3", "details": "Heavy steel-shod plate sabatons"},
        {"id": 47, "name": "Dragonskin Boots", "weight": "3.0", "protection": "4", "details": "Rare fireproof dragonhide boots"},
    ],
}


def find_key_recursive(data: dict, target_key: str):
    """Recursively searches for a target key within deeply nested dicts or lists."""
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for value in data.values():
            result = find_key_recursive(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_key_recursive(item, target_key)
            if result is not None:
                return result
    return None


def get_item_from_any_slot(object_type_id: int) -> dict | None:
    """Scans the entire database for an item by ID — used as a global fallback."""
    for items in WIKI_ITEM_DATABASE.values():
        for item in items:
            if item["id"] == object_type_id:
                return item
    return None


def get_equipment_summary(data: dict) -> list[dict]:
    """
    Extracts equipped items from save data and maps them to the Wiki layout.
    Each entry includes: slot_index, slot_name, objectName, objectType,
    objectIndex, enchantment, details, is_empty.
    """
    slot_names = [
        "Light Source", "Head", "Neck", "Right Hand", "Chest",
        "Left Hand", "Gloves", "Ring 1", "Legs", "Ring 2", "Boots",
    ]

    raw_equipment = find_key_recursive(data, "equippedItems")

    if not data or not raw_equipment:
        logger.warning("Key 'equippedItems' missing in save file.")
        return [
            {
                "slot_index": idx, "slot_name": name, "objectName": "Empty Slot",
                "objectType": 0, "objectIndex": 0, "enchantment": "",
                "details": "", "is_empty": True,
            }
            for idx, name in enumerate(slot_names)
        ]

    summary = []
    for idx, slot_title in enumerate(slot_names):
        if idx >= len(raw_equipment):
            break

        item_data = raw_equipment[idx]
        obj_type = item_data.get("objectType", 0)
        enchantment = item_data.get("enchantment", "") or ""

        if obj_type == 0:
            item_name = "Empty Slot"
            item_details = ""
        else:
            allowed = WIKI_ITEM_DATABASE.get(slot_title, [])
            match = next((i for i in allowed if i["id"] == obj_type), None)
            if not match:
                match = get_item_from_any_slot(obj_type)

            if match:
                item_name = match["name"]
                item_details = f"{match.get('details', '')} (Wgt: {match.get('weight', '0')})"
            else:
                item_name = item_data.get("objectName", f"Unknown #{obj_type}")
                item_details = "Custom loaded entity"

        summary.append({
            "slot_index":  idx,
            "slot_name":   slot_title,
            "objectName":  item_name,
            "objectType":  obj_type,
            "objectIndex": item_data.get("objectIndex", 0),
            "enchantment": enchantment,
            "details":     item_details,
            "is_empty":    obj_type == 0,
        })

    return summary


def update_equipped_item(
    data: dict,
    slot_index: int,
    new_object_type: int,
    new_name: str,
    enchantment: str = "",
) -> None:
    """
    Mutates a single equipment slot in memory.
    enchantment: spell name to inject, empty string for non-magical items.
    """
    raw_equipment = find_key_recursive(data, "equippedItems")
    if not raw_equipment or slot_index >= len(raw_equipment):
        logger.error("Out of bounds or invalid equipment structure for slot %d.", slot_index)
        return

    slot = raw_equipment[slot_index]
    slot["objectType"] = int(new_object_type)
    slot["enchantment"] = enchantment

    if int(new_object_type) == 0:
        slot["objectName"] = ""
        slot["objectTypeName"] = ""
        slot["objectIndex"] = 0
    else:
        slot["objectName"] = new_name
        match = get_item_from_any_slot(new_object_type)
        if match:
            slot["objectTypeName"] = "Weapon" if "damage" in match else "Armour"

    logger.info("Slot #%d updated: type=%d name=%r enchantment=%r",
                slot_index, new_object_type, new_name, enchantment)

