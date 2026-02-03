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

from dataclasses import dataclass

from pystudy_cli.tui.colours import RESET, col


@dataclass
class FamiliarityLevel:
    ui_text: str
    colour_code: str
    weight: float

VERSION_NUM = "v0.2.0"

FAMILIARITY_LEVELS: dict[int, FamiliarityLevel] = {
    0: FamiliarityLevel("New", col(207), 0),
    1: FamiliarityLevel("Learning", col(141), 0.15),
    2: FamiliarityLevel("Familiar", col(111), 0.4),
    3: FamiliarityLevel("Proficient", col(81), 0.7),
    4: FamiliarityLevel("Mastered", col(122), 1)
}

NUM_MCQ_OPTIONS = 4

FALLBACK_STATUS_BAR_WIDTH = 80

def _main():
    print("Testing familiarity levels")
    for idx, level in FAMILIARITY_LEVELS.items():
        print(f"Familiarity Level {idx}: {level.colour_code}{level.ui_text}{RESET}")

# Defaults
DEFAULT_CARDS_PER_ROUND: int = 7
DEFAULT_PRACTICE_TEST_LEN: int = 10
DEFAULT_SMART_GRADING_STRICTNESS: float = 0.8

if __name__ == "__main__":
    _main()