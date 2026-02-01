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

"""
This module provides a custom exception hook to log unhandled exceptions
to a file with specific formatting, while ignoring user-initiated exits.
"""

import os
import sys
import traceback
from datetime import datetime
from pystudy_cli.core.constants import FALLBACK_STATUS_BAR_WIDTH
from pystudy_cli.core import paths

# Store the original excepthook
original_excepthook = sys.excepthook

def custom_excepthook(exc_type, exc_value, exc_tb):
    """
    Custom exception hook to log unhandled exceptions to a file,
    ignoring KeyboardInterrupt and EOFError.
    """

    # Excepthook has its own copy of the colour function
    def col(code: int, bg: bool = False): # 256 colours
        return f"\033[{48 if bg else 38};5;{code}m"

    # Ignore user-initiated exits
    if issubclass(exc_type, (KeyboardInterrupt, EOFError)):
        # Call the original hook to preserve default exit behavior
        original_excepthook(exc_type, exc_value, exc_tb)
        sys.exit(1)

    # Get terminal width for the separator, with a fallback
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = FALLBACK_STATUS_BAR_WIDTH

    separator = "=" * width

    # Format the timestamp as requested: DD/MM/YY @ HH:MM am/pm
    timestamp = datetime.now().strftime("%d/%m/%y @ %I:%M %p").lower()

    # Format the traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    formatted_traceback = "".join(tb_lines)

    # Construct the full log message
    log_message = (
        f"{timestamp}\n\n"
        f"{separator}\n"
        f"{formatted_traceback}"
        f"{separator}\n\n"
    )

    # Append to the log file
    with open(paths.ROOT_DIR / "traceback.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_message)

    # Also print to stderr so the user sees the error in the console
    print(f"\n{col(197)}!{col(189)}  Oops, something went wrong!")
    print(f"{col(220)}i{col(189)}  A 'traceback.log' file has been created.")
    print(f"{col(220)}i{col(189)}  For support, contact Louis @ <...> and attach the 'traceback.log' file.")  # TODO: add contact
    print(f"\n{col(220)}i{col(189)}  Full traceback (for nerds)")
    print(col(146) + log_message, file=sys.stderr)

    sys.exit(1)

def setup_traceback_logger():
    """Assigns the custom exception hook to sys.excepthook."""
    sys.excepthook = custom_excepthook
