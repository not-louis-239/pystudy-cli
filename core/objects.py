from typing import Self, TypeAlias, cast

JSONValue: TypeAlias = (
    str | int | float | bool | None |
    list["JSONValue"] |
    dict[str, "JSONValue"]
)
JSONObject: TypeAlias = dict[str, JSONValue]

class JSONConvertible:
    """Base class for dict-convertible items, e.g. decks, cards."""

    def to_json(self) -> JSONObject:
        """Serialise to dict"""
        raise NotImplementedError

    @classmethod
    def from_json(cls, data: JSONObject) -> Self:
        """Create from dict"""
        raise NotImplementedError

class Card(JSONConvertible):
    """Individual flashcards."""

    def __init__(self, term: str, definition: str) -> None:
        self.term = term
        self.definition = definition

    def to_json(self) -> JSONObject:
        return {
            "term": self.term,
            "definition": self.definition
        }

    @classmethod
    def from_json(cls, data: JSONObject) -> Self:
        return cls(
            cast(str, data["term"]),
            cast(str, data["definition"])
        )

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