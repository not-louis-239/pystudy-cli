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
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from pystudy_cli.core import paths
from pystudy_cli.core.profile import StudyProfile
from pystudy_cli.core.objects import JSONObject, ConfigObject

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

def load_data(path = paths.DATA_DIR / "save_data.json") -> tuple[StudyProfile, LoadStatus]:
    """
    Load data from save files.
    """

    msg = None

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data: JSONObject = json.load(f)

        print("Data")
        profile = StudyProfile.from_json(raw_data)

        print("Profile")
        category = LoadStatCategory.SUCCESS

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
