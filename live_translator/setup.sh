#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Creating virtual environment in $DIR/venv..."
python3 -m venv "$DIR/venv"
echo "Installing dependencies..."
"$DIR/venv/bin/pip" install -r "$DIR/requirements.txt"
echo "Setup complete. Use ./run.sh to start the application."
