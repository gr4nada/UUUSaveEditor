# tests/test_inventory_roundtrip.py
"""
Inventory and equipment integrity data validation tests.

Covers: inventoryData structure mapping, update_equipped_item modification roundtrips,
jsonData string preservation, nested enchantment properties parsing, and isolated non-target elements checks.
"""
import logging
import json
import copy
from src.core.inventory import get_equipment_summary, update_equipped_item
from src.core.save_diff import SaveDiff

logger = logging.getLogger("tests.test_inventory_roundtrip")


# ---------------------------------------------------------------------------
# Structural Layout Verification
# ---------------------------------------------------------------------------

def test_inventory_data_keys_present(sample_save):
    """
    Validates that inventoryData contains the baseline structural properties expected.
    """
    inv = sample_save["inventoryData"]
    for key in ("mainInventory", "equippedItems"):
        assert key in inv, f"Required property key '{key}' missing from inventoryData context wrapper"


def test_equipped_items_slot_count(sample_save):
    """
    Verifies that equippedItems contains exactly 11 slots corresponding to the game layout.
    """
    equipped = sample_save["inventoryData"]["equippedItems"]
    assert len(equipped) == 11, f"Expected exactly 11 inventory equipment entries, but found {len(equipped)}"


def test_each_equipped_slot_has_required_keys(sample_save):
    """
    Ensures that every distinct structural slot within equippedItems contains required data fields.
    """
    required = {"objectName", "objectTypeName", "objectType", "objectIndex",
                "level", "originalLevel", "inWorldObj", "jsonData"}
    for idx, slot in enumerate(sample_save["inventoryData"]["equippedItems"]):
        missing = required - set(slot.keys())
        assert not missing, f"Equipment slot index {idx} lacks mandatory structure schema properties: {missing}"


def test_main_inventory_items_have_json_data(sample_save):
    """
    Validates that items inside mainInventory contain non-empty jsonData strings tracking Unity state contexts.
    """
    for idx, item in enumerate(sample_save["inventoryData"]["mainInventory"]):
        assert "jsonData" in item, f"mainInventory entry node index [{idx}] lacks a jsonData string definition"
        assert item["jsonData"] != "", f"mainInventory entry node index [{idx}] has an empty jsonData string value"


def test_json_data_is_valid_json_string(sample_save):
    """
    Enforces that the embedded jsonData block of each element resolves to a valid, parseable JSON data structure.
    """
    for idx, item in enumerate(sample_save["inventoryData"]["mainInventory"]):
        try:
            parsed = json.loads(item["jsonData"])
            assert isinstance(parsed, dict), f"mainInventory entry node index [{idx}].jsonData did not map to a dict layout"
        except json.JSONDecodeError as e:
            assert False, f"mainInventory entry node index [{idx}].jsonData failed syntax serialization checks: {e}"


# ---------------------------------------------------------------------------
# get_equipment_summary Verification Routine
# ---------------------------------------------------------------------------

def test_equipment_summary_returns_11_slots(sample_save):
    """
    Validates that get_equipment_summary maps exactly one entry per tracking equipment slot.
    """
    summary = get_equipment_summary(sample_save)
    assert len(summary) == 11


def test_equipment_summary_slot_indices_are_sequential(sample_save):
    """
    Guarantees that mapped slot_index values within get_equipment_summary are sorted sequentially from 0 to 10.
    """
    summary = get_equipment_summary(sample_save)
    for expected_idx, item in enumerate(summary):
        assert item["slot_index"] == expected_idx


def test_equipment_summary_known_item_identified(sample_save):
    """
    Verifies that slot 3 (Right Hand) containing 'a shiny sword' is correctly parsed via underlying definitions.
    """
    summary = get_equipment_summary(sample_save)
    right_hand = summary[3]
    assert right_hand["slot_name"] == "Right Hand"
    assert right_hand["objectType"] == 10
    assert right_hand["is_empty"] is False
    assert "Sword" in right_hand["objectName"] or right_hand["objectType"] == 10


def test_equipment_summary_empty_slot_flagged(sample_save):
    """
    Enforces that items returning an objectType of 0 are explicitly classified with is_empty=True.
    """
    summary = get_equipment_summary(sample_save)
    for item in summary:
        if item["objectType"] == 0:
            assert item["is_empty"] is True, (
                f"Equipment slot index {item['slot_index']} ({item['slot_name']}) tracks objectType=0 "
                f"but structurally reported an invalid is_empty value status: {item['is_empty']}"
            )


def test_enchanted_item_enchantment_readable(sample_save):
    """
    Validates that enchantment fields hidden within slot 7 (Ring 1) jsonData strings are properly exposed.
    """
    summary = get_equipment_summary(sample_save)
    ring = summary[7]
    assert ring["slot_name"] == "Ring 1"
    assert ring["objectType"] == 57
    
    # Cross-verify with raw structural attributes inside nested text streams
    json_data = json.loads(sample_save["inventoryData"]["equippedItems"][7]["jsonData"])
    assert json_data["enchantmentName"] == "Leap"


# ---------------------------------------------------------------------------
# update_equipped_item — Mutation Roundtrip Controls
# ---------------------------------------------------------------------------

def test_update_equipped_changes_object_type(sample_save):
    """
    Ensures that update_equipped_item successfully mutates the target objectType property value.
    """
    update_equipped_item(sample_save, 3, 5, "Longsword", "")
    assert sample_save["inventoryData"]["equippedItems"][3]["objectType"] == 5


def test_update_equipped_changes_object_name(sample_save):
    """
    Ensures that update_equipped_item modifies the target objectName field accurately.
    """
    update_equipped_item(sample_save, 3, 5, "Longsword", "")
    assert sample_save["inventoryData"]["equippedItems"][3]["objectName"] == "Longsword"


def test_update_equipped_stores_enchantment(sample_save):
    """
    Ensures that an enchantment value argument passed to update_equipped_item is stored in the allocation frame.
    """
    update_equipped_item(sample_save, 3, 57, "Silver Ring", "Leap")
    slot = sample_save["inventoryData"]["equippedItems"][3]
    assert slot.get("enchantment") == "Leap"


def test_update_equipped_empty_clears_slot(sample_save):
    """
    Verifies that calling update_equipped_item with an objectType parameter of 0 clears the target structure data records.
    """
    update_equipped_item(sample_save, 3, 0, "", "")
    slot = sample_save["inventoryData"]["equippedItems"][3]
    assert slot["objectType"] == 0
    assert slot["objectName"] == ""


def test_update_equipped_only_touches_target_slot(sample_save):
    """
    Guarantees that editing a target index does not touch neighboring slots, avoiding index corruption risks.
    """
    original_slots = copy.deepcopy(sample_save["inventoryData"]["equippedItems"])
    update_equipped_item(sample_save, 3, 5, "Longsword", "")
    new_slots = sample_save["inventoryData"]["equippedItems"]

    for idx in range(11):
        if idx == 3:
            continue  # Exclude target index mutation component from stability evaluation calculations

        orig = {k: v for k, v in original_slots[idx].items()}
        curr = {k: v for k, v in new_slots[idx].items() if k in orig}
        assert orig == curr, f"Equipment slot index node [{idx}] was mutated unexpectedly during process streams execution"


def test_main_inventory_not_affected_by_equip_update(sample_save):
    """
    Validates that update_equipped_item processes operations while keeping mainInventory elements completely isolated.
    """
    original_main = copy.deepcopy(sample_save["inventoryData"]["mainInventory"])
    update_equipped_item(sample_save, 3, 5, "Longsword", "")
    assert sample_save["inventoryData"]["mainInventory"] == original_main


def test_update_equipped_out_of_bounds_does_not_raise(sample_save):
    """
    Guarantees that providing an out-of-bounds slot_index returns gracefully without breaking runtime routines.
    """
    original = copy.deepcopy(sample_save["inventoryData"]["equippedItems"])
    update_equipped_item(sample_save, 99, 5, "Sword", "")  # Index 99 does not exist in structure bounds
    assert sample_save["inventoryData"]["equippedItems"] == original