import sys
import math
from typing import Callable
from readchar import readkey
from datetime import datetime
from tui.revision_modes import flashcard_mode, learn_mode, test_mode
# import pygame as pg

from tui.ui_elements import clear_screen, show_hotkey, cursor_input, int_convertible
from core import save_data, load_data
from core import StudyProfile, Deck, Card
from core.constants import VERSION_NUM
from tui.colours import (
    col, WHITE, LGREY, DGREY, BASE_COL, RESET,
    TITLE_COL, AQUAMARINE, LIGHT_YELLOW, LIGHT_BLUE,
    ERROR_COL, SUCCESS_COL,
    CARD_DEF_COL, CARD_IDX_COL, CARD_TERM_COL,
    DECK_IDX_COL, DECK_NAME_COL,
)
from core.exceptions import DeckExistsError, DeckNotFoundError

# TODO: Card editor
def card_editor(deck: Deck):
    current_idx = 0

    while True:
        clear_screen()

        if not deck.cards:
            current_idx = 0
            print(f"{LGREY}Minimap")
            print(f"{BASE_COL}This deck doesn't have any cards yet!\n")
            show_hotkey("n", "insert new card", 9)
            show_hotkey("enter", "exit editor", 9)

            key = cursor_input()
            if key == 'n':
                deck.cards.insert(current_idx + 1, Card('...', '...'))
            elif key == '\n':
                return

            continue

        card = deck.cards[current_idx]

        print(f"{LGREY}Minimap")

        minimap: str = ''
        for i in range(len(deck.cards)):
            if i%40 == 0 and i != 0:
                minimap += "\n"
            elif i%10 == 0 and i != 0:
                minimap += " "  # Whitespace every 10th card for visual separation

            colour = AQUAMARINE if i==current_idx else col(60) if i%2==0 else col(103)
            minimap += colour + "▄▄"
        print(minimap)

        print()
        show_hotkey("z", "edit term", 12)
        show_hotkey("x", "edit definition", 12)
        show_hotkey("w", "previous", 12)
        show_hotkey("s", "next", 12)
        show_hotkey("shift-w", "move card up", 12)
        show_hotkey("shift-s", "move card down", 12)
        show_hotkey("n", "insert new card", 12)
        show_hotkey("o", "delete card", 12)
        show_hotkey("enter", "exit editor", 12)

        print(f"\n{col(189)}Editing Card {AQUAMARINE}{current_idx+1}{RESET}\n")
        print(f"{LIGHT_BLUE}Term: {LGREY}{card.term}")
        print(f"{LIGHT_BLUE}Def:  {BASE_COL}{card.definition}")

        key = cursor_input()

        # Edit term
        if key == 'z':
            print(f"{LGREY}\nEnter new term {BASE_COL}(or Enter to cancel)")
            new_term = input(f"{AQUAMARINE}> {WHITE}").strip()
            if new_term:
                card.term = new_term

        # Edit definition
        elif key == 'x':
            print(f"{LGREY}\nEnter new definition {BASE_COL}(or Enter to cancel)")
            new_def = input(f"{AQUAMARINE}> {WHITE}").strip()
            if new_def:
                card.definition = new_def

        # Previous card
        elif key == 'w':
            current_idx -= 1
            current_idx %= len(deck.cards)

        # Next card
        elif key == 's':
            current_idx += 1
            current_idx %= len(deck.cards)

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
        elif key == 'o':
            deck.cards.pop(current_idx)
            if current_idx >= len(deck.cards):
                current_idx -= 1

        # Exit editor
        elif key == '\n':
            return

def deck_menu(profile: StudyProfile, deck: Deck):
    while True:
        clear_screen(full=True)

        print(f"{BASE_COL}Deck: {LIGHT_YELLOW}{deck.name}{BASE_COL}\n")

        # Show cards
        if deck.cards:
            max_len = int(math.log10(len(deck.cards)))+1
            for i, card in enumerate(deck.cards, start=1):
                print(f"{CARD_IDX_COL}{i:>{max_len}}. {CARD_TERM_COL}{card.term}")
                print(f"{CARD_DEF_COL}{card.definition}{BASE_COL}")
        else:
            print(f"{BASE_COL}This deck doesn't have any cards yet!")

        print(f"{WHITE}\nWhat would you like to do?{BASE_COL}")
        show_hotkey('e', 'modify cards')
        show_hotkey('t', 'rename deck')
        show_hotkey('r', 'revise deck')
        show_hotkey('q', 'close deck')
        action = cursor_input()

        # Add/remove cards
        if action == 'e':
            card_editor(deck)

        # Rename deck
        elif action == 't':
            new_name = input(f"{LGREY}\nEnter new name (or press Enter to cancel): {AQUAMARINE}").strip()
            if not new_name:
                continue

            if int_convertible(new_name):
                input(f"{ERROR_COL}Invalid: Deck name cannot be a pure integer! {BASE_COL}(Enter to return)")
                continue

            existing_names = {d.name for d in profile.decks if d is not deck}
            if new_name in existing_names:
                input(f"{ERROR_COL}Invalid: That deck name is already taken by another deck! {BASE_COL}(Enter to return)")
                continue

            deck.name = new_name

        # Revise deck
        elif action == 'r':
            print(f"\n{WHITE}Select revision mode {LGREY}(or press Enter to cancel){WHITE}:")
            print(f"{LGREY}1    {BASE_COL}Flashcards")
            print(f"{LGREY}2    {BASE_COL}Learn")
            print(f"{LGREY}3    {BASE_COL}Practice Test")

            try:
                mode = cursor_input()
                if mode == '\n':
                    continue
                mode = int(mode)
                if not 1 <= mode <= 3:
                    raise ValueError
            except ValueError:
                input(f"{ERROR_COL}Invalid mode. {BASE_COL}(Enter to return)")
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

def config_menu(profile: StudyProfile):
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

        print(f"{LIGHT_YELLOW}Config{BASE_COL}\n")

        for i, (label, getter, setter, type_) in enumerate(CONFIG_ENTRIES):
            cursor = f"{AQUAMARINE}> {BASE_COL}" if i == current_idx else "  "
            value = getter()

            # Formatting
            print(f"{cursor}{BASE_COL}{label:<29}{col(121)}{value}")

        print()
        print(f"{LGREY}w/s    {BASE_COL}select")
        print(f"{LGREY}a/d    {BASE_COL}change")
        print(f"{LGREY}q      {BASE_COL}return")

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


def input_loop(profile: StudyProfile):
    print(f"{TITLE_COL}Python Study Suite v{VERSION_NUM}{BASE_COL}")
    print(f"\n{WHITE}Hi, {col(123)}{profile.name}{WHITE}!{BASE_COL}")

    print(f"{WHITE}\nDecks{BASE_COL}")
    if not profile.decks:
        print(f"You don't have any decks yet!")
    else:
        for i, deck in enumerate(profile.decks, 1):
            print(f"{DECK_IDX_COL}{i}. {DECK_NAME_COL}{deck.name} {DGREY}({len(deck.cards)} cards)")

    print(f"{WHITE}\nWhat would you like to do?{BASE_COL}")
    show_hotkey('n', 'new deck')
    show_hotkey('e', 'open deck')
    show_hotkey('r', 'delete deck')
    show_hotkey('c', 'view config')
    show_hotkey('q', 'quit')
    action = cursor_input()

    # New deck
    if action == 'n':
        deck_name = input(f"{LGREY}\nEnter deck name (or press Enter to cancel): {AQUAMARINE}").strip()
        if not deck_name:
            return
        if int_convertible(deck_name):
            input(f"{ERROR_COL}Invalid: Deck name cannot be a pure integer! {BASE_COL}(Enter to return)")
            return

        try:
            profile.new_deck(datetime.now().isoformat(), deck_name)
            input(f"{WHITE}Deck {AQUAMARINE}{deck_name}{WHITE} created. {BASE_COL}(Enter to return)")
        except DeckExistsError:
            input(f"{ERROR_COL}Invalid: Deck name must be unique. {BASE_COL}(Enter to return)")

    # Open deck
    elif action == 'e':
        if not profile.decks:
            input(f"{ERROR_COL}\nNo decks to open. {LGREY}Try creating one first! {BASE_COL}(Enter to return)")
            return

        deck_name = input(f"\n{LGREY}Enter the name (or index) of a deck to open (or press Enter to cancel): {AQUAMARINE}").strip()
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
                input(f"{ERROR_COL}That deck doesn't exist!{BASE_COL} (Enter to return)")
                return
            deck_menu(profile, deck)

        # Invalid index
        except IndexError:
            input(f"{ERROR_COL}Invalid index! (must be an integer from 1 to {len(profile.decks)}) {BASE_COL}(Enter to return)")
            return

    # Remove deck
    elif action == 'r':
        deck_name = input(f"{LGREY}\nEnter deck name to delete (or press Enter to cancel): {AQUAMARINE}").strip()
        if not deck_name:
            return

        confirm = input(f"{LGREY}Are you sure you want to delete this deck (this action cannot be undone)? (y/n) {AQUAMARINE}").strip().lower()
        if confirm == 'y':
            try:
                profile.remove_deck(deck_name)
                input(f"{WHITE}Deck {AQUAMARINE}{deck_name}{WHITE} removed. {BASE_COL}(Enter to return)")
            except DeckNotFoundError:
                input(f"{ERROR_COL}Invalid: Deck does not exist. {BASE_COL}(Enter to return)")

    # Config
    elif action == 'c':
        config_menu(profile)

    # Quit
    elif action == 'q':
        print(f"{LGREY}\nAre you sure you want to quit?")
        print(f"{BASE_COL}(q - quit | other - return)")
        confirm = cursor_input()

        if confirm == 'q':
            print(f"{BASE_COL}\nSaving data and exiting...")

            while True:
                status = save_data(profile.to_json())
                if status == 'success':
                    print(f"{SUCCESS_COL}Data saved!")
                    break

                retry = input(
                    f"{ERROR_COL}Saving data failed: {WHITE}{status}{ERROR_COL}. "
                    f"{LGREY}Retry? (y/n) {WHITE}"
                ).strip().lower()
                if retry != 'y':
                    print(f"{BASE_COL}Exiting without saving...")
                    break

            print(f"{BASE_COL}Goodbye!")
            sys.exit(0)

def main():
    # Load data
    clear_screen()
    print(f"{DGREY}Loading data...{BASE_COL}")
    raw_profile, status = load_data()
    profile = StudyProfile.from_json(raw_profile)

    if status == "success":
        print(f"{SUCCESS_COL}Data loaded!{BASE_COL}")
    elif status == "new":
        print(f"{ERROR_COL}No data file found. {LGREY}Making a new one...{BASE_COL}")
    elif status == "corrupted":
        print(f"{ERROR_COL}Data file seems corrupted. {LGREY}Making a new one...{BASE_COL}")
    else:
        print(f"{ERROR_COL}Unexpected error: {WHITE}{status}{ERROR_COL}. {LGREY}Making a new one...{BASE_COL}")

    if profile.config.warn_interrupt:
        print(f"{ERROR_COL}\nWARNING: {LGREY}Unexpected exits (Ctrl-C, Ctrl-D) may result in data corruption or loss.{RESET}")

    # Initial setup
    if not profile.name:
        name = input(f"{WHITE}\nWhat is your name? {AQUAMARINE}")
        profile.name = name
        print()

    # Input loop
    while True:
        try:
            input_loop(profile)
            save_data(profile.to_json())
            clear_screen()
        except (KeyboardInterrupt, EOFError):
            print(f"{ERROR_COL}Interrupted!")
            print(f"\n{LGREY}Attempting panic save...{BASE_COL}")
            try:
                save_data(profile.to_json())
                print(f"{SUCCESS_COL}Data saved! {RESET}But don't push your luck next time!")
                print(f"{ERROR_COL}Panic save may contain malformed data.")
            except Exception:
                print(f"{ERROR_COL}Panic save failed. Your fault bucko!{RESET}")
            finally:
                sys.exit(1)

if __name__ == "__main__":
    main()