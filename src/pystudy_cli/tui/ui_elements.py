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
from readchar import readkey
from pystudy_cli.tui.colours import LIGHT_GREY, BASE_COL, ACCENT_COL, WHITE, RESET, TITLE_COL
from pystudy_cli.core.constants import VERSION_NUM, FALLBACK_STATUS_BAR_WIDTH
from datetime import datetime

def int_convertible(string: str) -> bool:
    """Check if a string is integer-convertible."""
    try:
        int(string)
        return True
    except ValueError:
        return False

def cursor_input():
    print(f"{ACCENT_COL}>{WHITE} ", end='', flush=True)
    action = readkey()
    print(action)

    return action

def clear_screen(full=False) -> None:
    if full:
        os.system('cls' if os.name == 'nt' else 'clear')
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    print("\033[H\033[J", end='')

def show_hotkey(
        hotkey: str, desc: str, alignment=5,
        hotkey_col=LIGHT_GREY, desc_col=BASE_COL
    ):
    print(f"{hotkey_col}{hotkey:<{alignment}}{desc_col}{desc}{BASE_COL}")

def display_status_bar(context_text: str = ""):
    """Displays a status bar at the top of the screen with centered context."""
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = FALLBACK_STATUS_BAR_WIDTH

    # 1. Create uncoloured components
    version_str = f"PyStudy CLI v{VERSION_NUM}"
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
            f"{TITLE_COL}{version_str}{RESET}"
            f"{' ' * left_ws_len}"
            f"{BASE_COL}{context_text}{RESET}"
            f"{' ' * right_ws_len}"
            f"{ACCENT_COL}{time_str}{RESET}"
        )
    else:  # No context text, just left and right align version and time
        spacing = width - (len(version_str) + len(time_str))
        if spacing < 0:
            spacing = 0

        bar = (
            f"{TITLE_COL}{version_str}{RESET}"
            f"{' ' * spacing}"
            f"{ACCENT_COL}{time_str}{RESET}"
        )

    print(bar)
    print(f"{ACCENT_COL}{'─' * width}{RESET}")
