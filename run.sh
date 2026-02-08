#!/bin/bash
# Convenient script to run Rheolwyr from source
# This correctly sets up the PYTHONPATH so relative imports work

# Determine the absolute path to this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

if [ ! -d "$PROJECT_ROOT/src" ]; then
    echo "Error: src directory not found in $PROJECT_ROOT"
    exit 1
fi

export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Run the module
python3 -m rheolwyr.main "$@"
