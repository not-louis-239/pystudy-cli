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

import copy
import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from pystudy_cli.core import paths
from pystudy_cli.core.constants import NEW_STATE
from pystudy_cli.core.profile import StudyProfile


class LoadStatCategory(Enum):
    SUCCESS = auto()
    NEW = auto()
    CORRUPT = auto()
    ERROR = auto()

@dataclass
class LoadStatus:
    category: LoadStatCategory
    msg: str

def save_data(data: StudyProfile, path: Path = paths.DATA_DIR / "save_data.json") -> str | None:
    """
    WARNING: data must be serialised first.
    Returns None if success, else return error description.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True) # Ensure parent directories exist

        # Write to temporary file to avoid corruption
        # if the program errors mid-write
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data.to_json(), f, indent=4, ensure_ascii=False)
        tmp.replace(path)

    except Exception as e:
        return str(e)

    return None

def load_data(filename = paths.DATA_DIR / "save_data.json") -> tuple[StudyProfile, LoadStatus]:
    """
    Load JSON data from a file and sync keys with NEW_STATE.

    Returns a tuple:
    * state dict
    * status object
    """

    msg = None

    try:
        with open(filename, "r", encoding="utf-8") as f:
            state = json.load(f)
        category = LoadStatCategory.SUCCESS
    except FileNotFoundError:
        state = copy.deepcopy(NEW_STATE)
        category = LoadStatCategory.NEW
    except json.JSONDecodeError:
        state = copy.deepcopy(NEW_STATE)
        category = LoadStatCategory.CORRUPT
    except Exception as e:
        state = copy.deepcopy(NEW_STATE)
        category = LoadStatCategory.ERROR
        msg = str(e)

    # Add missing keys
    for k in NEW_STATE.keys():
        if k not in state:
            state[k] = NEW_STATE[k]

    # Remove deprecated keys
    for k in list(state.keys()):
        if k not in NEW_STATE:
            del state[k]

    return StudyProfile.from_json(state), LoadStatus(category, msg if msg is not None else "")
