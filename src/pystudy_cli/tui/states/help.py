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



from pystudy_cli.tui.colours import (
    COL_ACCENT,
    COL_BASE,
    COL_DARK_GREY,
    COL_LIGHT_GREY,
    COL_WHITE,
    RESET,
)
from pystudy_cli.tui.ui_elements import (
    clear_screen,
    display_status_bar,
)

def help_menu():
    clear_screen()
    display_status_bar("Help")

    print(f"\n{COL_WHITE}How to Use the CLI{RESET}")
    print(f"{COL_ACCENT}───────────────────────{RESET}")

    print(f"\n{COL_LIGHT_GREY}The CLI uses two different input methods:{RESET}")
    print(f"{COL_ACCENT}  - {COL_WHITE}Menus:{COL_BASE} To navigate menus, press the key corresponding to the action (e.g., 'n'). You do not need to press Enter.")
    print(f"{COL_ACCENT}  - {COL_WHITE}Text Entry:{COL_BASE} When prompted to type (e.g., to name a deck), type your text and press Enter to confirm.")

    print(f"\n{COL_WHITE}Main Menu{RESET}")
    print(f"{COL_ACCENT}─────────{RESET}")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}n (new deck):{COL_BASE} Create a new, empty deck.")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}o (open deck):{COL_BASE} Open an existing deck to view, edit, or revise its cards.")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}d (delete deck):{COL_BASE} Permanently delete a deck.")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}s (settings):{COL_BASE} Change application settings.")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}h (help):{COL_BASE} Displays this help menu.")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}q (quit):{COL_BASE} Save your data and exit the program.")

    print(f"\n{COL_WHITE}Deck Menu{RESET}")
    print(f"{COL_ACCENT}─────────{RESET}")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}m (modify cards):{COL_BASE} Opens the card editor to add, remove, or change cards.")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}t (rename deck):{COL_BASE} Change the name of the current deck.")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}r (revise deck):{COL_BASE} Choose a study mode (Flashcards, Learn, Test).")
    print(f"{COL_ACCENT}  - {COL_LIGHT_GREY}q (close deck):{COL_BASE} Return to the main menu.")

    input(f"\n{COL_DARK_GREY}(Press Enter to return to the main menu){RESET}")
