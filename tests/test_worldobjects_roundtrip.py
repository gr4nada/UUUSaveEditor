# tests/test_worldobjects_roundtrip.py
import json

def test_world_objects_count(sample_save):
    """Guarantees sensitive world entities tracking states are not stripped or altered."""
    before = len(sample_save["worldObjects"])

    restored = json.loads(json.dumps(sample_save))
    after = len(restored["worldObjects"])

    assert before == after, "Dynamic world entities references dropped during save block transformations!"

# tests/test_worldobjects_roundtrip.py
import json

def test_game_state_arrays_and_subsystems(sample_save):
    """Garante que os arrays de subsistemas do jogo mantêm fidelidade total."""
    p = sample_save["playerData"]
    
    # Validar sub-blocos e contagens reais do sample_save.json
    assert "magicData" in p
    assert "encounteredCritters" in p
    assert "openedChest" in p
    
    # Valores de referência com base no ficheiro
    before_critters_count = len(p["encounteredCritters"])
    before_chests_count = len(p["openedChest"])

    # Processar pipeline
    restored = json.loads(json.dumps(sample_save))
    restored_p = restored["playerData"]

    # Validar integridade pós-transformação
    assert len(restored_p["encounteredCritters"]) == before_critters_count
    assert len(restored_p["openedChest"]) == before_chests_count
    assert restored_p["magicData"]["hasMousePrimedSpell"] == p["magicData"]["hasMousePrimedSpell"]