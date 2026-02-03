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

from typing import Callable

from readchar import readkey

from pystudy_cli.core.profile import StudyProfile
from pystudy_cli.tui.colours import (
    COL_ACCENT,
    COL_BASE,
    COL_LIGHT_GREY,
    col,
)
from pystudy_cli.tui.ui_elements import (
    clear_screen,
    display_status_bar,
)

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
