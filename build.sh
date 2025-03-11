#!/usr/bin/env bash

# Install the required Python version
pyenv install 3.13.0
pyenv global 3.13.0

# Install dependencies from requirements.txt
pip install --no-cache-dir --force-reinstall -r requirements.txt
