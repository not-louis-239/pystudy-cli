from pathlib import Path
from core.custom_types import Colour
from tui.colours import col, RESET
from dataclasses import dataclass

@dataclass
class FamiliarityLevel:
    ui_text: str
    colour_code: str

VERSION_NUM: str = "0.2.0"

# Base directory
BASE_DIR: Path = Path(__file__).resolve().parent

# Colours
WHITE: Colour = (255, 255, 255)

# New state for the first time the program runs
NEW_STATE: dict = {
    "name": "",
    "decks": [],
    "config": {
        "warn_interrupt": False
    }
}

FAMILIARITY_LEVELS: dict[int, FamiliarityLevel] = {
    0: FamiliarityLevel("New", col(207)),
    1: FamiliarityLevel("Learning", col(141)),
    2: FamiliarityLevel("Familiar", col(111)),
    3: FamiliarityLevel("Proficient", col(81)),
    4: FamiliarityLevel("Mastered", col(122))
}

NUM_MCQ_OPTIONS = 4

def _main():
    for idx, level in FAMILIARITY_LEVELS.items():
        print(f"Familiarity Level {idx}: {level.colour_code}{level.ui_text}{RESET}")

if __name__ == "__main__":
    _main()