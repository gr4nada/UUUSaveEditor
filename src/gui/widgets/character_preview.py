# src/gui/widgets/character_preview.py
"""
CharacterPreviewWidget — painel lateral permanente.

Layout (top → bottom):
  Portrait (120×120)
  ─────────────────
  Name
  Class
  Level N  ·  Dungeon N
  ─────────────────
  Paper Doll (180×300)

portrait_id 0-4 → corpo masculino; 5-9 → corpo feminino (mapeamento 1:1).
"""
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import logging

logger = logging.getLogger("gui.widgets.character_preview")

_ASSETS       = "assets"
_PORTRAIT_SZ  = (120, 120)
_DOLL_W       = 180
_DOLL_H       = 300

from src.gui.constants import OFFSETS_FEMALE, OFFSETS_MALE, ITEM_ID_TO_PART_TYPE, ITEM_ID_TO_SPRITE_BASE 

def _strip_white(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    img.putdata([
        (0, 0, 0, 0) if p[0] >= 240 and p[1] >= 240 and p[2] >= 240 else p
        for p in img.getdata()
    ])
    return img


class CharacterPreviewWidget(ttk.LabelFrame):
    """
    Painel lateral fixo.

    API pública:
        update(portrait_id, equipped_slots, name, class_name, level, dungeon_level)
        clear()
    """

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, text=" Character ", padding=6, **kwargs)
        self._photos: list[ImageTk.PhotoImage] = []
        self._build()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def update(
        self,
        portrait_id:    int  = 0,
        equipped_slots: dict | None = None,
        name:           str  = "",
        class_name:     str  = "",
        level:          int  = 0,
        dungeon_level:  int  = 0,
    ) -> None:
        self._photos.clear()
        pid    = max(0, min(portrait_id, 9))
        female = pid >= 5

        self._render_portrait(pid)
        self._update_identity(name, class_name, level, dungeon_level)
        self._render_doll(pid, female, equipped_slots or {})

    def clear(self) -> None:
        self._photos.clear()
        self._portrait_canvas.delete("all")
        self._doll_canvas.delete("all")
        self._placeholder(self._portrait_canvas, _PORTRAIT_SZ)
        self._placeholder(self._doll_canvas, (_DOLL_W, _DOLL_H))
        self._name_var.set("—")
        self._class_var.set("—")
        self._level_var.set("—")

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # Portrait canvas
        self._portrait_canvas = tk.Canvas(
            self, width=_PORTRAIT_SZ[0], height=_PORTRAIT_SZ[1],
            bg="#111", highlightthickness=1, highlightbackground="#2a2a2a")
        self._portrait_canvas.pack(pady=(2, 6))

        # Bloco de identidade
        id_frame = ttk.Frame(self)
        id_frame.pack(fill="x", padx=4, pady=(0, 6))

        self._name_var  = tk.StringVar(value="—")
        self._class_var = tk.StringVar(value="—")
        self._level_var = tk.StringVar(value="—")

        ttk.Label(id_frame, textvariable=self._name_var,
                  font=("Arial", 9, "bold"), foreground="#ffffff",
                  anchor="center").pack(fill="x")
        ttk.Label(id_frame, textvariable=self._class_var,
                  font=("Arial", 8), foreground="#aaaaff",
                  anchor="center").pack(fill="x")
        ttk.Label(id_frame, textvariable=self._level_var,
                  font=("Arial", 8), foreground="#888",
                  anchor="center").pack(fill="x")

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=4, pady=4)

        # Paper doll canvas
        self._doll_canvas = tk.Canvas(
            self, width=_DOLL_W, height=_DOLL_H,
            bg="#0d0d0d", highlightthickness=1, highlightbackground="#2a2a2a")
        self._doll_canvas.pack(pady=(0, 4))

        self.clear()

    # ------------------------------------------------------------------
    # Identidade
    # ------------------------------------------------------------------

    def _update_identity(self, name: str, class_name: str,
                          level: int, dungeon_level: int) -> None:
        self._name_var.set(name or "—")
        self._class_var.set(class_name or "—")
        level_str = f"Level {level}"
        if dungeon_level:
            level_str += f"  ·  Dungeon {dungeon_level}"
        self._level_var.set(level_str)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def _render_portrait(self, pid: int) -> None:
        path = os.path.join(_ASSETS, "Portrait", f"{pid}.png")
        self._portrait_canvas.delete("all")
        try:
            img   = Image.open(path).convert("RGBA")
            img   = img.resize(_PORTRAIT_SZ, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._photos.append(photo)
            self._portrait_canvas.create_image(
                _PORTRAIT_SZ[0] // 2, _PORTRAIT_SZ[1] // 2,
                image=photo, anchor="center")
        except Exception as e:
            logger.warning("Portrait %d: %s", pid, e)
            self._placeholder(self._portrait_canvas, _PORTRAIT_SZ, f"#{pid}")

    def _render_doll(self, pid: int, female: bool, equipped: dict) -> None:
        self._doll_canvas.delete("all")
        # Body base
        body_path = os.path.join(_ASSETS, "Bodies", f"{pid}.png")
        try:
            body  = _strip_white(Image.open(body_path))
            scale = min(_DOLL_W / body.width, (_DOLL_H - 30) / body.height)
            body  = body.resize((int(body.width * scale), int(body.height * scale)),
                                 Image.Resampling.NEAREST)
            bx    = (_DOLL_W - body.width) // 2
            by    = (_DOLL_H - body.height) // 2
            photo = ImageTk.PhotoImage(body)
            self._photos.append(photo)
            self._doll_canvas.create_image(bx, by, image=photo, anchor="nw")
        except Exception as e:
            logger.warning("Body %d: %s", pid, e)
        # 2. Armour layers (Renderização com ordem de camadas fixa)
        armour_dir = "Armour_f" if female else "Armour_m"
        offsets_table = OFFSETS_FEMALE if female else OFFSETS_MALE

        # Definimos a ordem cirúrgica das camadas: Botas -> Pernas -> Peito -> Luvas -> Elmo
        # Cada número corresponde ao ID do SLOT do inventário
        ORDERED_ARMOUR_SLOTS = [8, 10, 4, 6, 1]

        for slot_idx in ORDERED_ARMOUR_SLOTS:
            slot_data = equipped.get(slot_idx)
            if not slot_data:
                continue
                
            item_id = slot_data.get("objectType", 0)
            
            if item_id not in ITEM_ID_TO_SPRITE_BASE:
                continue

            base_index = ITEM_ID_TO_SPRITE_BASE[item_id]
            qc = max(0, min(slot_data.get("qualityClass", 0), 3))
            
            if qc == 0:
                sprite_idx = "_damaged"
            elif qc == 1:
                sprite_idx = "_worn"
            elif qc == 2:
                sprite_idx = "_servicable"
            elif qc == 3:
                sprite_idx = "_excellent"
            else:
                sprite_idx = ""

            spath = os.path.join(_ASSETS, armour_dir, f"{item_id}{sprite_idx}.png")
            
            try:
                if not os.path.exists(spath):
                    continue
                    
                spr = _strip_white(Image.open(spath))

                current_scale = 1.1
                bx, by = 0, 0
                # Modificador de ajuste fino caso precise dar um tapa no tamanho geral
                ARMOUR_SIZE_MODIFIER = 3.6
                armour_scale = current_scale * ARMOUR_SIZE_MODIFIER
                
                nw = max(1, int(spr.width  * armour_scale))
                nh = max(1, int(spr.height * armour_scale))
                spr = spr.resize((nw, nh), Image.Resampling.NEAREST)
                
                photo = ImageTk.PhotoImage(spr)
                self._photos.append(photo)
                
                part_type = ITEM_ID_TO_PART_TYPE[item_id]
                ox, oy = offsets_table[part_type]
                
                ox_final = bx + int(ox * current_scale)
                oy_final = by + int(oy * current_scale)
                
                self._doll_canvas.create_image(ox_final, oy_final, image=photo, anchor="nw")
                
            except Exception as e:
                logger.debug("Armour slot=%d item_id=%d: %s", slot_idx, item_id, e)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _placeholder(canvas: tk.Canvas, size: tuple, label: str = "") -> None:
        w, h = size
        canvas.create_rectangle(1, 1, w-1, h-1, outline="#1e1e1e", fill="#0a0a0a")
        if label:
            canvas.create_text(w//2, h//2, text=label, fill="#2a2a2a", font=("Arial", 9))