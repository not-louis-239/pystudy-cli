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

import math


from pystudy_cli.core.constants import FAMILIARITY_LEVELS
from pystudy_cli.core.objects import Deck
from pystudy_cli.core.profile import StudyProfile
from pystudy_cli.tui.colours import (
    COL_ACCENT,
    COL_BASE,
    COL_CARD_DEF,
    COL_CARD_INDEX,
    COL_ERROR,
    COL_LIGHT_GREY,
    COL_WHITE,
)
from pystudy_cli.tui.revision_modes import flashcard_mode, learn_mode, test_mode
from pystudy_cli.tui.ui_elements import (
    clear_screen,
    cursor_input,
    display_status_bar,
    int_convertible,
    show_hotkey,
)
from pystudy_cli.tui.states.card_editor import card_editor

def deck_menu(profile: StudyProfile, deck: Deck):
    while True:
        clear_screen(full_clear=True)
        display_status_bar(f"{deck.name} > {'No' if len(deck.cards) == 0 else len(deck.cards)} Cards")

        # Show cards
        if deck.cards:
            # Calculate card counts and max width
            card_counts: dict[int, int] = {
                lvl_int: sum(1 for card in deck.cards if card.familiarity_level == lvl_int)
                for lvl_int in FAMILIARITY_LEVELS
            }
            max_width = max(len(lvl.ui_text) for lvl in FAMILIARITY_LEVELS.values())

            # Calculate study progress
            total_weight = 0
            for lvl_int, count in card_counts.items():
                new_weight = FAMILIARITY_LEVELS[lvl_int].weight * count
                total_weight += new_weight
            progress = total_weight / len(deck.cards)

            print(f"{COL_WHITE}Study Progress: {COL_ACCENT}{progress:.2%}")
            print(f"{COL_WHITE}\nProgress Breakdown")

            for lvl_int, count in card_counts.items():
                lvl = FAMILIARITY_LEVELS[lvl_int]
                print(f"{lvl.colour_code}{lvl.ui_text:<{max_width+2}} {COL_BASE}{count} ")

            print(f"{COL_WHITE}\nCards{COL_BASE}")
            max_len = int(math.log10(len(deck.cards)))+1
            for i, card in enumerate(deck.cards, start=1):
                f_lvl = FAMILIARITY_LEVELS[card.familiarity_level]
                print(f"{COL_CARD_INDEX}{i:>{max_len}}. {f_lvl.colour_code}{card.term}")
                print(f"{COL_CARD_DEF}{card.def_}{COL_BASE}")
        else:
            print(f"{COL_BASE}This deck doesn't have any cards yet!")

        print(f"{COL_WHITE}\nWhat would you like to do?{COL_BASE}")
        show_hotkey('m', 'modify cards')
        show_hotkey('t', 'rename deck')
        show_hotkey('r', 'revise deck')
        show_hotkey('q', 'close deck')
        action = cursor_input()

        # Add/remove cards
        if action == 'm':
            card_editor(deck)

        # Rename deck
        elif action == 't':
            new_name = input(f"{COL_LIGHT_GREY}\nEnter new name (or press Enter to cancel): {COL_ACCENT}").strip()
            if not new_name:
                continue

            if int_convertible(new_name):
                input(f"{COL_ERROR}Invalid: Deck name cannot be a pure integer! {COL_BASE}(Enter to return)")
                continue

            existing_names = {d.name for d in profile.decks if d is not deck}
            if new_name in existing_names:
                input(f"{COL_ERROR}Invalid: That deck name is already taken by another deck! {COL_BASE}(Enter to return)")
                continue

            # Only change the display name, not filename
            # This avoids breaking refs in the head data file
            deck.name = new_name

        # Revise deck
        elif action == 'r':
            print(f"\n{COL_WHITE}Select revision mode {COL_LIGHT_GREY}(or press Enter to cancel){COL_WHITE}:")
            print(f"{COL_LIGHT_GREY}1    {COL_BASE}flashcards")
            print(f"{COL_LIGHT_GREY}2    {COL_BASE}learn")
            print(f"{COL_LIGHT_GREY}3    {COL_BASE}practice test")

            try:
                mode = cursor_input()
                if mode == '\n':
                    continue
                mode = int(mode)
                if not 1 <= mode <= 3:
                    raise ValueError
            except ValueError:
                input(f"{COL_ERROR}Invalid mode. {COL_BASE}(Enter to return)")
                continue

            if mode == 1:
                flashcard_mode(deck)
            elif mode == 2:
                learn_mode(deck)
            elif mode == 3:
                test_mode(deck)

        # Close deck
        elif action == 'q':
            return
