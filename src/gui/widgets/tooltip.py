# src/gui/widgets/tooltip.py
"""
Tooltip — widget de dica flutuante para Tkinter.

Uso:
    from src.gui.widgets.tooltip import Tooltip

    btn = ttk.Button(parent, text="Save")
    Tooltip(btn, "Save changes to disk  (Ctrl+S)")

    # Texto dinâmico — passa callable:
    Tooltip(lbl, lambda: f"Item: {item['name']}")

Comportamento:
  - Aparece após DELAY ms de hover (padrão 500ms)
  - Desaparece ao mover o mouse para fora do widget
  - Segue o mouse horizontalmente, posição fixa vertical (abaixo do widget)
  - Destrói e recria a janela a cada exibição — sem estado residual
  - Seguro para usar em múltiplos widgets ao mesmo tempo
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable

_DELAY_MS   = 500     # tempo de hover antes de aparecer
_PAD_X      = 8       # padding horizontal interno
_PAD_Y      = 4       # padding vertical interno
_OFFSET_Y   = 20      # distância vertical abaixo do ponteiro


class Tooltip:
    """
    Associa um tooltip a qualquer widget Tkinter.

    Parâmetros
    ----------
    widget   Widget ao qual o tooltip é anexado
    text     String fixa  OU  callable sem argumentos que retorna string.
             Callable é avaliado no momento da exibição — útil para
             conteúdo que muda (ex: nome do item em slots dinâmicos).
    delay    Milissegundos de hover antes de aparecer (padrão: 500)
    """

    def __init__(
        self,
        widget: tk.Widget,
        text: str | Callable[[], str],
        delay: int = _DELAY_MS,
    ) -> None:
        self._widget  = widget
        self._text    = text
        self._delay   = delay
        self._tip_win: tk.Toplevel | None = None
        self._after_id: str | None        = None

        widget.bind("<Enter>",  self._on_enter,  add="+")
        widget.bind("<Leave>",  self._on_leave,  add="+")
        widget.bind("<Button>", self._on_leave,  add="+")   # click cancela

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def update_text(self, text: str | Callable[[], str]) -> None:
        """Atualiza o texto sem recriar o Tooltip."""
        self._text = text

    def destroy(self) -> None:
        """Remove o tooltip e desanexa os bindings."""
        self._cancel()
        self._hide()

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_enter(self, _event: tk.Event) -> None:
        self._cancel()
        self._after_id = self._widget.after(self._delay, self._show)

    def _on_leave(self, _event: tk.Event) -> None:
        self._cancel()
        self._hide()

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------

    def _show(self) -> None:
        if self._tip_win:
            return

        text = self._text() if callable(self._text) else self._text
        if not text:
            return

        # Posição: logo abaixo do ponteiro, dentro dos limites da tela
        try:
            x = self._widget.winfo_pointerx() + 12
            y = self._widget.winfo_pointery() + _OFFSET_Y
        except Exception:
            return

        self._tip_win = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)   # sem decoração de janela
        tw.wm_attributes("-topmost", True)
        tw.wm_geometry(f"+{x}+{y}")

        # Fundo e borda manuais (sem ttk para garantir aparência consistente)
        frame = tk.Frame(tw, bg="#1e1e2e", bd=1, relief="solid",
                         highlightbackground="#555", highlightthickness=1)
        frame.pack()

        tk.Label(
            frame,
            text=text,
            bg="#1e1e2e",
            fg="#e0e0e0",
            font=("Segoe UI", 9) if _system_is_windows() else ("Arial", 9),
            justify="left",
            padx=_PAD_X,
            pady=_PAD_Y,
            wraplength=340,
        ).pack()

    def _hide(self) -> None:
        if self._tip_win:
            try:
                self._tip_win.destroy()
            except Exception:
                pass
            self._tip_win = None

    def _cancel(self) -> None:
        if self._after_id:
            try:
                self._widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None


def _system_is_windows() -> bool:
    import sys
    return sys.platform.startswith("win")


# ---------------------------------------------------------------------------
# Conveniência: decorator para adicionar tooltip a qualquer widget
# ---------------------------------------------------------------------------

def attach(widget: tk.Widget, text: str | Callable[[], str],
           delay: int = _DELAY_MS) -> Tooltip:
    """
    Atalho funcional para criar um Tooltip e retorná-lo.

    Uso:
        tip = attach(my_button, "Clique para salvar")
    """
    return Tooltip(widget, text, delay)
