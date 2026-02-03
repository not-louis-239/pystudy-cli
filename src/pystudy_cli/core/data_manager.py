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

"""File manager for local user data"""

import json
import re
import uuid
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Iterable

from pystudy_cli.core import paths
from pystudy_cli.core.profile import StudyProfile
from pystudy_cli.core.objects import JSONObject, ConfigObject
from pystudy_cli.core.objects import Deck


class LoadStatCategory(Enum):
    SUCCESS = auto()
    NEW = auto()
    CORRUPT = auto()
    PARTIAL = auto()
    ERROR = auto()

@dataclass
class LoadStatus:
    category: LoadStatCategory
    msg: str

def slugify_filename(name: str) -> str:
    """Convert a deck filename to a filesystem-safe version."""

    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "deck"

def make_deck_filename(name: str, existing: Iterable[str] | None = None) -> str:
    existing_set = set(existing or [])
    while True:
        slug = slugify_filename(name)
        suffix = uuid.uuid4().hex[:8]
        filename = f"{slug}-{suffix}.json"
        if filename not in existing_set:
            return filename

def write_json_atomic(path: Path, data: JSONObject) -> None:
    """Helper to write JSON data to a file.
    Writes to a temporary file first to avoid
    data truncation or corruption if the program errors
    mid-write."""

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    tmp.replace(path)

def trash_deck(path: Path) -> None:
    trash_dir = paths.TRASH_DIR
    trash_dir.mkdir(parents=True, exist_ok=True)
    target = trash_dir / path.name
    if target.exists():
        target = trash_dir / f"{path.stem}-{uuid.uuid4().hex[:8]}{path.suffix}"
    path.replace(target)

def save_profile(data: StudyProfile, path: Path = paths.DATA_DIR / "save_data.json") -> str | None:
    """Returns None if success, else return error description."""
    try:
        paths.DECKS_DIR.mkdir(parents=True, exist_ok=True)
        deck_filenames = []
        for deck in data.decks:
            if not deck.filename:
                raise ValueError(f"deck '{deck.name}' is missing a filename")
            deck_filenames.append(deck.filename)
            write_json_atomic(paths.DECKS_DIR / deck.filename, deck.to_json())

        # Move stale deck files not referenced by the head file to trash
        existing_files = {p.name for p in paths.DECKS_DIR.glob("*.json")}
        for stale in existing_files - set(deck_filenames):
            trash_deck(paths.DECKS_DIR / stale)

        write_json_atomic(path, data.to_json())

    except Exception as e:
        return str(e)

    return None

def load_profile(path = paths.DATA_DIR / "save_data.json") -> tuple[StudyProfile, LoadStatus]:
    """
    Load data from save files.
    """

    msg = None

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data: JSONObject = json.load(f)

        name = str(raw_data.get("name", ""))
        config = ConfigObject.from_json(raw_data.get("config", {}))

        decks: list[Deck] = []
        errors: list[str] = []

        if "deck_files" in raw_data:
            deck_files_raw = raw_data.get("deck_files", [])
            assert isinstance(deck_files_raw, list)

            deck_files = [str(f) for f in deck_files_raw]
            for filename in deck_files:
                try:
                    decks.append(load_deck(filename))
                except Exception as e:
                    errors.append(f"{filename}: {e}")
        elif "decks" in raw_data:
            existing = set()
            deck_files_raw = raw_data.get("decks", [])
            assert isinstance(deck_files_raw, list)

            for deck_data in deck_files_raw:
                filename = make_deck_filename(str(deck_data.get("name", "deck")), existing)  # type: ignore
                existing.add(filename)
                decks.append(Deck.from_json(deck_data, filename))  # type: ignore

        profile = StudyProfile(name, decks, config)
        category = LoadStatCategory.SUCCESS if not errors else LoadStatCategory.PARTIAL
        if errors:
            msg = "Some deck files could not be loaded: " + "; ".join(errors)

    except FileNotFoundError:
        profile = StudyProfile("", [], ConfigObject())
        category = LoadStatCategory.NEW

    except json.JSONDecodeError:
        profile = StudyProfile("", [], ConfigObject())
        category = LoadStatCategory.CORRUPT

    except Exception as e:
        profile = StudyProfile("", [], ConfigObject())
        category = LoadStatCategory.ERROR
        msg = str(e)

    return profile, LoadStatus(category, msg if msg is not None else "")

def save_deck(deck: Deck, filename: str):
    write_json_atomic(paths.DECKS_DIR / filename, deck.to_json())

def load_deck(filename: str) -> Deck:
    path = paths.DECKS_DIR / filename

    if not path.exists():
        raise FileNotFoundError("deck file doesn't exist")

    if path.is_dir():
        raise IsADirectoryError("this is a directory")

    with open(path, "r", encoding="utf-8") as f:
        return Deck.from_json(json.load(f), filename)
