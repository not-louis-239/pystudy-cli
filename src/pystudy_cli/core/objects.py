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

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Self, Mapping, Any, cast

from pystudy_cli.core.constants import FAMILIARITY_LEVELS
from pystudy_cli.core.custom_types import JSONObject, JSONValue

class JSONConvertible(ABC):
    """
    Base class for items that are convertible to and from JSON, e.g. decks, cards.
    Use this for objects that should persist between sessions.
    """

    @abstractmethod
    def to_json(self) -> JSONObject:
        """Serialise to dict"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_json(cls, data: JSONObject) -> Self:
        """Create from dict"""
        raise NotImplementedError

@dataclass
class Card(JSONConvertible):
    """Individual flashcards."""
    term: str = ""
    def_: str = ""
    familiarity_level: int = 0

    def to_json(self) -> JSONObject:
        return asdict(self)

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> Card:
        return cls(
            term=data["term"],
            def_=data["def_"],
            familiarity_level=data["familiarity_level"]
        )

@dataclass
class Deck(JSONConvertible):
    """Individual containers for cards."""
    creation_date: str
    name: str
    cards: list[Card]
    filename: str

    def to_json(self) -> JSONObject:
        return {
            "creation_date": self.creation_date,
            "name": self.name,
            "cards": [card.to_json() for card in self.cards]
        }

    @classmethod
    def from_json(cls, data: JSONObject, filename: str) -> Self:
        assert isinstance(data["name"], str)
        assert isinstance(data["creation_date"], str)

        return cls(
            creation_date=data["creation_date"],
            name=data["name"],
            cards=[Card.from_json(card_data) for card_data in cast(list, data.get("cards", []))],
            filename=filename
        )

@dataclass
class ConfigObject(JSONConvertible):
    warn_interrupt: bool = False

    def to_json(self) -> JSONObject:
        """Serialise to dict"""
        return asdict(self)

    @classmethod
    def from_json(cls, data: JSONValue) -> Self:
        assert isinstance(data, dict)

        """Create from dict"""
        return cls(
            warn_interrupt=bool(data.get("warn_interrupt", False))
        )

def on_correct(card: Card):
    if card.familiarity_level == 0:
        # Skip two steps if new card correct instantly
        card.familiarity_level += 2
        return

    card.familiarity_level += 1
    card.familiarity_level = min(len(FAMILIARITY_LEVELS) - 1, card.familiarity_level)

def on_incorrect(card: Card):
    card.familiarity_level -= 1

    # A card can only drop to the lowest "still learning stage".
    # It shouldn't drop to "completely new" if revised at least once.
    card.familiarity_level = max(1, card.familiarity_level)
