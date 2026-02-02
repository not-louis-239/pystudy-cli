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

import sys
from datetime import datetime


from pystudy_cli.core.data_manager import save_profile
from pystudy_cli.core.exceptions import DeckExistsError, DeckNotFoundError
from pystudy_cli.core.profile import StudyProfile
from pystudy_cli.tui.colours import (
    COL_ACCENT,
    COL_BASE,
    COL_DARK_GREY,
    COL_DECK_INDEX,
    COL_DECK_NAME,
    COL_ERROR,
    COL_LIGHT_GREY,
    COL_SUCCESS,
    COL_WHITE,
    COL_NAME,
)
from pystudy_cli.tui.ui_elements import (
    clear_screen,
    cursor_input,
    display_status_bar,
    int_convertible,
    show_hotkey,
)
from pystudy_cli.tui.states.deck_menu import deck_menu
from pystudy_cli.tui.states.settings import settings_menu
from pystudy_cli.tui.states.help import help_menu

def input_loop(profile: StudyProfile):
    clear_screen()
    display_status_bar()

    print(f"\n{COL_WHITE}Hi, {COL_NAME}{profile.name}{COL_WHITE}!{COL_BASE}")

    print(f"{COL_WHITE}\nDecks{COL_BASE}")
    if not profile.decks:
        print("You don't have any decks yet!")
    else:
        for i, deck in enumerate(profile.decks, 1):
            print(f"{COL_DECK_INDEX}{i}. {COL_DECK_NAME}{deck.name} {COL_DARK_GREY}({len(deck.cards)} cards)")

    print(f"{COL_WHITE}\nWhat would you like to do?{COL_BASE}")
    show_hotkey('n', 'new deck')
    show_hotkey('o', 'open deck')
    show_hotkey('d', 'delete deck')
    show_hotkey('s', 'settings')
    show_hotkey('h', 'help')
    show_hotkey('q', 'quit')
    action = cursor_input()

    # New deck
    if action == 'n':
        deck_name = input(f"{COL_LIGHT_GREY}\nEnter deck name (or press Enter to cancel): {COL_ACCENT}").strip()
        if not deck_name:
            return
        if int_convertible(deck_name):
            input(f"{COL_ERROR}Invalid: Deck name cannot be a pure integer! {COL_BASE}(Enter to return)")
            return

        try:
            profile.new_deck(datetime.now().isoformat(), deck_name)
            input(f"{COL_WHITE}Deck {COL_ACCENT}{deck_name}{COL_WHITE} created. {COL_BASE}(Enter to return)")
        except DeckExistsError:
            input(f"{COL_ERROR}Invalid: Deck name must be unique. {COL_BASE}(Enter to return)")

    # Open deck
    elif action == 'o':
        if not profile.decks:
            input(f"{COL_ERROR}\nNo decks to open. {COL_LIGHT_GREY}Try creating one first! {COL_BASE}(Enter to return)")
            return

        deck_name = input(f"\n{COL_LIGHT_GREY}Enter the name (or index) of a deck to open (or press Enter to cancel): {COL_ACCENT}").strip()
        if not deck_name:
            return

        # Index input
        try:
            deck_idx = int(deck_name) - 1   # possible ValueError
            deck = profile.decks[deck_idx]  # possible IndexError

            if not 0 <= deck_idx < len(profile.decks):
                raise IndexError

            deck_menu(profile, deck)

        # Name input
        except ValueError:
            deck = next((deck for deck in profile.decks if deck.name == deck_name), None)
            if deck is None:
                input(f"{COL_ERROR}That deck doesn't exist!{COL_BASE} (Enter to return)")
                return
            deck_menu(profile, deck)

        # Invalid index
        except IndexError:
            input(f"{COL_ERROR}Invalid index! (must be an integer from 1 to {len(profile.decks)}) {COL_BASE}(Enter to return)")
            return

    # Remove deck
    elif action == 'd':
        deck_name = input(f"{COL_LIGHT_GREY}\nEnter deck name to delete (or press Enter to cancel): {COL_ACCENT}").strip()
        if not deck_name:
            return

        confirm = input(f"{COL_LIGHT_GREY}Are you sure you want to delete this deck (this action cannot be undone)? (y/n) {COL_ACCENT}").strip().lower()
        if confirm == 'y':
            try:
                profile.remove_deck(deck_name)
                input(f"{COL_WHITE}Deck {COL_ACCENT}{deck_name}{COL_WHITE} removed. {COL_BASE}(Enter to return)")
            except DeckNotFoundError:
                input(f"{COL_ERROR}Invalid: Deck does not exist. {COL_BASE}(Enter to return)")

    # Settings
    elif action == 's':
        settings_menu(profile)

    # Help
    elif action == 'h':
        help_menu()

    # Quit
    elif action == 'q':
        print(f"{COL_LIGHT_GREY}\nAre you sure you want to quit?")
        print(f"{COL_BASE}(q - quit | other - return)")
        confirm = cursor_input()

        if confirm == 'q':
            print(f"{COL_BASE}\nSaving data and exiting...")

            while True:
                status = save_profile(profile)
                if status is None:
                    print(f"{COL_SUCCESS}Data saved!")
                    break

                retry = input(
                    f"{COL_ERROR}Saving data failed: {COL_WHITE}{status}{COL_ERROR}. "
                    f"{COL_LIGHT_GREY}Retry? (y/n) {COL_WHITE}"
                ).strip().lower()
                if retry != 'y':
                    print(f"{COL_BASE}Exiting without saving...")
                    break

            print(f"{COL_BASE}Goodbye!\033[0m")
            sys.exit(0)