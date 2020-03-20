#!/usr/bin/env bash
# If you have multiple version of python3, you can export PYTHON3_BIN to determine which you want to use
export PYTHON3_BIN=${PYTHON3_BIN:-"python3"}

if [ ! -d "$HOME/.virtualenvs/synth-pops" ]; then
  echo "Creating virtual at ~/.virtualenvs/synth-pops using $PYTHON3_BIN -m venv ~/.virtualenvs/synth-pops"
  $PYTHON3_BIN -m venv ~/.virtualenvs/synth-pops || rm -rf ~/.virtualenvs/synth-pops

  if [ -f ~/.virtualenvs/synth-pops/bin/activate ]; then
    source ~/.virtualenvs/synth-pops/bin/activate
    pip install wheel
    pip install -e .
  else
    echo "ERROR Installing virtualenv. Check output"
  fi
fi

echo "Activating environment. This will only work if you called this script in the follow manners"
echo ". ./bootstrap.sh"
echo "or"
echo "source ./bootstrap.sh"

if [ -f ~/.virtualenvs/synth-pops/bin/activate ]; then
  source ~/.virtualenvs/synth-pops/bin/activate
else
  echo "ERROR: Virtual Environment not found!"
fi