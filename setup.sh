#!/usr/bin/env bash
# Creates the venv (if missing) and installs dependencies.
# Run with `source setup.sh` (not `./setup.sh`) so the venv stays active
# in your current shell afterward.
set -e

if [ ! -d venv ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "venv ready and activated. In new shells, run: source venv/bin/activate"
