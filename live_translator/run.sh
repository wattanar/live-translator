#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export OMP_NUM_THREADS=4
source "$DIR/venv/bin/activate"
python3 "$DIR/main.py" "$@"
