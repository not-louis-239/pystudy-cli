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



from pystudy_cli.core.objects import Card, Deck
from pystudy_cli.tui.colours import (
    COL_ACCENT,
    COL_BASE,
    COL_LIGHT_GREY,
    COL_UNANSWERED1,
    COL_UNANSWERED2,
    COL_WHITE,
)
from pystudy_cli.tui.ui_elements import (
    clear_screen,
    cursor_input,
    display_status_bar,
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
        print(f"{COL_ACCENT}Def:  {COL_BASE}{card.def_}")

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
                card.def_ = new_def

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
