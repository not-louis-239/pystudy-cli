import os
from readchar import readkey
from tui.colours import LIGHT_GREY, BASE_COL, ACCENT_COL, WHITE, RESET, TITLE_COL
from core.constants import VERSION_NUM
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
        hotkey: str, desc: str, alignment=4,
        hotkey_col=LIGHT_GREY, desc_col=BASE_COL
    ):
    print(f"{hotkey_col}{hotkey:<{alignment}}{desc_col}{desc}{BASE_COL}")

def display_status_bar(context_text: str = ""):
    """Displays a status bar at the top of the screen."""
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80

    version_str = f"Python Study Suite v{VERSION_NUM}"
    time_str = datetime.now().strftime('%H:%M')  # TODO: add to config: show time as 24-hour time (bool)

    full_right_str = f"{context_text} | {time_str}" if context_text else time_str
    spacing = width - len(version_str) - len(full_right_str)

    if spacing < 1:
        spacing = 1

    print(f"{TITLE_COL}{version_str}{' ' * spacing}{ACCENT_COL}{full_right_str}{RESET}")
    print(f"{ACCENT_COL}{'─' * width}{RESET}")
