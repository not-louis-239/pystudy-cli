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

from pystudy_cli.core.data_manager import load_profile, save_profile, LoadStatCategory
from pystudy_cli.tui.colours import (
    COL_ACCENT,
    COL_BASE,
    COL_DARK_GREY,
    COL_ERROR,
    COL_LIGHT_GREY,
    COL_SUCCESS,
    COL_WHITE,
    RESET,
)
from pystudy_cli.tui.ui_elements import (
    clear_screen,
)
from pystudy_cli.tui.states.input_loop import input_loop

def main():
    # Load data
    clear_screen()
    print(f"{COL_DARK_GREY}Loading data...{COL_BASE}")
    profile, status = load_profile()

    if status.category == LoadStatCategory.SUCCESS:
        print(f"{COL_SUCCESS}Data loaded!{COL_BASE}")
    elif status.category == LoadStatCategory.NEW:
        print(f"{COL_ERROR}No data file found. {COL_LIGHT_GREY}Making a new one...{COL_BASE}")
    elif status.category == LoadStatCategory.CORRUPT:
        print(f"{COL_ERROR}Data file seems corrupted. {COL_LIGHT_GREY}Making a new one...{COL_BASE}")
    else:
        print(f"{COL_ERROR}Unexpected error: {COL_WHITE}{status.msg}{COL_ERROR}. {COL_LIGHT_GREY}Making a new file...{COL_BASE}")

    if profile.config.warn_interrupt:
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
            save_profile(profile)
        except (KeyboardInterrupt, EOFError):
            print(f"{COL_ERROR}Interrupted!")
            print(f"\n{COL_LIGHT_GREY}Attempting panic save...{COL_BASE}")

            try:
                save_profile(profile)
                print(f"{COL_SUCCESS}Data saved! {RESET}But don't push your luck next time!")
                print(f"{COL_ERROR}Panic save may contain malformed data.")
            except Exception:
                print(f"{COL_ERROR}Panic save failed. Your fault bucko!{RESET}")
            finally:
                sys.exit(1)

if __name__ == "__main__":
    main()
