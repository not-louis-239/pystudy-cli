import os
from readchar import readkey
from tui.colours import LGREY, BASE_COL, AQUAMARINE, WHITE

def int_convertible(string: str) -> bool:
    """Check if a string is integer-convertible."""
    try:
        int(string)
        return True
    except ValueError:
        return False

def cursor_input():
    print(f"{AQUAMARINE}>{WHITE} ", end='', flush=True)
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
        hotkey_col=LGREY, desc_col=BASE_COL
    ):
    print(f"{hotkey_col}{hotkey:<{alignment}}{desc_col}{desc}")