#!/usr/bin/env python3

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
import sys
from typing import Callable, Literal

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from pystudy_cli.core.traceback_logger import setup_traceback_logger

UI = Literal["tui", "gui"]

def get_runner(ui: UI) -> Callable[[], None]:
    if ui == "tui":
        from pystudy_cli.tui.run_tui import main as _run
    elif ui == "gui":
        from pystudy_cli.gui.run_gui import main as _run
    else:
        raise ValueError(f"Bro I can't find the UI ({ui}), are you mad?!")

    return _run

def main():
    setup_traceback_logger()
    runner = get_runner("tui")
    runner()

if __name__ == "__main__":
    main()
