"""
This module provides a custom exception hook to log unhandled exceptions
to a file with specific formatting, while ignoring user-initiated exits.
"""

import sys
import traceback
import os
from datetime import datetime

# Store the original excepthook
original_excepthook = sys.excepthook

def custom_excepthook(exc_type, exc_value, exc_tb):
    """
    Custom exception hook to log unhandled exceptions to a file,
    ignoring KeyboardInterrupt and EOFError.
    """
    # Ignore user-initiated exits
    if issubclass(exc_type, (KeyboardInterrupt, EOFError)):
        # Call the original hook to preserve default exit behavior
        original_excepthook(exc_type, exc_value, exc_tb)
        return

    # Get terminal width for the separator, with a fallback
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80

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
    with open("traceback.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_message)

    # Also print to stderr so the user sees the error in the console
    print(log_message, file=sys.stderr)


def setup_traceback_logger():
    """
    Assigns the custom exception hook to sys.excepthook.
    """
    sys.excepthook = custom_excepthook
