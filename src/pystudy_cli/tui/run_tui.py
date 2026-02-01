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
import sys
from datetime import datetime
from typing import Callable

from readchar import readkey

from pystudy_cli.core.constants import FAMILIARITY_LEVELS
from pystudy_cli.core.data_manager import load_data, save_data
from pystudy_cli.core.exceptions import DeckExistsError, DeckNotFoundError
from pystudy_cli.core.objects import Card, Deck
from pystudy_cli.core.profile import StudyProfile
from pystudy_cli.tui.colours import (
    COL_ACCENT,
    COL_BASE,
    COL_CARD_DEF,
    COL_CARD_INDEX,
    COL_DARK_GREY,
    COL_DECK_INDEX,
    COL_DECK_NAME,
    COL_ERROR,
    COL_LIGHT_GREY,
    COL_SUCCESS,
    COL_UNANSWERED1,
    COL_UNANSWERED2,
    COL_WHITE,
    RESET,
    COL_NAME,
    col,
)
from pystudy_cli.tui.revision_modes import flashcard_mode, learn_mode, test_mode
from pystudy_cli.tui.ui_elements import (
    clear_screen,
    cursor_input,
    display_status_bar,
    int_convertible,
    show_hotkey,
)


def card_editor(deck: Deck):
    current_idx = 0

    while True:
        clear_screen()

        card_count = len(deck.cards)
        context = f"{deck.name}"
        if card_count > 0:
            context += f" > Card {current_idx + 1}/{card_count}"
        else:
            context += " > No Cards"
        display_status_bar(context)

        if not deck.cards:
            current_idx = 0
            print(f"{COL_LIGHT_GREY}Minimap")
            print(f"{COL_BASE}This deck doesn't have any cards yet!\n")
            show_hotkey("n", "insert new card")
            show_hotkey("q", "exit editor")

            key = cursor_input()
            if key == 'n':
                deck.cards.insert(current_idx + 1, Card('...', '...'))
            elif key == 'q':
                return

            continue

        card = deck.cards[current_idx]

        print(f"{COL_LIGHT_GREY}Minimap")

        minimap: str = ''
        for i in range(len(deck.cards)):
            if i%40 == 0 and i != 0:
                minimap += "\n"
            elif i%10 == 0 and i != 0:
                minimap += " "  # Whitespace every 10th card for visual separation

            colour = COL_ACCENT if i==current_idx else (COL_UNANSWERED2 if i%2==0 else COL_UNANSWERED1)
            minimap += colour + "▆▆"
        print(minimap)

        print()
        show_hotkey("z", "edit term", 12)
        show_hotkey("x", "edit definition", 12)
        show_hotkey("w", "previous", 12)
        show_hotkey("s", "next", 12)
        show_hotkey("shift-w", "move card up", 12)
        show_hotkey("shift-s", "move card down", 12)
        show_hotkey("n", "insert new card", 12)
        show_hotkey("d", "delete card", 12)
        show_hotkey("q", "exit editor", 12)

        print(f"\n{COL_ACCENT}Term: {COL_LIGHT_GREY}{card.term}")
        print(f"{COL_ACCENT}Def:  {COL_BASE}{card.definition}")

        key = cursor_input()

        # Edit term
        if key == 'z':
            print(f"{COL_LIGHT_GREY}\nEnter new term {COL_BASE}(or Enter to cancel)")
            new_term = input(f"{COL_ACCENT}> {COL_WHITE}").strip()
            if new_term:
                card.term = new_term

        # Edit definition
        elif key == 'x':
            print(f"{COL_LIGHT_GREY}\nEnter new definition {COL_BASE}(or Enter to cancel)")
            new_def = input(f"{COL_ACCENT}> {COL_WHITE}").strip()
            if new_def:
                card.definition = new_def

        # Previous card
        elif key == 'w':
            current_idx -= 1
            current_idx = max(0, current_idx)

        # Next card
        elif key == 's':
            current_idx += 1
            current_idx = min(len(deck.cards) - 1, current_idx)

        # Move card up
        elif key == 'W':
            if current_idx > 0:
                deck.cards[current_idx], deck.cards[current_idx-1] = deck.cards[current_idx-1], deck.cards[current_idx]  # Swaps a card with the card before it
                current_idx -= 1

        # Move card down
        elif key == 'S':
            if current_idx < len(deck.cards) - 1:
                deck.cards[current_idx], deck.cards[current_idx+1] = deck.cards[current_idx+1], deck.cards[current_idx]  # Swaps a card with the card after it
                current_idx += 1

        # Insert new card
        elif key == 'n':
            deck.cards.insert(current_idx + 1, Card('...', '...'))

        # Delete card
        elif key == 'd':
            deck.cards.pop(current_idx)
            if current_idx >= len(deck.cards):
                current_idx -= 1

        # Exit editor
        elif key == 'q':
            return

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
                print(f"{COL_CARD_DEF}{card.definition}{COL_BASE}")
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

def settings_menu(profile: StudyProfile):
    # A config entry is: (label, getter, setter, type)
    CONFIG_ENTRIES: list[tuple[str, Callable, Callable, type]] = [
        (
            "Warn Interrupt on Startup",
            lambda: profile.config.warn_interrupt,
            lambda value: setattr(profile.config, "warn_interrupt", value),
            bool
        )
    ]

    current_idx = 0

    while True:
        clear_screen()
        display_status_bar("Settings")

        for i, (label, getter, setter, type_) in enumerate(CONFIG_ENTRIES):
            cursor = f"{COL_ACCENT}> {COL_BASE}" if i == current_idx else "  "
            value = getter()

            # Formatting
            print(f"{cursor}{COL_BASE}{label:<29}{col(121)}{value}")

        print()
        print(f"{COL_LIGHT_GREY}w/s    {COL_BASE}select")
        print(f"{COL_LIGHT_GREY}a/d    {COL_BASE}change")
        print(f"{COL_LIGHT_GREY}q      {COL_BASE}return")

        key = readkey().lower()

        if key == 'w':
            current_idx = (current_idx - 1) % len(CONFIG_ENTRIES)

        elif key == 's':
            current_idx = (current_idx + 1) % len(CONFIG_ENTRIES)

        elif key == 'a' or key == 'd':
            label, getter, setter, type_ = CONFIG_ENTRIES[current_idx]
            value = getter()

            if type_ == bool:
                setter(not value)

            # future: int, enum, colour, keybind, etc.

        elif key == 'q':
            return


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
                status = save_data(profile)
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

def main():
    # Load data
    clear_screen()
    print(f"{COL_DARK_GREY}Loading data...{COL_BASE}")
    profile, status = load_data()

    if status == "success":
        print(f"{COL_SUCCESS}Data loaded!{COL_BASE}")
    elif status == "new":
        print(f"{COL_ERROR}No data file found. {COL_LIGHT_GREY}Making a new one...{COL_BASE}")
    elif status == "corrupted":
        print(f"{COL_ERROR}Data file seems corrupted. {COL_LIGHT_GREY}Making a new one...{COL_BASE}")
    else:
        print(f"{COL_ERROR}Unexpected error: {COL_WHITE}{status}{COL_ERROR}. {COL_LIGHT_GREY}Making a new one...{COL_BASE}")

    if profile.config.warn_interrupt:  # FIXME: doesn't show
        print(f"{COL_ERROR}\nWARNING: {COL_LIGHT_GREY}Unexpected exits (Ctrl-C, Ctrl-D) may result in data corruption or loss.{RESET}")

    # Initial setup
    if not profile.name:
        try:
            name = input(f"{COL_WHITE}\nWhat is your name? {COL_ACCENT}")  # TODO: Make name configurable in settings
        except (KeyboardInterrupt, EOFError):
            print(f"\n{RESET}Exited.")
            sys.exit(0)

        profile.name = name
        print()

    # Input loop
    while True:
        try:
            input_loop(profile)
            save_data(profile)
        except (KeyboardInterrupt, EOFError):
            print(f"{COL_ERROR}Interrupted!")
            print(f"\n{COL_LIGHT_GREY}Attempting panic save...{COL_BASE}")

            try:
                save_data(profile)
                print(f"{COL_SUCCESS}Data saved! {RESET}But don't push your luck next time!")
                print(f"{COL_ERROR}Panic save may contain malformed data.")
            except Exception:
                print(f"{COL_ERROR}Panic save failed. Your fault bucko!{RESET}")
            finally:
                sys.exit(1)

if __name__ == "__main__":
    main()
