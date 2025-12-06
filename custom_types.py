import pygame as pg
from typing import TypeAlias

Colour: TypeAlias = tuple[int, int, int]
AColour: TypeAlias = tuple[int, int, int, int]

RealNumber: TypeAlias = int | float
Coord2: TypeAlias = tuple[RealNumber, RealNumber]
DiscreteCoord2: TypeAlias = tuple[int, int]
Surface: TypeAlias = pg.Surface