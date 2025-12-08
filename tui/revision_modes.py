# XXX: This module has a chance to break at times.

import random
import difflib
from core.objects import Deck
from core.constants import FAMILIARITY_LEVELS, NUM_MCQ_OPTIONS
from tui.ui_elements import clear_screen, show_hotkey, cursor_input, display_status_bar
from tui.colours import (
    BASE_COL, DARK_GREY, LIGHT_GREY, WHITE, LEARNING_COL,
    RESET,
    ACCENT_COL, SUCCESS_COL, ERROR_COL,
    CARD_TERM_COL, CARD_DEF_COL
)

class Question:
    """Base class for Question objects."""
    def __init__(self, text: str, correct_ans: str):
        self.text = text
        self.correct_ans = correct_ans
        self.user_ans = ""

    def is_correct(self, threshold: float, smart_grading: bool = False) -> bool:
        if smart_grading:
            similarity = difflib.SequenceMatcher(None, self.user_ans.lower(), self.correct_ans.lower()).ratio()
            return similarity >= threshold
        return self.user_ans.strip().lower() == self.correct_ans.strip().lower()

class MCQuestion(Question):
    def __init__(
            self, text: str, options: list[str], correct_ans_idx: int):
        self.text = text
        self.options = options
        self.correct_ans_idx = correct_ans_idx
        self.user_ans_idx: int | None = None

    def is_correct(self) -> bool:
        if self.user_ans_idx is None:
            return False
        return self.user_ans_idx == self.correct_ans_idx

def gen_written_qs(deck: Deck, num_questions: int) -> list[Question]:
    cards_sample = random.sample(deck.cards, min(num_questions, len(deck.cards)))
    questions = [
        Question(card.term, card.definition)
        for card in cards_sample
    ]
    return questions

def gen_mcqs(deck: Deck, num_questions: int) -> list[MCQuestion]:
    if len(deck.cards) < NUM_MCQ_OPTIONS:
        # Not enough cards to generate meaningful distractors
        return []

    all_defs: list[str] = [c.definition for c in deck.cards]
    cards_sample = random.sample(deck.cards, min(num_questions, len(deck.cards)))
    questions = []

    for card in cards_sample:
        # Remove this card's def without identity weirdness
        distractor_pool = [d for d in all_defs if d != card.definition]

        # Select distractors
        distractors = random.sample(distractor_pool, NUM_MCQ_OPTIONS - 1)

        options: list[str] = [*distractors, card.definition]
        random.shuffle(options)
        correct_idx = options.index(card.definition)

        questions.append(MCQuestion(card.term, options, correct_idx))
    return questions

def flashcard_mode(deck: Deck):
    if not deck.cards:
        input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
        return

    # Setup
    cards_to_review = list(deck.cards)

    clear_screen()
    display_status_bar(f"Flashcards | {deck.name}")

    print(f"\n{WHITE}Shuffle cards before starting? (y/n) {BASE_COL}")
    shuffle: bool = cursor_input().lower() == 'y'
    if shuffle:
        random.shuffle(cards_to_review)

    # Main loop
    while True:
        learning_cards = []
        known_cards = []

        # Round loop
        for i, card in enumerate(cards_to_review):
            revealed = False

            # Card display loop
            while True:
                clear_screen()
                context = (f"Flashcards | {deck.name} | Card {i+1}/{len(cards_to_review)} | "
                           f"Learning: {len(learning_cards)} | Known: {len(known_cards)}")
                display_status_bar(context)

                # Card UI
                print(f"{CARD_TERM_COL}Term: {BASE_COL}{card.term}")
                if revealed:
                    print(f"{CARD_DEF_COL}Def:  {BASE_COL}{card.definition}\n")
                    show_hotkey('l', f'mark {LEARNING_COL}learning')
                    show_hotkey('k', f'mark {SUCCESS_COL}known')
                    show_hotkey('q', 'exit session')
                else:
                    print(f"{CARD_DEF_COL}Def:  {DARK_GREY}(Press space to reveal){BASE_COL}\n")
                    show_hotkey('space', 'reveal', 9)
                    show_hotkey('q', 'exit session', 9)

                key = cursor_input()

                if key == 'q':
                    print(f"\n{LIGHT_GREY}Are you sure you want to exit? (y/n)")
                    if cursor_input().lower() == 'y':
                        return
                    continue  # Go back to the card display loop

                if key == ' ':
                    revealed = True
                    continue

                if revealed:
                    if key == 'l':
                        learning_cards.append(card)
                        break
                    elif key == 'k':
                        known_cards.append(card)
                        break

        # End of round display loop
        while True:
            clear_screen()
            display_status_bar(f"Flashcards | {deck.name} | Round Complete")
            print(f"{SUCCESS_COL}Round Complete!{RESET}\n")
            print(f"{WHITE}* {LEARNING_COL}Learning: {BASE_COL}{len(learning_cards)} cards")
            print(f"{WHITE}* {SUCCESS_COL}Known:    {BASE_COL}{len(known_cards)} cards")

            # All cards known
            if not learning_cards:
                print(f"\n{SUCCESS_COL}Congratulations! {ACCENT_COL}You've learned all the cards in this session!{RESET}")
                show_hotkey('r', 'restart session')
                show_hotkey('q', 'return to menu')

                choice = cursor_input().lower()
                if choice == 'r':
                    cards_to_review = list(deck.cards)
                    if shuffle:
                        random.shuffle(cards_to_review)
                        break  # Return to beginning of main loop
                elif choice == 'q':
                    return
                continue  # to next iteration of display loop

            # Still learning some cards
            print(f"\n{WHITE}What next?{RESET}")
            show_hotkey('l', 'review learning cards')
            show_hotkey('r', 'restart session from beginning')
            show_hotkey('q', 'exit to menu')

            choice = cursor_input().lower()
            if choice == 'l':
                cards_to_review = learning_cards
                if shuffle:
                    random.shuffle(cards_to_review)
                break  # Next round
            elif choice == 'r':
                cards_to_review = list(deck.cards)
                if shuffle:
                    random.shuffle(cards_to_review)
                break  # Next round
            elif choice == 'q':
                return

def learn_mode(deck: Deck) -> None:
    if not deck.cards:
        input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
        return

    while True:
        pass

def test_mode(deck: Deck) -> None:
    if not deck.cards:
        input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
        return

    while True:
        pass