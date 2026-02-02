#!/bin/bash

# Config
PYTHON_VERSION="3.14"
VENV_DIR=".venv"
MAIN_SCRIPT="main.py"
REQUIREMENTS_FILE="requirements.txt"

## Functions

# Check if a command exists
command_exists() {
    type "$1" &> /dev/null ;
}

# Main
main() {
    # Check for Python
    echo "Checking for Python ${PYTHON_VERSION}..."
    if ! command_exists "python${PYTHON_VERSION}"; then
        echo "Error: Python ${PYTHON_VERSION} is not installed." >&2
        echo "Please install Python ${PYTHON_VERSION} from https://python.org before running this script." >&2
        exit 1
    fi
    echo "Python ${PYTHON_VERSION} found successfully."

    echo "Checking for virtual environment..."

    # Create and activate virtual environment
    if [ ! -d "${VENV_DIR}" ]; then
        # Make virtual environment if it doesn't exist
        echo "Creating virtual environment in ${VENV_DIR}..."
        "python${PYTHON_VERSION}" -m venv "${VENV_DIR}"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to create virtual environment." >&2
            exit 1
        fi
        echo "Virtual environment created."
    else
        echo "Virtual environment found in ${VENV_DIR}."
    fi

    echo "Activating virtual environment..."
    source "${VENV_DIR}/bin/activate"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to activate virtual environment." >&2
        exit 1
    fi
    echo "Virtual environment activated."

    # Install dependencies if requirements.txt exists and pip is available
    if [ -f "${REQUIREMENTS_FILE}" ]; then
        echo "Checking for and installing dependencies from ${REQUIREMENTS_FILE}..."

        if command_exists "pip"; then
            if ! pip check &> /dev/null; then
                echo "Installing/updating dependencies..."
                pip install -r "${REQUIREMENTS_FILE}"
                if [ $? -ne 0 ]; then
                    echo "Error: Failed to install dependencies." >&2
                    deactivate
                    exit 1
                fi
                echo "Dependencies installed/updated."
            else
                echo "Dependencies already satisfied."
            fi
        else
            echo "Error: pip not found in virtual environment: failed to install dependencies." >&2
            deactivate
            exit 1
        fi
    else
        echo "No ${REQUIREMENTS_FILE} found. Cannot install dependencies."
        deactivate
        exit 1
    fi

    # Run the main application
    python "${MAIN_SCRIPT}" || python3 "${MAIN_SCRIPT}"  # try python3 if python fails
    APP_EXIT_CODE=$?

    # Deactivate virtual environment
    echo "Deactivating virtual environment..."
    deactivate
    if [ $? -ne 0 ]; then
        echo "Warning: Failed to deactivate virtual environment. Please run 'deactivate' manually." >&2
    fi

    echo "PyStudy CLI program finished with exit code ${APP_EXIT_CODE}."
    exit ${APP_EXIT_CODE}
}

# Call main with all script arguments
main "$@"
