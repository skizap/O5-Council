#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3.11}"
VENV_DIR="${VENV_DIR:-.venv}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: $PYTHON_BIN is not available on this system."
  exit 1
fi

echo "Creating virtual environment in $VENV_DIR"
"$PYTHON_BIN" -m venv "$VENV_DIR"

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Upgrading pip"
pip install --upgrade pip

echo "Installing O5 Council in editable mode"
pip install -e .

echo
echo "Installation complete."
echo "Activate the environment with: source $VENV_DIR/bin/activate"
echo "Launch the app with: o5-council"
