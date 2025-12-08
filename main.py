from typing import Literal, Callable
from core.traceback_logger import setup_traceback_logger

UI = Literal["tui", "gui"]

def get_runner(ui: UI) -> Callable[[], None]:
    if ui == "tui":
        from tui.run_tui import main as _run
    elif ui == "gui":
        from gui.run_gui import main as _run
    else:
        raise ValueError(f"Bro I can't find the UI ({ui}), are you mad?!")

    return _run

def main():
    setup_traceback_logger()
    runner = get_runner("tui")
    runner()

if __name__ == "__main__":
    main()