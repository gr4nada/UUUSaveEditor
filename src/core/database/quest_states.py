# src/core/database/quest_states.py
"""
Quest Intelligence (Sprint 13) — narrative states for quest flags.

Today QuestFlags[i] is treated as bool (0/1) by GUI, but the underlying
array already stores integers (`questFlags: list[int]`). Multiple quest flags
actually encode multi-step progression within the same integer — this table
documents, flag by flag, the meaning of each observable integer value, based
on reverse engineering of conversation scripts (.cnv) and community research
on Ultima Underworld 2.

Format:
    QUEST_STATES: dict[str, dict[int, dict]] = {
        "<flag_name>": {
            <int_value>: {"label": "<short name>", "desc": "<description>"},
            ...
        },
        ...
    }

Flags missing from this mapping are treated as simple binary (0 = Inactive / 1+ = Active)
by the `describe_state()` function below — it is not necessary to list all
QUEST_FLAGS here, only those with 3+ narrative progression states are worth
documenting.

The UI (skills_quests_tab) uses `quest_state_options(flag_name)` to populate
the state selector and `describe_state(flag_name, value)` for the "State Description"
column of the Treeview.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Narrative states by flag
#
# Only flags with 3+ step progression need an entry here.
# Binary flags (MetDrOwl, GazerKilled, RodrickKilled, CanSpeakToKetcheval,
# BefriendedLizardmen, ShouldFindTalismans, ConvoWithMurgo) use the generic
# fallback of describe_state() and don't need an entry.
# ---------------------------------------------------------------------------

QUEST_STATES: dict[str, dict[int, dict]] = {

    # --- MurgoFreed — complete Murgo arc, from captivity to reward ---
    "MurgoFreed": {
        0: {"label": "Imprisoned",
            "desc": "Murgo is still imprisoned in the Dwarf cells on Level 2; "
                    "the Avatar has not reached him yet."},
        1: {"label": "Freed",
            "desc": "Murgo was freed from the cells. He now roams free "
                    "on Level 2 and can be found for additional conversations."},
        2: {"label": "Reward Delivered",
            "desc": "Murgo rewarded the Avatar (item or information) after "
                    "liberation — closes his personal arc."},
    },

    # --- TalkedToHagbard — introduction to human refugees ---
    "TalkedToHagbard": {
        0: {"label": "Not Found",
            "desc": "The Avatar has not yet located Hagbard among the human "
                    "refugees on Level 3."},
        1: {"label": "Introduction Made",
            "desc": "Hagbard introduced himself and explained the refugees' "
                    "situation, opening the faction quests."},
        2: {"label": "Trust Established",
            "desc": "Hagbard began to trust the Avatar and reveals additional "
                    "information about Tyball's plans."},
    },

    # --- FindGurstang — search for missing dwarf ---
    "FindGurstang": {
        0: {"label": "Search Not Started",
            "desc": "The Avatar has not yet received the mission to search for Gurstang."},
        1: {"label": "Search Active",
            "desc": "The Avatar was tasked with finding the missing dwarf "
                    "Gurstang and is searching for him on Level 2."},
        2: {"label": "Gurstang Found (Alive)",
            "desc": "Gurstang was found alive; his status can be "
                    "reported back to whoever requested the search."},
        3: {"label": "Gurstang Found (Dead)",
            "desc": "Only Gurstang's body or belongings were found — "
                    "the search ended in tragedy."},
    },

    # --- WhereIsZak — locate the blind merchant ---
    "WhereIsZak": {
        0: {"label": "Unknown",
            "desc": "The whereabouts of Zak, the blind merchant, have not yet "
                    "been asked or discovered."},
        1: {"label": "Clue Obtained",
            "desc": "The Avatar obtained a clue about where Zak might be, "
                    "but has not found him in person yet."},
        2: {"label": "Zak Located",
            "desc": "Zak was found in person by the Avatar on Level 2."},
    },

    # --- BronusBookGoBoom — sabotage of Bronus's book ---
    "BronusBookGoBoom": {
        0: {"label": "Not Started",
            "desc": "The Avatar has not yet received the trapped book or "
                    "delivery mission for Bronus."},
        1: {"label": "Book in Avatar's Possession",
            "desc": "The Avatar is carrying the book intended for Bronus, "
                    "but has not yet delivered it."},
        2: {"label": "Delivered / Detonated",
            "desc": "The book was delivered to Bronus and the sabotage event "
                    "(explosion) was triggered, completing the quest."},
    },

    # --- KnightOfCrux — Order of the Crux Gamata ceremony ---
    "KnightOfCrux": {
        0: {"label": "Not a Member",
            "desc": "The Avatar has not yet been invited or initiated into "
                    "the Order of the Crux Gamata on Level 5."},
        1: {"label": "Trials in Progress",
            "desc": "The Avatar was accepted as a candidate and is fulfilling "
                    "the trials required by the Order."},
        2: {"label": "Knight of the Crux Gamata",
            "desc": "The Avatar completed the ceremony and was made a Knight "
                    "of the Order, gaining recognition and possibly "
                    "access to restricted areas of Level 5."},
    },

    # --- TalismansLeft — narrative progress marker for Grand Quest ---
    # Note: Do NOT confuse with playerData.talismansCollected /
    # talismansDestroyed (Sprint 10, Story tab) — this flag is a *narrative*
    # marker (which dialogues/events have triggered because of progress),
    # not the actual numerical counter of talismans.
    "TalismansLeft": {
        0: {"label": "Quest Not Started",
            "desc": "The Grand Quest of the 8 Talismans has not yet been formally "
                    "explained to the Avatar by any NPC."},
        1: {"label": "Quest Known",
            "desc": "The Avatar knows of the Grand Quest's existence, but has not "
                    "progressed enough for NPCs to comment on "
                    "progress yet."},
        2: {"label": "Progress Recognized",
            "desc": "Relevant NPCs now comment on the Avatar's progress in "
                    "collecting Talismans — mid-progress dialogue "
                    "has been unlocked."},
        3: {"label": "Nearly Complete",
            "desc": "End-phase dialogues about the Talismans have been "
                    "unlocked — most have already been recovered."},
    },

    # --- Dreams — progression of prophetic dreams from Ghost ---
    # Note: Related but distinct from playerData.dreamsRemaining[6]
    # (Sprint 10) — this flag marks *which narrative dreams* have occurred,
    # not the countdown per talisman.
    "Dreams": {
        0: {"label": "No Dream",
            "desc": "The Avatar has not yet had any prophetic vision from the "
                    "Ghost."},
        1: {"label": "First Dream",
            "desc": "The Avatar had the first vision — typically a vague "
                    "warning about the danger posed by Tyball/Cabirus."},
        2: {"label": "Recurring Dreams",
            "desc": "Additional visions have occurred, gradually revealing more "
                    "of the antagonist's plan and Talisman locations."},
        3: {"label": "Final Vision",
            "desc": "The Avatar received the culminating vision, typically "
                    "associated with the climax of the main story."},
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def quest_state_options(flag_name: str) -> dict[int, dict]:
    """
    Returns {integer_value: {"label", "desc"}} for the flag.

    If the flag does not have an entry in QUEST_STATES, returns the generic
    binary fallback {0: Inactive, 1: Active} — suitable for simple flags
    (MetDrOwl, GazerKilled, RodrickKilled, etc.).
    """
    if flag_name in QUEST_STATES:
        return QUEST_STATES[flag_name]
    return {
        0: {"label": "Inactive", "desc": "This flag has not been activated yet."},
        1: {"label": "Active",   "desc": "This flag has been activated (completed/reached)."},
    }


def describe_state(flag_name: str, value: int) -> dict:
    """
    Returns {"label", "desc"} for the current value of `flag_name`.

    Values outside the known map (e.g., an integer larger than the largest
    documented state, coming from an externally edited save) fall back to a
    descriptive message that still shows the raw value, instead of breaking the UI.
    """
    options = quest_state_options(flag_name)
    if value in options:
        return options[value]
    max_known = max(options.keys())
    return {
        "label": f"Unknown ({value})",
        "desc": f"Value {value} not documented for this flag "
                f"(known states: 0–{max_known}). This may be a valid game state "
                f"not yet mapped, or data from an externally edited save.",
    }


def max_known_state(flag_name: str) -> int:
    """Returns the highest documented state value for `flag_name`."""
    return max(quest_state_options(flag_name).keys())


def is_multi_state(flag_name: str) -> bool:
    """True if `flag_name` has 3+ documented narrative progression states."""
    return flag_name in QUEST_STATES and len(QUEST_STATES[flag_name]) > 2
