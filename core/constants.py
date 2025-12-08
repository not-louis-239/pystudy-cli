from pathlib import Path
from core.custom_types import Colour

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

FAMILIARITY_LEVELS: dict[int, str] = {
    0: "New",
    1: "Learning",
    2: "Familiar",
    3: "Proficient",
    4: "Mastered"
}

NUM_MCQ_OPTIONS = 4