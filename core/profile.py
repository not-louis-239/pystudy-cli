"""The profile module - stores logic for StudyProfile, including converting to and from JSON."""

from typing import Self
from core.objects import (
    JSONConvertible, JSONObject,
    Deck
)
from core.exceptions import DeckError, DeckNotFoundError, DeckExistsError

class StudyProfile(JSONConvertible):
    """Top-level class for managing state as a whole."""

    def __init__(self, name: str, decks: list[Deck]) -> None:
        super().__init__()
        self.name = name
        self.decks = decks

    def to_json(self) -> JSONObject:
        """Serialise to dict"""
        return {
            "name": self.name,
            "decks": [d.to_json() for d in self.decks]
        }

    @classmethod
    def from_json(cls, data: JSONObject) -> Self:
        """Create from dict"""
        return cls(
            data['name'],                                     # type: ignore
            [Deck.from_json(deck) for deck in data['decks']]  # type: ignore
        )

    def new_deck(self, timestamp: str, name: str) -> None:
        """Adds a new deck to the instance. Deck names must be unique."""
        if not name:
            raise DeckError("name cannot be empty")
        if any(deck.name == name for deck in self.decks):
            raise DeckExistsError("deck name must be unique")

        new = Deck(timestamp, name)
        self.decks.append(new)

    def remove_deck(self, name: str) -> None:
        """Remove a deck from the instance and return a status code."""
        to_remove = next((deck for deck in self.decks if deck.name == name), None)
        if to_remove is None:
            raise DeckNotFoundError("deck doesn't exist")

        self.decks.remove(to_remove)
