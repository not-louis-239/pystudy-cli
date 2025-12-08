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
    def __init__(self, text: str, correct_ans: str):
        self.text = text
        self.correct_ans = correct_ans
        self.user_ans = ""

    def is_correct(self, smart_grading: bool = False, threshold: float = 0.8) -> bool:
        if smart_grading:
            similarity = difflib.SequenceMatcher(None, self.user_ans.lower(), self.correct_ans.lower()).ratio()
            return similarity >= threshold
        return self.user_ans.strip().lower() == self.correct_ans.strip().lower()

class MultipleChoiceQuestion(Question):
    def __init__(self, text: str, options: list[str], correct_ans_idx: int, user_answer_idx: int = -1):  # -1 = not selected
        self.text = text
        self.options = options
        self.correct_ans_idx = correct_ans_idx
        self.user_ans_idx = user_answer_idx

    def is_correct(self) -> bool: # smart_grading ignored for MCQ
        try:
            return int(self.user_ans_idx) - 1 == self.correct_ans_idx
        except ValueError:
            return False

def gen_written_qs(deck: Deck, num_questions: int) -> list[Question]:
    questions = []
    cards_sample = random.sample(deck.cards, min(num_questions, len(deck.cards)))
    for card in cards_sample:
        questions.append(Question(card.term, card.definition))
    return questions

def gen_mcqs(deck: Deck, num_questions: int) -> list[MultipleChoiceQuestion]:
    if len(deck.cards) < NUM_MCQ_OPTIONS:
        # Not enough cards to generate meaningful distractors
        return []

    questions = []
    cards_sample = random.sample(deck.cards, min(num_questions, len(deck.cards)))

    for card in cards_sample:
        # Select 3 distractors
        distractors = random.sample([c.definition for c in deck.cards if c != card], NUM_MCQ_OPTIONS-1)

        options = distractors + [card.definition]
        random.shuffle(options)
        correct_idx = options.index(card.definition)

        questions.append(MultipleChoiceQuestion(card.term, options, correct_idx))
    return questions

def flashcard_mode(deck: Deck):
    if not deck.cards:
        input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
        return

    # Initial setup
    cards_to_review = list(deck.cards)

    clear_screen()
    display_status_bar(f"Flashcards | {deck.name}")

    print(f"\n{WHITE}Shuffle cards before starting? (y/n) {BASE_COL}")
    shuffle_choice = cursor_input().lower()
    if shuffle_choice == 'y':
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
                print(f"\n{CARD_TERM_COL}Term: {BASE_COL}{card.term}\n")

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

                if not revealed and key == ' ':
                    revealed = True
                    continue

                if revealed:
                    if key == 'l':
                        learning_cards.append(card)
                        break  # Go to next card in the round
                    elif key == 'k':
                        known_cards.append(card)
                        break  # Go to next card in the round

        # End of round
        clear_screen()
        display_status_bar(f"Flashcards | {deck.name} | Round Complete")

        print(f"\n{SUCCESS_COL}Round Complete!{RESET}")
        print(f"{WHITE}* {LEARNING_COL}Learning: {BASE_COL}{len(learning_cards)} cards")
        print(f"{WHITE}* {SUCCESS_COL}Known:    {BASE_COL}{len(known_cards)} cards")

        # All cards known
        if not learning_cards:
            print(f"\n{SUCCESS_COL}Congratulations! You've learned all the cards in this session!{RESET}")
            show_hotkey('r', 'restart session')
            show_hotkey('q', 'return to menu')

            while True:
                choice = cursor_input().lower()
                if choice == 'r':
                    cards_to_review = list(deck.cards)
                    if shuffle_choice == 'y': random.shuffle(cards_to_review)
                    break
                elif choice == 'q':
                    return
            continue  # To next full session

        # Some cards still learning
        print(f"\n{WHITE}What next?{RESET}")
        show_hotkey('l', 'review learning cards')
        show_hotkey('r', 'restart session from beginning')
        show_hotkey('q', 'exit to menu')

        while True:
            choice = cursor_input().lower()
            if choice == 'l':
                cards_to_review = learning_cards
                # We don't ask to shuffle again, use initial choice
                if shuffle_choice == 'y': random.shuffle(cards_to_review)
                break
            elif choice == 'r':
                cards_to_review = list(deck.cards)
                if shuffle_choice == 'y': random.shuffle(cards_to_review)
                break
            elif choice == 'q':
                return

        if choice in ('l', 'r'):
            continue

def learn_mode(deck: Deck) -> None:
    if not deck.cards:
        input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
        return

    # Config
    clear_screen()
    display_status_bar(f"Learn Mode | {deck.name} | Setup")

    # Get cards per round
    while True:
        try:
            cards_per_round_str = input(f"{WHITE}How many cards per round? (1-{len(deck.cards)}) (default: 7): {ACCENT_COL}")
            if not cards_per_round_str:
                cards_per_round = 7
                break
            cards_per_round = int(cards_per_round_str)
            if 1 <= cards_per_round <= len(deck.cards):
                break
            print(f"{ERROR_COL}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")
        except ValueError:
            print(f"{ERROR_COL}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")

    # Get shuffle option
    print(f"{WHITE}Shuffle cards? (y/n) (default: y): {ACCENT_COL}")
    shuffle = cursor_input().lower() in ['y', '\n']

    # Get smart grading option
    print(f"{WHITE}Enable smart grading? (y/n) (default: y): {ACCENT_COL}")
    smart_grading = cursor_input().lower() in ['y', '\n']

    # Main loop
    while True:
        # Card selection
        non_mastered_cards = [card for card in deck.cards if card.familiarity_level != len(FAMILIARITY_LEVELS) - 1]

        if not non_mastered_cards:
            # All cards mastered
            clear_screen()
            display_status_bar(f"Learn Mode | {deck.name} | Complete!")
            print(f"\n{SUCCESS_COL}You've mastered everything!{RESET}")
            print(f"\n{WHITE}What now?{RESET}")
            show_hotkey('r', 'reset progress and restart')
            show_hotkey('q', 'quit to menu')

            while True:
                choice = cursor_input().lower()
                if choice == 'r':
                    for card in deck.cards:
                        card.familiarity_level = 0
                    break  # Go to beginning of main while loop
                elif choice == 'q':
                    return
            continue

        # Sort by familiarity to prioritize less known cards
        if shuffle:
            random.shuffle(non_mastered_cards)
        else:
            non_mastered_cards.sort(key=lambda c: c.familiarity_level)  # Ascending by default

        round_cards = non_mastered_cards[:cards_per_round]

        # Round loop
        for i, card in enumerate(round_cards):
            clear_screen()
            display_status_bar(f"Learn Mode | {deck.name} | Card {i+1}/{len(round_cards)}")

            print(f"\n{CARD_TERM_COL}Term:      {BASE_COL}{card.term}\n")

            user_answer = input(f"{WHITE}Your Def: {ACCENT_COL}")

            # Grading
            is_correct = False
            if smart_grading:
                similarity = difflib.SequenceMatcher(None, user_answer.lower(), card.definition.lower()).ratio()
                if similarity >= 0.8:  # TODO: Make this configurable
                    is_correct = True
            else:
                if user_answer.strip().lower() == card.definition.strip().lower():
                    is_correct = True

            # Feedback
            clear_screen()
            display_status_bar(f"Learn Mode | {deck.name} | Card {i+1}/{len(round_cards)}")
            print(f"\n{CARD_TERM_COL}Term: {BASE_COL}{card.term}\n")

            if is_correct:
                card.on_correct()
                print(f"{SUCCESS_COL}Correct!{RESET}")
                if user_answer == card.definition:
                    print(f"{LIGHT_GREY}Your answer:    {BASE_COL}{card.definition}")
                else:
                    print(f"{LIGHT_GREY}Your answer:    {BASE_COL}{user_answer}")
                    print(f"{LIGHT_GREY}Exact answer:   {BASE_COL}{card.definition}")
            else:
                card.on_incorrect()
                print(f"{ERROR_COL}Incorrect.{RESET}")
                print(f"{LIGHT_GREY}Your answer:    {BASE_COL}{user_answer}")
                print(f"{LIGHT_GREY}Correct answer: {BASE_COL}{card.definition}")

            print(f"{LIGHT_GREY}Familiarity: {FAMILIARITY_LEVELS[card.familiarity_level]}")
            input(f"\n{DARK_GREY}(Press Enter to continue){RESET}")

        # End of round
        clear_screen()
        display_status_bar(f"Learn Mode | {deck.name} | Round Complete")
        print(f"\n{SUCCESS_COL}Round Complete!{RESET}")
        print("\nWhat next?")
        show_hotkey('c', 'Continue to next round')
        show_hotkey('q', 'Quit to menu')

        while True:
            choice = cursor_input().lower()
            if choice == 'c':
                break
            elif choice == 'q':
                return
        continue

def test_mode(deck: Deck) -> None:  # XXX: can't exit after entering
    while True:
        if not deck.cards:
            input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
            return

        # Configuration
        while True:
            clear_screen()
            display_status_bar(f"Test Mode | {deck.name} | Setup")

            # Get number of questions
            while True:
                try:
                    num_questions_str = input(f"{WHITE}How many questions? (1-{len(deck.cards)}) (defualt: 10): {ACCENT_COL}")
                    if not num_questions_str:
                        num_questions = min(10, len(deck.cards))  # TODO: Make this configurable
                        break
                    num_questions = int(num_questions_str)
                    if 1 <= num_questions <= len(deck.cards):
                        break
                    print(f"{ERROR_COL}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")
                except ValueError:
                    print(f"{ERROR_COL}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")

            # Get question type
            print(f"\n{WHITE}Select question type:{RESET}")  # TODO: User should be able to choose both
            print(f"{LIGHT_GREY}1    {BASE_COL}multiple choice")
            print(f"{LIGHT_GREY}2    {BASE_COL}written answer")

            question_type = cursor_input()

            questions = []
            if question_type == '1':
                if len(deck.cards) < 4:
                    input(f"{ERROR_COL}Not enough cards for Multiple Choice (min 4).{RESET} (Enter to continue)")
                    continue
                questions = gen_mcqs(deck, num_questions)
                break
            elif question_type == '2':
                questions = gen_written_qs(deck, num_questions)
                break
            else:
                input(f"{ERROR_COL}Invalid selection.{RESET} (Enter to continue)")

        # Test Taking
        for i, q in enumerate(questions):
            clear_screen()
            display_status_bar(f"Test Mode | {deck.name} | Question {i+1}/{len(questions)}")
            print(f"\n{WHITE}{q.text}{RESET}\n")

            if isinstance(q, MultipleChoiceQuestion):  # TODO: User should be able to navigate questions with minimap
                for j, option in enumerate(q.options, 1):
                    print(f"{LIGHT_GREY}{j}. {BASE_COL}{option}")
                q.user_ans = input(f"\n{WHITE}Your choice (1-{NUM_MCQ_OPTIONS}): {ACCENT_COL}")
            else: # Written Answer
                q.user_ans = input(f"{WHITE}Your answer: {ACCENT_COL}")

        # Results
        clear_screen()
        display_status_bar(f"Test Mode | {deck.name} | Results")

        score = sum(1 for q in questions if q.is_correct())
        print(f"\n{WHITE}Test Complete! Your score: {SUCCESS_COL if score == len(questions) else ACCENT_COL}{score}/{len(questions)}{RESET}\n")

        for i, q in enumerate(questions):
            is_correct = q.is_correct()
            result_icon = f"{SUCCESS_COL}✔" if is_correct else f"{ERROR_COL}✘"
            print(f"{result_icon} {WHITE}Q{i+1}: {q.text}{RESET}")
            if isinstance(q, MultipleChoiceQuestion):
                try:
                    user_choice_idx = int(q.user_ans) - 1  # XXX: idx 0 -> -1, which yields the last answer
                    user_answer_text = q.options[user_choice_idx]
                except (ValueError, IndexError):
                    user_answer_text = "Invalid choice"
            else:
                user_answer_text = q.user_ans

            print(f"{LIGHT_GREY}  Your answer:   {BASE_COL if is_correct else ERROR_COL}{user_answer_text}{RESET}")
            if not is_correct:
                print(f"{LIGHT_GREY}  Correct answer: {SUCCESS_COL}{q.correct_ans}{RESET}")  # XXX: breaks on MCQs
            print()

        # Post-test menu
        print(f"\n{WHITE}What next?{RESET}")
        show_hotkey('r', 'retry same test')
        show_hotkey('n', 'new test')
        show_hotkey('q', 'quit to menu')

        while True:
            choice = cursor_input().lower()
            if choice == 'r':
                # This is complex to implement without saving the 'questions' list somewhere.
                # For now, we can just re-generate, which is effectively a new test with same settings.
                print("Re-generating test with same settings...")
                # A more robust implementation would save and re-run. For now, we loop.
                # This break will be caught by an outer loop if we add one.
                # For simplicity of this implementation, we will treat it like 'n'.
                break # Re-run the while True loop in test_mode
            elif choice == 'n':
                break # Re-run the while True loop in test_mode
            elif choice == 'q':
                return

        # Loop back to the start of the function if user chose 'r' or 'n'
        if choice in ('r', 'n'):
            # This recursive call will work, but it can lead to a deep call stack.
            # A while loop is better practice. For this case, it's simple enough.
            continue