"""File to manage core assets"""

# from pathlib import Path  # TODO: Use this to load images and sounds
import pygame as pg
from core.constants import BASE_DIR

class AssetBank:
    def __init__(self) -> None:
        """Base method to set assets."""
        self.augment()

    def augment(self) -> None:
        """Base method to adjust assets."""
        pass

    def _load(self) -> None:
        """Base method to load individual assets."""
        raise NotImplementedError

class Sounds(AssetBank):
    def __init__(self) -> None:
        self.augment()

    def _load(self, name: str) -> pg.mixer.Sound:
        return pg.mixer.Sound(BASE_DIR / "assets" / "images" / name)