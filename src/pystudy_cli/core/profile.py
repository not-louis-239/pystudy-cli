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

"""The profile module - stores logic for StudyProfile, including converting to and from JSON."""

from dataclasses import dataclass, asdict
from typing import Self

from pystudy_cli.core.exceptions import DeckError, DeckExistsError, DeckNotFoundError
from pystudy_cli.core.objects import ConfigObject, Deck, JSONConvertible, JSONObject, Card

@dataclass
class StudyProfile(JSONConvertible):
    """Top-level class for managing state as a whole."""
    name: str
    decks: list[Deck]
    config: ConfigObject

    def to_json(self) -> JSONObject:
        """Serialise to dict"""
        return asdict(self)

    @classmethod
    def from_json(cls, data: JSONObject) -> Self:
        assert isinstance(data, dict)
        assert isinstance(data["name"], str)

        """Create from dict"""
        profile = cls(
            name=data["name"],
            config=ConfigObject.from_json(
                data["config"]
            ),
            decks=[
                Deck(
                    creation_date=str(deck_data["creation_date"]),
                    name=str(deck_data["name"]),
                    cards=[
                        Card(
                            term=str(card["term"]),
                            def_=str(card["def_"]),
                            familiarity_level=int(card.get("familiarity_level", 0))
                        ) for card in deck_data.get("cards", [])
                    ]
                ) for deck_data in data.get("decks", None) or []  # type: ignore
            ]
        )

        return profile

    def new_deck(self, timestamp: str, name: str) -> None:
        """Adds a new deck to the instance. Deck names must be unique."""
        if not name:
            raise DeckError("name cannot be empty")
        if any(deck.name == name for deck in self.decks):
            raise DeckExistsError("deck name must be unique")

        new = Deck(timestamp, name, [])
        self.decks.append(new)

    def remove_deck(self, name: str) -> None:
        """Remove a deck from the instance, raise if it doesn't exist."""
        to_remove = next((deck for deck in self.decks if deck.name == name), None)
        if to_remove is None:
            raise DeckNotFoundError("deck doesn't exist")

        self.decks.remove(to_remove)
