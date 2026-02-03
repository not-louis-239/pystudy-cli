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

import pygame as pg

from pystudy_cli.core import paths


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
        self.wrong_answer = self._load("wrong_answer.ogg")
        self.correct_answer = self._load("correct_answer.ogg")
        self.click = self._load("button_click.ogg")

        self.augment()

    def _load(self, name: str) -> pg.mixer.Sound:
        return pg.mixer.Sound(paths.SOUNDS_DIR / name)
