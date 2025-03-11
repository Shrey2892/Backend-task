#!/usr/bin/env bash

# Ensure the correct Python version is used (Render should pick from runtime.txt)
python --version

# Install dependencies
pip install --no-cache-dir --force-reinstall -r requirements.txt
