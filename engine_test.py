import logging
from src.core.save_manager import load_save, save_game_data
from src.core.character import get_character_summary, update_character

logger = logging.getLogger("engine_test")

def run_manual_test():
    target_slot = 0  # Feel free to change to test slot 0 through 9
    logger.info(f"=== STARTING RUNTIME TEST (Slot {target_slot}) ===")
    
    try:
        # 1. Attempting to decompress and load the slot
        logger.info(r"[*] Loading file from AppData\LocalLow...")
        raw_data = load_save(target_slot)
        p_data = raw_data['playerData']

        logger.info("--- AVAILABLE KEYS IN PLAYER DATA ---")
        for key in p_data.keys():
            # Se a chave parecer relacionada a inventário ou itens, vamos dar um destaque
            if any(word in key.lower() for word in ["item", "inv", "equip", "slot", "wear", "hand"]):
                logger.info(f"[FOUND ITEM KEY] -> {key}: {p_data[key]}")
            else:
                logger.debug(f"Standard Key: {key}")
        # 2. Extracting character details using our engine
        summary = get_character_summary(raw_data)
        logger.info("[+] Save file loaded successfully!")
        logger.info(f"    Avatar Name:  {summary['attributes']['playerName']}")
        logger.info(f"    Class:        {summary['attributes']['playerClass']}")
        logger.info(f"    Current HP:   {summary['attributes']['hp']} / Max: {summary['attributes']['vitality']}")
        logger.info(f"    Sword Skill:  {summary['skills'].get('Sword', 0)}")
        
        # 3. Simulating safe data modifications
        logger.info("\n[*] Simulating data injection from GUI variables...")
        mock_new_attributes = {"hp": 999, "vitality": 999, "strength": 100}
        mock_new_skills = {"Sword": 30, "Casting": 30}
        
        update_character(raw_data, mock_new_attributes, mock_new_skills)
        logger.info("[+] Local data updated successfully inside the Python dictionary.")
        
        # 4. Optional: Write back to disk (Commented out by default to safeguard your real saves)
        # logger.info("[*] Packing and compressing back to .json.gz...")
        # save_game_data(target_slot, raw_data)
        # logger.info("[+] File written successfully. Run the game to test changes!")
        logger.info("\n[SUCCESS] Core engine test finished with no runtime errors.")

    except FileNotFoundError:
        logger.error(f"\n[ERROR] Slot {target_slot} was not found. Please create a character in this slot inside the game first.")
    except Exception as e:
        logger.exception(f"\n[FATAL ERROR] An unexpected exception occurred: {e}")

if __name__ == "__main__":
    run_manual_test()