import random
import difflib
from core.objects import Deck
from core.constants import (
    FAMILIARITY_LEVELS, NUM_MCQ_OPTIONS, DEFAULT_CARDS_PER_ROUND,
    DEFAULT_SMART_GRADING_STRICTNESS, DEFAULT_PRACTICE_TEST_LEN
)
from tui.ui_elements import clear_screen, show_hotkey, cursor_input, display_status_bar
from tui.colours import (
    BASE_COL, DARK_GREY, LIGHT_GREY, WHITE, LEARNING_COL, RESET,
    ACCENT_COL, SUCCESS_COL, ERROR_COL, UNANSWERED1_COL, UNANSWERED2_COL, ANSWERED1_COL, ANSWERED2_COL,
    CARD_TERM_COL, CARD_DEF_COL, CARD_IDX_COL
)

class Question:
    """Base class for Question objects."""
    def __init__(self, text: str, correct_ans: str):
        self.text = text
        self.correct_ans = correct_ans
        self.user_ans: str | None = None

    @staticmethod
    def is_correct_answer(
        correct_ans: str, user_ans: str | None,
        smart_grading: bool = False,
        strictness: float = DEFAULT_SMART_GRADING_STRICTNESS
    ) -> bool:
        if user_ans is None:
            return False

        user_ans_clean = user_ans.strip().lower()
        correct_ans_clean = correct_ans.strip().lower()

        if smart_grading:
            similarity = difflib.SequenceMatcher(None, user_ans_clean, correct_ans_clean).ratio()
            return similarity >= strictness
        return user_ans_clean == correct_ans_clean

    def is_correct(self, smart_grading: bool = False,
                   strictness: float = DEFAULT_SMART_GRADING_STRICTNESS) -> bool:
        return Question.is_correct_answer(
            self.correct_ans, self.user_ans,
            smart_grading, strictness
        )

class MCQuestion(Question):
    def __init__(
            self, text: str, options: list[str], correct_ans: int):
        self.text = text
        self.options = options
        self.correct_ans: int = correct_ans  # Zero-based indices for MCQs
        self.user_ans: int | None = None     # None = no answer selected

    def is_correct(self) -> bool:
        if self.user_ans is None:
            return False
        return self.user_ans == self.correct_ans

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
        # Remove the current card's def
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
    display_status_bar(f"{deck.name} > Flashcards")

    shuffle_input = input(f"\n{WHITE}Shuffle cards before starting? (y/n) {ACCENT_COL}").strip().lower()
    shuffle: bool = shuffle_input == 'y'
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
                context = (f"{deck.name} > Flashcards > Card {i+1}/{len(cards_to_review)} > "
                           f"{len(learning_cards)} Learning | {len(known_cards)} Known")
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
                    exit_input = input(f"\n{LIGHT_GREY}Are you sure you want to exit? (y/n) {ACCENT_COL}").strip().lower()
                    if exit_input == 'y':
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
            display_status_bar(f"{deck.name} > Flashcards > Round Complete")
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

    # Config
    while True:
        clear_screen()
        display_status_bar(f"{deck.name} > Learn Mode > Setup")

        # Cards per round
        try:
            cards_per_round_str = input(f"{WHITE}How many cards per round? (1-{len(deck.cards)}) (default: {DEFAULT_CARDS_PER_ROUND}): {ACCENT_COL}")
            if not cards_per_round_str:
                cards_per_round = DEFAULT_CARDS_PER_ROUND
                break
            cards_per_round = int(cards_per_round_str)
            if 1 <= cards_per_round <= len(deck.cards):
                break
            print(f"{ERROR_COL}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")
        except ValueError:
            print(f"{ERROR_COL}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")

    # Get shuffle option
    shuffle_input = input(f"{WHITE}Shuffle cards? (y/n) (default: y) {ACCENT_COL}").strip().lower()
    shuffle = shuffle_input in ['y', '']

    # Get smart grading option
    smart_grading_input = input(f"{WHITE}Enable smart grading? (y/n) (default: y) {ACCENT_COL}").strip().lower()
    smart_grading = smart_grading_input in ['y', '']

    # Main loop
    while True:
        # Select cards
        learning_cards = [card for card in deck.cards if card.familiarity_level < len(FAMILIARITY_LEVELS)-1]

        # Display loop for if all cards are mastered
        if not learning_cards:
            while True:
                clear_screen()
                display_status_bar(f"{deck.name} > Learn Mode > Complete!")
                print(f"{SUCCESS_COL}You've mastered everything!{RESET}")
                print(f"\n{WHITE}What now?{RESET}")
                show_hotkey('r', 'reset card progress and restart')
                show_hotkey('q', 'return to menu')

                choice = cursor_input()

                # TODO: Add 'keep going' option that preserves progress but starts a new round
                if choice == 'r':
                    reset_progress_input = input(f"\n{BASE_COL}Are you sure you want to reset progress? (y/n) {ACCENT_COL}").strip().lower()
                    reset_progress = reset_progress_input == 'y'
                    if reset_progress:
                        # Reset mastery
                        for card in deck.cards:
                            card.familiarity_level = 0
                        break  # Go to beginning of main while loop
                elif choice == 'q':
                    return
            continue

        # Sort by familiarity to prioritise less known cards
        if shuffle:
            random.shuffle(learning_cards)
        else:
            learning_cards.sort(key=lambda card: card.familiarity_level)  # Weakest cards first

        # Take first few cards (weakest ones if not shuffled)
        round_cards = learning_cards[:cards_per_round]

        # Round loop
        for i, card in enumerate(round_cards):
            # Card UI
            clear_screen()
            display_status_bar(f"{deck.name} > Learn Mode > Card {i+1}/{len(round_cards)}")
            print(f"\n{CARD_TERM_COL}Term:      {BASE_COL}{card.term}\n")
            user_ans = input(f"{WHITE}Your Def: {ACCENT_COL}")

            # Grading
            is_correct_answer = Question.is_correct_answer(card.definition, user_ans, smart_grading)

            # TODO: smart grading strictness should be configurable via a ConfigObject

            # Feedback
            clear_screen()
            display_status_bar(f"{deck.name} > Learn Mode > Card {i+1}/{len(round_cards)}")
            print(f"\n{CARD_TERM_COL}Term: {BASE_COL}{card.term}\n")

            if is_correct_answer:
                card.on_correct()
                print(f"{SUCCESS_COL}Correct!{RESET}")
                if user_ans.strip().lower() == card.definition.strip().lower():
                    print(f"{LIGHT_GREY}Your answer:    {BASE_COL}{card.definition}")
                else:
                    print(f"{LIGHT_GREY}Your answer:    {BASE_COL}{user_ans}")
                    print(f"{LIGHT_GREY}Exact answer:   {BASE_COL}{card.definition}")
            else:
                card.on_incorrect()
                print(f"{ERROR_COL}Incorrect.{RESET}")
                print(f"{LIGHT_GREY}Your answer:    {BASE_COL}{user_ans}")
                print(f"{LIGHT_GREY}Correct answer: {BASE_COL}{card.definition}")

            print(f"{LIGHT_GREY}Familiarity: {FAMILIARITY_LEVELS[card.familiarity_level]}")
            input(f"\n{DARK_GREY}(Press Enter to continue){RESET}")

        # End of round display
        while True:
            clear_screen()
            display_status_bar(f"{deck.name} > Learn Mode > Round Complete")
            print(f"{SUCCESS_COL}Round Complete!{RESET}")
            print("\nWhat next?")
            show_hotkey('c', 'proceed to next round')
            show_hotkey('q', 'quit to menu')

            choice = cursor_input().lower()
            if choice == 'c':
                break
            elif choice == 'q':
                return

def test_mode(deck: Deck) -> None:
    if not deck.cards:
        input(f"{ERROR_COL}This deck has no cards to revise! {BASE_COL}(Enter to return)")
        return

    # Main loop
    while True:
        # Config
        while True:
            clear_screen()
            display_status_bar(f"{deck.name} > Test Mode > Setup")

            # Get number of questions
            while True:
                try:
                    num_questions_str = input(f"{WHITE}How many questions? (1-{len(deck.cards)}) (defualt: {DEFAULT_PRACTICE_TEST_LEN}): {ACCENT_COL}")
                    if not num_questions_str:
                        num_questions = min(DEFAULT_PRACTICE_TEST_LEN, len(deck.cards))  # TODO: Make this configurable
                        break
                    num_questions = int(num_questions_str)
                    if 1 <= num_questions <= len(deck.cards):
                        break
                    print(f"{ERROR_COL}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")
                except ValueError:
                    print(f"{ERROR_COL}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")

            # Get question type
            print(f"\n{WHITE}Select question type:{RESET}")  # TODO: User should be able to choose both MCQs and written questions
            print(f"{LIGHT_GREY}1    {BASE_COL}multiple choice")
            print(f"{LIGHT_GREY}2    {BASE_COL}written answer")

            question_type = cursor_input()

            if question_type == '1':
                if len(deck.cards) < NUM_MCQ_OPTIONS:
                    input(f"{ERROR_COL}Not enough cards for Multiple Choice (min {NUM_MCQ_OPTIONS}).{RESET} (Enter to continue)")
                    continue
                questions = gen_mcqs(deck, num_questions)
                break
            elif question_type == '2':
                questions = gen_written_qs(deck, num_questions)
                break
            else:
                input(f"{ERROR_COL}Invalid selection.{RESET} (Enter to continue)")
                continue

        current_q_idx = 0

        # Test taking display loop
        while True:
            current_q = questions[current_q_idx]

            clear_screen()
            display_status_bar(f"{deck.name} > Test Mode > Question {current_q_idx+1}/{len(questions)}")

            # Minimap
            print(f"{LIGHT_GREY}Minimap")
            minimap: str = ''
            for i, q in enumerate(questions):
                if i%40 == 0 and i != 0:
                    minimap += "\n"
                elif i%10 == 0 and i != 0:
                    minimap += " "  # Whitespace every 10th question for visual separation

                # Current question
                if i == current_q_idx:
                    colour = ACCENT_COL

                # Answered questions
                elif q.user_ans is not None:
                    colour = ANSWERED2_COL if i%2==0 else ANSWERED1_COL

                # Unanswered questions
                else:
                    colour = UNANSWERED2_COL if i%2==0 else UNANSWERED1_COL

                minimap += colour + "▆▆"
            print(minimap)

            print()
            show_hotkey('w', 'previous question')
            show_hotkey('s', 'next question')
            show_hotkey('e', 'edit answer')
            show_hotkey('r', 'submit test')
            show_hotkey('q', 'quit test')

            print(f"\n{ACCENT_COL}Question {current_q_idx+1}{DARK_GREY}/{len(questions)}")
            print(f"{BASE_COL}{current_q.text}")

            # MCQs
            if isinstance(current_q, MCQuestion):
                for i, option in enumerate(current_q.options, 1):
                    print(f"{CARD_IDX_COL}{i}. {CARD_DEF_COL}{option}")
                print()
                if current_q.user_ans is None:
                    print(f"{DARK_GREY}You haven't entered an answer yet!")
                else:
                    print(f"{LIGHT_GREY}Your answer: {BASE_COL}{current_q.user_ans+1}")
            # Written questions
            else:
                print()
                if current_q.user_ans is None:
                    print(f"{DARK_GREY}You haven't entered an answer yet!")
                else:
                    print(f"{LIGHT_GREY}Your answer: {BASE_COL}{current_q.user_ans}")

            key = cursor_input().lower()

            # Previous question
            if key == 'w':
                current_q_idx -= 1
                current_q_idx = max(0, current_q_idx)

            # Next question
            elif key == 's':
                current_q_idx += 1
                current_q_idx = min(len(questions)-1, current_q_idx)

            # Edit answer
            elif key == 'e':
                new_ans = input(f"\n{LIGHT_GREY}Enter your answer: {BASE_COL}")
                if isinstance(current_q, MCQuestion):
                    try:
                        current_q.user_ans = int(new_ans)
                        if not 1 <= current_q.user_ans <= NUM_MCQ_OPTIONS:
                            raise ValueError
                        current_q.user_ans -= 1
                    except ValueError:
                        current_q.user_ans = None
                        print(f"{ERROR_COL}Invalid: enter an integer from 1 to {NUM_MCQ_OPTIONS}.")
                else:
                    current_q.user_ans = new_ans

            # Submit test
            elif key == 'r':
                print()
                unanswered_count = sum(1 for q in questions if q.user_ans is None)
                if unanswered_count > 0:
                    print(f"{ACCENT_COL}You have {unanswered_count} unanswered question{'s' if unanswered_count > 1 else ''}.")
                submit_input = input(f"{BASE_COL}Are you sure you want to submit the test? (y/n) {ACCENT_COL}").strip().lower()
                if submit_input == 'y':
                    break

            # Quit test
            elif key == 'q':
                quit_input = input(f"\n{BASE_COL}Are you sure you want to quit? (you will lose your progress for this test) (y/n) {ACCENT_COL}").strip().lower()
                if quit_input == 'y':
                    return

        # Score and question display is precomputed outside the display
        # loop to avoid re-computing every keypress and wasting resources.
        score = sum(1 for q in questions if q.is_correct())
        score_frac = score / len(questions)
        question_display: str = ""
        for i, q in enumerate(questions):
            is_correct = q.is_correct()
            result_icon = f"{SUCCESS_COL}✔" if is_correct else f"{ERROR_COL}✘"
            question_display += f"{result_icon} {WHITE}Q{i+1}: {q.text}{RESET}\n"

            # Handle unanswered questions
            if q.user_ans is None:
                question_display += f"  {DARK_GREY}Unanswered.{RESET}\n\n"
                continue

            # Handle MCQs
            if isinstance(q, MCQuestion):
                user_idx = q.user_ans
                correct_idx = q.correct_ans
                if is_correct:
                    question_display += f"  {LIGHT_GREY}Your answer:    {SUCCESS_COL}({correct_idx + 1}) {q.options[correct_idx]}{RESET}\n\n"
                else:
                    question_display += f"  {LIGHT_GREY}Your answer:    {ERROR_COL}({q.user_ans + 1}) {q.options[user_idx]}{RESET}\n"
                    question_display += f"  {LIGHT_GREY}Correct answer: {SUCCESS_COL}({correct_idx + 1}) {q.options[correct_idx]}{RESET}\n\n"
                continue

            # Handle written questions
            is_exact_match = q.user_ans.strip().lower() == q.correct_ans.strip().lower()

            if is_correct:
                if is_exact_match:
                    # Correct and exact match
                    question_display += f"  {LIGHT_GREY}Your answer:    {SUCCESS_COL}{q.correct_ans}{RESET}\n\n"
                else:
                    # Correct due to Smart Grading
                    question_display += f"  {LIGHT_GREY}Your answer:    {SUCCESS_COL}{q.user_ans}{RESET}\n"
                    question_display += f"  {LIGHT_GREY}Exact answer:   {SUCCESS_COL}{q.correct_ans}{RESET}\n\n"
            else:
                # Incorrect
                question_display += f"  {LIGHT_GREY}Your answer:    {ERROR_COL}{q.user_ans}{RESET}\n"
                question_display += f"  {LIGHT_GREY}Correct answer: {SUCCESS_COL}{q.correct_ans}{RESET}\n\n"

        # Result display loop
        while True:
            clear_screen()
            display_status_bar(f"{deck.name} > Test Mode > Results")

            print(f"\n{WHITE}Test Complete!")
            print(f"{BASE_COL}Your score is {SUCCESS_COL if score == len(questions) else ACCENT_COL}{score}/{len(questions)} {DARK_GREY}({score_frac:.2%}){RESET}\n")

            print(question_display)  # FIXME: Question display sometimes wraps weird

            print(f"\n{WHITE}What next?{RESET}")
            # TODO: add retry with same settings option
            show_hotkey('n', 'new test')
            show_hotkey('q', 'quit to menu')

            choice = cursor_input().lower()

            if choice == 'n':
                break
            elif choice == 'q':
                return
