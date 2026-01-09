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

import pygame as pg
from pathlib import Path
from typing import Literal
from core.custom_types import Surface, Coord2, Colour, AColour
from core.constants import WHITE

def draw_text(surface: Surface, pos: Coord2,
              horiz_align: Literal["left", "centre", "right"],
              vert_align: Literal["top", "centre", "bottom"],
              text: str, colour: Colour, size: int, font_path: Path | None = None):
    if font_path:
        font = pg.font.Font(str(font_path), size)
    else:
        font = pg.font.SysFont(None, size)

    img = font.render(text, True, colour)
    r = img.get_rect()

    # Horizontal
    if horiz_align == "left":
        setattr(r, "left", pos[0])
    elif horiz_align == "centre":
        setattr(r, "centerx", pos[0])
    elif horiz_align == "right":
        setattr(r, "right", pos[0])
    else:
        raise ValueError("Invalid horiz_align")

    # Vertical
    if vert_align == "top":
        setattr(r, "top", pos[1])
    elif vert_align == "centre":
        setattr(r, "centery", pos[1])
    elif vert_align == "bottom":
        setattr(r, "bottom", pos[1])
    else:
        raise ValueError("Invalid vert_align")

    surface.blit(img, r)

def draw_transparent_rect(surface: Surface, pos: Coord2, size: Coord2,
                          bg_colour: AColour = (0, 0, 0, 180),
                          border_thickness=0, border_colour: Colour = WHITE,
                          ):
    """Draws a semi-transparent rectangle with a border onto a surface.
    For a transparent rect only, set border thickness to 0."""
    box_surf = pg.Surface(size, pg.SRCALPHA)
    box_surf.fill(bg_colour)
    if border_thickness:
        pg.draw.rect(box_surf, border_colour, box_surf.get_rect(), border_thickness)
    surface.blit(box_surf, pos)

def seconds_to_time(seconds: int) -> str:
    """Accepts a seconds parameter and creates a time display

    seconds:      int (e.g.   50_400)
    Return value: str (e.g. 02:00 pm)
    """

    base_h = (seconds // 3600) % 24

    suffix = "am" if base_h < 12 else "pm"
    h = base_h % 12 or 12
    m = (seconds // 60) % 60

    return f"{h:02d}:{m:02d} {suffix}"