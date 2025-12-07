import os
from tui.colours import LGREY, BASE_COL

def clear_screen(full=False) -> None:
    if full:
        os.system('cls' if os.name == 'nt' else 'clear')
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    print("\033[H\033[J")

def show_hotkey(
        hotkey: str, desc: str,
        hotkey_col=LGREY, desc_col=BASE_COL
    ):
    print(f"{hotkey_col}{hotkey:<4}{desc_col}{desc}")