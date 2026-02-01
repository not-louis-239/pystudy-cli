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

# Define colours

def rgb(r: int, g: int, b: int, bg: bool = False) -> str:
    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"

def col(code: int, bg: bool = False): # 256 colours
    return f"\033[{48 if bg else 38};5;{code}m"

RESET = '\033[0m'
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Base palette
COL_WHITE = col(231)
COL_BASE = col(254)
COL_LIGHT_GREY = col(248)
COL_DARK_GREY = col(240)

# Theme colours
COL_TITLE = col(215)
COL_ACCENT = col(222)

# State colours
COL_SUCCESS = col(77)
COL_ERROR = col(197)
COL_WARNING = col(221)

# Cards
COL_CARD_INDEX = COL_LIGHT_GREY
COL_CARD_TERM = COL_BASE
COL_CARD_DEF = COL_LIGHT_GREY

# Decks
COL_DECK_INDEX = COL_LIGHT_GREY
COL_DECK_NAME = COL_BASE
COL_LEARNING = COL_WARNING

# Minimap colours
COL_UNANSWERED1 = col(239)
COL_UNANSWERED2 = col(242)
COL_ANSWERED1 = col(247)
COL_ANSWERED2 = col(250)
COL_CURRENT_CARD = COL_ACCENT

# Other colours
COL_NAME = col(123)

def _main():
    print("=== 256-Color Palette ===")
    for i in range(256):  # Palette viewer
        print(f"{col(i, False)} {i:3} {RESET}", end="")
        if (i + 1) % 16 == 0:
            print()

    print("\n=== Application Colour Palette ===\n")

    print(f"{COL_WHITE}WHITE: Sample Text{RESET}")
    print(f"{COL_BASE}BASE_COL: Sample Text{RESET}")
    print(f"{COL_LIGHT_GREY}LIGHT_GREY: Sample Text{RESET}")
    print(f"{COL_DARK_GREY}DARK_GREY: Sample Text{RESET}")

    print(f"{COL_TITLE}TITLE_COL: Sample Text{RESET}")
    print(f"{COL_ACCENT}ACCENT_COL: Sample Text{RESET}\n")

    print(f"{COL_SUCCESS}SUCCESS_COL: Sample Text{RESET}")
    print(f"{COL_ERROR}ERROR_COL: Sample Text{RESET}")
    print(f"{COL_WARNING}LIGHT_YELLOW: Sample Text{RESET}\n")

    print(f"{COL_CARD_INDEX}CARD_IDX_COL: Sample Text{RESET}")
    print(f"{COL_CARD_TERM}CARD_TERM_COL: Sample Text{RESET}")
    print(f"{COL_CARD_DEF}CARD_DEF_COL: Sample Text{RESET}\n")

    print(f"{COL_DECK_INDEX}DECK_IDX_COL: Sample Text{RESET}")
    print(f"{COL_DECK_NAME}DECK_NAME_COL: Sample Text{RESET}")
    print(f"{COL_LEARNING}LEARNING_COL: Sample Text{RESET}\n")

    print(f"{COL_UNANSWERED1}COL_UNANSWERED1: Sample Text{RESET}")
    print(f"{COL_UNANSWERED2}COL_UNANSWERED2: Sample Text{RESET}")
    print(f"{COL_ANSWERED1}COL_ANSWERED1: Sample Text{RESET}")
    print(f"{COL_ANSWERED2}COL_ANSWERED2: Sample Text{RESET}")
    print(f"{COL_CURRENT_CARD}COL_CURRENT_CARD: Sample Text{RESET}\n")
    print(f"{COL_NAME}COL_NAME: Sample Text{RESET}\n")

if __name__ == "__main__":
    _main()