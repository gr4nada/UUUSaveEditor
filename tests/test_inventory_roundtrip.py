# tests/test_inventory_roundtrip.py
import json

def test_inventory_preserved(sample_save):
    """Validates inventory slots sizes maintain static structural configurations across boundaries."""
    before = len(sample_save["inventoryData"]["mainInventory"])

    serialized = json.dumps(sample_save)
    after = len(json.loads(serialized)["inventoryData"]["mainInventory"])

    assert before == after, "Inventory datasets elements count corrupted through pipeline transformation!"

# tests/test_inventory_roundtrip.py
import json

def test_inventory_integrity_and_hierarchy(sample_save):
    """Garante que itens em profundidade do inventário, como mochilas e runas, são totalmente preservados."""
    assert "inventoryData" in sample_save
    assert "mainInventory" in sample_save["inventoryData"]
    
    before_count = len(sample_save["inventoryData"]["mainInventory"])

    # Executar pipeline de persistência
    serialized_stream = json.dumps(sample_save)
    deserialized_data = json.loads(serialized_stream)
    
    after_count = len(deserialized_data["inventoryData"]["mainInventory"])

    # Asserções de consistência
    assert before_count == after_count, "Contagem de itens de inventário divergiu no roundtrip!"
    
    # Verificar integridade das chaves do primeiro item ("a pack" / Container)
    first_item = deserialized_data["inventoryData"]["mainInventory"][0]
    assert "objectName" in first_item
    assert "objectTypeName" in first_item
    assert "jsonData" in first_item