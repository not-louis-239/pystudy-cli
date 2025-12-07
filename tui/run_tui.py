import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from datetime import datetime

from tui import clear_screen, show_hotkey
from core import save_data, load_data
from core import StudyProfile, Deck
from tui.colours import *
from core.exceptions import DeckError, DeckExistsError, DeckNotFoundError

def deck_menu(profile: StudyProfile, deck: Deck):
    while True:
        clear_screen()

        print(f"{BASE_COL}Deck Opened: {LIGHT_YELLOW}{deck.name}{BASE_COL}")

        print(f"{WHITE}\nWhat would you like to do?{BASE_COL}")
        show_hotkey('e', 'view/modify cards')
        show_hotkey('t', 'rename deck')
        show_hotkey('r', 'revise deck')
        show_hotkey('q', 'close deck')

        action = input(f"{AQUAMARINE}>{WHITE} ").strip().lower()

        # Add/remove cards
        if action == 'e':
            pass  # TODO

        # Rename deck
        elif action == 't':
            pass  # TODO

        # Revise deck
        elif action == 'r':
            pass  # TODO

        # Close deck
        elif action == 'q':
            return

def input_loop(profile: StudyProfile):
    print(f"{TITLE_COL}Python Study Suite v1.0.0{BASE_COL}")
    print(f"\n{WHITE}Hi, {col(123)}{profile.name}{WHITE}!{BASE_COL}")

    print(f"{WHITE}\nDecks{BASE_COL}")
    if not profile.decks:
        print(f"You don't have any decks yet!")
    else:
        for deck in profile.decks:
            print(deck.name)

    print(f"{WHITE}\nWhat would you like to do?{BASE_COL}")
    show_hotkey('n', 'new deck')
    show_hotkey('e', 'open deck')
    show_hotkey('r', 'delete deck')
    show_hotkey('q', 'quit')

    action = input(f"{AQUAMARINE}>{WHITE} ").strip().lower()

    # New deck
    if action == 'n':
        deck_name = input(f"{LGREY}\nEnter deck name: {BASE_COL}(or press Enter to cancel) {AQUAMARINE}")
        try:
            profile.new_deck(datetime.now().isoformat(), deck_name)
            input(f"{WHITE}Deck {AQUAMARINE}{deck_name}{WHITE} created. {BASE_COL}(Enter to return)")
        except DeckExistsError:
            input(f"{ERROR_COL}Invalid: Deck name must be unique. {BASE_COL}(Enter to return)")
        except DeckError:  # Empty name
            pass

    # Open deck
    elif action == 'e':
        if not profile.decks:
            print(f"{ERROR_COL}No decks to open. {LGREY}Try creating one first!{BASE_COL}")
        else:
            deck_name = input(f"\n{LGREY}Enter the name of a deck to open: {AQUAMARINE}")

            deck = next((deck for deck in profile.decks if deck.name == deck_name), None)
            if deck is None:
                input(f"{ERROR_COL}That deck doesn't exist!{BASE_COL} (Enter to return)")
            else:
                deck_menu(profile, deck)

    # Remove deck
    elif action == 'r':
        deck_name = input(f"{LGREY}\nEnter deck name to delete: {AQUAMARINE}")
        confirm = input(f"{LGREY}Are you sure you want to delete this deck (this action cannot be undone)? (y/n) {AQUAMARINE}").strip().lower()
        if confirm == 'y':
            try:
                profile.remove_deck(deck_name)
                input(f"{WHITE}Deck {AQUAMARINE}{deck_name}{WHITE} removed. {BASE_COL}(Enter to return)")
            except DeckNotFoundError:
                input(f"{ERROR_COL}Invalid: Deck does not exist. {BASE_COL}(Enter to return)")

    # Quit
    elif action == 'q':
        confirm = input(f"{LGREY}Are you sure you want to quit? (y/n) {WHITE}").strip().lower()
        if confirm == 'y':
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

    clear_screen()

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
    print()

    # Initial setup
    if not profile.name:
        name = input(f"{WHITE}\nWhat is your name? {AQUAMARINE}")
        profile.name = name
        print()

    # Input loop
    while True:
        input_loop(profile)

if __name__ == "__main__":
    main()