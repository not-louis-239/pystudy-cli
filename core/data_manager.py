"""A bare file manager. Works with JSON only."""

import json
import copy
from core.constants import NEW_STATE

def save_data(data: dict, filename="save_data.json") -> str:
    """
    WARNING: data must be serialised first or else this function
    will throw an exception and potentially corrupt save data.

    Returns a string status code to indicate success or error
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return "success"
    except Exception as e:
        return str(e)

def load_data(filename="save_data.json") -> tuple[dict, str]:
    """
    Load JSON data from a file and sync keys with NEW_STATE.

    Returns a tuple:
    * state dict
    * status string
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            state = json.load(f)
        status = "success"
    except FileNotFoundError:
        state = copy.deepcopy(NEW_STATE)
        status = "new"
    except json.JSONDecodeError:
        state = copy.deepcopy(NEW_STATE)
        status = "corrupted"
    except Exception as e:
        state = copy.deepcopy(NEW_STATE)
        status = str(e)

    # Add missing keys
    for k in NEW_STATE.keys():
        if k not in state:
            state[k] = NEW_STATE[k]

    # Remove deprecated keys
    for k in list(state.keys()):
        if k not in NEW_STATE:
            del state[k]

    return state, status
