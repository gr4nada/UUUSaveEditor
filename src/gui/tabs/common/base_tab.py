"""
Base Tab Module

Provides a common foundation for all tabs in the Ultima Underworld Save Editor.
Encourages consistency, reduces boilerplate, and centralizes common patterns.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional, Callable
from abc import ABC, abstractmethod

from src.gui.constants import THEME


class BaseTab(ttk.Frame, ABC):
    """
    Abstract base class for all tabs in the application.
    
    Benefits:
        - Consistent initialization and styling
        - Common lifecycle methods (load, save, refresh)
        - Easy access to theme and common utilities
        - Support for change tracking and callbacks
    """

    def __init__(self, parent: ttk.Notebook, title: str = "Tab"):
        super().__init__(parent, padding=6, style="TFrame")
        
        self._title = title
        self._parent_notebook = parent
        self._has_unsaved_changes = False
        self._on_change_callbacks: list[Callable] = []
        
        # Common references
        self._save_game = None
        
        self._build_ui()
        self._setup_tracing()

    # ------------------------------------------------------------------
    # Abstract Methods (must be implemented by subclasses)
    # ------------------------------------------------------------------

    @abstractmethod
    def _build_ui(self) -> None:
        """Build the tab's user interface. Must be overridden."""
        pass

    @abstractmethod
    def load(self, save_game: Any) -> None:
        """Load data from save_game into the UI."""
        self._save_game = save_game

    # ------------------------------------------------------------------
    # Public API (available to all tabs)
    # ------------------------------------------------------------------

    def get_title(self) -> str:
        """Return the tab title."""
        return self._title

    def mark_as_changed(self) -> None:
        """Mark this tab as having unsaved changes."""
        self._has_unsaved_changes = True
        self._notify_change()

    def clear_changes(self) -> None:
        """Clear the unsaved changes flag."""
        self._has_unsaved_changes = False

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self._has_unsaved_changes

    def on_change(self, callback: Callable[[], None]) -> None:
        """Register a callback to be called when content changes."""
        if callback not in self._on_change_callbacks:
            self._on_change_callbacks.append(callback)

    def refresh(self) -> None:
        """Refresh the tab content (default: reload current save)."""
        if self._save_game:
            self.load(self._save_game)

    # ------------------------------------------------------------------
    # Protected Helpers
    # ------------------------------------------------------------------

    def _setup_tracing(self) -> None:
        """Override in subclass if you want automatic change detection."""
        pass

    def _notify_change(self) -> None:
        """Notify all registered callbacks."""
        for callback in self._on_change_callbacks:
            try:
                callback()
            except Exception:
                # Don't let one bad callback break everything
                pass

    def _make_label(self, parent, text: str, **kwargs) -> ttk.Label:
        """Helper to create consistently styled labels."""
        default = {"foreground": THEME.get("fg_muted", "gray")}
        default.update(kwargs)
        return ttk.Label(parent, text=text, **default)

    def _make_entry(self, parent, var: tk.StringVar | None = None, width: int = 12, **kwargs) -> ttk.Entry:
        """Helper to create consistently styled entries."""
        entry = ttk.Entry(parent, textvariable=var, width=width, **kwargs)
        return entry

    def _make_spinbox(self, parent, var: tk.StringVar | None = None, 
                     from_: int = 0, to: int = 100, width: int = 8, **kwargs) -> ttk.Spinbox:
        """Helper to create Spinbox with common settings."""
        return ttk.Spinbox(parent, textvariable=var, from_=from_, to=to, width=width, **kwargs)

    def _make_separator(self, parent, orient=tk.HORIZONTAL) -> ttk.Separator:
        """Create a styled separator."""
        return ttk.Separator(parent, orient=orient)

    # ------------------------------------------------------------------
    # Optional overrides
    # ------------------------------------------------------------------

    def get_data(self) -> Dict[str, Any]:
        """
        Return the data edited in this tab.
        Override in subclasses that need to export data.
        """
        return {}

    def apply_changes(self) -> bool:
        """
        Apply pending changes to the save_game.
        Return True if successful.
        """
        return True

    def on_tab_selected(self) -> None:
        """Called when this tab becomes visible."""
        pass

    def on_tab_hidden(self) -> None:
        """Called when another tab is selected."""
        pass