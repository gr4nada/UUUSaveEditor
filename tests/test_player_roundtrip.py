# tests/test_player_roundtrip.py

def test_player_fields_exist(sample_save):
    """Protects active entity parameters from structural schema erasure hazards."""
    p = sample_save["playerData"]

    required = [
        "playerName",
        "playerClass",
        "hp",
        "mana",
        "maxMana",
        "strength",
        "dexterity",
        "intellect",
        "skill",
        "questFlags",
        "xp"  # CHANGED: Asserts correct field key parameter mappings
    ]

    for field in required:
        assert field in p, f"Authoritative tracking property key field missing: {field}"

# tests/test_player_roundtrip.py

def test_player_fields_exist_and_types(sample_save):
    """Garante que as propriedades do jogador existem e mantêm consistência de tipos primitivos."""
    assert "playerData" in sample_save, "Bloco playerData não encontrado no save!"
    p = sample_save["playerData"]

    # Mapeamento de chaves conhecidas vs tipos esperados com base no ficheiro real
    expected_fields = {
        "playerName": str,      # Valor real: "TEST_AVATAR"
        "female": bool,         # Valor real: False
        "leftHanded": bool,     # Valor real: False
        "hp": int,              # Valor real: 82
        "vitality": int,        # Valor real: 82
        "mana": int,            # Valor real: 39
        "maxMana": int,         # Valor real: 39
        "xp": int,              # Valor real: 100114 (Confirmado 'xp' e não 'exp')
        "charLevel": int,       # Valor real: 14
        "skillPoints": int,     # Valor real: 1
        "skill": list,          # Array de habilidades
        "questFlags": list,     # Array de flags de progresso
    }

    for field, expected_type in expected_fields.items():
        assert field in p, f"Campo obrigatório ausente no playerData: {field}"
        assert isinstance(p[field], expected_type), f"Tipo incorreto para o campo {field}. Esperado {expected_type}."

def test_player_position_structure(sample_save):
    """Garante a precisão vetorial das coordenadas espaciais de posição do jogador."""
    position = sample_save["playerData"]["position"]
    for coordinate in ["x", "y", "z"]:
        assert coordinate in position
        assert isinstance(position[coordinate], float)