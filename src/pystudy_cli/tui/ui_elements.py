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

import os
from typing import Any
from datetime import datetime

import readchar

from pystudy_cli.core.constants import FALLBACK_STATUS_BAR_WIDTH
from pystudy_cli.tui.colours import (
    COL_ACCENT,
    COL_BASE,
    COL_LIGHT_GREY,
    COL_TITLE,
    COL_WHITE,
    RESET,
)


def int_convertible(val: Any, /) -> bool:
    """Check if a value is integer-convertible."""
    try:
        int(val)
        return True
    except (ValueError, TypeError):
        return False

def cursor_input():
    print(f"{COL_ACCENT}>{COL_WHITE} ", end='', flush=True)
    action = readchar.readkey()
    print(action)

    return action

def clear_screen(*, full_clear=False) -> None:
    if full_clear:
        os.system('cls' if os.name == 'nt' else 'clear')
        os.system('cls' if os.name == 'nt' else 'clear')
        return

    print("\033[H\033[J", end='')

def show_hotkey(
        hotkey: str, desc: str, alignment=5,
        hotkey_col=COL_LIGHT_GREY, desc_col=COL_BASE
    ):
    print(f"{hotkey_col}{hotkey:<{alignment}}{desc_col}{desc}{COL_BASE}")

def display_status_bar(context_text: str = ""):
    """Displays a status bar at the top of the screen with centered context."""
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = FALLBACK_STATUS_BAR_WIDTH

    # 1. Create uncoloured components
    version_str = "PyStudy CLI"
    time_str = datetime.now().strftime('%H:%M')

    # 2. Calculate layout
    if context_text:
        len_version = len(version_str)
        len_context = len(context_text)
        len_time = len(time_str)

        total_padding = width - (len_version + len_context + len_time)
        if total_padding < 0:
            total_padding = 0

        left_ws_len = total_padding // 2
        right_ws_len = total_padding - left_ws_len

        # Truncate context if needed
        if width < 50 and len(context_text) > 20:
            context_text = context_text[:17] + "..."

        # Assemble and colour final bar
        bar = (
            f"{COL_TITLE}{version_str}{RESET}"
            f"{' ' * left_ws_len}"
            f"{COL_BASE}{context_text}{RESET}"
            f"{' ' * right_ws_len}"
            f"{COL_ACCENT}{time_str}{RESET}"
        )
    else:  # No context text, just left and right align version and time
        spacing = width - (len(version_str) + len(time_str))
        if spacing < 0:
            spacing = 0

        bar = (
            f"{COL_TITLE}{version_str}{RESET}"
            f"{' ' * spacing}"
            f"{COL_ACCENT}{time_str}{RESET}"
        )

    print(bar)
    print(f"{COL_ACCENT}{'─' * width}{RESET}")
