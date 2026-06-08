# Ultima Underworld Unity Port - Save Game Editor

A lightweight, modular save game editor written in Python for Kweepa's modern Unity port of the classic RPG **Ultima Underworld: The Stygian Abyss**.

This tool decompresses, parses, and modifies the game's native save structure, giving you absolute control over your character's progression, attributes, skills, and world state without needing to inject code or modify the compiled game.

## Features

*   **Native Compatibility:** Automatically targets the standard Unity persistence path (`AppData/LocalLow/Kweepa/UnityUnderground/Saves`).
*   **GZip Stream Handling:** Seamlessly decompresses `.json.gz` save slots into editable Python dictionaries and re-packs them perfectly back into the game's expected compression format.
*   **Character Stats Editor:** Safely modify character attributes (`hp`, `mana`, `strength`, `dexterity`, `intellect`, `exp`, `charLevel`).
*   **19-Skill Matrix:** Individual or batch modification of all 19 official character skills (Attack, Casting, Lore, etc.) using safe bounds to prevent save corruption.
*   **Modular Architecture:** Built using clean, decoupled *Getters* and *Setters*—perfect for running as a command-line utility or linking into a custom GUI.

## Tech Stack

*   **Language:** Python 3.x
*   **Libraries (Standard Only):** `gzip`, `json`, `os`, `enum`, `tkinter` (for the optional UI component)

## How It Works

Kweepa's Unity port modernizes *Ultima Underworld*'s original DOS binary save structures by converting live game memory into structured JSON data, which is then compressed using `GZipStream` before being written to disk. 

This repository reverse-engineers that serialization pipeline, allowing safe out-of-game data manipulation while keeping the game's internal data integrity intact.

## Roadmap & Future Enhancements

- [x] Core GZip read/write framework.
- [x] Character Attributes & Skill Matrix editor.
- [ ] NPC World State & Attitude manipulator (Faction standing fixer).
- [ ] Visual Inventory Spawner (utilizing original sprite-sheet extraction).

---
*Disclaimer: This is an independent fan-made tool intended for testing, debugging, and modding purposes. "Ultima Underworld" is a trademark of Electronic Arts.*