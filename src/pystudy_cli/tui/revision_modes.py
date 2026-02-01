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

import difflib
import random

from pystudy_cli.core.constants import (
    DEFAULT_CARDS_PER_ROUND,
    DEFAULT_PRACTICE_TEST_LEN,
    DEFAULT_SMART_GRADING_STRICTNESS,
    FAMILIARITY_LEVELS,
    NUM_MCQ_OPTIONS,
)
from pystudy_cli.core.objects import Deck
from pystudy_cli.tui.colours import (
    COL_ACCENT,
    COL_ANSWERED1,
    COL_ANSWERED2,
    COL_BASE,
    COL_CARD_DEF,
    COL_CARD_INDEX,
    COL_CARD_TERM,
    COL_DARK_GREY,
    COL_ERROR,
    COL_LEARNING,
    COL_LIGHT_GREY,
    COL_SUCCESS,
    COL_UNANSWERED1,
    COL_UNANSWERED2,
    COL_WHITE,
    RESET,
)
from pystudy_cli.tui.ui_elements import (
    clear_screen,
    cursor_input,
    display_status_bar,
    show_hotkey,
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
        input(f"{COL_ERROR}This deck has no cards to revise! {COL_BASE}(Enter to return)")
        return

    # Setup
    cards_to_review = list(deck.cards)

    clear_screen()
    display_status_bar(f"{deck.name} > Flashcards")

    shuffle_input = input(f"\n{COL_WHITE}Shuffle cards before starting? (y/n) {COL_ACCENT}").strip().lower()
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
                print(f"{COL_CARD_TERM}Term: {COL_BASE}{card.term}")
                if revealed:
                    print(f"{COL_CARD_DEF}Def:  {COL_BASE}{card.definition}\n")
                    show_hotkey('l', f'mark {COL_LEARNING}learning')
                    show_hotkey('k', f'mark {COL_SUCCESS}known')
                    show_hotkey('q', 'exit session')
                else:
                    print(f"{COL_CARD_DEF}Def:  {COL_DARK_GREY}(Press space to reveal){COL_BASE}\n")
                    show_hotkey('space', 'reveal', 9)
                    show_hotkey('q', 'exit session', 9)

                key = cursor_input()

                if key == 'q':
                    exit_input = input(f"\n{COL_LIGHT_GREY}Are you sure you want to exit? (y/n) {COL_ACCENT}").strip().lower()
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
            print(f"{COL_SUCCESS}Round Complete!{RESET}\n")
            print(f"{COL_WHITE}* {COL_LEARNING}Learning: {COL_BASE}{len(learning_cards)} cards")
            print(f"{COL_WHITE}* {COL_SUCCESS}Known:    {COL_BASE}{len(known_cards)} cards")

            # All cards known
            if not learning_cards:
                print(f"\n{COL_SUCCESS}Congratulations! {COL_ACCENT}You've learned all the cards in this session!{RESET}")
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
            print(f"\n{COL_WHITE}What next?{RESET}")
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
        input(f"{COL_ERROR}This deck has no cards to revise! {COL_BASE}(Enter to return)")
        return

    # Config
    while True:
        clear_screen()
        display_status_bar(f"{deck.name} > Learn Mode > Setup")

        # Cards per round
        try:
            cards_per_round_str = input(f"{COL_WHITE}How many cards per round? (1-{len(deck.cards)}) (default: {DEFAULT_CARDS_PER_ROUND}): {COL_ACCENT}")
            if not cards_per_round_str:
                cards_per_round = DEFAULT_CARDS_PER_ROUND
                break
            cards_per_round = int(cards_per_round_str)
            if 1 <= cards_per_round <= len(deck.cards):
                break
            print(f"{COL_ERROR}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")
        except ValueError:
            print(f"{COL_ERROR}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")

    # Get shuffle option
    shuffle_input = input(f"{COL_WHITE}Shuffle cards? (y/n) (default: y) {COL_ACCENT}").strip().lower()
    shuffle = shuffle_input in ['y', '']

    # Get smart grading option
    smart_grading_input = input(f"{COL_WHITE}Enable smart grading? (y/n) (default: y) {COL_ACCENT}").strip().lower()
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
                print(f"{COL_SUCCESS}You've mastered everything!{RESET}")
                print(f"\n{COL_WHITE}What now?{RESET}")
                show_hotkey('r', 'reset card progress and restart')
                show_hotkey('q', 'return to menu')

                choice = cursor_input()

                # TODO: Add 'keep going' option that preserves progress but starts a new round
                if choice == 'r':
                    reset_progress_input = input(f"\n{COL_BASE}Are you sure you want to reset progress? (y/n) {COL_ACCENT}").strip().lower()
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
            print(f"\n{COL_CARD_TERM}Term:      {COL_BASE}{card.term}\n")
            user_ans = input(f"{COL_WHITE}Your Def: {COL_ACCENT}")

            # Grading
            is_correct_answer = Question.is_correct_answer(card.definition, user_ans, smart_grading)

            # TODO: smart grading strictness should be configurable via a ConfigObject

            # Feedback
            clear_screen()
            display_status_bar(f"{deck.name} > Learn Mode > Card {i+1}/{len(round_cards)}")
            print(f"\n{COL_CARD_TERM}Term: {COL_BASE}{card.term}\n")

            if is_correct_answer:
                card.on_correct()
                print(f"{COL_SUCCESS}Correct!{RESET}")
                if user_ans.strip().lower() == card.definition.strip().lower():
                    print(f"{COL_LIGHT_GREY}Your answer:    {COL_BASE}{card.definition}")
                else:
                    print(f"{COL_LIGHT_GREY}Your answer:    {COL_BASE}{user_ans}")
                    print(f"{COL_LIGHT_GREY}Exact answer:   {COL_BASE}{card.definition}")
            else:
                card.on_incorrect()
                print(f"{COL_ERROR}Incorrect.{RESET}")
                print(f"{COL_LIGHT_GREY}Your answer:    {COL_BASE}{user_ans}")
                print(f"{COL_LIGHT_GREY}Correct answer: {COL_BASE}{card.definition}")

            print(f"{COL_LIGHT_GREY}Familiarity: {FAMILIARITY_LEVELS[card.familiarity_level]}")
            input(f"\n{COL_DARK_GREY}(Press Enter to continue){RESET}")

        # End of round display
        while True:
            clear_screen()
            display_status_bar(f"{deck.name} > Learn Mode > Round Complete")
            print(f"{COL_SUCCESS}Round Complete!{RESET}")
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
        input(f"{COL_ERROR}This deck has no cards to revise! {COL_BASE}(Enter to return)")
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
                    num_questions_str = input(f"{COL_WHITE}How many questions? (1-{len(deck.cards)}) (defualt: {DEFAULT_PRACTICE_TEST_LEN}): {COL_ACCENT}")
                    if not num_questions_str:
                        num_questions = min(DEFAULT_PRACTICE_TEST_LEN, len(deck.cards))  # TODO: Make this configurable
                        break
                    num_questions = int(num_questions_str)
                    if 1 <= num_questions <= len(deck.cards):
                        break
                    print(f"{COL_ERROR}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")
                except ValueError:
                    print(f"{COL_ERROR}Invalid: please enter an integer between 1 and {len(deck.cards)}.{RESET}")

            # Get question type
            print(f"\n{COL_WHITE}Select question type:{RESET}")  # TODO: User should be able to choose both MCQs and written questions
            print(f"{COL_LIGHT_GREY}1    {COL_BASE}multiple choice")
            print(f"{COL_LIGHT_GREY}2    {COL_BASE}written answer")

            question_type = cursor_input()

            if question_type == '1':
                if len(deck.cards) < NUM_MCQ_OPTIONS:
                    input(f"{COL_ERROR}Not enough cards for Multiple Choice (min {NUM_MCQ_OPTIONS}).{RESET} (Enter to continue)")
                    continue
                questions = gen_mcqs(deck, num_questions)
                break
            elif question_type == '2':
                questions = gen_written_qs(deck, num_questions)
                break
            else:
                input(f"{COL_ERROR}Invalid selection.{RESET} (Enter to continue)")
                continue

        current_q_idx = 0

        # Test taking display loop
        while True:
            current_q = questions[current_q_idx]

            clear_screen()
            display_status_bar(f"{deck.name} > Test Mode > Question {current_q_idx+1}/{len(questions)}")

            # Minimap
            print(f"{COL_LIGHT_GREY}Minimap")
            minimap: str = ''
            for i, q in enumerate(questions):
                if i%40 == 0 and i != 0:
                    minimap += "\n"
                elif i%10 == 0 and i != 0:
                    minimap += " "  # Whitespace every 10th question for visual separation

                # Current question
                if i == current_q_idx:
                    colour = COL_ACCENT

                # Answered questions
                elif q.user_ans is not None:
                    colour = COL_ANSWERED2 if i%2==0 else COL_ANSWERED1

                # Unanswered questions
                else:
                    colour = COL_UNANSWERED2 if i%2==0 else COL_UNANSWERED1

                minimap += colour + "▆▆"
            print(minimap)

            print()
            show_hotkey('w', 'previous question')
            show_hotkey('s', 'next question')
            show_hotkey('e', 'edit answer')
            show_hotkey('r', 'submit test')
            show_hotkey('q', 'quit test')

            print(f"\n{COL_ACCENT}Question {current_q_idx+1}{COL_DARK_GREY}/{len(questions)}")
            print(f"{COL_BASE}{current_q.text}")

            # MCQs
            if isinstance(current_q, MCQuestion):
                for i, option in enumerate(current_q.options, 1):
                    print(f"{COL_CARD_INDEX}{i}. {COL_CARD_DEF}{option}")
                print()
                if current_q.user_ans is None:
                    print(f"{COL_DARK_GREY}You haven't entered an answer yet!")
                else:
                    print(f"{COL_LIGHT_GREY}Your answer: {COL_BASE}{current_q.user_ans+1}")
            # Written questions
            else:
                print()
                if current_q.user_ans is None:
                    print(f"{COL_DARK_GREY}You haven't entered an answer yet!")
                else:
                    print(f"{COL_LIGHT_GREY}Your answer: {COL_BASE}{current_q.user_ans}")

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
                new_ans = input(f"\n{COL_LIGHT_GREY}Enter your answer: {COL_BASE}")
                if isinstance(current_q, MCQuestion):
                    try:
                        current_q.user_ans = int(new_ans)
                        if not 1 <= current_q.user_ans <= NUM_MCQ_OPTIONS:
                            raise ValueError
                        current_q.user_ans -= 1
                    except ValueError:
                        current_q.user_ans = None
                        print(f"{COL_ERROR}Invalid: enter an integer from 1 to {NUM_MCQ_OPTIONS}.")
                else:
                    current_q.user_ans = new_ans

            # Submit test
            elif key == 'r':
                print()
                unanswered_count = sum(1 for q in questions if q.user_ans is None)
                if unanswered_count > 0:
                    print(f"{COL_ACCENT}You have {unanswered_count} unanswered question{'s' if unanswered_count > 1 else ''}.")
                submit_input = input(f"{COL_BASE}Are you sure you want to submit the test? (y/n) {COL_ACCENT}").strip().lower()
                if submit_input == 'y':
                    break

            # Quit test
            elif key == 'q':
                quit_input = input(f"\n{COL_BASE}Are you sure you want to quit? (you will lose your progress for this test) (y/n) {COL_ACCENT}").strip().lower()
                if quit_input == 'y':
                    return

        # Score and question display is precomputed outside the display
        # loop to avoid re-computing every keypress and wasting resources.
        score = sum(1 for q in questions if q.is_correct())
        score_frac = score / len(questions)
        question_display: str = ""
        for i, q in enumerate(questions):
            is_correct = q.is_correct()
            result_icon = f"{COL_SUCCESS}✔" if is_correct else f"{COL_ERROR}✘"
            question_display += f"{result_icon} {COL_WHITE}Q{i+1}: {q.text}{RESET}\n"

            # Handle unanswered questions
            if q.user_ans is None:
                question_display += f"  {COL_DARK_GREY}Unanswered.{RESET}\n\n"
                continue

            # Handle MCQs
            if isinstance(q, MCQuestion):
                user_idx = q.user_ans
                correct_idx = q.correct_ans
                if is_correct:
                    question_display += f"  {COL_LIGHT_GREY}Your answer:    {COL_SUCCESS}({correct_idx + 1}) {q.options[correct_idx]}{RESET}\n\n"
                else:
                    question_display += f"  {COL_LIGHT_GREY}Your answer:    {COL_ERROR}({q.user_ans + 1}) {q.options[user_idx]}{RESET}\n"
                    question_display += f"  {COL_LIGHT_GREY}Correct answer: {COL_SUCCESS}({correct_idx + 1}) {q.options[correct_idx]}{RESET}\n\n"
                continue

            # Handle written questions
            is_exact_match = q.user_ans.strip().lower() == q.correct_ans.strip().lower()

            if is_correct:
                if is_exact_match:
                    # Correct and exact match
                    question_display += f"  {COL_LIGHT_GREY}Your answer:    {COL_SUCCESS}{q.correct_ans}{RESET}\n\n"
                else:
                    # Correct due to Smart Grading
                    question_display += f"  {COL_LIGHT_GREY}Your answer:    {COL_SUCCESS}{q.user_ans}{RESET}\n"
                    question_display += f"  {COL_LIGHT_GREY}Exact answer:   {COL_SUCCESS}{q.correct_ans}{RESET}\n\n"
            else:
                # Incorrect
                question_display += f"  {COL_LIGHT_GREY}Your answer:    {COL_ERROR}{q.user_ans}{RESET}\n"
                question_display += f"  {COL_LIGHT_GREY}Correct answer: {COL_SUCCESS}{q.correct_ans}{RESET}\n\n"

        # Result display loop
        while True:
            clear_screen()
            display_status_bar(f"{deck.name} > Test Mode > Results")

            print(f"\n{COL_WHITE}Test Complete!")
            print(f"{COL_BASE}Your score is {COL_SUCCESS if score == len(questions) else COL_ACCENT}{score}/{len(questions)} {COL_DARK_GREY}({score_frac:.2%}){RESET}\n")

            print(question_display)  # FIXME: Question display sometimes wraps weird

            print(f"\n{COL_WHITE}What next?{RESET}")
            # TODO: add retry with same settings option
            show_hotkey('n', 'new test')
            show_hotkey('q', 'quit to menu')

            choice = cursor_input().lower()

            if choice == 'n':
                break
            elif choice == 'q':
                return
