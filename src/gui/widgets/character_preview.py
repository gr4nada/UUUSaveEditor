# src/gui/widgets/character_preview.py
"""
CharacterPreviewWidget — painel lateral permanente (direita).

Portrait + Paper Doll composto (body base + armour layers).

Regras de portrait/body:
  portrait 0-4  → masculino → Bodies/000-004.png
  portrait 5-9  → feminino  → Bodies/005-009.png
  body_index = portrait_id  (1:1 mapping)

Assim trocar portrait troca body automaticamente — sem seleção manual de body.

Estrutura dos 64 sprites de armour (stride=16 por qualityClass):
  quality 0 (pristine) → sprites 0-15
  quality 1 (worn)     → sprites 16-31
  quality 2 (damaged)  → sprites 32-47
  quality 3 (broken)   → sprites 48-63
  Dentro de cada bloco de 16:
    [0-2]  Chest (33×44)
    [3-5]  Legs  (19×51)
    [6-8]  Boots (33×15)
    [9-11] Gloves (21×14)
    [12-14] Helmet (20×20)
    [15]   spare
"""

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import logging

logger = logging.getLogger("gui.widgets.character_preview")

_ASSETS = "assets"

# Canvas dimensions — painel generoso conforme redesign
_PORTRAIT_SIZE = (120, 120)
_DOLL_W, _DOLL_H = 180, 300

_SLOT_TO_ARMOUR_PART = {
    4:  0,   # Chest
    8:  1,   # Legs
    10: 2,   # Boots
    6:  3,   # Gloves
    1:  4,   # Helmet
}

# Offsets recalculados para o canvas maior (180×300)
_PART_OFFSETS = {
    0: (70,  82),    # Chest
    1: (78, 148),    # Legs
    2: (68, 228),    # Boots
    3: (38, 124),    # Gloves
    4: (70,  14),    # Helmet
}

# Escala de ampliação dos sprites de armour
_ARMOUR_SCALE = 2.4


def _remove_white(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    cleaned = [
        (0, 0, 0, 0) if (p[0] >= 240 and p[1] >= 240 and p[2] >= 240) else p
        for p in img.getdata()
    ]
    img.putdata(cleaned)
    return img


class CharacterPreviewWidget(ttk.LabelFrame):
    """
    Painel lateral fixo com portrait e paper doll.

    Uso:
        preview = CharacterPreviewWidget(parent)
        preview.pack(fill="both", expand=True)

        preview.update(
            portrait_id=2,
            equipped_slots={4: {'qualityClass':2,'objectType':34}, ...}
        )
    """

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, text=" Character ", padding=6, **kwargs)
        # Todas as referências de foto — crítico para evitar GC do Tkinter
        self._photos: list[ImageTk.PhotoImage] = []
        self._build()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def update(
        self,
        portrait_id: int = 0,
        equipped_slots: dict | None = None,
    ) -> None:
        """
        Atualiza portrait e paper doll.

        portrait_id determina tanto a imagem de portrait quanto o body:
          0-4 → masculino (Bodies/000-004)
          5-9 → feminino  (Bodies/005-009)

        equipped_slots: {slot_index: {'objectType': int, 'qualityClass': int}}
        """
        self._photos.clear()
        pid = max(0, min(portrait_id, 9))
        female = pid >= 5

        self._render_portrait(pid)
        self._render_doll(pid, female, equipped_slots or {})

    def clear(self) -> None:
        self._photos.clear()
        self._portrait_canvas.delete("all")
        self._doll_canvas.delete("all")
        self._placeholder(self._portrait_canvas, _PORTRAIT_SIZE)
        self._placeholder(self._doll_canvas, (_DOLL_W, _DOLL_H))

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # Portrait
        ttk.Label(self, text="Portrait", font=("Arial", 8, "bold"),
                  foreground="#888").pack(pady=(2, 2))

        self._portrait_canvas = tk.Canvas(
            self,
            width=_PORTRAIT_SIZE[0], height=_PORTRAIT_SIZE[1],
            bg="#111", highlightthickness=1, highlightbackground="#2a2a2a",
        )
        self._portrait_canvas.pack(pady=(0, 8))

        # Paper doll
        ttk.Label(self, text="Paper Doll", font=("Arial", 8, "bold"),
                  foreground="#888").pack(pady=(0, 2))

        self._doll_canvas = tk.Canvas(
            self,
            width=_DOLL_W, height=_DOLL_H,
            bg="#0d0d0d", highlightthickness=1, highlightbackground="#2a2a2a",
        )
        self._doll_canvas.pack()

        self.clear()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render_portrait(self, portrait_id: int) -> None:
        path = os.path.join(_ASSETS, "Portrait", f"{portrait_id:03d}.png")
        self._portrait_canvas.delete("all")
        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize(_PORTRAIT_SIZE, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._photos.append(photo)
            cx, cy = _PORTRAIT_SIZE[0] // 2, _PORTRAIT_SIZE[1] // 2
            self._portrait_canvas.create_image(cx, cy, image=photo, anchor="center")
        except Exception as e:
            logger.warning("Portrait %d: %s", portrait_id, e)
            self._placeholder(self._portrait_canvas, _PORTRAIT_SIZE, f"#{portrait_id}")

    def _render_doll(self, portrait_id: int, female: bool, equipped_slots: dict) -> None:
        self._doll_canvas.delete("all")

        # 1. Body base — índice = portrait_id (mapeamento 1:1)
        body_path = os.path.join(_ASSETS, "Bodies", f"{portrait_id:03d}.png")
        try:
            body = _remove_white(Image.open(body_path))
            scale = min(_DOLL_W / body.width, (_DOLL_H - 30) / body.height)
            bw = int(body.width  * scale)
            bh = int(body.height * scale)
            body = body.resize((bw, bh), Image.Resampling.NEAREST)
            bx = (_DOLL_W - bw) // 2
            by = (_DOLL_H - bh) // 2
            photo = ImageTk.PhotoImage(body)
            self._photos.append(photo)
            self._doll_canvas.create_image(bx, by, image=photo, anchor="nw")
        except Exception as e:
            logger.warning("Body %d: %s", portrait_id, e)

        # 2. Armour layers
        armour_dir = "Armour_f" if female else "Armour_m"
        for slot_idx, part_idx in _SLOT_TO_ARMOUR_PART.items():
            slot_data = equipped_slots.get(slot_idx, {})
            if slot_data.get("objectType", 0) == 0:
                continue

            qc = max(0, min(slot_data.get("qualityClass", 0), 3))
            sprite_idx = qc * 16 + part_idx * 3
            spath = os.path.join(_ASSETS, armour_dir, f"sprite_{sprite_idx:03d}.png")
            try:
                spr = _remove_white(Image.open(spath))
                nw = max(1, int(spr.width  * _ARMOUR_SCALE))
                nh = max(1, int(spr.height * _ARMOUR_SCALE))
                spr = spr.resize((nw, nh), Image.Resampling.NEAREST)
                photo = ImageTk.PhotoImage(spr)
                self._photos.append(photo)
                ox, oy = _PART_OFFSETS[part_idx]
                self._doll_canvas.create_image(ox, oy, image=photo, anchor="nw")
            except Exception as e:
                logger.debug("Armour slot=%d part=%d: %s", slot_idx, part_idx, e)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _placeholder(canvas: tk.Canvas, size: tuple, label: str = "") -> None:
        w, h = size
        canvas.create_rectangle(1, 1, w - 1, h - 1, outline="#1e1e1e", fill="#0a0a0a")
        if label:
            canvas.create_text(w // 2, h // 2, text=label, fill="#2a2a2a",
                                font=("Arial", 9))
