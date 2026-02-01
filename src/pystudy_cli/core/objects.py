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

from typing import Self, TypeAlias, cast
from pystudy_cli.core.constants import FAMILIARITY_LEVELS

JSONValue: TypeAlias = (
    str | int | float | bool | None |
    list["JSONValue"] |
    dict[str, "JSONValue"]
)
JSONObject: TypeAlias = dict[str, JSONValue]

class JSONConvertible:
    """
    Base class for items that are convertible to and from JSON, e.g. decks, cards.
    Use this for objects that should persist between sessions.
    """

    def to_json(self) -> JSONObject:
        """Serialise to dict"""
        raise NotImplementedError

    @classmethod
    def from_json(cls, data: JSONObject) -> Self:
        """Create from dict"""
        raise NotImplementedError

class Card(JSONConvertible):
    """Individual flashcards."""

    def __init__(self, term: str, definition: str, familiarity_level: int = 0) -> None:
        self.term = term
        self.definition = definition
        self.familiarity_level = familiarity_level

    def to_json(self) -> JSONObject:
        return {
            "term": self.term,
            "definition": self.definition,
            "familiarity_level": self.familiarity_level
        }

    @classmethod
    def from_json(cls, data: JSONObject) -> Self:
        return cls(
            cast(str, data["term"]),
            cast(str, data["definition"]),
            cast(int, data.get("familiarity_level", 0))
        )

    def on_correct(self):
        if self.familiarity_level == 0:
            self.familiarity_level = 2  # Skip two steps
            return
        self.familiarity_level += 1
        self.familiarity_level = min(len(FAMILIARITY_LEVELS) - 1, self.familiarity_level)

    def on_incorrect(self):
        self.familiarity_level -= 1
        self.familiarity_level = max(1, self.familiarity_level)

class Deck(JSONConvertible):
    """Individual containers for cards."""

    def __init__(self, creation_date: str, name: str, cards: list[Card] = []) -> None:
        self.creation_date = creation_date
        self.name = name
        self.cards = cards

    def to_json(self) -> JSONObject:
        return {
            "creation_date": self.creation_date,
            "name": self.name,
            "cards": [card.to_json() for card in self.cards]
        }

    @classmethod
    def from_json(cls, data: JSONObject) -> Self:
        return cls(
            creation_date=cast(str, data["creation_date"]),
            name=cast(str, data["name"]),
            cards=[
                Card.from_json(c)  # type: ignore
                for c in cast(list[Card], data["cards"])
            ]
        )

class ConfigObject(JSONConvertible):
    def __init__(
            self,
            warn_interrupt: bool
        ) -> None:
        self.warn_interrupt = warn_interrupt

    def to_json(self) -> JSONObject:
        """Serialise to dict"""
        return {
            "warn_interrupt": self.warn_interrupt
        }

    @classmethod
    def from_json(cls, data: JSONObject) -> Self:
        """Create from dict"""
        return cls(
            warn_interrupt=data['warn_interrupt']  # type: ignore
        )