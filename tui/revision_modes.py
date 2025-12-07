import random
import difflib
from core.objects import Deck
from core.constants import FAMILIARITY_LEVELS
from tui.ui_elements import clear_screen, show_hotkey, cursor_input, display_status_bar
from tui.colours import (
    BASE_COL, DARK_GREY, LIGHT_GREY, WHITE,
    RESET,
    ACCENT_COL, SUCCESS_COL, ERROR_COL,
    CARD_TERM_COL, CARD_DEF_COL
)


class Question:
    def __init__(self, question_text: str, correct_answer: str):
        self.question_text = question_text
        self.correct_answer = correct_answer
        self.user_answer = ""
    
    def is_correct(self, smart_grading: bool = False) -> bool:
        if smart_grading:
            similarity = difflib.SequenceMatcher(None, self.user_answer.lower(), self.correct_answer.lower()).ratio()
            return similarity >= 0.8
        return self.user_answer.strip().lower() == self.correct_answer.strip().lower()

class MultipleChoiceQuestion(Question):
    def __init__(self, question_text: str, options: list[str], correct_answer_idx: int):
        super().__init__(question_text, options[correct_answer_idx])
        self.options = options
        self.correct_answer_idx = correct_answer_idx
    
    def is_correct(self, smart_grading: bool = False) -> bool: # smart_grading ignored for MCQ
        try:
            return int(self.user_answer) - 1 == self.correct_answer_idx
        except (ValueError, IndexError):
            return False


def generate_written_questions(deck: Deck, num_questions: int) -> list[Question]:
    questions = []
    cards_sample = random.sample(deck.cards, min(num_questions, len(deck.cards)))
    for card in cards_sample:
        q_text = f"What is the definition of '{card.term}'?"
        questions.append(Question(q_text, card.definition))
    return questions

def generate_mcq_questions(deck: Deck, num_questions: int) -> list[MultipleChoiceQuestion]:
    if len(deck.cards) < 4:
        # Not enough cards to generate meaningful distractors
        return []

    questions = []
    cards_sample = random.sample(deck.cards, min(num_questions, len(deck.cards)))
    
    for card in cards_sample:
        q_text = f"What is the definition of '{card.term}'?"
        
        # Select 3 distractors
        distractors = random.sample([c.definition for c in deck.cards if c != card], 3)
        
        options = distractors + [card.definition]
        random.shuffle(options)
        correct_idx = options.index(card.definition)
        
        questions.append(MultipleChoiceQuestion(q_text, options, correct_idx))
    return questions


def flashcard_mode(deck: Deck):
    if not deck.cards:
        input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
        return

    # --- Initial Setup ---
    cards_to_review = list(deck.cards)

    clear_screen()
    display_status_bar(f"Flashcards | {deck.name}")
    print(f"\n{WHITE}Shuffle cards before starting? (y/n){BASE_COL}")
    shuffle_choice = cursor_input().lower()
    if shuffle_choice == 'y':
        random.shuffle(cards_to_review)

    # --- Main Loop ---
    while True:
        learning_cards = []
        known_cards = []

        # --- Round Loop ---
        for i, card in enumerate(cards_to_review):
            revealed = False
            # --- Card Display Loop ---
            while True:
                clear_screen()
                context = (f"Flashcards | {deck.name} | Card {i+1}/{len(cards_to_review)} | "
                           f"Learning: {len(learning_cards)} | Known: {len(known_cards)}")
                display_status_bar(context)

                # Card UI
                print(f"\n{CARD_TERM_COL}Term: {BASE_COL}{card.term}\n")

                if revealed:
                    print(f"{CARD_DEF_COL}Definition: {BASE_COL}{card.definition}\n")
                    show_hotkey('l', 'Mark as Learning')
                    show_hotkey('k', 'Mark as Known')
                    show_hotkey('q', 'Exit Session')
                else:
                    print(f"{CARD_DEF_COL}Definition: {DARK_GREY}(Press space to reveal){BASE_COL}\n")
                    show_hotkey('space', 'Reveal')
                    show_hotkey('q', 'Exit Session')

                key = cursor_input()

                if key == 'q':
                    print(f"\n{LIGHT_GREY}Are you sure you want to exit? (y/n){ACCENT_COL}")
                    if cursor_input().lower() == 'y':
                        return
                    else:
                        continue # Go back to the card display loop

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

        # --- Round End ---
        clear_screen()
        display_status_bar(f"Flashcards | {deck.name} | Round Complete")

        print(f"\n{SUCCESS_COL}Round Complete!{RESET}")
        print(f"  {ACCENT_COL}Learning:{BASE_COL} {len(learning_cards)} cards")
        print(f"  {SUCCESS_COL}Known:{BASE_COL}    {len(known_cards)} cards")

        # --- All Cards Known ---
        if not learning_cards:
            print(f"\n{SUCCESS_COL}Congratulations! You've learned all the cards in this session!{RESET}")
            show_hotkey('r', 'Restart session')
            show_hotkey('q', 'Exit to menu')

            while True:
                choice = cursor_input().lower()
                if choice == 'r':
                    cards_to_review = list(deck.cards)
                    if shuffle_choice == 'y': random.shuffle(cards_to_review)
                    break
                elif choice == 'q':
                    return
            if choice == 'r':
                continue # To next full session

        # --- Some Cards Still Learning ---
        print(f"\n{WHITE}What next?{RESET}")
        show_hotkey('l', 'Review "Learning" cards')
        show_hotkey('r', 'Restart session from beginning')
        show_hotkey('q', 'Exit to menu')

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
            continue # To next round (either learning or full)


def learn_mode(deck: Deck) -> None:
    if not deck.cards:
        input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
        return

    # --- Configuration ---
    clear_screen()
    display_status_bar(f"Learn Mode | {deck.name} | Setup")

    # Get cards per round
    while True:
        try:
            cards_per_round_str = input(f"{WHITE}How many cards per round? (1-{len(deck.cards)}) [default: 10]: {ACCENT_COL}")
            if not cards_per_round_str:
                cards_per_round = 10
                break
            cards_per_round = int(cards_per_round_str)
            if 1 <= cards_per_round <= len(deck.cards):
                break
            else:
                print(f"{ERROR_COL}Please enter a number between 1 and {len(deck.cards)}.{RESET}")
        except ValueError:
            print(f"{ERROR_COL}Invalid input. Please enter a number.{RESET}")
    
    # Get shuffle option
    shuffle_choice = input(f"{WHITE}Shuffle cards? (y/n) [default: y]: {ACCENT_COL}").lower()
    shuffle_on = shuffle_choice != 'n'

    # Get smart grading option
    smart_grading_choice = input(f"{WHITE}Enable smart grading? (y/n) [default: y]: {ACCENT_COL}").lower()
    smart_grading_on = smart_grading_choice != 'n'
    similarity_threshold = 0.8 # for smart grading

    # --- Main Session Loop ---
    while True:
        # --- Card Selection ---
        non_mastered_cards = [card for card in deck.cards if card.familiarity_level != "Mastered"]

        if not non_mastered_cards:
            # --- Session Complete ---
            clear_screen()
            display_status_bar(f"Learn Mode | {deck.name} | Complete!")
            print(f"\n{SUCCESS_COL}Congratulations! You have mastered all cards in this deck!{RESET}")
            print(f"\n{WHITE}Would you like to reset all progress and start over?{RESET}")
            show_hotkey('r', 'Reset and restart')
            show_hotkey('q', 'Quit to menu')
            
            while True:
                choice = cursor_input().lower()
                if choice == 'r':
                    for card in deck.cards:
                        card.familiarity_level = "New"
                    # Go to beginning of main while loop
                    break 
                elif choice == 'q':
                    return
            if choice == 'r':
                continue

        # Sort by familiarity to prioritize less known cards
        familiarity_map = {level: i for i, level in enumerate(FAMILIARITY_LEVELS)}
        non_mastered_cards.sort(key=lambda c: familiarity_map[c.familiarity_level])

        if shuffle_on:
            random.shuffle(non_mastered_cards)

        round_cards = non_mastered_cards[:cards_per_round]

        # --- Round Loop ---
        for i, card in enumerate(round_cards):
            clear_screen()
            display_status_bar(f"Learn Mode | {deck.name} | Card {i+1}/{len(round_cards)}")
            
            print(f"\n{CARD_TERM_COL}Term: {BASE_COL}{card.term}\n")
            
            user_answer = input(f"{WHITE}Your Definition: {ACCENT_COL}")
            
            # --- Grading ---
            correct_def = card.definition
            is_correct = False
            if smart_grading_on:
                similarity = difflib.SequenceMatcher(None, user_answer.lower(), correct_def.lower()).ratio()
                if similarity >= similarity_threshold:
                    is_correct = True
            else:
                if user_answer.strip().lower() == correct_def.strip().lower():
                    is_correct = True
            
            # --- Feedback ---
            clear_screen()
            display_status_bar(f"Learn Mode | {deck.name} | Card {i+1}/{len(round_cards)}")
            print(f"\n{CARD_TERM_COL}Term: {BASE_COL}{card.term}\n")
            
            if is_correct:
                card.on_correct()
                print(f"{SUCCESS_COL}Correct!{RESET}")
                print(f"{LIGHT_GREY}Familiarity: {card.familiarity_level}")
            else:
                card.on_incorrect()
                print(f"{ERROR_COL}Incorrect.{RESET}")
                print(f"{LIGHT_GREY}Your answer: {BASE_COL}{user_answer}")
                print(f"{LIGHT_GREY}Correct answer: {BASE_COL}{correct_def}")
                print(f"{LIGHT_GREY}Familiarity: {card.familiarity_level}")

            input(f"\n{DARK_GREY}(Press Enter to continue...){RESET}")

        # --- End of Round ---
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
        if choice == 'c':
            continue


def test_mode(deck: Deck) -> None:
    if not deck.cards:
        input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
        return

    # --- Configuration ---
    while True:
        clear_screen()
        display_status_bar(f"Test Mode | {deck.name} | Setup")

        # Get number of questions
        while True:
            try:
                num_questions_str = input(f"{WHITE}How many questions? (1-{len(deck.cards)}) [default: 10]: {ACCENT_COL}")
                if not num_questions_str:
                    num_questions = min(10, len(deck.cards))
                    break
                num_questions = int(num_questions_str)
                if 1 <= num_questions <= len(deck.cards):
                    break
                else:
                    print(f"{ERROR_COL}Please enter a number between 1 and {len(deck.cards)}.{RESET}")
            except ValueError:
                print(f"{ERROR_COL}Invalid input. Please enter a number.{RESET}")

        # Get question type
        print(f"\n{WHITE}Select question type:{RESET}")
        print(f"{LIGHT_GREY}1    {BASE_COL}Multiple Choice")
        print(f"{LIGHT_GREY}2    {BASE_COL}Written Answer")
        
        question_type = cursor_input()

        questions = []
        if question_type == '1':
            if len(deck.cards) < 4:
                input(f"{ERROR_COL}Not enough cards for Multiple Choice (min 4).{RESET} (Enter to continue)")
                continue
            questions = generate_mcq_questions(deck, num_questions)
            break
        elif question_type == '2':
            questions = generate_written_questions(deck, num_questions)
            break
        else:
            input(f"{ERROR_COL}Invalid selection.{RESET} (Enter to continue)")


    # --- Test Taking ---
    for i, q in enumerate(questions):
        clear_screen()
        display_status_bar(f"Test Mode | {deck.name} | Question {i+1}/{len(questions)}")
        print(f"\n{WHITE}{q.question_text}{RESET}\n")

        if isinstance(q, MultipleChoiceQuestion):
            for j, option in enumerate(q.options):
                print(f"{LIGHT_GREY}{j+1}. {BASE_COL}{option}")
            q.user_answer = input(f"\n{WHITE}Your choice (1-4): {ACCENT_COL}")
        else: # Written Answer
            q.user_answer = input(f"{WHITE}Your answer: {ACCENT_COL}")

    # --- Results ---
    clear_screen()
    display_status_bar(f"Test Mode | {deck.name} | Results")
    
    score = sum(1 for q in questions if q.is_correct())
    print(f"\n{WHITE}Test Complete! Your score: {SUCCESS_COL if score == len(questions) else ACCENT_COL}{score}/{len(questions)}{RESET}\n")

    for i, q in enumerate(questions):
        is_correct = q.is_correct()
        result_icon = f"{SUCCESS_COL}✔" if is_correct else f"{ERROR_COL}✘"
        print(f"{result_icon} {WHITE}Q{i+1}: {q.question_text}{RESET}")
        if isinstance(q, MultipleChoiceQuestion):
            try:
                user_choice_idx = int(q.user_answer) - 1
                user_answer_text = q.options[user_choice_idx]
            except (ValueError, IndexError):
                user_answer_text = "Invalid choice"
        else:
            user_answer_text = q.user_answer
            
        print(f"{LIGHT_GREY}  Your answer:   {BASE_COL if is_correct else ERROR_COL}{user_answer_text}{RESET}")
        if not is_correct:
            print(f"{LIGHT_GREY}  Correct answer: {SUCCESS_COL}{q.correct_answer}{RESET}")
        print()

    # --- Post-Test Menu ---
    print(f"\n{WHITE}What next?{RESET}")
    show_hotkey('r', 'Retry same test')
    show_hotkey('n', 'New test')
    show_hotkey('q', 'Quit to menu')
    
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
        test_mode(deck)