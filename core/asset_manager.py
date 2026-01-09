# Copyright 2025-2026 Louis Masarei-Boulton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

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