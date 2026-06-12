# src/gui/widgets/icon_loader.py
"""
IconLoader — serviço centralizado de carregamento de imagens.

Serve ícones de itens (assets/icons/{objectType}.png)
e portraits de critters (assets/WhoAmI/{whoami_id}.png).

Cache por (tipo, tamanho) evita recarregar o mesmo asset várias vezes.
Todas as imagens passam por remoção de fundo branco.

Singleton via get_instance() — todas as tabs compartilham o mesmo cache.
"""
from __future__ import annotations
import os
import logging
from PIL import Image, ImageTk

logger = logging.getLogger("gui.widgets.icon_loader")

_ICONS_DIR  = os.path.join("assets", "icons")
_WHOAMI_DIR = os.path.join("assets", "WhoAmI")

# Tamanhos canônicos usados nas diferentes views
ICON_SMALL  = (24, 24)   # Treeview de items (world objects, loot)
ICON_MEDIUM = (32, 32)   # Treeview de inventory tab
WHOAMI_SIZE = (68, 68)   # Portrait do critter no detail panel

_WHITE_THRESHOLD = 240


def _remove_white(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    data = [(0, 0, 0, 0) if p[0] >= _WHITE_THRESHOLD
            and p[1] >= _WHITE_THRESHOLD
            and p[2] >= _WHITE_THRESHOLD
            else p
            for p in img.getdata()]
    img.putdata(data)
    return img


def _fit_into(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Redimensiona mantendo proporção, centraliza em canvas transparente."""
    img.thumbnail(size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - img.width)  // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y), img)
    return canvas


class IconLoader:
    """
    Cache de ImageTk.PhotoImage.

    Uso:
        loader = IconLoader.get_instance()
        photo  = loader.get_item_icon(object_type, size=ICON_SMALL)
        photo  = loader.get_whoami_portrait(whoami_id, size=WHOAMI_SIZE)
    """

    _instance: IconLoader | None = None

    @classmethod
    def get_instance(cls) -> IconLoader:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        # (key, size) → PhotoImage
        self._cache: dict[tuple, ImageTk.PhotoImage] = {}
        self._fallback_item:   dict[tuple, ImageTk.PhotoImage] = {}
        self._fallback_whoami: dict[tuple, ImageTk.PhotoImage] = {}

    def get_item_icon(
        self,
        object_type: int,
        size: tuple[int, int] = ICON_SMALL,
    ) -> ImageTk.PhotoImage:
        """
        Retorna PhotoImage para o object_type dado.
        Tenta assets/icons/{n}.png e assets/icons/{n:03d}.png.
        Fallback: quadrado cinza escuro.
        """
        key = ("item", object_type, size)
        if key in self._cache:
            return self._cache[key]

        path = self._find_icon_path(object_type)
        if path:
            try:
                img = _remove_white(Image.open(path))
                img = _fit_into(img, size)
                photo = ImageTk.PhotoImage(img)
                self._cache[key] = photo
                return photo
            except Exception as e:
                logger.debug("icon load failed type=%d: %s", object_type, e)

        photo = self._make_fallback(size)
        self._cache[key] = photo
        return photo

    def get_whoami_portrait(
        self,
        whoami_id: int,
        size: tuple[int, int] = WHOAMI_SIZE,
    ) -> ImageTk.PhotoImage | None:
        """
        Retorna PhotoImage para o portrait do NPC/critter.
        Retorna None se não houver asset para este whoami_id.
        """
        key = ("whoami", whoami_id, size)
        if key in self._cache:
            return self._cache[key]

        path = self._find_whoami_path(whoami_id)
        if not path:
            return None

        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._cache[key] = photo
            return photo
        except Exception as e:
            logger.debug("whoami portrait load failed id=%d: %s", whoami_id, e)
            return None

    def clear(self) -> None:
        """Libera o cache. Chamar entre loads de saves diferentes."""
        self._cache.clear()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_icon_path(object_type: int) -> str | None:
        for name in (str(object_type), f"{object_type:03d}"):
            p = os.path.join(_ICONS_DIR, f"{name}.png")
            if os.path.exists(p):
                return p
        return None

    @staticmethod
    def _find_whoami_path(whoami_id: int) -> str | None:
        for name in (str(whoami_id), f"{whoami_id:03d}"):
            for ext in ("png", "gif"):
                p = os.path.join(_WHOAMI_DIR, f"{name}.{ext}")
                if os.path.exists(p):
                    return p
        return None

    @staticmethod
    def _make_fallback(size: tuple[int, int]) -> ImageTk.PhotoImage:
        img = Image.new("RGBA", size, (30, 30, 30, 200))
        return ImageTk.PhotoImage(img)
